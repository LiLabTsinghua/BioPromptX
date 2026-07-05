# import json
# from collections import defaultdict
#
# # =========================
# # 1. 读取数据
# # =========================
# with open("kinetic_paper_value.json", "r", encoding="utf-8") as f:
#     text_results = json.load(f)
#
# with open("all_detected_tables_kinetic.json", "r", encoding="utf-8") as f:
#     table_results = json.load(f)
#
# # =========================
# # 2. 构建 text-based 索引
# #    { PubMed_ID: {param_type: set(values)} }
# # =========================
# text_index = {}
#
# for item in text_results:
#     pmid = item["PubMed_ID"]
#     text_index[pmid] = {
#         "kcat": set(item["Kinetic Parameters"].get("kcat", [])),
#         "Km": set(item["Kinetic Parameters"].get("Km", [])),
#         "kcat/Km": set(item["Kinetic Parameters"].get("kcat/Km", []))
#     }
#
# # =========================
# # 3. 表格结果去重
# # =========================
# filtered_results = {}
#
# for pmid, tables in table_results.items():
#     filtered_results[pmid] = {
#         "kcat": [],
#         "Km": [],
#         "kcat/Km": []
#     }
#
#     # 文本中已有的参数
#     text_params = text_index.get(pmid, {
#         "kcat": set(),
#         "Km": set(),
#         "kcat/Km": set()
#     })
#
#     for table in tables:
#         kp = table.get("Kinetic Parameters", {})
#
#         for param in ["kcat", "Km", "kcat/Km"]:
#             for value in kp.get(param, []):
#                 if value not in text_params[param]:
#                     filtered_results[pmid][param].append(value)
#
#     # 可选：去重（防止多个表格重复）
#     for param in filtered_results[pmid]:
#         filtered_results[pmid][param] = list(dict.fromkeys(filtered_results[pmid][param]))
#
# # =========================
# # 4. 写出结果
# # =========================
# with open("table_only_kinetics.json", "w", encoding="utf-8") as f:
#     json.dump(filtered_results, f, indent=2, ensure_ascii=False)


import json

# =========================
# 1. 读取 JSON
# =========================
with open("table_only_kinetics.json", "r", encoding="utf-8") as f:
    kinetic_data = json.load(f)

with open("kinetic_paper_new.json", "r", encoding="utf-8") as f:
    paper_data = json.load(f)["paper result"]

# =========================
# 2. 整合
# =========================
merged_results = []

for paper in paper_data:
    pubmed_id = paper["PubMed_ID"]

    kinetic_params = kinetic_data.get(pubmed_id, {
        "kcat": [],
        "Km": [],
        "kcat/Km": []
    })

    merged_results.append({
        "PubMed_ID": pubmed_id,
        "paper result": paper.get("paper result", ""),
        "Kinetic Parameters": {
            "kcat": kinetic_params.get("kcat", []),
            "Km": kinetic_params.get("Km", []),
            "kcat/Km": kinetic_params.get("kcat/Km", [])
        }
    })

# =========================
# 3. 保存结果
# =========================
with open("table_only_kinetics_value.json", "w", encoding="utf-8") as f:
    json.dump(merged_results, f, indent=2, ensure_ascii=False)

print(f"✅ 合并完成，共处理 {len(merged_results)} 篇文章")
