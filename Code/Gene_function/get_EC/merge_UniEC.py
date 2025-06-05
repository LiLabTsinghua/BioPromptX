import pandas as pd

# 读取包含Entry和EC number的tsv文件
df1 = pd.read_csv('/home/zhetao/Human_gene/Info_Extration/gene_function/Get_Function/split200_gene_function/final_result/amino_acid_result_gene_comparison.tsv', sep='\t')

# 读取仅包含Entry的tsv文件
df2 = pd.read_csv('amino_acid_result_gene_comparison_checked_split_function_EC.tsv', sep='\t')

# 合并两个数据帧，基于"Entry"列
merged_df = pd.merge(df2, df1[['Entry', 'EC number']], on='Entry', how='left')

# 将结果保存到新的tsv文件
merged_df.to_csv('amino_acid_result_gene_comparison_checked_split_function_EC_UniEC.tsv', sep='\t', index=False)