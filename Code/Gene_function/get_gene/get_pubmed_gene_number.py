import json
import pandas as pd

# 读取 JSON 文件
with open("/home/zhetao/Human_gene/Info_Extration/gene_function/sliced200_amino_acid_paper_gene_combine.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# 统计每篇文章中的基因数量并合并基因名字
records = []
for article in data:
    pubmed_id = article.get("PubMed_ID", "").strip()
    genes = article.get("Genes", [])
    gene_count = len(genes)
    genes_str = ", ".join(genes)  # 用逗号连接所有基因名
    records.append({
        "PubMed_ID": pubmed_id,
        "Gene_Count": gene_count,
        "Genes": genes_str
    })

# 保存到 Excel 文件
df = pd.DataFrame(records)
df.to_excel("gene_count_amino_acid.xlsx", index=False)

print("统计结果已保存为 gene_counts_per_article.xlsx")
