import json
import re


def normalize_value(value):
    """标准化数值，去除单位部分和符号，保留数值"""
    # 只保留数值部分（包括负号和小数点）
    match = re.match(r'([\-+]?\d*\.\d+|\d+)', value)
    if match:
        return match.group(0)  # 返回标准化后的数值部分
    return value  # 如果没有匹配到有效数值，则返回原值


def add_table_kinetic_params_to_paper_kinetics(paper_kinetics_file, table_kinetics_file, output_file):
    # 读取表格提取的酶动力学参数文件
    with open(table_kinetics_file, 'r', encoding='utf-8') as f:
        table_kinetics_data = json.load(f)

    # 读取正文提取的酶动力学参数文件
    with open(paper_kinetics_file, 'r', encoding='utf-8') as f:
        paper_kinetics_data = json.load(f)

    # 遍历表格提取的数据
    for table_entry in table_kinetics_data:
        doi = table_entry['doi']
        table_kinetics = table_entry['Kinetic Parameters']

        # 查找对应 DOI 的正文提取结果
        for paper_entry in paper_kinetics_data:
            if paper_entry['doi'] == doi:
                # 如果正文提取中有酶动力学参数，则将表格提取的参数添加到现有参数中
                if 'Kinetic Parameters' in paper_entry:
                    for param_name in ['kcat', 'Km', 'kcat/Km']:
                        for value in table_kinetics[param_name]:
                            # 标准化参数值（去除单位信息和符号）进行检查
                            normalized_value = normalize_value(value)

                            # 检查值是否已经存在，如果不存在，则添加
                            if not any(normalize_value(existing_value) == normalized_value for existing_value in
                                       paper_entry['Kinetic Parameters'][param_name]):
                                paper_entry['Kinetic Parameters'][param_name].append(value)
                else:
                    # 如果正文提取结果没有酶动力学参数，直接添加
                    paper_entry['Kinetic Parameters'] = table_kinetics
                break

    # 将修改后的结果保存到新的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(paper_kinetics_data, f, ensure_ascii=False, indent=4)


# 示例调用
add_table_kinetic_params_to_paper_kinetics(
    paper_kinetics_file='/home/zhetao/Human_gene/Info_Extration/Dataset_Process/SC_doi_kinetic.json',  # 正文提取的酶动力学参数文件
    table_kinetics_file='SC_tables_result_combined.json',  # 表格提取的酶动力学参数文件
    output_file='/home/zhetao/Human_gene/Info_Extration/Dataset_Process/SC_kinetic_combined.json'  # 输出文件
)
