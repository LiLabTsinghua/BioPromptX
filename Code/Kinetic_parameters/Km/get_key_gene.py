import json
import re
import os
from time import sleep
from Info_Extration.enzyme_info.qwen_api import qwen_api
from tqdm import tqdm


# Define a new prompt for extracting kinetic parameters (Km),
# ensuring both substrate and enzyme are returned
def locate_kinetic_parameter_prompt(text, parameter_value):
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
        Text: ''' {text} '''
        Based on the above text, locate the substrate, and enzyme associated with the given kinetic parameter Km.

        Parameter value: {parameter_value}

        Your task is to identify and extract the corresponding substrate and enzyme of the Parameter value based on the text above:
        Please return the name of the key gene for the corresponding enzyme.

        The output must be a JSON object in json format.
        If the article only mentions the substrate corresponding to this parameter and there is no co-substrate.
        {{
            "substrate": "corresponding substrate name",
            "enzyme": "Key genes of the corresponding enzyme"
        }}
        If the article mentions that this parameter corresponds to substrate and co-substrate, extract both substrate and co-substrate
        {{
            "substrate": "corresponding substrate name, co-substrate name",
            "enzyme": "Key genes of the corresponding enzyme"
        }}
        Example1:
        {{
            "substrate": "glucose",
            "enzyme": "gcd"
        }}
        Example2:
        {{
            "substrate": "NADH, Acetoin",
            "enzyme": "geneA"
        }}

        Please ensure that all results must be mentioned in the article.
        If no valid associations are found, output: {{"substrate": null, "enzyme": null}}.
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    try:
        json_data = json.loads(result)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from API response: {result}")
        return {"strain name": None, "substrate": None, "enzyme": None}

    return json_data


# Process JSON file and extract Km-related kinetic parameters
def process_json(input_path='nature.json', output_path='output_results.json', temp_path='temp_results.json'):
    with open(input_path, 'r') as file:
        data = json.load(file)

    results = []
    start_index = 0

    # Resume from checkpoint if temporary file exists
    if os.path.exists(temp_path):
        with open(temp_path, 'r') as temp_file:
            temp_data = json.load(temp_file)
            results = temp_data['results']
            start_index = temp_data['last_processed_index'] + 1

    with tqdm(total=len(data), desc="Processing", unit="paper") as pbar:
        for index, content in enumerate(data, start=start_index):
            doi = content.get("doi", "Unknown DOI")
            paper_text = content.get('full paper', '')

            # Skip entries with empty full text
            if not paper_text.strip():
                print(f"No text found for DOI {doi}. Skipping.")
                results.append({"doi": doi, "parameters": []})
                continue

            # Only extract Km parameters
            combined_params = content.get('parameters', [])
            extracted_data = []

            # Process only 'Km' entries
            for param in combined_params:
                value = param.get('value')
                substrate_name = param.get('substrate')

                if substrate_name:
                    # Extract substrate-enzyme association from text
                    result = locate_kinetic_parameter_prompt(paper_text, value)
                    extracted_data.append({
                        "value": value,
                        "substrate&co": substrate_name,
                        "enzyme": result.get('enzyme', None)  # Extracted enzyme gene
                    })

            results.append({
                "doi": doi,
                "full paper": paper_text,
                "parameters": extracted_data
            })

            # Save progress after each iteration
            if (index + 1) % 1 == 0:
                with open(temp_path, 'w') as temp_file:
                    json.dump({
                        'results': results,
                        'last_processed_index': index
                    }, temp_file, indent=4)
                print(f"Progress saved at index {index}.")

            pbar.update(1)
            sleep(1)

    # Save final results
    with open(output_path, 'w') as outfile:
        json.dump(results, outfile, indent=4)

    # Remove temporary file after completion
    if os.path.exists(temp_path):
        os.remove(temp_path)


# Test function for processing a specific DOI (optional)
def process_json_test(input_path='nature.json', output_path='output_results.json', temp_path='temp_results.json'):
    with open(input_path, 'r') as file:
        data = json.load(file)

    results = []
    start_index = 0

    # Resume from checkpoint if exists
    if os.path.exists(temp_path):
        with open(temp_path, 'r') as temp_file:
            temp_data = json.load(temp_file)
            results = temp_data['results']
            start_index = temp_data['last_processed_index'] + 1

    with tqdm(total=len(data), desc="Processing", unit="paper") as pbar:
        for index, (doi, content) in enumerate(data.items(), start=start_index):

            # Only test a specific DOI
            if doi == "10.1038_srep16520":

                paper_text = content.get('full paper', '')

                # Skip if no text is available
                if not paper_text.strip():
                    print(f"No text found for DOI {doi}. Skipping.")
                    results.append({"doi": doi, "parameters": []})
                    continue

                # Extract Km parameters only
                combined_params = content.get('Combined Kinetic Parameters', {})
                extracted_data = []

                if 'Km' in combined_params:
                    for value in combined_params['Km']:
                        result = locate_kinetic_parameter_prompt(paper_text, 'Km', value)
                        print(result)
                        extracted_data.append({
                            "value": value,
                            "substrate": result.get("substrate"),
                            "enzyme": result.get("enzyme")
                        })

                results.append({"doi": doi, "parameters": extracted_data})

                # Save progress
                if (index + 1) % 1 == 0:
                    with open(temp_path, 'w') as temp_file:
                        json.dump({
                            'results': results,
                            'last_processed_index': index
                        }, temp_file, indent=4)
                    print(f"Progress saved at index {index}.")

                pbar.update(1)


if __name__ == '__main__':
    process_json(
        'Ecoli_kinetic_combined_substrate.json',
        "Ecoli_kinetic_combined_substrate_enzyme.json"
    )
