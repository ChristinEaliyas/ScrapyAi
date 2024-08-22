import csv

FILENAME = "aptitude_questions.csv"

def json_conversion(data):
    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Extracting details
        category = data.get('Category', '')
        sub_category = data.get('Sub-Category', '')
        questions = data.get('Questions', [])
        options = data.get('Options', [])
        answers = data.get('Answers', [])
        
        for i in range(len(questions)):
            question = questions[i] if i < len(questions) else ""
            option_list = options[i] if i < len(options) else []
            answer = answers[i] if i < len(answers) else ""

            
            writer.writerow([
                category,
                sub_category,
                question,
                answer,
                *option_list
            ])
