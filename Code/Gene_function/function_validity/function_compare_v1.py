import pandas as pd
from time import sleep
from tqdm import tqdm
from qwen_api import qwen_api  # 调用模型的接口


# 调用模型接口，判断两个基因功能是否一致
def compare_gene_functions_with_prompt(gene_function1, gene_function2):
    system_prompt = 'You are a knowledgeable assistant in molecular biology.'

    prompt = f"""
    Two gene functions are described below:\n
    Gene Function1: '''{gene_function1}'''
    Gene Function2: '''{gene_function2}'''

    Please determine if the functions described for Gene are consistent or different.

    If the functions are fully consistent, respond with 'Yes, the gene’s two function descriptions are consistent'.
    If the functions are partly consistent, respond with 'Unclear, the gene’s two function descriptions are not entirely consistent'.
    If the functions are entirely different, respond with 'No, the gene’s two function descriptions are inconsistent'.

    Output strictly follow the example and don't output any other information.'
    """

    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)

    # Check if result is None, and handle it appropriately
    if result is None:
        return "impossible judge"  # 或者返回其他占位符

    return result.strip()


# 读取TSV文件并调用模型判断基因功能是否一致
def compare_gene_functions_in_tsv(input_file, output_file):
    # 读取TSV文件
    df = pd.read_csv(input_file, sep='\t')

    # 假设基因功能描述存储在名为 'Function [CC]' 和 'Confirmed Gene Function' 的列中
    gene_function_column1 = df['Function [CC]']
    gene_function_column2 = df['Gene Function Description']

    # 创建新列来存储模型判断结果
    comparison_results = []

    # 使用tqdm显示进度条
    for g1_func, g2_func in tqdm(zip(gene_function_column1, gene_function_column2), total=len(gene_function_column1),
                                 desc="Comparing gene functions"):
        # 检查 Function 列的值是否为 "PubMed_ID not found" 或 "Not found"
        if g2_func in ["PubMed_ID not found", "Not found", "Not mentioned in the provided article."]:
            comparison_results.append("")  # 或者使用 pd.NA 或 np.nan
        else:
            # 调用模型接口比较基因功能描述
            result = compare_gene_functions_with_prompt(g1_func, g2_func)
            comparison_results.append(result)
            sleep(1)  # 加上延迟避免频繁调用API

    # 将比较结果添加到数据框的新列
    df['Function Comparison Result2'] = comparison_results

    # 保存结果到新的TSV文件
    df.to_csv(output_file, sep='\t', index=False)
    print(f"Comparison results saved to {output_file}")


if __name__ == '__main__':
    # 定义输入和输出的TSV文件路径
    input_file = 'carbon_result_gene_Q30B_comparison_checked_split_function.tsv'  # 替换为你的输入文件路径
    output_file = 'carbon_result_gene_Q30B_comparison_checked_split_function_result.tsv'  # 替换为你的输出文件路径

    # 调用函数进行基因功能比较
    compare_gene_functions_in_tsv(input_file, output_file)