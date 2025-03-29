__author__ = "qiao"

"""
Classify whether the candidate article introduces a new risk score / calculator.
"""

import json
import os

from openai import AzureOpenAI

client = AzureOpenAI(
	api_version="2023-09-01-preview",
	azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
	api_key=os.getenv("OPENAI_API_KEY"),
)

if __name__ == "__main__":
	# load cached results
	target_path = "file1_sample_classification_results.jsonl"
	done_pmids = []
	if os.path.exists(target_path):
		with open(target_path, "r") as f:
			for line in f.readlines():
				done_pmids.append(json.loads(line.strip())["pmid"])
	done_pmids = set(done_pmids)

	# loop over all pmids
	cands = json.load(open("file0_sample_candidate_articles.json", "r"))
	for pmid, info in cands.items():
		if pmid in done_pmids:
			continue

		prompt = "Here is a PubMed article:\n" 
		prompt += info["t"] + "\n" 
		prompt += info["a"] + "\n"
		prompt += "Does this article describe a new risk score or risk calculator? In healthcare, a risk score quantitatively estimates the probability of a clinical event or outcome, such as disease development or progression, within a specified period. These scores are derived from algorithms using variables like patient demographics, clinical history, laboratory results, and other relevant health indicators. They aid clinicians in decision-making, allowing for personalized patient care and resource allocation. Simply answer with \"yes\" or \"no\":"

		response = client.chat.completions.create(
			model="gpt-35-turbo",
			messages=[{"role": "user", "content": prompt}],
			temperature=0,
		)

		result = response.choices[0].message.content

		with open(target_path, "a") as f:
			f.write(json.dumps({"pmid": pmid, "result": result}) + "\n")

		done_pmids.add(pmid)
