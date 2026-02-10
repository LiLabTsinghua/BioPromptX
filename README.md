# BioPromptX: A Method for Automated Cell Information Extraction Based on Large Language Models

# 🧬 LLM-based Biological Knowledge Extraction Framework

> Automated gene function annotation and enzyme kinetic parameter mining for digital cell modeling.
> <img width="1507" height="728" alt="fig1" src="https://github.com/user-attachments/assets/4f5968b8-e2fc-4545-8146-62661aa9c97f" />


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
<img width="2218" height="1705" alt="fig2" src="https://github.com/user-attachments/assets/03656baa-bfa7-43d8-9b92-502566ba2fa1" />

Benchmark result of kinetic parameter extraction
<img width="1815" height="1655" alt="fig3" src="https://github.com/user-attachments/assets/be115454-ee08-4ab2-a284-6c9bc97eb139" />

Dataset and Benchmark for using reinforcement learning method to generate optimized prompts
<img width="2001" height="830" alt="fig4" src="https://github.com/user-attachments/assets/1be05371-f41c-485c-9770-c5214d50dc8f" />

The workflow and data analysis of generated database
<img width="2332" height="1055" alt="Fig5" src="https://github.com/user-attachments/assets/1862605f-e8a1-4b0e-a7d3-e1c94fbd9465" />


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
