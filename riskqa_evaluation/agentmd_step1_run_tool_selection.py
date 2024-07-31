__author__ = "qiao"

"""
Run the AgentMD tool selection on RiskQA.
"""

import os
from openai import AzureOpenAI

client = AzureOpenAI(
	api_version="2023-09-01-preview",
	azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
	api_key=os.getenv("OPENAI_API_KEY"),
)

import faiss
import json
from transformers import AutoModel, AutoTokenizer
from agentmd_retrieval_utils import encode_tools, encode_patient
import sys

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
	# first loading the riskqa dataset
	riskqa = json.load(open("dataset/riskqa.json"))
	
	# then loading the calcs
	verified_calcs = json.load(open("tools/riskcalcs.json"))

	# the model to select tools
	model = sys.argv[1]

	# loading the retrieval model
	query_enc = AutoModel.from_pretrained("ncbi/MedCPT-Query-Encoder").to("cuda")	
	article_enc = AutoModel.from_pretrained("ncbi/MedCPT-Article-Encoder").to("cuda")
	tokenizer = AutoTokenizer.from_pretrained("ncbi/MedCPT-Query-Encoder")

	# generate tool embeddings
	# pmids are the inds for tools
	index, pmids = get_tools_index(article_enc, tokenizer, verified_calcs)

	output = {}

	for idx, entry in enumerate(riskqa):
		idx = str(idx)

		# encode the risk
		risk_embed = encode_patient(entry["question"], query_enc, tokenizer)

		# retrieve tools  
		scores, tool_inds = index.search(risk_embed, k=10)
		tool_inds = tool_inds[0]
		patient_tools = [pmids[idx] for idx in tool_inds]

		prompt = "Please choose the most appropriate tool from the listed ones to solve the question below:\n"
		prompt += entry["question"] + "\n"

		for tool_id in patient_tools:
			prompt += f"Tool ID: {tool_id}; Title: {verified_calcs[tool_id]['title'].strip()}; Purpose: {verified_calcs[tool_id]['purpose'].strip()}\n"
		
		prompt += "Please copy the most appropriate tool: "

		response = client.chat.completions.create(
			model=model,
			messages=[{"role": "user", "content": prompt}],
			temperature=0,
		)

		answer = response.choices[0].message.content

		if "Tool ID: " in answer:
			answer = answer.split("Tool ID: ")[-1][:8]
		else:
			# Used the first retrieved tool
			answer = patient_tools[0]

		output[idx] = answer
	
	with open(f"results/{model}_riskqa_tools.json", "w") as f:
		json.dump(output, f, indent=4)
