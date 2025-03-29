# Curating tools with AgentMD

## Step 0: Processing PubMed data
A full list of PMIDs returned by the Boolean query is shown in `file1_full_classification_results.json`, and the corresponding PubMed abstracts can be downloaded at https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/.
One can use `file0_sample_candidate_articles.json` to run demonstration scripts in this directory.

## Step 1: Calculator Screening

The first step is screening potential calculator-describing abstracts by GPT-3.5-Turbo. Please run:

```bash
python step1_classify.py
```

The demonstration code results will be saved as `file0_sample_candidate_articles.json`. We also provided the pre-computed full results in `file1_full_classification_results.jsonl`.

## Step 2: Calculator Drafting

The second step is to draft calculators in a structured format with GPT-4. Please run:

```bash
python step2_draft_calcs.py
```

The results will be saved in `./dir1_pubmed_risk_calcs/` and indexed by their corresponding PMIDs.

## Step 3: Calculator Verification

The third step is the verification of drafted calculators. Please run:

```bash
python step3_verify_calcs.py
```

The results will be saved in `./dir2_risk_calc_verifications/` and indexed by their corresponding PMIDs.

## Acknowledgments

This research was supported by the NIH Intramural Research Program, National Library of Medicine, and 1K99LM014024.

## Disclaimer

This tool shows the results of research conducted in the Computational Biology Branch, NLM. The information produced on this website is not intended for direct diagnostic use or medical decision-making without review and oversight by a clinical professional. Individuals should not change their health behavior solely on the basis of information produced on this website. NIH does not independently verify the validity or utility of the information produced by this tool. If you have questions about the information produced on this website, please see a health care professional. More information about NCBI's disclaimer policy is available.

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
