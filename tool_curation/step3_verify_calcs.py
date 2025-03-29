__author__ = "qiao"

"""
Verify the drafted clinical calculators
"""

import glob
import json
import os
import sys

from openai import AzureOpenAI

client = AzureOpenAI(
	api_version="2023-09-01-preview",
	azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
	api_key=os.getenv("OPENAI_API_KEY"),
)

if __name__ == "__main__":
	pmid2info = json.load(open("file0_sample_candidate_articles.json")) 
	
	for path in glob.glob("dir1_pubmed_risk_calcs/*"):

		if ".py" in path:
			continue

		pmid = os.path.basename(path)
		target_path = os.path.join("dir2_risk_calc_verifications", pmid)

		if os.path.exists(target_path):
			continue
		
		with open(path, "r") as f:
			text = f.read()
		
		if text.lower().strip() == "no":
			continue
		
		questions = [
			"Are the parameters clearly defined in the #Computation? If a parameter can have different scores, the definitions for each score must be provided.",
			"Are the parameters defined exactly the same in the article and the calculator?",
			"Is the #Computation logic in the calculator fully based on the original article without any assumptions? Answer no if the article does not provide clear computing logics or weights.",
			"Is the #Interpretation of the calculator fully based on the original article without any assumptions? Score ranges and corresponding risks should be exactly the same between the calculator and the article.",
			"Is the #Interpretation of the calculator useful? A useful calculator should contain quantitative risk rates or qualitative risk groups for different score ranges.",
			"Is the calculator free from any bug or other issue?",
		]
		answer_list = []

		system = "You are a critical evaluator for a calculator that's supposed to describe a PubMed article. The calculator might contain errors. Always response in a JSON dict formatted as Dict{\"reasoning\": Str(critical_reasoning), \"answer\": Str(yes/no)}."

		prompt = ""
		prompt += "Here is the original PubMed article:\n"
		prompt += pmid2info[pmid]["t"] + "\n"
		prompt += pmid2info[pmid]["a"] + "\n"
		prompt += "Here is the calculator that's supposed to describe the article above:\n"
		prompt += text + "\n\n"

		early_stop = False

		for question in questions:
			q_prompt = prompt + question

			messages = [
				{"role": "system", "content": system},
				{"role": "user", "content": q_prompt},
			]

			response = client.chat.completions.create(
				model="gpt-4",
				messages=messages,
				temperature=0,
			)

			response = json.loads(response.choices[0].message.content)

			answer_list.append(response)

			if response["answer"].lower() == "no":
				early_stop = True
			
			if early_stop:
				break

		with open(target_path, "w") as f:
			json.dump(answer_list, f, indent=4)
