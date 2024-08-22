import os

from api import generate_option, generate_question
from utils import json_conversion


def Recheck():
    FOLDER_PATH = "New Files.csv"

def main():
    FOLDER_PATH = "New Files"
    failed_files = []

    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith('.txt'):
            file_path = os.path.join(FOLDER_PATH, filename)
            print(f"Processing file: {filename}")
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    response = generate_question(content)

                    # Check if 'Options' field exists and has at least 2 items
                    options_field_exists = 'Options' in response
                    options_count_valid = options_field_exists and all(len(options) >= 2 for options in response.get('Options', []))

                    if not options_count_valid:
                        print("Generating Options")
                        response = generate_option(response)
                        options_field_exists = 'Options' in response
                        options_count_valid = options_field_exists and all(len(options) >= 2 for options in response.get('Options', []))

                    # Proceed with JSON conversion if options are valid
                    if options_count_valid:
                        json_conversion(response)
                    else:
                        failed_files.append(filename)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
                failed_files.append(filename)
                
    if failed_files:
        print("Failed files:", failed_files)

if __name__ == "__main__":
    main()