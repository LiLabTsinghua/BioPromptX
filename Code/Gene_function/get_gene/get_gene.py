import json
import re
import os
from time import sleep
from qwen_api import qwen_api
from tqdm import tqdm  # Import tqdm for progress bar

# Define function to generate direct prompts for extracting genes
def direct_prompt(text):
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
                Based on the following text, extract all the genes(gene names) mentioned in the content.\n
                Text: ''' {text} '''
                Please extract all the genes(gene names) mentioned in the text provided above. Ensure that the output is a JSON object formatted as follows:
                
                Output:
                {{"genes": ["gene1", "gene2", "gene3"]}}\n
                Output should strictly follow this format and make sure that the output genes(gene names) are not duplicated."""  # Updated prompt format

    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)
    return result

# Function to clean and extract JSON string from API response
def extract_json_string(gene_result):
    match = re.search(r"{.*}", gene_result)  # Adjusted regex to match the object format
    if match:
        return match.group(0)  # Return the JSON object as a string
    else:
        return None

# Define function to process the JSON file with progress bar
def process_json(input_path='nature.json', output_path='output_results.json', temp_path='temp_results1.json'):
    # Read the input JSON file
    with open(input_path, 'r') as file:
        data = json.load(file)

    # Initialize list for storing results
    results = []

    # Check if a temp file exists to resume from previous progress
    start_index = 0
    if os.path.exists(temp_path):
        with open(temp_path, 'r') as temp_file:
            temp_data = json.load(temp_file)
            results = temp_data['results']
            start_index = temp_data['last_processed_index'] + 1

    # Create a progress bar
    with tqdm(total=len(data['NER result']) - start_index, desc="Processing", unit="paper") as pbar:
        # Iterate over each paper in the JSON data starting from last processed index
        for index, item in enumerate(data['NER result'][start_index:], start=start_index):
            for result in item['paper result']:
                text = result.get('text', '')  # Using 'text' field for gene extraction

                if not text.strip():
                    print(f"No text found for DOI {item.get('doi')}. Skipping.")
                    result['Genes'] = []  # If no text, set Genes to an empty list
                    continue

                # Call direct_prompt function and store the result
                gene_result = direct_prompt(text)

                # Clean and extract JSON string
                cleaned_json_str = extract_json_string(gene_result)

                if cleaned_json_str:
                    try:
                        gene_data = json.loads(cleaned_json_str)  # Attempt to parse the cleaned JSON string
                        result['Genes'] = gene_data.get('genes', [])  # Access the 'genes' key in the object
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON for text. Cleaned response was: {cleaned_json_str}")
                        result['Genes'] = []  # Fallback to an empty list if decoding fails
                else:
                    print(f"No valid JSON found for text. Original response was: {gene_result}")
                    result['Genes'] = []  # Fallback to an empty list if no JSON found

            # Append modified item to results
            results.append(item)

            # Save progress every 10 papers
            if (index + 1) % 10 == 0:
                with open(temp_path, 'w') as temp_file:
                    json.dump({'results': results, 'last_processed_index': index}, temp_file, indent=4)
                print(f"Progress saved at index {index}.")

            # Update the progress bar
            pbar.update(1)

            # Add a small delay to avoid hitting the API too quickly
            sleep(1)

    # Save the final results to a new JSON file
    with open(output_path, 'w') as outfile:
        json.dump(results, outfile, indent=4)

    # Remove the temp file after successful completion
    if os.path.exists(temp_path):
        os.remove(temp_path)

if __name__ == '__main__':
    process_json('sliced200_amino_acid_paper.json', 'sliced200_amino_acid_paper_gene_70B.json')
