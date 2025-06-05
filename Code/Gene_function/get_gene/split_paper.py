import os
import json
import re

# 论文切分函数，每段最多 max_words 个单词
def slice_paper_content(paper_text, max_words=200):
    sentences = re.split(r'(?<=[.!?]) +', paper_text)  # 按句号、问号、感叹号后空格进行切分
    slices = []
    current_slice = []
    word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())

        if word_count + sentence_word_count > max_words:
            if current_slice:  # 只有在当前切片非空时才进行切片
                slices.append(' '.join(current_slice))
            current_slice = [sentence]
            word_count = sentence_word_count
        else:
            current_slice.append(sentence)
            word_count += sentence_word_count

    if current_slice:
        slices.append(' '.join(current_slice))

    return slices


# 读取之前生成的 JSON 文件
input_json = "carbon_paper.json"  # 你的 JSON 文件路径
output_json = "sliced200_carbon_paper.json"

with open(input_json, "r", encoding="utf-8") as f:
    data = json.load(f)

# 处理 JSON 数据，按照 DOI 组织
result = {
    "NER result": []
}

# 遍历 JSON 中的每篇论文
for paper in data:
    pubmed_id = paper.get("PubMed_ID")  # 获取 PubMed ID
    paper_content = paper.get("content")  # 获取论文正文

    if not paper_content:
        continue  # 跳过空内容

    # 切分论文内容
    sliced_content = []
    slices = slice_paper_content(paper_content)

    for slice_text in slices:
        sliced_content.append({"text": slice_text})

    # 组织结果
    result["NER result"].append({
        "PubMed_ID": pubmed_id,  # 这里用 PubMed ID 代替 DOI
        "content": paper_content,
        "paper result": sliced_content
    })

# 保存到新的 JSON 文件
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

# 调试信息
if not result["NER result"]:
    print("⚠️ Warning: No results found. Check the input data.")
else:
    print(f"✅ Processing complete. Results saved to {output_json}.")
