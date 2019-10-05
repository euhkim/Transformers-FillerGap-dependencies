#!/usr/bin/python3
import sys
import torch
from pytorch_transformers import TransfoXLTokenizer, TransfoXLModel

# Load pre-trained model tokenizer (vocabulary)
tokenizer = TransfoXLTokenizer.from_pretrained('transfo-xl-wt103')

# Load pre-trained model (weights)
model = TransfoXLModel.from_pretrained('transfo-xl-wt103')

# Read items from file
with open('items_fg_emb_gpt2_sai.csv', encoding='utf8') as f:
	text = f.read().splitlines()

# Write to file
orig_stdout = sys.stdout
f = open('out_fg_emb_txl_sai.txt', 'w')
sys.stdout = f

# Write Column Headers
print("SentenceID, Surprisal, Condition, EmbeddingLevel")

for s in text:
	splits = s.split(',')
	item = splits[1] 
	indexed_tokens = tokenizer.encode(item)

	# Convert inputs to PyTorch tensors
	tokens_tensor = torch.tensor([indexed_tokens])

	# If you have a GPU, put everything on cuda
	tokens_tensor = tokens_tensor.to('cuda')
	model.to('cuda')

	# Predict all tokens
	with torch.no_grad():
		predictions, past = model(tokens_tensor)

	predictions = torch.nn.functional.softmax(predictions,-1)

	# get the predictions 
	result = predictions[0, -1, :]
	word_id = tokenizer.encode('at')[0]
	#word_id = tokenizer.encode('and')[0]

	score = result[word_id]
	surprisal =  -1*torch.log2( score )
	
	# If are using have a GPU, you must copy tensor to host before printing:
	surprisal = surprisal.cpu()

	# Output
	print(splits[0], surprisal.numpy(), splits[2],splits[3],sep=u",")

# Close output stream
sys.stdout = orig_stdout
f.close()
