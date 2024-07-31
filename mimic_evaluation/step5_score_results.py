__author__ = "qiao"

"""
Using the selected tools.
"""

import json
import contextlib
import os
import io
import re
import traceback

import pandas as pd

import openai
openai.api_type = "azure"
openai.api_base = "https://bionlp-gpt4.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = "48f46b68e4e14c3c8a9be9522dbdc6e7"

if __name__ == "__main__":
	# loading the cached patient predictions 
	output_path = "file8b_risk_ranking.json"
	if os.path.exists(output_path):
		output = json.load(open(output_path))
	else:
		output = {}

	# loading the patient dataset
	patients = json.load(open("file0_mimic_patients.json"))
	
	# loading the patient tool-using results
	patient2results = json.load(open("file4_patient_tool_results.json"))

	for patient_id, tool2results in patient2results.items():
		for tool, results in tool2results.items():
			uid = "-".join([patient_id, tool])
			if uid in output: continue

			system = "You are a helpful assistant for a hospital warning system. Your task is to determine the specificity, urgency, severity, and absence of a risk calculator result applied to a patient. Your response will be used for research purposes only."
			
			note = patients[patient_id][0]
			prompt = f"Here is the patient note: \n{note}\n\n"
			summary = results[0]
			prompt += f"Here is the calculator result: \n{summary}\n\n"
			prompt += "Specificity (0-100) denotes the confidence of the calculator result. Specificity is low if there are missing values and the range is wide between the risk scores of the best-case and worst-case scenarios. Specificity is high if there is no range estimation (best and worse case scenarios) and the risk calculator result contains only one specific score (not a range).\n"
			prompt += "Urgency (0-100) denotes whether the risk considered by the calculator is acute or chronic. Urgency is high if there is immediate danger worth medical attention. On the other hand, urgency is low if the risk is about 1-year or 5-year.\n"
			prompt += "Severity (0-100) denotes the extent of the calculated risk. Severity is high if the predicted risk probability is close to 100%. Severity if low if the predicted risk probability is close to 0%.\n"
			prompt += "Absence (0-100) denotes whether the calculated risk is missing in the original patient note. Absence is 100 if the calculator result (the risk, not the calculator name) is not considered or reflected in the patient note. Absence is 0 if the calculator result has already happened or been considered in the patient note.\n"
			prompt += 'Please be critical and only output a json dict formatted as: {"rationale": Str(detailed_explanations_for_all_scores), "specificity": float(0-100), "urgency": float(0-100), "severity": float(0-100), "absence": float(0-100)}.'


			messages = [
				{"role": "system", "content": system},
				{"role": "user", "content": prompt},
			]

			response = openai.ChatCompletion.create(
				engine="gpt-4",
				messages=messages,
				temperature=0.0,
			)

			response = response["choices"][0]["message"]["content"]

			output[uid] = response

			with open(output_path, "w") as f:
				json.dump(output, f, indent=4)
