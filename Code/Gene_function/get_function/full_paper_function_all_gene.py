import json
import os
from time import sleep
from llama_api import ollama_api
from tqdm import tqdm  # Import tqdm for progress bar
from qwen_api import qwen_api


def gene_function_prompt(gene, full_text):
    system_prompt = 'You are a knowledgeable assistant in molecular biology.'

    prompt = f"""
    Based on the following article, describe the function of the gene {gene} in JSON format.\n
    Article full text: '''{full_text}'''

    Please strictly follow the JSON output format:
    If the gene function is mentioned in the article.
    Output format:
    {{
        "Gene": "{gene}",
        "Function": "Summarize the gene function in detail."
    }}

    If the gene function is not mentioned in the article.
    Output format:
    {{
        "Gene": "{gene}",
        "Function": "Not mentioned in the provided article."
    }}

    Make sure all information comes solely from the article content and not from your pre-existing knowledge.
    """

    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    # Check if result is None, and handle it appropriately
    if result is None:
        return json.dumps({
            "Gene": gene,
            "Function": "Not mentioned in the provided article."
        })

    try:
        # Validate if the result is a valid JSON string
        parsed_result = json.loads(result.strip())
        return parsed_result
    except json.JSONDecodeError:
        # Handle cases where the API does not return a valid JSON
        return {
            "Gene": gene,
            "Function": "Invalid JSON output from the API."
        }


def load_existing_results(output_path):
    """Load existing results from output file, if any, and return the count of already processed articles."""
    if os.path.exists(output_path):
        with open(output_path, 'r') as outfile:
            results = json.load(outfile)
            return results, len(results)
    return [], 0  # Return an empty list if the file doesn't exist


def process_json(input_path='nature.json', output_path='nature_gene_functions.json'):
    # Read the JSON file
    with open(input_path, 'r') as file:
        data = json.load(file)

    # Assuming 'paper result' contains the list of articles
    papers = data

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

            # Get the gene frequencies dictionary
            gene_frequencies = paper.get('Gene Frequencies', {})

            # Filter genes with frequency 0 or 1
            genes = [gene for gene, freq in gene_frequencies.items() if freq == 0 or freq == 1]

            # Add "Low Frequency Gene Functions" even if there are no genes with frequency 0 or 1
            if not genes:
                paper['Low Frequency Gene Functions'] = []
            else:
                function_list = []
                # Extract and store the function of each gene
                for gene in genes:
                    function_result = gene_function_prompt(gene, full_text)
                    function_list.append(function_result)

                    # Add a small delay to avoid hitting the API too quickly
                    sleep(1)

                paper['Low Frequency Gene Functions'] = function_list

            # Append modified item to results
            results.append(paper)

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
        'sliced200_amino_acid_function_EC.json',
        'sliced200_amino_acid_all_gene_function_EC.json')
