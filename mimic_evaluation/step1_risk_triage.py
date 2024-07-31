__author__ = "qiao"

"""
Applying AgentMD to MIMIC patients.
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
	# parameters
	output_path = "results/file1_patient_risks.json"

	# loading the cached results
	if os.path.exists(output_path):
		output = json.load(open(output_path)) 
	else:
		output = {}

	# loading the MIMIC prediction dataset
	dataset = pd.read_csv("dataset/test.csv")	

	# iterate over the patient dataset
	for row in dataset.iterrows():
		# load the patient data
		_, data = row
		patient_id = str(data["id"])
		patient = data["text"]
		death = data["hospital_expire_flag"]

		# if already cached, continue
		if patient_id in output:
			continue
		
		# construct prompt
		system = "You are a helpful assistant doctor. Your task is to generate a list of risks for the given patient. Your response is for research purpose only and will not be used in clinical practice."

		prompt = "Here is the patient admission note:\n"
		prompt += patient + "\n\n"

		prompt += "Please generate a list of 5 potential clinical risks that are significant, urgent, and specific to the patient. Output a json list where each element is a self-contained short risk string that contains both the risk event and the underlying condition, e.g. \"X due to Y\". Please be concise, and each risk should only contain several words."

		messages = [
			{"role": "system", "content": system},
			{"role": "user", "content": prompt},
		]
		
		try:
			response = client.chat.completions.create(
				model="gpt-4",
				messages=messages,
				temperature=0.0,
			)

			answer = response.choices[0].message.content
			answer = json.loads(answer)

			output[patient_id] = answer

			with open(output_path, "w") as f:
				json.dump(output, f, indent=4)

		except Exception as e:
			print(e)
			continue
