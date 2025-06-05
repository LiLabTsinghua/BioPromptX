import json
import os
from time import sleep
from Info_Extration.enzyme_info.qwen_api import qwen_api
from tqdm import tqdm


def locate_enzyme_ec_number(text, enzyme_name):
    """
    Extract the EC number for the specified enzyme from the text using the API.
    """
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
    Please read the article carefully.

    Article: ''' {text} '''

    The above Article contain an enzyme key gene identified as "{enzyme_name}". Your task is to analyze the text and extract the EC (Enzyme Commission) number associated with the enzyme (if explicitly mentioned).

    Provide the extracted information in the following JSON format:

    {{
        "EC number": "1.1.1.1",
    }}

    If no EC number is found, return:
    {{
        "EC number": null
    }}
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    try:
        json_data = json.loads(result)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from API response: {result}")
        return {"EC number": None}

    return json_data


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
        for index, content in enumerate(data, start=start_index):
            doi = content.get("doi", "Unknown DOI")
            paper_text = content.get('full paper', '')
            if not paper_text.strip():
                print(f"No text found for DOI {doi}. Skipping.")
                results.append({"doi": doi, "parameters": []})
                continue

            # 只提取 kcat 参数
            combined_params = content.get('parameters', [])
            extracted_data = []

            # 只处理 'kcat' 参数
            for param in combined_params:
                value = param.get('value')
                substrate = param.get('substrate&co')
                substrate_full_name = param.get('substrate full name')
                strain = param.get('strain name')
                enzyme = param.get('enzyme')
                organism = param.get('organism')

                if enzyme:
                    # 提取底物的全名
                    result = locate_enzyme_ec_number(paper_text, enzyme)
                    extracted_data.append({
                        "value": value,
                        "substrate&co": substrate,
                        "substrate full name": substrate_full_name,
                        "strain name": param.get('strain name'),
                        "organism": organism,
                        "enzyme": enzyme,
                        "EC number": result.get("EC number"),
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
    process_json(
        'SC_kinetic_combined_substrate_fullname_enzyme_organism_strain.json',
        'SC_kinetic_combined_substrate_fullname_enzyme_organism_strain_EC.json')
