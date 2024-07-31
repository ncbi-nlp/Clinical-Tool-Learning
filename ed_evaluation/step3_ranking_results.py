__author__ = "qiao"

"""
Give an overall score for the ranking patients.
"""

import json
import os
from openai import AzureOpenAI
import sys

client = AzureOpenAI(
	api_version="2023-09-01-preview",
	azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
	api_key=os.getenv("OPENAI_API_KEY"),
)

if __name__ == "__main__":
	# model choice
	model = sys.argv[1]

	# loading cached results
	output_path = f"results/calc2results_score_{model}.json"

	if os.path.exists(output_path):
		outputs = json.load(open(output_path))
	else:
		outputs = {}
	

	# loading the calculator2results dict
	calc2results = json.load(open(f"results/calc2results_{model}.json"))

	for calc_id, pid2results in calc2results.items():

		# if calc id not even in outputs, initalize the dict
		if calc_id not in outputs:
			outputs[calc_id] = {}

		# pid and the computed summary
		for pid, summary in pid2results.items():
			
			# already cached, then continue
			if pid in outputs[calc_id]:
				continue
			
			system = "You are a helpful medical assistant, and your task is to give an overall score (0-100) given a summary of medical calculation. Higher scores denote more urgent and severe conditions that require immediate attention. If the calculation result contains a wide range, give a low score due to its uncertainty."

			prompt = f"Here is the summary: {summary}\n"
			prompt += "Output only the overall score (0-100): "

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
			outputs[calc_id][pid] = output

			with open(output_path, "w") as f:
				json.dump(outputs, f, indent=4)
