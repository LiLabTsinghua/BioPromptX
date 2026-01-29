import pandas as pd
from collections import Counter

# 读取TSV文件
df = pd.read_csv('/home/zhetao/Human_gene/Info_Extration/gene_function/Get_Function/split200_gene_function/final_result/carbon_result_gene_DS32_comparison_checked_split_function_result.tsv', sep='\t')

# 获取最后三列
last_three_columns = df.columns[-3:]


# 定义一个函数来进行投票
def vote(row):
    # 检查是否有空值，如果有则返回None
    if row.isnull().any():
        return None

    # 统计每个值的出现次数
    value_counts = Counter(row)

    # 找到出现次数最多的值
    most_common_value, most_common_count = value_counts.most_common(1)[0]

    # 如果出现次数大于等于2，则返回该值，否则返回None
    if most_common_count >= 2:
        return most_common_value
    else:
        return None


# 应用投票函数并创建新列
df['vote_result'] = df[last_three_columns].apply(vote, axis=1)

# 保存结果到新的TSV文件
df.to_csv('/home/zhetao/Human_gene/Info_Extration/gene_function/Get_Function/split200_gene_function/final_result/carbon_result_gene_DS32_comparison_checked_split_function_result_voted.tsv', sep='\t', index=False)