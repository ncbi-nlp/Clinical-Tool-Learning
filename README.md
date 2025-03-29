# AgentMD: Empowering Language Agents for Risk Prediction with Large-Scale Clinical Tool Learning

## Introduction

**Background**: Clinical calculators play a vital role in healthcare by offering accurate evidence-based predictions for various purposes, such as diagnosis and prognosis. Nevertheless, their widespread utilization is often hindered by usability challenges and poor dissemination. Augmenting large language models (LLMs) with extensive collections of clinical calculators presents an opportunity to overcome these obstacles and improve workflow efficiency, but the scalability of manual curation and machine adoption poses a significant challenge. 

**Methods**: We introduce AgentMD, a novel LLM-based autonomous agent capable of curating and applying calculators across various clinical contexts. Using the medical literature, AgentMD first curates a diverse set of clinical calculators with executable functions as an automatic tool maker. With the curated tools, AgentMD autonomously selects and applies the relevant clinical calculators to any given patient as a tool user. 

**Findings**: As a tool maker, AgentMD has curated RiskCalcs, a large collection of 2,164 diverse clinical calculators with over 85% accuracy for quality checks and over 90% pass rate for unit tests. With regards to its tool using capability, AgentMD significantly outperforms chain-of-thought prompting with GPT-4 (87.7% vs. 40.9% accuracy) on RiskQA, an end-to-end benchmark manually annotated in this work. Further evaluation results on 698 emergency department admission notes confirm that AgentMD accurately computes medical risks with real-world patient data at an individual level. Moreover, AgentMD can provide population-level insights for institutional risk management as demonstrated using 9,822 patient notes from MIMIC-III.

**Interpretation**: Our study illustrates the exceptional capabilities of language agents to learn clinical calculators and to further utilize curated calculators for both individual patient care and at-scale healthcare analytics.

## Configuration

To run AgentMD, one needs to first set up the OpenAI API either directly through OpenAI or through Microsoft Azure. Here we use Microsoft Azure because it is compliant with the Health Insurance Portability and Accountability Act (HIPAA). Please set the environment variables accordingly:

```bash
export OPENAI_ENDPOINT=YOUR_AZURE_OPENAI_ENDPOINT_URL
export OPENAI_API_KEY=YOUR_AZURE_OPENAI_API_KEY
```

The code has been tested with Python 3.9.13 using CentOS Linux release 7.9.2009 (Core). Please install the required Python packages by (it should take less than 10 minutes on a modern machine):

```bash
pip install -r requirements.txt
```

## Instructions

This repository contains the evaluation scripts for three use cases of AgentMD:

- **Evaluation on the RiskQA dataset**. The RiskQA dataset, the RiskCalcs toolkit, and the evaluation code are available under `./riskqa_evaluation`. Please follow the instructions in `./riskqa_evaluation/README.md` to use AgentMD.
- **Evaluation with ED patients**. We put the AgentMD code for our experiments with Yale ED provider notes under `./ed_evaluation`. However, due to privacy concerns, we are not able to release the ED provider notes from Yale Medicine. As such, users would need to use their own clinical notes to run it.
- **Evaluation with MIMIC patients**. The preprocessing code for MIMIC-III notes as well as the AgentMD code are available under `./mimic_evaluation`. One would need to first download and preprocess the MIMIC-III dataset to run the code, following the instructions at `./ed_evaluation`.

## Acknowledgments

This research was supported by the NIH Intramural Research Program, National Library of Medicine, and 1K99LM014024.

## Disclaimer

This tool shows the results of research conducted in the Computational Biology Branch, DIR/NLM. The information produced on this website is not intended for direct diagnostic use or medical decision-making without review and oversight by a clinical professional. Individuals should not change their health behavior solely on the basis of information produced on this website. NIH does not independently verify the validity or utility of the information produced by this tool. If you have questions about the information produced on this website, please see a health care professional. More information about NCBI's disclaimer policy is available.

## Citation

If you find this repo helpful, please cite AgentMD by:
```bibtex
@article{jin2024agentmd,
  title={AgentMD: Empowering Language Agents for Risk Prediction with Large-Scale Clinical Tool Learning},
  author={Jin, Qiao and Wang, Zhizheng and Yang, Yifan and Zhu, Qingqing and Wright, Donald and Huang, Thomas and Wilbur, W John and He, Zhe and Taylor, Andrew and Chen, Qingyu and others},
  journal={arXiv preprint arXiv:2402.13225},
  year={2024}
}
```
