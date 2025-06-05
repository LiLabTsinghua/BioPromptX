import json
import os
from time import sleep
from Info_Extration.enzyme_info.qwen_api import qwen_api
from tqdm import tqdm

# Define Prompt Functions
def extract_kcat_prompt(text):
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
        Text: ''' {text} '''
        Please read this article carefully.
        
        Based on the text above, extract all occurrences of the kcat value and its associated units mentioned in the content.
        
        Your task is to extract the numeric values and their exact units for the kcat parameter. 
        
        Please extract in the format: value (unit), where 'value' is a number and 'unit' is a recognized unit (e.g., s⁻¹, s-1, min⁻¹, min-1 etc.). Don't extract parameter values that without kcat units.
        
        If no valid kcat values are mentioned, output: 
        {{ 
            "kcat": [] 
        }}
        If kcat is mentioned, output in the format: 
        {{
            "kcat": ["value1 (unit1)", "value2 (unit2)"]
        }}

        Do not omit any kcat values in anywhere of the article including bracketed text in the article.
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)
    return result

def extract_km_prompt(text):
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
        Text: ''' {text} '''
        Please read this article carefully.
        
        Based on the text above, extract all occurrences of the Km value and its associated units mentioned in the content.
        
        Your task is to extract only the numeric values and their exact units for the Km parameter. Non-numeric content (such as "-") does not need to be extracted.
        
        Please extract in the format: value (unit), where 'value' is a number and 'unit' is a recognized unit (e.g., mM, M, µM, nM, µmol/L, mol/L, mol·L⁻¹ etc.). Don't extract parameter values that without Km units.
        
        If no valid Km values are mentioned, output: 
        {{
            "Km": [] 
        }}
        If Km is mentioned, output in the format: 
        {{
            "Km": ["value1 (unit1)", "value2 (unit2)"]
        }}
        
        Do not omit any Km values in anywhere of the article including bracketed text in the article.
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)
    return result

def extract_kcat_km_prompt(text):
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
        Text: ''' {text} '''
        Please read this article carefully.
        
        Based on the text above, extract all occurrences of the kcat/Km value and its associated units mentioned in the content. Non-numeric content (such as "-") does not need to be extracted.
        
        Your task is to extract only the numeric values and their exact units for the kcat/Km parameter.
        
        Please extract in the format: value (unit), where 'value' is a number and 'unit' is a recognized unit (e.g., M⁻¹·s⁻¹, M⁻¹min⁻¹, mM⁻¹·s⁻¹, mM⁻¹·min⁻¹ etc.). Don't extract parameter values that without kcat/Km.
        
        If no valid kcat/Km values are mentioned, output: 
        {{ 
            "kcat/Km": [] 
        }}
        If kcat/Km is mentioned, output in the format: 
        {{
            "kcat/Km": ["value1 (unit1)", "value2 (unit2)"]
        }}
        
        Do not omit any kcat/Km values in anywhere of the article including bracketed text in the article.
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)
    return result

# Process JSON Function
def process_json(input_path='nature.json', output_path='output_results.json', temp_path='temp_results1.json'):
    # Read the input JSON file
    with open(input_path, 'r') as file:
        data = json.load(file)

    results = []
    start_index = 0

    if os.path.exists(temp_path):
        with open(temp_path, 'r') as temp_file:
            temp_data = json.load(temp_file)
            results = temp_data['results']
            start_index = temp_data['last_processed_index'] + 1

    with tqdm(total=len(data['paper result']) - start_index, desc="Processing", unit="paper") as pbar:
        for index, item in enumerate(data['paper result'][start_index:], start=start_index):
            text = item.get('paper result', '')

            if not text.strip():
                print(f"No text found for DOI {item.get('doi')}. Skipping.")
                kinetic_parameters = {"kcat": [], "Km": [], "kcat/Km": []}
            else:
                # Call the APIs for kcat, Km, and kcat/Km
                kcat_response = extract_kcat_prompt(text)
                km_response = extract_km_prompt(text)
                kcat_km_response = extract_kcat_km_prompt(text)

                # Parse the API responses
                try:
                    kcat_data = json.loads(kcat_response) if kcat_response else {"kcat": []}
                    km_data = json.loads(km_response) if km_response else {"Km": []}
                    kcat_km_data = json.loads(kcat_km_response) if kcat_km_response else {"kcat/Km": []}
                except json.JSONDecodeError:
                    print(f"Error decoding JSON response: kcat_response={kcat_response}, km_response={km_response}, kcat_km_response={kcat_km_response}")
                    kcat_data = {"kcat": []}
                    km_data = {"Km": []}
                    kcat_km_data = {"kcat/Km": []}

                kinetic_parameters = {
                    "kcat": kcat_data.get("kcat", []),
                    "Km": km_data.get("Km", []),
                    "kcat/Km": kcat_km_data.get("kcat/Km", [])
                }

            item['Kinetic Parameters'] = kinetic_parameters
            results.append(item)

            if (index + 1) % 1 == 0:
                with open(temp_path, 'w') as temp_file:
                    json.dump({'results': results, 'last_processed_index': index}, temp_file, indent=4)
                print(f"Progress saved at index {index}.")

            pbar.update(1)
            sleep(1)

    with open(output_path, 'w') as outfile:
        json.dump(results, outfile, indent=4)

    if os.path.exists(temp_path):
        os.remove(temp_path)

if __name__ == '__main__':
    process_json('SC_doi.json', 'SC_doi_kinetic.json')
