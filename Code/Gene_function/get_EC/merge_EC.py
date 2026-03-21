import csv
import json

# read tsv
tsv_file = 'amino_acid_result_gene_comparison_checked_split_function.tsv'
output_tsv_file = 'amino_acid_result_gene_comparison_checked_split_function_EC.tsv'

# read JSON
json_file = 'sliced200_amino_acid_all_gene_function_EC_complemented_all_EC.json'
with open(json_file, 'r') as f:
    json_data = json.load(f)

# Create a dictionary to facilitate quick lookups by PubMed_ID
pubmed_dict = {item['PubMed_ID']: item for item in json_data}

# open and read tsv
with open(tsv_file, 'r') as tsvfile, open(output_tsv_file, 'w', newline='') as outfile:
    reader = csv.DictReader(tsvfile, delimiter='\t')
    fieldnames = reader.fieldnames + ['EC_complement']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')

    writer.writeheader()

    for row in reader:
        pubmed_id = row['PubMed_ID']
        actual_result = row['Actual Result']

        gene_name = actual_result.strip('[]')

        if pubmed_id in pubmed_dict:
            entry = pubmed_dict[pubmed_id]

            gene_function = None

            for gene_func in entry['Gene Functions']:
                if gene_func['Gene'] == gene_name:
                    gene_function = gene_func['EC number']
                    break

            if not gene_function:
                for gene_func in entry['Low Frequency Gene Functions']:
                    if gene_func['Gene'] == gene_name:
                        gene_function = gene_func['EC number']
                        break

            row['EC_complement'] = gene_function if gene_function else 'Not found'
        else:
            row['EC_complement'] = 'PubMed_ID not found'

        # write new row
        writer.writerow(row)

print(f"处理完成，结果已保存到 {output_tsv_file}")
