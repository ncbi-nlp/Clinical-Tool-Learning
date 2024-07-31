__author__ = "qiao"

import json
from sklearn.metrics import accuracy_score
import sys

def extract_answer(answer):
	for choice in ["A", "B", "C", "D", "E", "F"]:
		if choice + "." in answer:
			return choice
	
	return "X"

if __name__ == "__main__":
	# loading the riskqa
	riskqa = json.load(open("dataset/riskqa.json"))

	# result path is an argument
	result_path = sys.argv[1]

	# loading the predictions
	gpt = json.load(open(result_path))
	gpt_answers = []

	all_answers = []
	all_preds = []

	for idx, entry in enumerate(riskqa):
		idx = str(idx)

		if idx not in gpt:
			gpt_answer = "X"
		else:	
			if type(gpt[idx]) is str:
				gpt_answer = gpt[idx]
			else:
				gpt_answer = gpt[idx][0]
			gpt_answer = extract_answer(gpt_answer)

		all_answers.append(entry["answer"])
		all_preds.append(gpt_answer)
	
	print(accuracy_score(all_answers, all_preds))
