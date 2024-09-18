import json
import os
import torch
import time
import re
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_model_and_tokenizer(local_model_path, device):
    model = AutoModelForCausalLM.from_pretrained(
        local_model_path,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(local_model_path)
    return model, tokenizer

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

def extract_entities_from_response(response):
    entities = re.findall(r"##(.*?)##", response)
    return entities

def categorize_entities(entities, original_sentence, model2, tokenizer2, device, category_file_path):
    with open(category_file_path, "r", encoding="utf-8") as f:
        category_data = json.load(f, strict=False)

    first_level = category_data["first-level"].lower()
    first_level_category = []
    second_level_category = []
    entity_categories = []

    for entity in entities:
        entity_lower = entity.lower()
        query = f'The ##{entity_lower}## in the sentence: "{original_sentence}" belong to which entity in the first list: {first_level}'
        entity_type = generate_response(model2, tokenizer2, query, device).strip().lower()
        first_level_category.append(entity_type)

    if "second-level" not in category_data:
        return first_level_category

    for count, entity in enumerate(entities):
        if first_level_category[count] not in category_data["second-level"]:
            return []
        second_level = category_data["second-level"][first_level_category[count]].lower()
        entity_lower = entity.lower()
        query = f'The ##{entity_lower}## in the sentence: "{original_sentence}" belong to which entity in the second list: {second_level}'
        entity_type = generate_response(model2, tokenizer2, query, device).strip().lower()
        second_level_category.append(entity_type)

    if "third-level" not in category_data:
        return second_level_category

    for count, entity in enumerate(entities):
        if second_level_category[count] not in category_data["third-level"]:
            return []
        third_level = category_data["third-level"][second_level_category[count]].lower()
        entity_lower = entity.lower()
        query = f'The ##{entity_lower}## in the sentence: "{original_sentence}" belong to which entity in the third list: {third_level}'
        entity_type = generate_response(model2, tokenizer2, query, device).strip().lower()
        entity_categories.append(entity_type)

    return entity_categories

def find_non_overlapping_phrases(sentence1, sentence2):
    def extract_phrases_without_hash(sentence):
        phrases = []
        clean_sentence = sentence.replace("##", "")
        start = 0
        original_index = 0

        while original_index < len(sentence):
            original_index = sentence.find("##", original_index)
            if original_index == -1:
                break
            end_index = sentence.find("##", original_index + 2)
            if end_index == -1:
                break
            phrase = sentence[original_index + 2:end_index]
            clean_start = len(sentence[:original_index].replace("##", ""))
            clean_end = clean_start + len(phrase)
            phrases.append((clean_start, clean_end, phrase))
            original_index = end_index + 2
        return phrases

    phrases1 = extract_phrases_without_hash(sentence1)
    phrases2 = extract_phrases_without_hash(sentence2)

    non_overlapping_phrases = []

    for start2, end2, phrase2 in phrases2:
        overlap_found = False
        for start1, end1, phrase1 in phrases1:
            if not (end2 <= start1 or end1 <= start2):
                overlap_found = True
                break
        if not overlap_found:
            non_overlapping_phrases.append(phrase2)

    return non_overlapping_phrases

def process_json_input(input_file, output_file, model1, tokenizer1, model2, tokenizer2, device, repeat, limit, category_file_path):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f, strict=False)

    result_data = {}
    start_time = time.time()

    count = 0

    for i, sentence_data in data.items():
        user_input = sentence_data["sentence"]
        
        if user_input:
            response = generate_response(model1, tokenizer1, user_input, device)
            entities = extract_entities_from_response(response)

            for j in range(repeat - 1):
                new_response = generate_response(model1, tokenizer1, user_input, device)
                entities += find_non_overlapping_phrases(response, new_response)

            if entities:
                categories = categorize_entities(entities, user_input, model2, tokenizer2, device, category_file_path)
                if categories == []:
                    continue
                result_data[i] = {
                    "sentence": user_input,
                    "entity": entities,
                    "category": categories
                }

        elapsed_time = time.time() - start_time
        print(f"Processed conversation {i.replace('sentence', '')}/{len(data)} - Elapsed time: {elapsed_time:.2f} seconds")

        with open(output_file, "w", encoding="utf-8") as f_out:
            json.dump(result_data, f_out, indent=4, ensure_ascii=False)

        count += 1
        if limit != -1 and count >= limit:
            break

def main():
    device = "cuda"
    repeat = 3
    limit = 300
    local_model_path1 = "path/to/model1"
    local_model_path2 = "path/to/model2"
    input_file = "path/to/input.json"
    output_file = "path/to/output.json"
    category_file_path = "path/to/category.json"
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("")

    model1, tokenizer1 = load_model_and_tokenizer(local_model_path1, device)
    model2, tokenizer2 = load_model_and_tokenizer(local_model_path2, device)
    
    process_json_input(input_file, output_file, model1, tokenizer1, model2, tokenizer2, device, repeat, limit, category_file_path)

if __name__ == "__main__":
    main()
