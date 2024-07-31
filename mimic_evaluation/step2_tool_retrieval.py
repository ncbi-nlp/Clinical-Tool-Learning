__author__ = 'qiao'

"""
Predicting in-hospital mortality with MIMIC admission notes.
"""

import json
import os
import sys
import pandas as pd

import faiss
from transformers import AutoModel, AutoTokenizer

from agentmd_retrieval_utils import encode_tools, encode_patient

def get_tools_index(model, tokenizer, verified_calcs):
	"""Get the Faiss index for the tools."""	
	verified_pmids = list(verified_calcs.keys())
	pmid2info = json.load(open("dataset/pmid2info.json"))

	# initialize tool texts for encoding
	# also the tool titles (for idx -> title)
	tool_texts = []

	# loop over summaries
	for pmid in verified_pmids:
		info = pmid2info[pmid]

		# add to tool_texts
		tool_texts.append(
			[
				info["t"], 
				info["a"],
			]
		)

	tool_embeds = encode_tools(tool_texts, model, tokenizer)
	index = faiss.IndexFlatIP(768)
	index.add(tool_embeds)

	return index, verified_pmids 

if __name__ == "__main__":
	verified_calcs = json.load(open("tools/riskcalcs.json"))

	# loading the pre-computed risks
	patient_risks = json.load(open("results/file1_patient_risks.json"))	

	# loading the retrieval model
	query_enc = AutoModel.from_pretrained("ncbi/MedCPT-Query-Encoder").to("cuda")	
	article_enc = AutoModel.from_pretrained("ncbi/MedCPT-Article-Encoder").to("cuda")
	tokenizer = AutoTokenizer.from_pretrained("ncbi/MedCPT-Query-Encoder")

	# generate tool embeddings
	# pmids are the inds for tools
	index, pmids = get_tools_index(article_enc, tokenizer, verified_calcs)

	output = {}

	# iterate over patients
	for patient_id, risks in patient_risks.items():
		results = {}

		# loop over the LLM-generated risks
		for risk in risks:
			# encode the risk
			risk_embed = encode_patient(risk, query_enc, tokenizer)

			# retrieve tools  
			scores, tool_inds = index.search(risk_embed, k=10)
			tool_inds = tool_inds[0]
			patient_tools = [pmids[idx] for idx in tool_inds]

			results[risk] = patient_tools	

		output[patient_id] = results
	
	with open("results/file2_patient_risk_tools.json", "w") as f:
		json.dump(output, f, indent=4)
