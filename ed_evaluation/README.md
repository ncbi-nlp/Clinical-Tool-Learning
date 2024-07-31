## Data

Due to privacy concerns, we cannot release the emergency department notes from Yale Medicine. This direcoty provides the code that can work on the user-provided clinical notes from emergency care.  

## Step 1: AgentMD tool selection

```bash
python step1_selecting_calcs.py 
```

## Step 2: AgentMD tool computation

```bash
python step2_selecting_calcs.py 
```

## Step 3: AgentMD tool summarization and scoring

```bash
python step3_ranking_results.py 
```

## Acknowledgments

This research was supported by the NIH Intramural Research Program, National Library of Medicine, and 1K99LM014024.

## Disclaimer

This tool shows the results of research conducted in the Computational Biology Branch, NCBI/NLM. The information produced on this website is not intended for direct diagnostic use or medical decision-making without review and oversight by a clinical professional. Individuals should not change their health behavior solely on the basis of information produced on this website. NIH does not independently verify the validity or utility of the information produced by this tool. If you have questions about the information produced on this website, please see a health care professional. More information about NCBI's disclaimer policy is available.

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
