import pandas as pd

# read tsv contain Entry and EC number
df1 = pd.read_csv('amino_acid_result_gene_comparison.tsv', sep='\t')

# read Entry only tsv
df2 = pd.read_csv('amino_acid_result_gene_comparison_checked_split_function_EC.tsv', sep='\t')

# Combine data
merged_df = pd.merge(df2, df1[['Entry', 'EC number']], on='Entry', how='left')


merged_df.to_csv('amino_acid_result_gene_comparison_checked_split_function_EC_UniEC.tsv', sep='\t', index=False)
