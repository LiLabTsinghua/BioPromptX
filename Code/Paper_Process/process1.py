import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
import json
import time
from loguru import logger
from tqdm import tqdm

from magic_pdf.pipe.UNIPipe import UNIPipe
from magic_pdf.pipe.OCRPipe import OCRPipe
from magic_pdf.pipe.TXTPipe import TXTPipe
from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter
import magic_pdf.model as model_config

model_config.__use_inside_model__ = True


def json_md_dump(
        md_writer,
        pdf_name,
        md_content,
):
    md_writer.write(
        content=md_content,
        path=os.path.join(md_writer.path, f"{pdf_name}.md")
    )


def find_pdfs_in_directory(directory):
    pdf_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_paths.append(os.path.join(root, file))
    return pdf_paths


def get_subfolders(directory):
    return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]


def pdf_parse_main(
        pdf_path_list: str,
        parse_method: str = 'auto',
        model_json_path: str = None,
        is_json_md_dump: bool = True,
        output_directory: str = None
):
    if model_json_path:
        model_json = json.loads(open(model_json_path, "r", encoding="utf-8").read())
    else:
        model_json = []

    for pdf_path in tqdm(pdf_path_list, desc="Processing PDFs", unit="file"):
        pdf_name = os.path.basename(pdf_path).split(".")[0]
        pdf_subfolder = os.path.basename(os.path.dirname(pdf_path))

        try:
            # Create a new output directory using the specified output directory
            output_path = os.path.join(output_directory, pdf_subfolder)
            os.makedirs(output_path, exist_ok=True)

            pdf_bytes = open(pdf_path, "rb").read()

            md_writer = DiskReaderWriter(output_path)
            image_writer = DiskReaderWriter(output_path)  # Save images to the same output folder

            if parse_method == "auto":
                jso_useful_key = {"_pdf_type": "", "model_list": model_json}
                pipe = UNIPipe(pdf_bytes, jso_useful_key, image_writer)
            elif parse_method == "txt":
                pipe = TXTPipe(pdf_bytes, model_json, image_writer)
            elif parse_method == "ocr":
                pipe = OCRPipe(pdf_bytes, model_json, image_writer)
            else:
                logger.error("Unknown parse method, only auto, ocr, txt allowed")
                exit(1)

            pipe.pipe_classify()

            if not model_json:
                if model_config.__use_inside_model__:
                    pipe.pipe_analyze()
                else:
                    logger.error("Need model list input")
                    exit(1)

            pipe.pipe_parse()

            md_content = pipe.pipe_mk_markdown(pdf_name, drop_mode="none")

            if is_json_md_dump:
                json_md_dump(md_writer, pdf_name, md_content)

            # Copy the original PDF to the new output directory
            original_pdf_destination = os.path.join(output_path, os.path.basename(pdf_path))
            with open(original_pdf_destination, "wb") as f:
                f.write(pdf_bytes)

        except Exception as e:
            logger.exception(e)


# Test
if __name__ == '__main__':
    start_time = time.time()
    directory = "/home/zhetao/Human_gene/Info_Extration/Bionumbers/get_data/pdf/bionumbers_papers_md+fig"  # Change this to your PDF directory
    output_directory = "/home/zhetao/Human_gene/Info_Extration/Bionumbers/get_data/pdf/bionumbers_papers_md+fig"  # Change this to your desired output directory

    # Get subfolder names in input and output directories
    input_subfolders = get_subfolders(directory)
    output_subfolders = get_subfolders(output_directory)

    logger.info(f"Found {len(input_subfolders)} subfolders in input directory.")
    logger.info(f"Found {len(output_subfolders)} subfolders in output directory.")

    # Identify subfolders that are in input but not in output
    subfolders_to_process = set(input_subfolders) - set(output_subfolders)

    logger.info(f"Found {len(subfolders_to_process)} subfolders to process: {subfolders_to_process}")

    # Collect unprocessed PDFs from the identified subfolders
    unprocessed_pdfs = []
    for subfolder in subfolders_to_process:
        subfolder_path = os.path.join(directory, subfolder)
        pdfs_in_subfolder = find_pdfs_in_directory(subfolder_path)
        unprocessed_pdfs.extend(pdfs_in_subfolder)

    logger.info(f"Found {len(unprocessed_pdfs)} unprocessed PDF files to process.")

    pdf_parse_main(unprocessed_pdfs, output_directory=output_directory)
    print('花费时间', time.time() - start_time)
