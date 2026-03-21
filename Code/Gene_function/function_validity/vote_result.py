import pandas as pd
from collections import Counter

# Read tsv
df = pd.read_csv('/home/zhetao/Human_gene/Info_Extration/gene_function/Get_Function/split200_gene_function/final_result/carbon_result_gene_DS32_comparison_checked_split_function_result.tsv', sep='\t')

# get last 3 col
last_three_columns = df.columns[-3:]


# vote
def vote(row):
    # Check blank
    if row.isnull().any():
        return None

    # Calculate
    value_counts = Counter(row)

    most_common_value, most_common_count = value_counts.most_common(1)[0]

    # Vote process
    if most_common_count >= 2:
        return most_common_value
    else:
        return None


df['vote_result'] = df[last_three_columns].apply(vote, axis=1)

# save
df.to_csv('carbon_result_gene_DS32_comparison_checked_split_function_result_voted.tsv', sep='\t', index=False)
