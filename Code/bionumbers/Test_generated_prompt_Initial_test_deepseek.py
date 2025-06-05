import re
import json
import pandas as pd
from openai import OpenAI
import time

# Initialize the DeepSeek client
client = OpenAI(api_key="sk-3630bcbc16fe459ab1f3cc72b8e5a24f", base_url="https://api.deepseek.com")

def extract_information_with_prompt(text, prompt, max_retries=5):
    full_message = f"{prompt}\n\nText: {text}"
    retries = 0

    while retries < max_retries:
        try:
            # Call DeepSeek API
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": full_message},
                ],
                stream=False
            )

            # Extract the response content
            result = response.choices[0].message.content

            # Use regex to extract JSON-like content
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, result, re.DOTALL)

            if match:
                # Try to parse the matched JSON string
                json_data = json.loads(match.group(0))
                print("Successfully extracted JSON:", json_data)
                return match.group(0)  # Return the JSON string
            else:
                print("No JSON found in response. Retrying...")
                retries += 1
                time.sleep(1)  # Wait for 1 second before retrying

        except (json.JSONDecodeError, AttributeError) as e:
            # Handle JSON parsing errors or regex match failures
            print(f"Error parsing JSON: {e}. Retrying...")
            retries += 1
            time.sleep(1)  # Wait for 1 second before retrying

    # If max retries reached, return an empty JSON object
    print(f"Max retries ({max_retries}) reached. Returning empty JSON.")
    return "{}"


def load_text_from_json(json_file_path):
    """Load multiple articles from a JSON file"""
    with open(json_file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def load_prompts_from_excel(excel_file_path, header_col1, header_col2):
    """Load extraction content and corresponding prompts from an Excel file"""
    # Use pandas to read the Excel file
    df = pd.read_excel(excel_file_path)

    # Ensure column headers match the input
    if header_col1 not in df.columns or header_col2 not in df.columns:
        raise ValueError(f"Column headers '{header_col1}' or '{header_col2}' not found in the Excel file.")

    # Convert data to a dictionary
    prompts = dict(zip(df[header_col1], df[header_col2]))
    return prompts


def save_results_to_json(results, output_file_path):
    """Save the results to a JSON file"""
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(results, file, indent=4)


def build_full_prompt(extraction_content, dynamic_prompt):
    """Build the full prompt by dynamically replacing extraction content"""
    # Fixed part of the prompt
    fixed_prompt = '''
    The output must be a JSON object in the following format:
    {{
        "{extraction_content}": ["value1 <unit1>; <Annotation1>", "value2 <unit2>; <Annotation2>"]
    }}

    If no valid {extraction_content} values are mentioned, output:
    {{
        "{extraction_content}": []
    }}
    '''

    # Escape the curly braces
    fixed_prompt = fixed_prompt.format(extraction_content=extraction_content)

    # Combine dynamic and fixed parts
    return f"{dynamic_prompt}\n{fixed_prompt}"


if __name__ == '__main__':
    # Define column headers
    header_col1 = "Extraction_Content"  # Replace with the name of your first column header
    header_col2 = "Prompt"  # Replace with the name of your second column header
    header_col3 = "Initial Prompt"

    # Load extraction content and corresponding prompts from Excel
    excel_file_path = 'all_generated_prompts_with_feedback.xlsx'  # Replace with your Excel file path
    prompts = load_prompts_from_excel(excel_file_path, header_col1, header_col3)

    # Load multiple articles from JSON file
    json_file_path = '/home/zhetao/Human_gene/Info_Extration/Bionumbers/text_papers/Length Scales Inside Cells.json'  # Replace with your JSON file path
    papers = load_text_from_json(json_file_path)

    # Define the extraction content name
    extraction_content = "Length Scales Inside Cells"  # Modify this as needed

    # Get the corresponding prompt
    if extraction_content in prompts:
        dynamic_prompt = prompts[extraction_content]
        dynamic_prompt = dynamic_prompt.strip('"')
    else:
        raise ValueError(f"Extraction content '{extraction_content}' not found in prompts.")

    # Build the full prompt
    full_prompt = build_full_prompt(extraction_content, dynamic_prompt)

    # Process each article and extract information
    results = []
    for paper in papers:
        pubmed_id = paper["PubMed_ID"]
        text_content = paper["content"]

        # Call function to extract information
        extracted_data = extract_information_with_prompt(text_content, full_prompt)

        # Add result to the results list
        results.append({
            "PubMed_ID": pubmed_id,
            "text_content": text_content,
            "Initial_Prompt_extracted_data": json.loads(extracted_data)  # Parse the JSON string to a dictionary
        })

    # Save the results to a new JSON file
    output_file_path = 'Length Scales Inside Cells_results_new.json'  # Replace with your desired output file path
    save_results_to_json(results, output_file_path)

    print(f"Extraction completed. Results saved to {output_file_path}")