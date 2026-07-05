import json
import re
import os
from time import sleep
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from Info_Extration.gene_function.DS_api import deepseek_api


# =========================
# 工具函数
# =========================

def clean_json_response(response: str) -> str:
    """清理 LLM 返回的 JSON 转义字符"""
    return re.sub(
        r'\\u[0-9a-fA-F]{4}',
        lambda m: m.group(0).encode().decode('unicode_escape'),
        response
    )


def extract_json_block(text: str):
    """
    从 LLM 返回中提取 JSON 对象（支持 ```json ... ``` 或纯 JSON）
    """
    if not text:
        return None

    # 1. ```json ... ```
    code_block = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if code_block:
        return code_block.group(1)

    # 2. fallback：第一个 {...}
    brace_block = re.search(r"(\{.*\})", text, re.S)
    if brace_block:
        return brace_block.group(1)

    return None


# =========================
# 参数提取函数
# =========================

def extract_kcat(text):
    system_prompt = "You are a helpful assistant."
    prompt = f"""
    Based on the following table, extract all occurrences of the kcat parameter values and their units.

    Table: '''{text}'''

    Recognized units:
    s⁻¹, s-1, min⁻¹, min-1, h⁻¹, h-1

    Output JSON only:
    {{
        "kcat": ["value (unit)"]
    }}
    """
    raw = deepseek_api(
        user_message=prompt,
        system_message=system_prompt,
        top_p=0.6
    )
    raw = clean_json_response(raw)

    json_text = extract_json_block(raw)
    if not json_text:
        return []

    try:
        return json.loads(json_text).get("kcat", [])
    except Exception:
        print("kcat parse failed:", raw)
        return []


def extract_Km(text):
    system_prompt = "You are a helpful assistant."
    prompt = f"""
    Based on the following table, extract all occurrences of the Km parameter values and their units.

    Table: '''{text}'''

    Recognized units:
    M, mM, µM, nM, µmol/L, mol/L, mol·L⁻¹

    Output JSON only:
    {{
        "Km": ["value (unit)"]
    }}
    """
    raw = deepseek_api(
        user_message=prompt,
        system_message=system_prompt,
        top_p=0.6
    )
    raw = clean_json_response(raw)

    json_text = extract_json_block(raw)
    if not json_text:
        return []

    try:
        return json.loads(json_text).get("Km", [])
    except Exception:
        print("Km parse failed:", raw)
        return []


def extract_kcat_Km(text):
    system_prompt = "You are a helpful assistant."
    prompt = f"""
    Based on the following table, extract all occurrences of the kcat/Km parameter values and their units.

    Table: '''{text}'''

    Recognized units:
    M⁻¹s⁻¹, M⁻¹min⁻¹, L·mol⁻¹·s⁻¹, L·mol⁻¹·min⁻¹

    Output JSON only:
    {{
        "kcat/Km": ["value (unit)"]
    }}
    """
    raw = deepseek_api(
        user_message=prompt,
        system_message=system_prompt,
        top_p=0.6
    )
    raw = clean_json_response(raw)

    json_text = extract_json_block(raw)
    if not json_text:
        return []

    try:
        return json.loads(json_text).get("kcat/Km", [])
    except Exception:
        print("kcat/Km parse failed:", raw)
        return []


# =========================
# 单个 table 处理函数（并行单元）
# =========================

def process_one_table(paper_id, table):
    markdown = table.get("markdown", "")
    params = table.setdefault("Kinetic Parameters", {})

    if not markdown.strip():
        return table

    # 已完整的直接跳过
    if params.get("kcat") and params.get("Km") and params.get("kcat/Km"):
        return table

    if not params.get("kcat"):
        params["kcat"] = extract_kcat(markdown)

    if not params.get("Km"):
        params["Km"] = extract_Km(markdown)

    if not params.get("kcat/Km"):
        params["kcat/Km"] = extract_kcat_Km(markdown)

    return table


# =========================
# 主函数：并行 + 中间文件断点保存
# =========================

def repair_missing_parameters_parallel(
    input_path="all_detected_tables.json",
    output_path="all_detected_tables_kinetic.json",
    max_workers=4
):
    with open(input_path, "r") as f:
        raw_data = json.load(f)

    # ⭐ 如果已有中间结果，直接继续
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            results = json.load(f)
    else:
        results = raw_data

    lock = Lock()
    futures = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for paper_id, tables in results.items():
            for table in tables:
                futures.append(
                    executor.submit(process_one_table, paper_id, table)
                )

        for _ in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Repairing kinetic parameters"
        ):
            try:
                _.result()
            except Exception as e:
                print("Task failed:", e)
                continue

            # 🔐 每完成一个 task 就立刻保存（断点安全）
            with lock:
                with open(output_path, "w") as f:
                    json.dump(results, f, indent=4)


# =========================
# main
# =========================

if __name__ == "__main__":
    repair_missing_parameters_parallel(
        input_path="all_detected_tables.json",
        output_path="all_detected_tables_kinetic.json",
        max_workers=10
    )
