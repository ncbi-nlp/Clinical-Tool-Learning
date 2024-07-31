__author__ = "qiao"

"""
mapping from the old index to the new index
"""

import json

if __name__ == "__main__":
	old2new = {
		"1": "1",
		"2": "2",
		"3": "3",
		"4": "4",
		"5": "5",
		"6": "6",
		"7": "7",
		"8": "8",
		"9": "9",
		"10": "10",
		"12": "11",
		"13": "12",
		"14": "13",
		"15": "14",
		"16": "15",
		"18": "16",
	}

	# loading the old id2calc dict
	old_id2calc = json.load(open("id2calc_text.json"))
	new_id2calc = {}

	for k, v in old_id2calc.items():
		if k in old2new:
			new = old2new[k]

			new_id2calc[new] = v

	print(len(new_id2calc))

	with open("id2calculator.json", "w") as f:
		json.dump(new_id2calc, f, indent=4)
