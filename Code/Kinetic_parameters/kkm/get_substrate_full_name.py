import json
import os
from time import sleep
from Info_Extration.enzyme_info.qwen_api import qwen_api
from tqdm import tqdm


def locate_full_substrate_name_prompt(text, substrate_name):
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
    Text: ''' {text} '''

    Based on the above text, the following substrate have been extracted:
    Extracted substrate: "{substrate_name}"

    Please check if the full name of the substrate appears **explicitly** in the article. If it does, return the full names **exactly as it appears in the article**. If the full name does not appear in the article, return the original name as I provided for you.

    The output must be a JSON object in the following format:
        {{
            "substrate full name": "corresponding full name of the substrate in the article"
        }}

        Example:
        input: "glucose"
        {{
            "substrate full name": "D-glucose"
        }}

    If the full name of the input substrate is not mentioned in the article, output the name of the input as the full name.
        Example：
        input: "NADPH"
        {{
            "substrate full name": "NADPH"
        }}
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    try:
        json_data = json.loads(result)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from API response: {result}")
        return {"substrate full name": None}

    return json_data


def process_json(input_path='nature.json', output_path='output_results.json', temp_path='temp_results1.json'):
    with open(input_path, 'r') as file:
        data = json.load(file)

    results = []
    start_index = 0

    # Check if the temp file exists and load progress if possible
    if os.path.exists(temp_path):
        with open(temp_path, 'r') as temp_file:
            temp_data = json.load(temp_file)
            results = temp_data['results']
            start_index = temp_data['last_processed_index'] + 1

    with tqdm(total=len(data), desc="Processing", unit="paper") as pbar:
        for index, content in enumerate(data[start_index:], start=start_index):
            doi = content.get("doi", "Unknown DOI")
            paper_text = content.get('full paper', '')
            if not paper_text.strip():
                print(f"No text found for DOI {doi}. Skipping.")
                results.append({"doi": doi, "parameters": []})
                continue

            # Extract parameters related to 'kcat'
            combined_params = content.get('parameters', [])
            extracted_data = []

            # Process only 'kcat' parameters
            for param in combined_params:
                value = param.get('value')
                substrate_name = param.get('substrate&co')
                print(f"substrate: {substrate_name}")
                if substrate_name:
                    # Split substrates if multiple are present (comma-separated)
                    substrates = [s.strip() for s in substrate_name.split(';')]

                    # Store the full names for each substrate
                    full_names = []
                    for substrate in substrates:
                        result = locate_full_substrate_name_prompt(paper_text, substrate)
                        full_names.append(
                            result.get("substrate full name", substrate))  # Default to the original name if not found

                    # Combine full names into a single string to match the original 'substrate&co'
                    combined_full_name = "; ".join(full_names)

                    # Append the data
                    extracted_data.append({
                        "value": value,
                        "substrate&co": substrate_name,  # Keep the original substrate&co intact
                        "substrate full name": combined_full_name,
                        "enzyme": param.get('enzyme', None)  # Assuming enzyme info is extracted somewhere else
                    })

            results.append({"doi": doi, "full paper": paper_text, "parameters": extracted_data})

            # Save progress periodically
            if (index + 1) % 1 == 0:  # You can adjust the frequency of saving the progress here
                with open(temp_path, 'w') as temp_file:
                    json.dump({'results': results, 'last_processed_index': index}, temp_file, indent=4)
                print(f"Progress saved at index {index}.")

            pbar.update(1)
            sleep(1)

    # Final output
    with open(output_path, 'w') as outfile:
        json.dump(results, outfile, indent=4)

    # Remove temporary progress file after successful completion
    if os.path.exists(temp_path):
        os.remove(temp_path)


if __name__ == '__main__':
    process_json(
        'SC_kinetic_combined_substrate_enzyme.json',
        'SC_kinetic_combined_substrate_fullname_enzyme.json'
    )
