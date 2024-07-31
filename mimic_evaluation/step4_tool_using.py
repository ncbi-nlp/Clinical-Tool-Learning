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
from openai import AzureOpenAI

client = AzureOpenAI(
	api_version="2023-09-01-preview",
	azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
	api_key=os.getenv("OPENAI_API_KEY"),
)

def capture_exec_output_and_errors(code):
	"""
	Executes the given code and captures its printed output and any error messages.

	Parameters:
	code (str): The Python code to execute.

	Returns:
	str: The captured output and error messages of the executed code.
	"""
	globals = {}

	with io.StringIO() as buffer, contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
		try:
			exec(code, globals)
		except Exception as e:
			# Print the error to the buffer
			traceback.print_exc()
		
		return buffer.getvalue()


def extract_python_code(text):
	pattern = r"```python\n(.*?)```"
	matches = re.findall(pattern, text, re.DOTALL)
	return "\n".join(matches)


def apply_calc(patient, calc):
	"""apply the calculator to a specific patient"""
	system = "You are a helpful assistant. Your task is to apply a medical calculator to an imaginary patient and interpret the result. You can write Python scripts and the user will execute them for you. The Python function in the calculator has already been in the enviroment, which you can re-use or revise if there is bug. Your responses will be used for research purposes only. Please start with \"Summary: \" to summarize the messages in one paragraph if you have finished the task. Please make sure to include the raw results of the calculator in the summary."

	prompt = "Here is the calculator:\n"
	prompt += calc + "\n"
	prompt += "Here is the patient information:\n"	
	prompt += patient + "\n"
	prompt += "Please apply this calculator to the patient. If there are missing values, please make a range estimation based on best and worst case scenarios inferred from the calculator computing logics. Please write Python scripts and print the results to help the computation. I will provide the stdout to you."

	prompt_code = extract_python_code(prompt)

	messages = [
		{"role": "system", "content": system},
		{"role": "user", "content": prompt},
	]
	
	n = 0

	while True:
		response = client.chat.completions.create(
			model="gpt-4",
			messages=messages,
			temperature=0,
		)
		n += 1
		print(f"Round {n}")
		print(response.choices[0].message.content)

		message = response.choices[0].message
		messages.append(message)

		if "Summary: " in message.content:
			return messages, message.content.split("Summary: ")[-1]
		
		else:
			message_code = extract_python_code(message.content)

			if message_code:
				code = prompt_code + message_code
				output = "I have executed your code, and the output is:\n" + capture_exec_output_and_errors(code)
			
			else:
				output = "If you have sucessfully applied the calculator. Please start a new message with \"Summary: \"."

			messages.append(
				{"role": "user", "content": output}
			)

		if n >= 20:
			return messages, "Failed"


if __name__ == "__main__":
	# loading the cached results
	output_path = "results/file4_patient_tool_results.json"
	if os.path.exists(output_path):
		output = json.load(open(output_path))
	else:
		output = {}

	patient_tools = json.load(open("results/file3_patient_tool_selection.json"))
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
		print(patient_id)

		# if already cached, continue
		if patient_id in output:
			continue

		# patient id not cached
		if patient_id not in patient_tools:
			continue

		tool2results = patient_tools[patient_id]

		eli_list = []

		output[patient_id] = {}

		try:
			# tool is indexed by PMID
			for tool, results in tool2results.items():
				answer = json.loads(results)
				eligibility = answer["patient_eligible"]	
				eli_list.append(eligibility)

				missing = answer["missing_all_parameters"]
				
				# if not eligible, not using it
				if eligibility.lower() != "yes": continue
				if missing.lower() != "no": continue

				calc = verified_calcs[tool]
				calc_text = ""
				for k, v in calc.items():
					if k == "example": continue
					calc_text += k.upper() + "\n"
					calc_text += str(v)

				messages, summary = apply_calc(patient, calc_text)

				output[patient_id][tool] = [summary, messages]

			with open(output_path, "w") as f:
				json.dump(output, f, indent=4)

		except Exception as E:
			print(E)
			continue
