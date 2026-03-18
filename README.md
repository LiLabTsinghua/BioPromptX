# BioPromptX: A Method for Automated Cell Information Extraction Based on Large Language Models

# 🧬 LLM-based Biological Knowledge Extraction Framework

> Automated gene function annotation and enzyme kinetic parameter mining for digital cell modeling.
><img width="1388" height="532" alt="fig1" src="https://github.com/user-attachments/assets/0e68f341-e525-4a48-8577-25b547c823f1" />
 


## 🔍 Overview
We present a fully automated large language model (LLM)-based framework for large-scale biological knowledge extraction, targeting gene function annotation and enzyme kinetic parameter mining. The workflow benchmarks multiple open-source LLMs (Llama, GPT, Qwen, and DeepSeek) and achieves high accuracy when validated against UniProt and BRENDA. To improve generality and scalability, we introduce a reinforcement learning–based prompt optimization strategy that automatically adapts prompts for user-defined extraction tasks. Across seven biological extraction tasks, the framework demonstrates robust and improved performance. As a practical application, we expanded gene function annotations for E. coli and S. cerevisiae, adding 520 and 353 previously unannotated genes, respectively. This framework enables continuous, scalable updating of biological knowledge bases and supports data-driven digital cell modeling.

## ✨ Key Features
- High recall rate
- Custom tasks
- High-Speed Processing Based on PDF

## 🧠 Methodology
The BioPromptX method proposed in this paper establishes a comprehensive automated information extraction workflow: First, the Miner-U tool parses biomedical literature PDFs into structured Markdown text. Next, through carefully designed prompt templates, open-source large language models (such as GPT and DeepSeek) are invoked to concurrently extract gene functional annotations and enzyme kinetic parameters from the text, with consistency validation scores obtained from authoritative databases (UniProt, BRENDA). To enhance adaptability across tasks, reinforcement learning (DQN) strategies are introduced to iteratively generate and optimize extraction prompts for user-defined tasks. Finally, the workflow is scaled for specific species (e.g., E. coli, yeast), building a complementary and updatable knowledge base of gene functions and kinetic parameters. This is deployed as an online platform enabling users to upload literature, select tasks, and receive automated extraction of structured results.


## 📊 Results
Benchmark result of gene function extraction
<img width="2218" height="1717" alt="fig2" src="https://github.com/user-attachments/assets/9a68f244-fd44-497d-ac3d-096d19361df6" />

Benchmark result of kinetic parameter extraction
<img width="1815" height="1675" alt="fig3" src="https://github.com/user-attachments/assets/cf9cbab3-6871-4f04-8a62-0a8fc198d906" />

Dataset and Benchmark for using reinforcement learning method to generate optimized prompts
<img width="2001" height="830" alt="fig4" src="https://github.com/user-attachments/assets/2de95042-2e95-4604-a8dd-cfb97b427fcd" />

The workflow and data analysis of generated database
<img width="2351" height="1082" alt="Fig5" src="https://github.com/user-attachments/assets/9d25fe55-d536-445d-bc85-89ba89d6ec0e" />


## 🚀 Installation
```txt
# 1. Clone this repository
https://github.com/LiLabTsinghua/BioPromptX.git
cd BioPromptX

# 2. Create and activate a conda environment (recommended)
conda create -n BioPromptX python=3.11
conda activate BioPromptX

# 3. Install dependencies
pip install -r requirements.txt
```

## 📚 Citation
How to cite this work

## 👍 Contact
Feiran Li: feiranli@sz.tsinghua.edu.cn
