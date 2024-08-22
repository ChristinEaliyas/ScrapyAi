import torch
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

# Set device to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

filename = 'quantitative-aptitude-ramandeep-singh.pdf'

if filename:
    loader = UnstructuredPDFLoader(file_path=filename)
    data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
chunks = text_splitter.split_documents(data)

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="nomic-embed-text", show_progress=True),
    collection_name="local-rag"
)

local_model = "llama3.1:8b-instruct-q8_0"
llm = ChatOllama(
    model=local_model,
    format="json",
    temperature=0.1,
    num_ctx = 4096,
    num_predict = 2500,
    top_k=20,
    top_p = 0.2,
    device=device
)
QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""You are an AI language model assistant. Your task is to generate five
    different versions of the given user question to retrieve relevant documents from
    a vector database. By generating multiple perspectives on the user question, your
    goal is to help the user overcome some of the limitations of the distance-based
    similarity search. Provide these alternative questions separated by newlines.
    Original question: {question}""",
)

retriever = MultiQueryRetriever.from_llm(
    vector_db.as_retriever(), 
    llm,
    prompt=QUERY_PROMPT
)

# RAG prompt
template = """Answer the question based ONLY on the following context:
{context}
If there are no Aptitute Question the reply No Questions found
Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

query = """
    Please analyze the given text and identify  aptitude questions in the Exersise 1. The output should be in JSON format, strictly following the structure provided below.
    The Question will always begin with a number (eg:1.Question, 2.Question)
    There are 10 Questions in the given context extract all of them

    The JSON structure should be as follows:
    {
        "Category": <CATEGORY>,
        "Sub-Category": <SUB_CATEGORY>,
        "Questions": [<QUESTION-1>, <QUESTION-2>, ...],
        "Options": [[<OPTION-1-A>, <OPTION-1-B>, <OPTION-1-C>, <OPTION-1-D>], 
                    [<OPTION-2-A>, <OPTION-2-B>, <OPTION-2-C>, <OPTION-2-D>], ...],
        "Answer": [<ANSWER-1>, <ANSWER-2>, ...]
    }
    -Replace <CATEGORY> with the general category of the questions (e.g., Mathematics, Logic).
    -Replace <SUB_CATEGORY> with a more specific category if applicable (e.g., Algebra, Number Series).
    -Replace <QUESTION-1>, <QUESTION-2>, etc., with the actual aptitude questions found in the content.
    -Replace <OPTION-1-A>, <OPTION-1-B>, etc., with all available answer options for each question.
    -Replace <ANSWER-1>, <ANSWER-2>, etc., with the correct answer for each question.
    Ensure the following:
        Disregard any non-question content, such as lists of topics, explanations, or promotional material.
        Only retrieve and include questions explicitly present in the content.
        The Answers can be found under explanation
        Do not generate any new questions.
        Only return the JSON response. Do not include any additional messages or text.

"""
response = chain.invoke(input=query)
vector_db.delete_collection()

print(response)




