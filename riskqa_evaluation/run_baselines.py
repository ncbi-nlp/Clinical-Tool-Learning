__author__ = "qiao"

"""
Run baselines for the RiskQA dataset.
"""

import sys
import json
import os

from openai import AzureOpenAI

client = AzureOpenAI(
	api_version="2023-09-01-preview",
	azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
	api_key=os.getenv("OPENAI_API_KEY"),
)

def print_question(entry):
	question = "Question: " + entry["question"] + "\n"
		
	for char, choice in entry["choices"].items():
		question += f"{char}. {choice}\n"
	
	return question


if __name__ == "__main__":
	tools = json.load(open("../file3b_calcs.json"))
	dataset = json.load(open("file4_riskqa.json"))	

	# this is for the abstract oracle
	pmid2info = json.load(open("../dir0_screening_pubmed/file1_candidate_articles.json"))

	# gpt-35-turbo or gpt-4
	model = sys.argv[1]

	# "yes" or "no" or ""
	oracle = sys.argv[2]
	
	output_path = f"file5_{model}_oracle{oracle}_results.json"

	if os.path.exists(output_path):
		output = json.load(open(output_path))
	else:
		output = {}

	acc_list = []

	for idx, entry in enumerate(dataset):
		idx = str(idx)
		if idx in output: continue

		pmid = entry["pmid"]		
	
		system = "You are a helpful assistant. Your task is to answer a mediacl examination question. Please indicate your answer choice (A/B/C/D/E) at the end of your answer by \"Therefore, the answer is A/B/C/D/E.\"."

		question = print_question(entry)
		prompt = question + "\n" 

		if oracle == "yes":
			prompt += f"Use {tools[pmid]['title'].strip()} to solve the question. Let's think step-by-step."

		elif oracle == "no":
			prompt += "Let's think step-by-step."

		elif oracle == "abstract":
			prompt += "Let's use this article to solve the question:\n"
			prompt += f"Title: {pmid2info[pmid]['t']}\n"
			prompt += f"Abstract: {pmid2info[pmid]['a']}\n"

		messages = [
			{"role": "system", "content": system},
			{"role": "user", "content": prompt},
		]

		response = openai.ChatCompletion.create(
			engine=model,
			messages=messages,
			temperature=0,
		)
		
		answer = response["choices"][0]["message"]["content"]

		output[idx] = answer

		with open(output_path, "w") as f:
			json.dump(output, f, indent=4)
