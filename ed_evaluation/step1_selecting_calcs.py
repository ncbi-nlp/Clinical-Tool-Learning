__author__ = "qiao"

"""
select the calculators to use for each patient
"""

import json
import os
from openai import AzureOpenAI
import pandas as pd

import sys

client = AzureOpenAI(
	api_version="2023-09-01-preview",
	azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
	api_key=os.getenv("OPENAI_API_KEY"),
)

if __name__ == "__main__":

	model = sys.argv[1]

	# loading cached results
	output_path = f"results/{model}_calc_selections.json"

	if os.path.exists(output_path):
		outputs = json.load(open(output_path))
	else:
		outputs = {}
	
	system = "You are a helpful assistant and your task is to select the calculators that a given patient is eligible for. Here are the candidate calculators:\n"
	system += open("tools/calc_desc.txt", "r").read()
	system += 'Please first explain what calculators a given patient is eligible for, and then output the list of calculaotr IDs. Please output a JSON dict formatted as Dict{"explanation": Str(explanation), "calculators": List[Int(ID)]}. Please be strict.'

	notes = pd.read_csv("dataset/notes_deidentified_verified.csv")

	for _, row in notes.iterrows():
		note_id = row["PAT_ENC_CSN_ID"]

		if note_id in outputs:
			continue

		note = row["deid_text_combined"]
		prompt = "Here is the patient note:\n"
		prompt += note + "\n"
		prompt += "Output in JSON: "

		messages = [
			{"role": "system", "content": system},
			{"role": "user", "content": prompt}
		]

		response = client.chat.completions.create(
			model=model,
			messages=messages,
			temperature=0,
		)

		output = response.choices[0].message.content
		outputs[note_id] = output 

		with open(output_path, "w") as f:
			json.dump(outputs, f, indent=4)
