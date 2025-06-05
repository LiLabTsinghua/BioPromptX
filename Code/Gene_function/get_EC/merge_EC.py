import csv
import json

# 读取 TSV 文件
tsv_file = '/home/zhetao/Human_gene/Info_Extration/gene_function/Get_Function/split200_gene_function/final_result/amino_acid_result_gene_comparison_checked_split_function.tsv'
output_tsv_file = 'amino_acid_result_gene_comparison_checked_split_function_EC.tsv'

# 读取 JSON 文件
json_file = 'sliced200_amino_acid_all_gene_function_EC_complemented_all_EC.json'
with open(json_file, 'r') as f:
    json_data = json.load(f)

# 创建一个字典，方便根据 PubMed_ID 快速查找
pubmed_dict = {item['PubMed_ID']: item for item in json_data}

# 打开 TSV 文件并读取内容
with open(tsv_file, 'r') as tsvfile, open(output_tsv_file, 'w', newline='') as outfile:
    reader = csv.DictReader(tsvfile, delimiter='\t')
    fieldnames = reader.fieldnames + ['EC_complement']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')

    writer.writeheader()

    for row in reader:
        pubmed_id = row['PubMed_ID']
        actual_result = row['Actual Result']

        # 去掉基因名称的方括号
        gene_name = actual_result.strip('[]')

        # 查找对应的 PubMed_ID 条目
        if pubmed_id in pubmed_dict:
            entry = pubmed_dict[pubmed_id]

            # 查找基因功能描述
            gene_function = None

            # 先在 Gene Functions 中查找
            for gene_func in entry['Gene Functions']:
                if gene_func['Gene'] == gene_name:
                    gene_function = gene_func['EC number']
                    break

            # 如果没有找到，再在 Low Frequency Gene Functions 中查找
            if not gene_function:
                for gene_func in entry['Low Frequency Gene Functions']:
                    if gene_func['Gene'] == gene_name:
                        gene_function = gene_func['EC number']
                        break

            # 将基因功能描述添加到新列中
            row['EC_complement'] = gene_function if gene_function else 'Not found'
        else:
            row['EC_complement'] = 'PubMed_ID not found'

        # 写入新行
        writer.writerow(row)

print(f"处理完成，结果已保存到 {output_tsv_file}")