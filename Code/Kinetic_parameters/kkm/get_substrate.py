import json
import re
import os
from time import sleep
from Info_Extration.enzyme_info.qwen_api import qwen_api
from tqdm import tqdm


# Define a new prompt function to directly extract kcat, Km, and kcat/Km along with their units
# Define a new prompt for extracting kinetic parameters, ensuring numerical values and units are returned
def locate_kinetic_parameter_prompt(text, parameter_type, parameter_value):
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
        Text: ''' {text} '''
        Based on the above text, locate the substrate associated with the given kinetic parameter kcat/Km.

        Parameter value: {parameter_value}

        Your task is to identify and extract the corresponding substrate and co-substrate of the Parameter value based on the text above. 
        If co-substrate is explicitly mentioned, extract it along with the substrate.

        The output must be a JSON object in json format.
        If no valid associated substrates are found.
        {{
            "substrate": null
        }}
        If the article mentions that this parameter corresponds to substrate and co-substrate, extract both substrate and co-substrate.
        {{
            "substrate": "substrate; co-substrate"
        }}
        If the article only mentions the substrate corresponding to this parameter and there is no co-substrate.
        {{
            "substrate": "substrate"
        }}
        
        Example1:
        substrate: NADH; co-substrate: Acetoin;
        {{
            "substrate": "NADH; Acetoin",
        }}
        substrate: glucose; co-substrate: Not mentioned;
        Example2:
        {{
            "substrate": "glucose",
        }}
        
        Ensure that:
        - All results must be mentioned in the article or table.
        - Substrate and co-substrate are extracted together if available.
    """
    # print(prompt)
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    try:
        json_data = json.loads(result)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from API response: {result}")
        return {"strain name": None, "substrate": None, "enzyme": None}

    return json_data


# Process JSON file and extract kcat-related kinetic parameters
def process_json(input_path='nature.json', output_path='output_results.json', temp_path='temp_results.json'):
    with open(input_path, 'r') as file:
        data = json.load(file)

    results = []
    start_index = 0

    if os.path.exists(temp_path):
        with open(temp_path, 'r') as temp_file:
            temp_data = json.load(temp_file)
            results = temp_data['results']
            start_index = temp_data['last_processed_index'] + 1

    with tqdm(total=len(data), desc="Processing", unit="paper") as pbar:
        for index, item in enumerate(data, start=start_index):  # Iterate through each item in the list
            doi = item.get("doi")
            paper_text = item.get('paper result', '')
            if not paper_text.strip():
                print(f"No text found for DOI {doi}. Skipping.")
                results.append({"doi": doi, "full paper": paper_text, "parameters": []})
                continue

            # Extract only kcat parameters
            combined_params = item.get('Kinetic Parameters', {})
            extracted_data = []

            if 'kcat/Km' in combined_params:
                for value in combined_params['kcat/Km']:
                    result = locate_kinetic_parameter_prompt(paper_text, 'kcat/Km', value)
                    extracted_data.append({
                        "value": value,
                        "substrate": result.get("substrate"),
                    })

            results.append({"doi": doi, "full paper": paper_text, "parameters": extracted_data})

            # Save progress periodically
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


# Test processing function (if needed)
def process_json_test(input_path='nature.json', output_path='output_results.json', temp_path='temp_results.json'):
    with open(input_path, 'r') as file:
        data = json.load(file)

    results = []
    start_index = 0

    if os.path.exists(temp_path):
        with open(temp_path, 'r') as temp_file:
            temp_data = json.load(temp_file)
            results = temp_data['results']
            start_index = temp_data['last_processed_index'] + 1

    with tqdm(total=len(data), desc="Processing", unit="paper") as pbar:
        for index, item in enumerate(data, start=start_index):  # Iterate through each item in the list
            doi = item.get("doi")
            paper_text = item.get('paper result', '')
            if not paper_text.strip():
                print(f"No text found for DOI {doi}. Skipping.")
                results.append({"doi": doi, "full paper": paper_text, "parameters": []})
                continue

            # Extract only kcat parameters
            combined_params = item.get('Kinetic Parameters', {})
            extracted_data = []

            if 'kcat/Km' in combined_params:
                for value in combined_params['kcat/Km']:
                    result = locate_kinetic_parameter_prompt(paper_text, 'kcat/Km', value)
                    extracted_data.append({
                        "value": value,
                        "substrate": result.get("substrate"),
                    })

            results.append({"doi": doi, "full paper": paper_text, "parameters": extracted_data})

            # Save progress periodically
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
    process_json('SC_kinetic_combined.json',"SC_kinetic_combined_substrate.json")
    # process_json_test('text_10paper_kinetic_combined.json',"text_10paper_kinetic_combined_result_new.json")
