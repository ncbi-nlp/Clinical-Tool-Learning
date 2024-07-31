__author__ = 'qiao'

"""
Predicting in-hospital mortality with MIMIC admission notes.
"""

import json
import os
import sys
import pandas as pd

from openai import AzureOpenAI

client = AzureOpenAI(
	api_version="2023-09-01-preview",
	azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
	api_key=os.getenv("OPENAI_API_KEY"),
)


if __name__ == "__main__":
	# loading the cached results
	output_path = f"results/file3_patient_tool_selection.json"

	if os.path.exists(output_path):
		output = json.load(open(output_path)) 
	else:
		output = {}

	# loading the candidate tools 
	patient_risk_tools = json.load(open("results/file2_patient_risk_tools.json"))	
	verified_calcs = json.load(open("tools/riskcalcs.json"))

	# loading the MIMIC prediction dataset
	dataset = pd.read_csv("dataset/test.csv")	

	# iterate over the patient dataset
	for row in dataset.iterrows():
		# load the patient data
		_, data = row
		patient_id = str(data["id"])
		patient = data["text"]
		death = data["hospital_expire_flag"]

		# some patients don't have tools cached
		if patient_id not in patient_risk_tools:
			continue
		risk_tools = patient_risk_tools[patient_id]

		if patient_id not in output:
			output[patient_id] = {}
	
		results = {}

		for risk, tools in risk_tools.items():
			# tools are indexed by PMIDs
			for pmid in tools:
				if pmid not in results:
					results[pmid] = {
						"count": 0,
					}

				results[pmid]["count"] += 1

		# loop over the candidate tools
		for pmid in results.keys():
			
			if pmid in output[patient_id]:
				continue

			system = "You are a critical evaluator. Your task is to judge whether the given patient belongs to the eligible population of the given medical calculator. Your response will be used for research purposes only."

			prompt = "Here is the patient admission note:\n"
			prompt += patient + "\n\n"
			prompt += "Here is the calculator:\n"
			prompt += json.dumps(verified_calcs[pmid], indent=4) + "\n"

			prompt += "Please think step-by-step and then judge whether (1) whether the patient is eligible to use the calculator; (2) whether all parameters for the calcualtors are missing in the patient note. Output a json dict formatted as Dict{\"step_by_step_reasoning\": Str(...), \"patient_eligible\": Str(yes|no), \"missing_all_parameters\": Str(yes|no)}."

			messages = [
				{"role": "system", "content": system},
				{"role": "user", "content": prompt},
			]
				
			response = client.chat.completions.create(
				model="gpt-4",
				messages=messages,
				temperature=0.0,
			)

			answer = response.choices[0].message.content

			output[patient_id][pmid] = answer

			with open(output_path, "w") as f:
				json.dump(output, f, indent=4)
