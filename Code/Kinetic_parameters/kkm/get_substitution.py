import json
import os
from time import sleep
from Info_Extration.enzyme_info.qwen_api import qwen_api
from tqdm import tqdm


def locate_enzyme_ec_number(text, parameter_value, strain, enzyme):
    """
    Extract the substitution (amino acid modification/mutation) corresponding to the specified enzyme kinetic parameter from the text using the API.
    Note: The function name suggests EC number extraction, but the logic extracts substitution information.
    """
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
        Text: ''' {text} '''
        Based on the above text, the following enzyme kinetic parameter kcat/Km value, strain name and key gene of corresponding enzyme has been extracted.

        kcat/Km value: {parameter_value}
        strain name: {strain}
        Key gene of the enzyme: "{enzyme}"

        Your task is to find the the kcat/Km value's corresponding substitution(amino acid modification, mutation, replacement) from the article I provided.

        The output must be a JSON object in the following format:
        {{
            "substitution": "corresponding substitution",
        }}

        Example:
        {{
            "substitution": "K141R",        
        }}

        When the text does not exactly mention the kcat/Km value's corresponding substitution.
        output: 
        {{
            "substitution": "wild type"
        }}

        If the substitution information is uncertain (such as none,-,Lys365Glu286).
        output: wild type.

        Attention, The format of the must as follows: 
        1. wild type
        2. single letter-position number-single letter.
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    try:
        json_data = json.loads(result)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from API response: {result}")
        return {"EC number": None}

    return json_data


def process_json(input_path='nature.json', output_path='output_results.json', temp_path='temp_results.json'):
    # Load the input JSON file
    with open(input_path, 'r') as file:
        data = json.load(file)

    results = []
    start_index = 0

    # Check if a temporary progress file exists to resume processing
    if os.path.exists(temp_path):
        with open(temp_path, 'r') as temp_file:
            temp_data = json.load(temp_file)
            results = temp_data['results']
            start_index = temp_data['last_processed_index'] + 1

    # Iterate through the data with a progress bar
    with tqdm(total=len(data), desc="Processing", unit="paper") as pbar:
        for index, content in enumerate(data, start=start_index):
            doi = content.get("doi", "Unknown DOI")
            paper_text = content.get('full paper', '')
            
            # Skip if no text is found for the DOI
            if not paper_text.strip():
                print(f"No text found for DOI {doi}. Skipping.")
                results.append({"doi": doi, "parameters": []})
                continue

            # Retrieve combined parameters
            combined_params = content.get('parameters', [])
            extracted_data = []

            # Process only 'kcat/Km' related parameters (logic currently processes all if enzyme exists)
            for param in combined_params:
                value = param.get('value')
                substrate = param.get('substrate&co')
                substrate_full_name = param.get('substrate full name')
                strain = param.get('strain name')
                enzyme = param.get('enzyme')
                organism = param.get('organism')

                if enzyme:
                    # Extract the full name of the substrate and corresponding substitution
                    result = locate_enzyme_ec_number(paper_text, value, strain, enzyme)
                    extracted_data.append({
                        "value": value,
                        "substrate&co": substrate,
                        "substrate full name": substrate_full_name,
                        "strain name": param.get('strain name'),
                        "organism": organism,
                        "enzyme": enzyme,
                        "substitution": result.get('substitution'),
                        "EC number": param.get("EC number"),
                    })

            results.append({"doi": doi, "full paper": paper_text, "parameters": extracted_data})

            # Save progress periodically (currently saves after every item due to % 1 == 0)
            if (index + 1) % 1 == 0:
                with open(temp_path, 'w') as temp_file:
                    json.dump({'results': results, 'last_processed_index': index}, temp_file, indent=4)
                print(f"Progress saved at index {index}.")

            pbar.update(1)
            sleep(1)

    # Write the final results to the output file
    with open(output_path, 'w') as outfile:
        json.dump(results, outfile, indent=4)

    # Remove the temporary file if it exists
    if os.path.exists(temp_path):
        os.remove(temp_path)


if __name__ == '__main__':
    process_json(
        'SC_kinetic_combined_substrate_fullname_enzyme_organism_strain_EC.json',
        'SC_kinetic_combined_substrate_fullname_enzyme_organism_strain_EC_substitution_new.json')
