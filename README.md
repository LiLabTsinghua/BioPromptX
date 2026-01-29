# BioPromptX: A Method for Automated Cell Information Extraction Based on Large Language Models

# 🧬 LLM-based Biological Knowledge Extraction Framework

> Automated gene function annotation and enzyme kinetic parameter mining for digital cell modeling.
> <img width="1517" height="728" alt="fig1" src="https://github.com/user-attachments/assets/0244a0a1-e015-4a10-853e-f8797f28d504" />


## 🔍 Overview
We present a fully automated large language model (LLM)-based framework for large-scale biological knowledge extraction, targeting gene function annotation and enzyme kinetic parameter mining. The workflow benchmarks multiple open-source LLMs (Llama, GPT, Qwen, and DeepSeek) and achieves high accuracy when validated against UniProt and BRENDA. To improve generality and scalability, we introduce a reinforcement learning–based prompt optimization strategy that automatically adapts prompts for user-defined extraction tasks. Across seven biological extraction tasks, the framework demonstrates robust and improved performance. As a practical application, we expanded gene function annotations for E. coli and S. cerevisiae, adding 520 and 353 previously unannotated genes, respectively. This framework enables continuous, scalable updating of biological knowledge bases and supports data-driven digital cell modeling.

## ✨ Key Features
- High recall rate
- Custom tasks
- High-Speed Processing Based on PDF

## 🧠 Methodology
The BioPromptX method proposed in this paper establishes a comprehensive automated information extraction workflow: First, the Miner-U tool parses biomedical literature PDFs into structured Markdown text. Next, through carefully designed prompt templates, open-source large language models (such as GPT and DeepSeek) are invoked to concurrently extract gene functional annotations and enzyme kinetic parameters from the text, with consistency validation scores obtained from authoritative databases (UniProt, BRENDA). To enhance adaptability across tasks, reinforcement learning (DQN) strategies are introduced to iteratively generate and optimize extraction prompts for user-defined tasks. Finally, the workflow is scaled for specific species (e.g., E. coli, yeast), building a complementary and updatable knowledge base of gene functions and kinetic parameters. This is deployed as an online platform enabling users to upload literature, select tasks, and receive automated extraction of structured results.


## 📊 Results
Benchmark result of gene function and kinetic parameter extraction
<img width="2244" height="1705" alt="fig2" src="https://github.com/user-attachments/assets/ee25d058-1374-4872-8ef6-e29194387e9e" />
<img width="1851" height="2307" alt="fig3" src="https://github.com/user-attachments/assets/65836e2d-b658-44d9-abd4-e002b1d4d140" />


## 🚀 Installation
beautifulsoup4==4.14.3
Bio==1.8.1
biopython==1.84
chardet==4.0.0
graphviz==0.20.3
langchain==1.2.7
langchain_openai==1.1.7
matplotlib==3.7.2
numpy==2.4.1
ollama==0.6.1
openai==2.16.0
openpyxl==3.0.10
paddleocr==3.3.2
paddlepaddle_gpu==3.2.0
pandas==2.0.3
pdf2image==1.17.0
pdfplumber==0.11.4
Pillow==12.1.0
rdflib==7.5.0
Requests==2.32.5
seaborn==0.13.2
sentencepiece==0.2.0
spacy==3.8.4
tenacity==8.2.2
tokenizers==0.22.2
torch==2.8.0
tqdm==4.65.0


## 📚 Citation
How to cite this work
