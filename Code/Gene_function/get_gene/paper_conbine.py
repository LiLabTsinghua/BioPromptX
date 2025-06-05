import json
from collections import defaultdict

# Function to merge and deduplicate genes in JSON results
def merge_deduplicate_genes(input_path='sliced_UniProt5_result.json', output_path='deduplicated_results.json'):
    with open(input_path, 'r') as file:
        data = json.load(file)

    merged_results = []
    for item in data:
        doi = item.get('PubMed_ID')
        # Use a set to store unique genes
        unique_genes = set()

        # Aggregate genes from all results for the same paper
        for result in item.get('paper result', []):
            genes = result.get('Genes', [])
            unique_genes.update(genes)  # Add genes to the set (automatically deduplicates)

        # Create a new result with the merged genes
        merged_item = {
            'PubMed_ID': doi,
            'content': item.get('content'),
            'Genes': list(unique_genes),  # Convert set back to list
            'paper result': item.get('paper result', []),  # Keep the original results if needed
        }
        merged_results.append(merged_item)

    # Save the merged results to a new JSON file
    with open(output_path, 'w') as outfile:
        json.dump(merged_results, outfile, indent=4)

if __name__ == '__main__':
    merge_deduplicate_genes('sliced200_amino_acid_paper_gene_70B.json', 'sliced200_amino_acid_paper_gene_70B_combine.json')
