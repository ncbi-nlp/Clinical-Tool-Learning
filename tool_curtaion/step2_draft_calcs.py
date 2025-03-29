__author__ = "qiao"

"""
Draft risk calculators
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
	system = "You are a helpful assistant programmer for medical calculators. Your task is to read a PubMed article about a medical calculator, and if applicable, write a two-step calculator: (1) calculator a risk score based on multiple criteria; (2) interpret different ranges of the computed risk score into probabilities of risks."
	
	pmid2info = json.load(open("file0_sample_candidate_articles.json"))
	
	cand_pmids = []
	with open("file1_full_classification_results.jsonl", "r") as f:
		for line in f.readlines():
			line = json.loads(line.strip())
			
			if line["result"].lower() == "yes":
				cand_pmids.append(line["pmid"])
	
	for pmid in cand_pmids:
		target_path = os.path.join("dir1_pubmed_risk_calcs", pmid)

		if os.path.exists(target_path):
			continue

		if pmid not in pmid2info:
			print(f"PMID {pmid} information not found. Please load the full file 0 candidate articles!")
			continue

		prompt = "Here is a PubMed article:\n"
		prompt += pmid2info[pmid]["t"] + "\n"
		prompt += pmid2info[pmid]["a"] + "\n"

		prompt += "Does the article describes a simple two-step risk calculator, where the first step is to compute a risk score, and the second step is to interpret different risk scores? If no, please directly and only output \"NO\". Otherwise, please standardize the calculator into:\n"

		prompt += "#Title\nThe name of the calculator(s).\n"

		prompt += "##Purpose\nDescribe when this calculator should be used.\n"

		prompt += "##Specialty\nshould be a list of calculator types, one or more of (Allergy and Immunology, Anesthesiology, Cardiology, Dermatology, Emergency Medicine, Endocrinology, Family Medicine, Gastroenterology, Geriatrics, Hematology, Infectious Disease, Internal Medicine, Nephrology, Neurology, Obstetrics and Gynecology, Oncology, Ophthalmology, Orthopedic Surgery, Otolaryngology, Pathology, Pediatrics, Physical Medicine and Rehabilitation, Plastic Surgery, Psychiatry, Pulmonology, Radiology, Rheumatology, Surgery, Urology), seperated by \",\".\n"

		prompt += "##Eligibility\nDescribe what patients are eligible.\n"

		prompt += "##Size\nThe exact number of patients used to derive this calculator. Only put a number here without any other texts.\n"

		prompt += "##Computation\nDetailed instructions of how to use the calculator, including Python functions with clear docstring documentation. Please be self-contained and detailed. For example, if the computation involves multiple items, please clearly list each item. If one item has multiple possible values (e.g., 0-2), you also need to clearly define what each value means.\n"

		prompt += "##Interpretation\nShould be a list, where each item describes the interpretation (actual risk) for a value or a range of the computed risk score.\n"

		prompt += "##Utility\nEvaluation results of the  clinical utility of the risk score, such as AUC, F-score, PPV.\n"

		prompt += "##Example\nGenerate a sample patient note and a detailed demonstration of using the calculator and interpret the results. Think step-by-step here.\n"

		prompt += "Please be as detailed as possible.\n"

		messages = [
			{"role": "system", "content": system},
			{"role": "user", "content": prompt},
		]

		response = client.chat.completions.create(
			model="gpt-4",
			messages=messages,
			temperature=0,
		)

		result = response.choices[0].message.content
		
		with open(target_path, "w") as f:
			f.write(result)
