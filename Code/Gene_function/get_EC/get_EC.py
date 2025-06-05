import json
import os
from time import sleep
from tqdm import tqdm
from qwen_api import qwen_api

def enzyme_ec_prompt(enzyme_name, full_text):
    system_prompt = 'You are a knowledgeable assistant in enzymology.'

    prompt = f"""
    Please read the article carefully.

    Article: ''' {full_text} '''

    The above Article contains an enzyme key gene identified as "{enzyme_name}". 
    Your task is to analyze the text and extract the EC (Enzyme Commission) number associated with the enzyme (if explicitly mentioned).

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

    # Check if result is None, and handle it appropriately
    if result is None:
        return json.dumps({
            "EC number": None
        })

    try:
        # Validate if the result is a valid JSON string
        parsed_result = json.loads(result.strip())
        return parsed_result
    except json.JSONDecodeError:
        # Handle cases where the API does not return a valid JSON
        return {
            "EC number": None
        }


def load_existing_results(output_path):
    """Load existing results from output file, if any, and return the count of already processed articles."""
    if os.path.exists(output_path):
        with open(output_path, 'r') as outfile:
            results = json.load(outfile)
            return results, len(results)
    return [], 0  # Return an empty list if the file doesn't exist


def process_json(input_path='nature.json', output_path='nature_gene_functions_with_ec_and_freq.json'):
    # Read the JSON file
    with open(input_path, 'r') as file:
        data = json.load(file)

    papers = data  # Assuming the papers are in the 'data'

    # Load existing results from the output file
    existing_results, processed_count = load_existing_results(output_path)
    results = existing_results  # Start from existing results
    save_frequency = 1  # Save every article

    # Create a progress bar
    with tqdm(total=len(papers), initial=processed_count, desc="Processing", unit="article") as pbar:
        # Iterate over each article in the JSON data
        for index, item in enumerate(papers[processed_count:], start=processed_count):
            paper = item
            full_text = paper.get('content', '')  # 'content' is the text in your structure

            # Use 'Genes' as gene list
            genes = paper.get('Genes', [])

            # Gene frequencies: Collect frequencies from the entire article, excluding certain keys
            gene_frequencies = {key: paper.get(key, 0) for key in paper.keys() if
                                key not in ['Genes', 'content', 'Gene Functions', 'paper result', 'PubMed_ID', 'Low Frequency Gene Functions']}

            # Skip this entry if the gene list is empty
            if not genes:
                continue

            # List to store low frequency gene functions and EC numbers
            low_freq_function_list = []

            # Process Low Frequency Gene Functions only
            for low_freq_gene in paper.get("Low Frequency Gene Functions", []):
                gene_name = low_freq_gene.get("Gene", "")
                if gene_name:
                    # Retrieve the EC number for the low frequency gene
                    ec_result = enzyme_ec_prompt(gene_name, full_text)
                    low_freq_function_result = {
                        "Gene": gene_name,
                        "Function": low_freq_gene.get("Function", ""),
                        "EC number": ec_result.get("EC number", None)
                    }
                    low_freq_function_list.append(low_freq_function_result)

                    # Add a small delay to avoid hitting the API too quickly
                    sleep(1)

            # Add the low frequency function list with EC numbers to the article dictionary
            item['Low Frequency Gene Functions'] = low_freq_function_list
            item['Gene Frequencies'] = gene_frequencies  # Keep frequencies in the correct section

            # Ensure PubMed_ID is at the top of the article
            paper_data = {"PubMed_ID": item.get("PubMed_ID", None)}
            paper_data.update(item)  # Add the rest of the paper data

            # Append modified item to results
            results.append(paper_data)

            # Save results after processing each article
            if (index + 1) % save_frequency == 0:
                with open(output_path, 'w') as outfile:
                    json.dump(results, outfile, indent=4)

            # Update the progress bar
            pbar.update(1)

    # Save remaining results after the loop
    with open(output_path, 'w') as outfile:
        json.dump(results, outfile, indent=4)


if __name__ == '__main__':
    process_json(
        'sliced200_carbon_all_gene_function_EC_complemented.json',
        'sliced200_carbon_all_gene_function_EC_complemented_all_EC.json')
