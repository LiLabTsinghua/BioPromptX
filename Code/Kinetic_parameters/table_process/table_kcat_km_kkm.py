import json
import re
import os
from time import sleep
from Info_Extration.enzyme_info.qwen_api import qwen_api
from tqdm import tqdm

# Clean escaped characters in JSON response
def clean_json_response(response: str) -> str:
    cleaned_response = re.sub(r'\\u[0-9a-fA-F]{4}', lambda match: match.group(0).encode().decode('unicode_escape'), response)
    return cleaned_response

# Extract kcat parameters
def extract_kcat(text):
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
    Based on the following table, extract all occurrences of the kcat parameter values and their units mentioned in the content.
    Table: ''' {text} '''
    Your task is to extract the numeric values and their exact units for the kcat parameter.
    Recognized units for kcat include s⁻¹, s-1, min⁻¹, min-1, h⁻¹, h-1.
    Non-numeric content such as "-", "ND", etc. do not need to be extracted.

    Example:
    - If kcat is mentioned, output: 
    {{
        "kcat": ["value1 (unit1)", "value2 (unit2)"]
    }}
    - If kcat is not mentioned, output: 
    {{
        "kcat": []
    }}

    Output should strictly follow the json format, without any additional information.
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    result = clean_json_response(result)

    try:
        json_data = json.loads(result)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from cleaned API response: {result}")
        json_data = {}

    return json_data.get("kcat", [])

# Extract Km parameters
def extract_Km(text):
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
    Based on the following table, extract all occurrences of the Km parameter values and their units mentioned in the content.
    Table: ''' {text} '''
    Your task is to extract the numeric values and their exact units for the Km parameter.
    Recognized units for Km include M, mM, µM, nM, µmol/L, mol/L, mol·L⁻¹.
    Non-numeric content such as "-", "ND", etc. do not need to be extracted.
    
    Example:
    - If Km is mentioned, output:
    {{
        "Km": ["value1 (unit1)", "value2 (unit2)"]
    }}
    - If Km is not mentioned, output:
    {{
        "Km": []
    }}

    Output should strictly follow the json format, without any additional information.
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    result = clean_json_response(result)

    try:
        json_data = json.loads(result)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from cleaned API response: {result}")
        json_data = {}

    return json_data.get("Km", [])

# Extract kcat/Km parameters
def extract_kcat_Km(text):
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
    Based on the following table, extract all occurrences of the kcat/Km parameter values and their units mentioned in the content.
    Table: ''' {text} '''
    Your task is to extract the numeric values and their exact units for the kcat/Km parameter.
    Recognized units for kcat/Km include M⁻¹s⁻¹, M⁻¹min⁻¹, L·mol⁻¹·s⁻¹, L·mol⁻¹·min⁻¹.
    Non-numeric content such as "-", "ND", etc. do not need to be extracted.

    Example:
    - If kcat/Km is mentioned, output:
    {{
        "kcat/Km": ["value1 (unit1)", "value2 (unit2)"]
    }}
    - If kcat/Km is not mentioned, output:
    {{
        "kcat/Km": []
    }}

    Output should strictly follow the json format, without any additional information.
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    result = clean_json_response(result)

    try:
        json_data = json.loads(result)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from cleaned API response: {result}")
        json_data = {}

    return json_data.get("kcat/Km", [])

# Process JSON file and handle extraction of text and tables
def process_json(input_path='nature.json', output_path='output_results.json', temp_path='temp_results1.json'):
    with open(input_path, 'r') as file:
        data = json.load(file)

    results = []
    start_index = 0

    if os.path.exists(temp_path):
        with open(temp_path, 'r') as temp_file:
            temp_data = json.load(temp_file)
            results = temp_data['results']
            start_index = temp_data['last_processed_index'] + 1

    with tqdm(total=len(data) - start_index, desc="Processing", unit="paper") as pbar:
        for index, (paper_title, paper_data) in enumerate(data.items(), start=start_index):
            if isinstance(paper_data, dict):
                paper_data_copy = paper_data.copy()
            else:
                paper_data_copy = {"content": paper_data}

            # Handle each table in paper_data
            tables_to_update = []

            for table_key, table_content in list(paper_data_copy.items()):
                if isinstance(table_content, str) and table_content.strip():
                    try:
                        # Extract kcat parameters
                        kcat_data = extract_kcat(table_content)

                        # Extract Km parameters
                        Km_data = extract_Km(table_content)

                        # Extract kcat/Km parameters
                        kcat_Km_data = extract_kcat_Km(table_content)

                        # Merge all extracted data
                        kinetic_data = {
                            "kcat": kcat_data,
                            "Km": Km_data,
                            "kcat/Km": kcat_Km_data
                        }

                        tables_to_update.append((table_key, kinetic_data))
                    except Exception as e:
                        print(f"Error processing table '{table_key}' in paper '{paper_title}': {e}")
                        tables_to_update.append((table_key, {"kcat": [], "Km": [], "kcat/Km": []}))

            # Update table content in paper_data_copy
            for table_key, kinetic_data in tables_to_update:
                paper_data_copy[table_key + '_Kinetic Parameters'] = kinetic_data

            # Handle case where paper_data is a string
            if isinstance(paper_data, str):
                results.append({paper_title: paper_data_copy['content']})
            else:
                results.append({paper_title: paper_data_copy})

            # Save progress periodically
            if (index + 1) % 1 == 0:
                with open(temp_path, 'w') as temp_file:
                    json.dump({'results': results, 'last_processed_index': index}, temp_file, indent=4)
                print(f"Progress saved at index {index}.")

            pbar.update(1)
            sleep(1)

    # Write final results to output file
    with open(output_path, 'w') as outfile:
        json.dump(results, outfile, indent=4)

    # Delete temporary file
    if os.path.exists(temp_path):
        os.remove(temp_path)


if __name__ == '__main__':
    process_json('SC_tables.json', 'SC_tables_result.json')
