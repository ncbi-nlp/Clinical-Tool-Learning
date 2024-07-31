__author__ = "qiao"

"""
Retrieve relevant tools given a patient description.
"""

import json
import faiss
from tqdm import trange
import torch

def encode_tools(
	tool_texts, 
	model,
	tokenizer,
	batch_size=16,
	device="cuda"
):
	"""Given a list of tools, return their encoded vectors"""
	tool_embeddings = []

	with torch.no_grad():
		for start_idx in trange(0, len(tool_texts), batch_size):
			encoded = tokenizer(
				tool_texts[start_idx: start_idx + batch_size], 
				truncation=True,
				padding=True,
				return_tensors="pt",
				max_length=512,
			)
			encoded.to(device)

			model_output = model(**encoded)
			tool_embeddings += model_output.last_hidden_state[:, 0, :].detach().cpu()

	tool_embeddings = torch.stack(tool_embeddings).numpy()
	
	return tool_embeddings


def encode_patient(
	patient,
	model,
	tokenizer,
	device="cuda"
):
	"""Given a patient note, return its encoded vector"""
	with torch.no_grad():
		encoded = tokenizer(
			[patient],
			truncation=True,
			padding=True,
			return_tensors="pt",
			max_length=512,
		)
		encoded.to(device)

		model_output = model(**encoded)
		patient_embedding = model_output.last_hidden_state[:, 0, :].detach().cpu()
	
	return patient_embedding.numpy()
