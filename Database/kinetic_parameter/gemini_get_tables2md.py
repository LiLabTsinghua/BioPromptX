import os
import json
import base64
from pathlib import Path
from io import BytesIO
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


# =========================
# 1. 初始化 LLM
# =========================
llm = ChatOpenAI(
    model="gemini-2.5-flash",
    openai_api_key="sk-vWajozo3cigbQOKHGQSjOPAydYAv2JsfssG6IzJH1mGE2N25",
    base_url="https://api.wlai.vip/v1",
    temperature=0
)


# =========================
# 2. Prompts
# =========================
TABLE_DETECT_PROMPT = """
You are given an image from a scientific paper.

Task:
Determine whether this image contains a TABLE.

Definition of a table:
- Data arranged in rows and columns
- With headers, gridlines, or clear column alignment

Answer strictly with:
Yes
or
No
"""

TABLE_TO_MD_PROMPT = """
This image contains a table from a scientific paper.

Task:
Extract the table content and convert it into Markdown format.

Rules:
- Preserve all rows and columns
- Do NOT add explanations
- Output Markdown table only
"""


# =========================
# 3. 工具函数
# =========================
def image_to_base64(img_path: Path) -> str:
    img = Image.open(img_path).convert("RGB")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def llm_with_image(prompt: str, image_b64: str) -> str:
    msg = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
            }
        ]
    )
    return llm.invoke([msg]).content.strip()


# =========================
# 4. 单个 paper 处理函数（并行单元）
# =========================
def process_single_paper(paper_dir: Path) -> tuple[str, list]:
    paper_id = paper_dir.name
    images_dir = paper_dir / "images"

    if not images_dir.exists():
        return paper_id, []

    paper_tables = []

    for img_path in sorted(images_dir.iterdir()):
        if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            continue

        try:
            img_b64 = image_to_base64(img_path)

            # Step 1: 判断是否为表格
            decision = llm_with_image(TABLE_DETECT_PROMPT, img_b64)
            if decision != "Yes":
                continue

            # Step 2: 表格转 Markdown
            md_table = llm_with_image(TABLE_TO_MD_PROMPT, img_b64)

            paper_tables.append({
                "image": str(img_path),
                "markdown": md_table
            })

        except Exception as e:
            print(f"[ERROR] {paper_id} | {img_path.name}: {e}")

    return paper_id, paper_tables


# =========================
# 5. 主流程（并行 + 增量保存 + 断点续跑）
# =========================
def process_all_papers(root_dir: str, output_json: str, max_workers: int = 6):
    root = Path(root_dir)

    # ===== 1. 加载已有结果（断点续跑）
    if os.path.exists(output_json):
        with open(output_json, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        results = {}

    lock = Lock()

    paper_dirs = [
        p for p in sorted(root.iterdir())
        if p.is_dir() and p.name not in results
    ]

    print(f"📄 Papers to process: {len(paper_dirs)}")

    # ===== 2. 并行执行
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_single_paper, paper_dir): paper_dir.name
            for paper_dir in paper_dirs
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing papers"):
            paper_id = futures[future]

            try:
                pid, paper_tables = future.result()

                if paper_tables:
                    with lock:
                        results[pid] = paper_tables
                        # 🔥 每完成一个 paper 就写盘
                        with open(output_json, "w", encoding="utf-8") as f:
                            json.dump(results, f, indent=2, ensure_ascii=False)

            except Exception as e:
                print(f"[FATAL] Paper {paper_id} failed: {e}")

    print(f"✅ Done. Results saved to: {output_json}")


# =========================
# 6. 运行入口
# =========================
if __name__ == "__main__":
    ROOT_DIR = "/home/zhetao/Human_gene/Info_Extration/gene_function/Get_Function/database/kinetic_parameter/md+figs/pdfs"
    OUTPUT_JSON = "all_detected_tables.json"

    process_all_papers(
        ROOT_DIR,
        OUTPUT_JSON,
        max_workers=6   # 👈 可根据 API 限速调整
    )
