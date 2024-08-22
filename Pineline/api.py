import requests
import json

def make_api_call(payload):
    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("API request failed:", str(e))
        return e

def generate_question(context):
    prompt = ("""
        Task: You are a Data Retrieval Bot designed to extract and verify aptitude questions, options, and answers from a given context.

        Question Extraction:
        Step 1: Carefully extract all aptitude questions from the provided context. Each question must be complete, starting with a number, and include all relevant details required to answer it.
        Step 2: Include any specific directions or instructions given to solve each question.
        Step 3: Verify that each extracted question is complete, meaningful, and contextually coherent.
        Constraint: Discard any question that is incomplete, unclear, lacks sufficient information, or does not start with a number. Ensure that the entire question is captured from the context, without omitting any part.
        
        Option and Answer Verification:
        Step 1: Identify and extract all options and answers corresponding to each question.
        Step 2: Validate that the options and answers are correctly associated with their respective questions.
        Step 3: Ensure that each option is complete, sensible, and meaningful, and that an answer is available for the corresponding question.
        Constraint: If any option is incomplete, nonsensical, or if the answer is missing or incorrect, remove the entire question along with its options and answers from the selection.
        
        Answer Validation:
        Step 1: Independently evaluate each retained question to determine the correct answer.
        Step 2: Compare the evaluated answer with the answer retrieved from the context.
        Constraint: If the evaluated answer does not match the retrieved answer, discard the corresponding question and its associated options and answers.
        
        Output Structure:
        Provide the output in the following JSON format:
        {
            "Category": "<CATEGORY>",
            "Sub-Category": "<SUB_CATEGORY>",
            "Questions": ["<QUESTION-1>", "<QUESTION-2>", ...],
              "Answers": ["<ANSWER-1>", "<ANSWER-2>", ...],
            "Options": [["<OPTION-1-A>", "<OPTION-1-B>", ...], ["<OPTION-2-A>", "<OPTION-2-B>", ...], ...]
        }
        
        Contextual Analysis:
        Constraint: Ensure that the entire process is carried out with meticulous attention to detail, prioritizing accuracy and consistency throughout the extraction and verification stages. Pay special attention to capturing complete questions, especially those that start with a number, and ensure no part of the question is missed.
        Input: WebPage Content:"""  + context
        )

    
    payload = {
        "model": "llama3.1:8b-instruct-q8_0",
        "prompt": prompt,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_ctx": 4096,
            "num_predict": 1000,
            "top_k": 20,
            "top_p": 0.2
        },
        "stream": False
    }

    response_data = make_api_call(payload)
    if response_data:
        try:
            model_response = response_data.get('response', {}).strip()
            if isinstance(model_response, dict):
                return model_response
            else:
                parsed_data = json.loads(model_response)
                return parsed_data
        except json.JSONDecodeError:
            return json.JSONDecodeError
    else:
        return None

def generate_option(context):
    if isinstance(context, dict):
        context = json.dumps(context, indent=4)  # Convert dict to JSON string for the prompt
    
    prompt = ("""
        Task: You are an Option-Generating Bot. Your task is to generate plausible and unique multiple-choice options for questions that currently have no associated options or incomplete options. You must also include the correct answer as one of the generated options. After generating the options, verify their uniqueness and ensure they meet the specified difficulty level.

        Input Context Format:
        The input will be provided in the following JSON format:
            {
                "Category": "<CATEGORY>",
                "Sub-Category": "<SUB-CATEGORY>",
                "Questions": ["<QUESTION-1>", "<QUESTION-2>", ...],
                "Answers": ["<ANSWER-1>", "<ANSWER-2>", ...],
                "Options": [["<OPTION-1-A>", "<OPTION-1-B>", ...], ["<OPTION-2-A>", "<OPTION-2-B>", ...], ...]
            }

        Task Instructions:
        1. **Identify Missing or Incomplete Options:** 
            - For each question in the "Questions" list, check if the corresponding entry in the "Options" list is empty, incomplete, or contains invalid formatting.

        2. **Generate Options:**
            - Create 3-4 plausible and unique multiple-choice options for each question that lacks options or has incomplete options.
            - Ensure that one of these options is the correct answer provided in the "Answers" list.
            - The options should be moderately difficult, meaning they should not be immediately obvious or overly simplistic. Use distracting elements (similar sounding words, plausible but incorrect information) to increase difficulty.

        3. **Ensure Uniqueness and Formatting:**
            - Ensure all generated options are unique within the set for each question. No two options should be identical or nearly identical.
            - All options should be formatted as strings.

        4. **Insert Options:**
            - Add the generated options to the corresponding position in the "Options" list, maintaining the correct index relationship with the "Questions" list.

        5. **Output Format:**
            - Return the final structured data in the exact same JSON format as the input, ensuring that all fields ("Category", "Sub-Category", "Questions", "Options", "Answers") are preserved and populated correctly:
                {
                    "Category": "<CATEGORY>",
                    "Sub-Category": "<SUB-CATEGORY>",
                    "Questions": ["<QUESTION-1>", "<QUESTION-2>", ...],
                    "Answers": ["<ANSWER-1>", "<ANSWER-2>", ...],
                    "Options": [["<OPTION-1-A>", "<OPTION-1-B>", ...], ["<OPTION-2-A>", "<OPTION-2-B>", ...], ...]
                }

        Constraints:
        - Do not modify any existing options or answers unless they are incomplete or incorrectly formatted.
        - Do not change the order of the questions, options, or answers.
        - Avoid using options that are overly similar in wording or meaning to prevent confusion.
        - Ensure that the output format strictly matches the input format.
        Input Question:"""+context)

    payload = {
        "model": "llama3.1:8b-instruct-q8_0",
        "prompt": prompt,
        "format": "json",
        "options": {
            "temperature": 0.5,
            "num_ctx": 4096,
            "num_predict": 1000,
            "top_k": 40,
            "top_p": 0.3
        },
        "stream": False
    }
    response_data = make_api_call(payload)
    if response_data:
        try:
            model_response = response_data.get('response', {}).strip()
            if isinstance(model_response, dict):
                return model_response
            else:
                parsed_data = json.loads(model_response)
                return parsed_data
        except Exception as e:
            print(e)
            return e
    else:
        return None

def check_question(data):
    prompt = """
    You are a Question Evaluator AI. Your task is to evaluate the given question based on the provided Category and Sub Category, then determine if the evaluated answer matches the given answer.

    Evaluate the Question:
    Analyze the provided Category and Sub Category to find the correct answer to the Question.
    Comparison:
    Compare the evaluated answer with the given Answer.
    Response:
    If the evaluated answer matches the given Answer, respond with "Yes."
    If the evaluated answer does not match the given Answer, respond with "No" and provide an explanation for the discrepancy.
    Constraints:

    Your response should be strictly limited to "Yes" or "No" followed by an explanation if necessary.
    No other responses or additional text should be included.
    Input Context Format:

    Category, Sub Category, Question, Answer, Option A, Option B, Option C, Option D
    Question:""" + data

    payload = {
    "model": "llama3.1:8b-instruct-q8_0",
    "prompt": prompt,
    "format": "json",
    "options": {
        "temperature": 0.5,
        "num_ctx": 4096,
        "num_predict": 1000,
        "top_k": 40,
        "top_p": 0.3
        },
        "stream": False
    }
    response_data = make_api_call(payload)
    if response_data:
        try:
            model_response = response_data.get('response', {}).strip()
            print(model_response)
        except Exception as e:
            print(e)
            return e
    else:
        return None