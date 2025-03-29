## Step 1: Running the AgentMD Tool Retrieval and Selection
The first step of AgentMD on RiskQA is to retrieval relevant calculators for a given question and then apply LLMs to select the appropriate one.

```bash
# syntax: python agentmd_step1_run_tool_selection.py ${model}
# ${model} can be any model indices in OpenAI or AzureOpenAI API
# example below
python agentmd_step1_run_tool_selection.py gpt-4o
```

The results will be saved in `results/${model}_riskqa_tools.json`.

## Step 2: Running the AgentMD Tool Computation
After getting the tool retrieval and selection results of a model, one can run the the AgentMD tool computation script below:

```bash
# syntax: python agentmd_step2_run_tool_computation.py ${model} ${oracle}
# ${model} can be any model indices in OpenAI or AzureOpenAI API
# ${oracle} can be either yes or no. If yes, the ground-truth tool will be used; Otherwise, the selected tool from step 1 will be used.
# example below
python agentmd_step2_run_tool_computation.py gpt-4o no
```

## Evaluation
To evaluate the results generated in Step 2, one can run:

```bash
# syntax: python get_overall_performance.py ${result_path} 
# ${result_path} is the path to the results save in step 2
# example below
python get_overall_performance.py results/gpt-4o_oracleno_riskqa_answers.json 
```

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
