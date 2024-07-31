__author__ = "qiao"

"""
Apply the selected tools to each patient with AgentMD.
"""

import json
import contextlib
import os
import io
import re
import traceback
import sys
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


def apply_calc(patient, calc, model):
	"""apply the calculator to a specific patient"""
	system = "You are a helpful assistant. Your task is to apply a medical calculator to a patient and interpret the result. You can write Python scripts and the user will execute them for you. The Python function in the calculator has already been in the enviroment, which you can re-use or revise if there is bug. Your responses will be used for research purposes only. Please start with \"Summary: \" to summarize the messages in one paragraph if you have finished the task. Please make sure to include the raw results of the calculator in the summary."

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
			model=model,
			messages=messages,
			temperature=0,
		)

		output = response.choices[0].message

		n += 1
		print(f"Round {n}")
		print(output.content)

		message = output 
		messages.append({"role": "assistant", "content": message.content})

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
	# gpt-4-32k or gpt-35-turbo-16k
	model = sys.argv[1]

	# loading the cached results
	output_path = f"results/patient_results_{model}.json"

	if os.path.exists(output_path):
		output = json.load(open(output_path))
	else:
		output = {}
	
	# tool selection results
	patient_tools = json.load(open(f"results/{model}_calc_selections.json"))

	id2calc_txt = json.load(open("tools/id2calculator.json"))

	# loading the patient dataset
	notes = pd.read_csv("dataset/notes_deidentified_verified.csv")

	for _, row in notes.iterrows():
		patient_id = str(row["PAT_ENC_CSN_ID"])
		note = row["deid_text_combined"]

		if patient_id not in output:
			output[patient_id] = {}

		tool_selection = patient_tools[patient_id]

		try:
			tools = json.loads(tool_selection)["calculators"]
		except:
			continue

		for tool in tools:
			tool = str(tool)

			# already cached
			if tool in output[patient_id]:
				continue
			
			# errors in the selection step
			if tool not in id2calc_txt:
				continue

			calc_text = id2calc_txt[tool]

			try:
				messages, summary = apply_calc(note, calc_text, model)
			except:
				continue

			output[patient_id][tool] = [summary, messages]

			with open(output_path, "w") as f:
				json.dump(output, f, indent=4)
