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
Benchmark result of gene function extraction
<img width="2244" height="1705" alt="fig2" src="https://github.com/user-attachments/assets/ee25d058-1374-4872-8ef6-e29194387e9e" />

Benchmark result of kinetic parameter extraction
<img width="1851" height="2307" alt="fig3" src="https://github.com/user-attachments/assets/65836e2d-b658-44d9-abd4-e002b1d4d140" />


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
