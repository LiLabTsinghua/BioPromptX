import json
import pandas as pd

# Read JSON
with open("/home/zhetao/Human_gene/Info_Extration/gene_function/sliced200_amino_acid_paper_gene_combine.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# Count the number of genes in each article and combine the gene names
records = []
for article in data:
    pubmed_id = article.get("PubMed_ID", "").strip()
    genes = article.get("Genes", [])
    gene_count = len(genes)
    genes_str = ", ".join(genes) 
    records.append({
        "PubMed_ID": pubmed_id,
        "Gene_Count": gene_count,
        "Genes": genes_str
    })

# Save
df = pd.DataFrame(records)
df.to_excel("gene_count_amino_acid.xlsx", index=False)

print("save as gene_counts_per_article.xlsx")
