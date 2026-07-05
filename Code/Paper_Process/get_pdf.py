import os
import time
import random
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from Bio import Entrez
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from requests.exceptions import HTTPError

# ========================
# 基本配置
# ========================
Entrez.email = "guozt23@mails.tsinghua.edu.cn"   # ← 改成你自己的 email

# ========================
# 工具函数
# ========================
def clean_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# ========================
# Sci-Hub 下载
# ========================
def download_from_scihub(doi, file_path, retries=3, timeout=6):
    headers = {
        "user-agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (X11; Linux x86_64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        ])
    }

    scihub_url = f"https://www.sci-hub.ren/{doi}"

    for attempt in range(retries):
        try:
            r = requests.get(scihub_url, headers=headers, timeout=timeout)
            r.raise_for_status()

            soup = BeautifulSoup(r.text, "html.parser")

            download_url = None
            if soup.iframe and soup.iframe.get("src"):
                download_url = soup.iframe["src"]
            elif soup.embed and soup.embed.get("src"):
                download_url = soup.embed["src"]

            if not download_url:
                print(f"⚠️ Sci-Hub 页面无 PDF: {doi}")
                return False

            if not download_url.startswith("http"):
                download_url = "https:" + download_url

            pdf_resp = requests.get(download_url, headers=headers, timeout=timeout)
            pdf_resp.raise_for_status()

            with open(file_path, "wb") as f:
                f.write(pdf_resp.content)

            print(f"✅ Sci-Hub 下载成功: {doi}")
            time.sleep(random.uniform(3, 6))
            return True

        except HTTPError as e:
            status = e.response.status_code if e.response else None

            # ⭐ 核心逻辑：429 限流
            if status == 429:
                wait_time = 10 + random.uniform(0, 5)
                print(f"⏸️ Sci-Hub 429 限流，暂停 {wait_time:.1f}s 后重试: {doi}")
                time.sleep(wait_time)
                continue  # 🔁 重试当前 DOI

            print(f"⚠️ Sci-Hub HTTP 错误({status}): {doi}")
            break  # 非 429，没必要继续 retry

        except Exception as e:
            print(f"⚠️ Sci-Hub 异常({attempt+1}/{retries}): {doi} | {e}")
            time.sleep(random.uniform(5, 10))

    return False



# ========================
# PMC 下载
# ========================
def get_pmc_id(pmid):
    try:
        handle = Entrez.elink(dbfrom="pubmed", db="pmc", id=pmid)
        records = Entrez.read(handle)
        handle.close()

        linksets = records[0].get("LinkSetDb", [])
        if not linksets:
            return None

        pmc_id = linksets[0]["Link"][0]["Id"]
        return f"PMC{pmc_id}"
    except:
        return None


def download_pmc_pdf(pmc_id, file_path):
    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/"
    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(r.content)
            print(f"✅ PMC 下载成功: {pmc_id}")
            return True
    except Exception as e:
        print(f"❌ PMC 下载失败: {pmc_id} | {e}")

    return False


# ========================
# Unpaywall 下载
# ========================
def get_doi_from_pmid(pmid):
    try:
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        records = Entrez.read(handle)
        handle.close()

        ids = records["PubmedArticle"][0]["PubmedData"]["ArticleIdList"]
        for _id in ids:
            if _id.attributes.get("IdType") == "doi":
                return str(_id)
    except:
        return None
    return None


def get_oa_pdf_url(doi, email="your_email@example.com"):
    try:
        url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
        resp = requests.get(url, timeout=6)
        data = resp.json()
        return data.get("best_oa_location", {}).get("url_for_pdf")
    except:
        return None


def download_pdf_from_url(url, file_path):
    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200 and "pdf" in r.headers.get("Content-Type", ""):
            with open(file_path, "wb") as f:
                f.write(r.content)
            print(f"✅ Unpaywall 下载成功")
            return True
    except Exception as e:
        print(f"❌ Unpaywall 下载失败: {e}")

    return False


# ========================
# 子进程：下载单个 PMID
# ========================
def download_one_pmid(pmid, save_dir):
    file_path = os.path.join(save_dir, clean_filename(pmid) + ".pdf")

    try:
        if os.path.exists(file_path):
            return pmid, "Success"

        doi = get_doi_from_pmid(pmid)

        if doi and download_from_scihub(doi, file_path):
            return pmid, "Success"

        pmc_id = get_pmc_id(pmid)
        if pmc_id and download_pmc_pdf(pmc_id, file_path):
            return pmid, "Success"

        if doi:
            oa_url = get_oa_pdf_url(doi)
            if oa_url and download_pdf_from_url(oa_url, file_path):
                return pmid, "Success"

        return pmid, "Failed"

    except Exception as e:
        print(f"❌ PMID {pmid} 异常: {e}")
        return pmid, "Error"


# ========================
# 主函数（多进程并发）
# ========================
def download_pdfs_from_tsv_parallel(
    tsv_path,
    save_dir="./pdfs",
    log_path="./download_log.csv",
    max_workers=4
):
    os.makedirs(save_dir, exist_ok=True)

    # --- 旧日志 ---
    processed_pmids = set()
    if os.path.exists(log_path):
        old_log = pd.read_csv(log_path)
        processed_pmids = set(old_log["PMID"].astype(str))

    # --- 读取 TSV ---
    df = pd.read_csv(tsv_path, sep="\t")
    pubmed_ids = set()

    for ids in df["PubMed_IDs"].dropna():
        for pmid in str(ids).split(","):
            pmid = pmid.strip()
            if pmid.isdigit():
                pubmed_ids.add(pmid)

    pubmed_ids = sorted(pubmed_ids)
    pubmed_ids = [p for p in pubmed_ids if p not in processed_pmids]

    print(f"📌 待下载 PMID 数量: {len(pubmed_ids)}")

    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(download_one_pmid, pmid, save_dir): pmid
            for pmid in pubmed_ids
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="并发下载 PDF"):
            pmid, status = future.result()
            results.append({"PMID": pmid, "Status": status})

            # 主进程写日志（安全）
            pd.DataFrame(results).to_csv(log_path, index=False)

            # 防封节奏
            time.sleep(random.uniform(0.2, 0.5))

    print("🎉 并发下载完成！日志写入：", log_path)


# ========================
# 程序入口（必须）
# ========================
if __name__ == "__main__":
    download_pdfs_from_tsv_parallel(
        tsv_path="uniprot_KP_uniprot_pubmed.tsv",
        save_dir="./pdfs_uniprot",
        log_path="./download_log_uniprot.csv",
        max_workers=2
    )
