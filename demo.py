import os
import torch
import time
import re
import subprocess
import json
from transformers import AutoModelForCausalLM, AutoTokenizer

def generate_response(model, tokenizer, query, device):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    model_inputs = tokenizer([text], return_tensors="pt").to(device)
    
    generated_ids = model.generate(
        input_ids=model_inputs.input_ids,
        max_new_tokens=512,
    )
    
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

def load_model_and_tokenizer(local_model_path, device):
    model = AutoModelForCausalLM.from_pretrained(
        local_model_path,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(local_model_path)
    return model, tokenizer

device = "cuda"
local_model_path2 = "./model/stage2/zeroshot/1b-sft"
model2, tokenizer2 = load_model_and_tokenizer(local_model_path2, device)
category_file_path = "./other_dataset/category/wiki.json"
original_sentence = "Kobe is out"
entity = "Kobe"
with open(category_file_path, "r", encoding="utf-8") as f:
    category_data = json.load(f, strict=False)
    first_level = category_data["first-level"].lower()
query = f'The ##{entity}## in the sentence: "{original_sentence}" belong to which entity in the first list: {first_level}?'
print(query)
entity_type = generate_response(model2, tokenizer2, query, device).strip().lower()

print(entity_type)