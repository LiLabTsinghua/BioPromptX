import json

# 输入的JSON文件
input_file = 'SC_tables_result.json'  # 请替换为实际的文件路径
output_file = 'SC_tables_result_combined.json'

# 加载输入数据
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 存储最终合并后的数据
merged_data = []

# 遍历每个 DOI 相关的数据
for article in data:
    for doi, tables in article.items():
        # 创建一个新的条目
        entry = {
            "doi": doi,
            "Kinetic Parameters": {
                "kcat": [],
                "Km": [],
                "kcat/Km": []
            }
        }

        # 确保tables是字典类型
        if isinstance(tables, dict):
            # 遍历每个表格
            for table_id, table_content in tables.items():
                # 提取表格的标题作为对表格的分类
                if table_id.endswith("Kinetic Parameters"):
                    # 这里假设 Kinetic Parameters 数据都以这个方式出现
                    if isinstance(table_content, dict):
                        for param_type in ["kcat", "Km", "kcat/Km"]:
                            # 对每个 Kinetic Parameters 项目进行合并
                            if param_type in table_content:
                                entry["Kinetic Parameters"][param_type].extend(table_content[param_type])

            # 将合并好的条目添加到结果列表
            merged_data.append(entry)
        else:
            # 如果没有表格，记录该DOI并跳过
            print(f"No tables found for DOI: {doi}")

# 输出到新文件
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=4)

print(f"处理完毕，合并后的数据已保存到 {output_file}")
