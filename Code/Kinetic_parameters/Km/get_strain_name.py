import json
import re
import os
from time import sleep
from Info_Extration.enzyme_info.qwen_api import qwen_api
from tqdm import tqdm


def locate_full_substrate_name_prompt(text, parameter_value, enzyme):
    system_prompt = 'You are a helpful assistant.'
    prompt = f"""
        Text: ''' {text} '''
        Based on the above text, the following enzyme kinetic parameter Km value and key gene of corresponding enzyme has been extracted.

        Km value: {parameter_value}
        Key gene of the enzyme: "{enzyme}"

        Your task is to find the strain name corresponding to the enzyme and Km value I provided in the article.

        The output must be a JSON object in the following format:
        {{
            "strain name": "corresponding strain name",
        }}

        If no valid associations are found, output: {{"strain name": null}}.
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
                enzyme = param.get('enzyme')
                # clean_substrate_name = param.get('clean substrate')
                print(f"enzyme: {enzyme}")
                if enzyme:
                    # 提取底物的全名
                    result = locate_full_substrate_name_prompt(paper_text, value, enzyme)
                    extracted_data.append({
                        "value": value,
                        "substrate&co": param.get('substrate&co'),
                        "substrate full name": param.get('substrate full name'),
                        "strain name": result.get('strain name'),
                        "organism": param.get('organism'),
                        "enzyme": param.get('enzyme', None)  # Assuming enzyme info is extracted somewhere else
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
        for index, content in enumerate(data, start=start_index):
            doi = ""
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
                substrate = param.get('substrate')
                enzyme = param.get('enzyme')
                substrate_full_name = param.get('substrate full name')

                if enzyme:
                    # 提取底物的全名
                    result = locate_full_substrate_name_prompt(paper_text, value, enzyme)
                    extracted_data.append({
                        "value": value,
                        "substrate": substrate,
                        "substrate full name": substrate_full_name,
                        "enzyme": enzyme,
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
        'Ecoli_kinetic_combined_substrate_fullname_enzyme_organism.json',
        'Ecoli_kinetic_combined_substrate_fullname_enzyme_organism_strain.json')
