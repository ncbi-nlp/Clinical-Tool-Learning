__author__ = "qiao"

"""
Using the selected tools with AgentMD.
"""

import json
import contextlib
import os
import io
import re
import sys
import traceback

import pandas as pd

from openai import AzureOpenAI

client = AzureOpenAI(
	api_version="2023-09-01-preview",
	azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
	api_key=os.getenv("OPENAI_API_KEY"),
)


def print_question(entry):
	question = "Question: " + entry["question"] + "\n"
		
	for char, choice in entry["choices"].items():
		question += f"{char}. {choice}\n"
	
	return question


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
	system = "You are a helpful assistant. Your task is to apply a medical calculator to solve an USMLE-style question. You can write Python scripts and the user will execute them for you. The Python function in the calculator has already been in the enviroment, which you can re-use or revise if there is bug. Your responses will be used for research purposes only. Please start with \"Answer: \" to choose the answer if you have finished the task. Please choose the closest answer if there is no exact match."

	prompt = "Here is the calculator:\n"
	prompt += calc + "\n"
	prompt += "Here is the USMLE question:\n"	
	prompt += patient + "\n"
	prompt += "Please apply this calculator to the patient. Please write Python scripts and `print()` the results to help the computation. I will provide the stdout to you."

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

		n += 1
		print(f"Round {n}")
		print(response.choices[0].message.content)

		message = response.choices[0].message.content
		messages.append(
			{"role": "assistant", "content": message}
		)

		if "Answer: " in message:
			return messages, message.split("Answer: ")[-1]
		
		else:
			message_code = extract_python_code(message)

			if message_code:
				code = prompt_code + message_code
				output = "I have executed your code, and the output is:\n" + capture_exec_output_and_errors(code)
			
			else:
				output = "If you have sucessfully applied the calculator. Please start a new message with \"Answer: \"."

			messages.append(
				{"role": "user", "content": output}
			)

		if n >= 20:
			return messages, "Failed"


if __name__ == "__main__":
	# AgentMD base model. Choices: gpt-4 & gpt-35-turbo
	model = sys.argv[1]

	# whether using the oracle tool: yes or no
	oracle = sys.argv[2]

	# loading the chosen tools
	qid2tool = json.load(open(f"results/{model}_riskqa_tools.json"))

	# loading the cached results
	output_path = f"results/{model}_oracle{oracle}_riskqa_answers.json"
	if os.path.exists(output_path):
		output = json.load(open(output_path))
	else:
		output = {}

	# loading the dataset & tools 
	riskqa = json.load(open("dataset/riskqa.json"))
	verified_calcs = json.load(open("tools/riskcalcs.json"))

	for idx, entry in enumerate(riskqa):
		idx = str(idx)

		if oracle == "yes":
			tool = entry["pmid"]
		else:
			tool = qid2tool[idx]

		# if already cached, continue
		if idx in output:
			continue

		try:
			calc = verified_calcs[tool]
			calc_text = ""
			for k, v in calc.items():
				if k == "example": continue
				calc_text += k.upper() + "\n"
				calc_text += str(v)

			patient = print_question(entry) 
			messages, summary = apply_calc(patient, calc_text)

			output[idx] = [summary, messages]

			with open(output_path, "w") as f:
				json.dump(output, f, indent=4)

		except Exception as E:
			print(E)
			continue
