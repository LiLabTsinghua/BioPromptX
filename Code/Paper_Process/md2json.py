import os
import json

def collect_md_by_pubmed(root_folder, output_json):
    result = []

    for subdir, dirs, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(".md"):
                md_path = os.path.join(subdir, file)
                try:
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 以文件名（去掉扩展名）作为 PubMed ID
                    pubmed_id = os.path.splitext(file)[0]

                    result.append({
                        "PubMed_ID": pubmed_id,
                        "Content": content
                    })
                except Exception as e:
                    print(f"读取文件失败: {md_path}, 错误: {e}")

    # 保存为 JSON 文件
    with open(output_json, 'w', encoding='utf-8') as out_f:
        json.dump(result, out_f, ensure_ascii=False, indent=2)

    print(f"已成功整理 {len(result)} 篇 md 文件，保存至 {output_json}")

# 使用方式（替换为你的实际路径）
root_folder = "/home/zhetao/MinerU-xiongwen/demo/process_code/complex_paper"
output_json = "/home/zhetao/MinerU-xiongwen/demo/process_code/complex_paper.json"
collect_md_by_pubmed(root_folder, output_json)
