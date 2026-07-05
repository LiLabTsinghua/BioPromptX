import json
import os
import re

# ================= 配置区域 =================
# 1. 指向你存放所有论文文件夹的根目录（绝对路径）
# 例如: "/home/zhetao/Human_gene/Info_Extration/gene_function/Get_Function/database/kinetic_parameter/md+figs/pdfs"
BASE_DIR = r"/home/zhetao/Human_gene/Info_Extration/gene_function/Get_Function/database/kinetic_parameter/md+figs/pdfs"

# 2. 你的 JSON 文件路径
JSON_PATH = '/home/zhetao/Human_gene/Info_Extration/gene_function/Get_Function/database/kinetic_parameter/all_detected_tables.json'


# ===========================================

def update_md_files():
    # 加载 JSON 数据
    if not os.path.exists(JSON_PATH):
        print(f"错误: 找不到 JSON 文件 {JSON_PATH}")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for paper_id, entries in data.items():
        # 构建该论文文件夹的绝对路径
        paper_folder_path = os.path.join(BASE_DIR, paper_id)

        # 定位 md 文件。假设 md 文件名和文件夹名一致，例如 10092885/10092885.md
        # 如果你的 md 文件名是固定的（如 index.md），请改为 "index.md"
        md_file_path = os.path.join(paper_folder_path, f"{paper_id}.md")

        if not os.path.exists(md_file_path):
            print(f"跳过: 找不到文件 {md_file_path}")
            continue

        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        modified = False
        for entry in entries:
            full_image_path_in_json = entry['image']
            table_markdown = entry['markdown']

            image_filename = os.path.basename(full_image_path_in_json)
            pattern = rf"!\[\]\(.*?{re.escape(image_filename)}\)"

            # 使用 re.search 找到原文中具体的图片标记字符串
            match = re.search(pattern, content)

            if match:
                match_str = match.group()  # 获取匹配到的原文，例如 ![](10026151/xxx.jpg)

                # 检查表格是否已存在，防止重复添加
                if table_markdown[:20] not in content:
                    # 【核心修改点】：使用字符串的 replace 而不是 re.sub
                    # 这样 table_markdown 里的任何特殊字符（\m, \n, \t）都会被当做普通文本处理
                    replacement = f"{match_str}\n\n{table_markdown}\n"
                    content = content.replace(match_str, replacement)

                    modified = True
                    print(f"已回填表格: {paper_id} -> {image_filename}")
            else:
                print(f"未匹配: {paper_id}.md 中未找到图片 {image_filename}")

        # 如果内容有变动，写回文件
        if modified:
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                print(f"文件已更新: {md_file_path}")


if __name__ == "__main__":
    update_md_files()
    print("任务处理完毕。")