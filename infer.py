import json
import os
import torch
import time
import re
import subprocess
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_model_and_tokenizer(local_model_path, device):
    model = AutoModelForCausalLM.from_pretrained(
        local_model_path,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(local_model_path)
    return model, tokenizer

def extract_entities_with_positions(sentence, response):
    entities = []
    for match in re.finditer(r"##(.*?)##", response):
        entity_text = match.group(1)
        start_idx = sentence.find(entity_text)
        if start_idx != -1:
            end_idx = start_idx + len(entity_text)
            entities.append({
                "text": entity_text,
                "start": start_idx,
                "end": end_idx
            })
        else:
            for m in re.finditer(re.escape(entity_text), sentence):
                entities.append({
                    "text": entity_text,
                    "start": m.start(),
                    "end": m.end()
                })
                break
    return entities

def merge_entities(entities_list):
    merged_entities = []
    for entities in entities_list:
        for entity in entities:
            overlap = False
            for m_entity in merged_entities:
                if not (entity['end'] <= m_entity['start'] or entity['start'] >= m_entity['end']):
                    if (entity['end'] - entity['start']) > (m_entity['end'] - m_entity['start']):
                        m_entity['text'] = entity['text']
                        m_entity['start'] = entity['start']
                        m_entity['end'] = entity['end']
                    overlap = True
                    break
            if not overlap:
                merged_entities.append(entity)
    return merged_entities

def categorize_entities(entities, original_sentence, model2, tokenizer2, device, category_file_path):
    with open(category_file_path, "r", encoding="utf-8") as f:
        category_data = json.load(f, strict=False)

    first_level = category_data["first-level"].lower()
    first_level_category = []
    second_level_category = []
    entity_categories = []

    for entity in entities:
        entity_lower = entity.lower()
        query = f'The ##{entity}## in the sentence: "{original_sentence}" belong to which entity in the first list: {first_level}?'
        entity_type = generate_response(model2, tokenizer2, query, device).strip().lower()
        first_level_category.append(entity_type)

    if not "second-level" in category_data:
        return first_level_category

    for count, entity in enumerate(entities):
        if first_level_category[count] not in category_data["second-level"]:
            return []
        second_level = category_data["second-level"][first_level_category[count]].lower()
        entity_lower = entity.lower()
        query = f'The ##{entity_lower}## in the sentence: "{original_sentence}" belong to which entity in the second list: {second_level}?'
        entity_type = generate_response(model2, tokenizer2, query, device).strip().lower()
        second_level_category.append(entity_type)

    if not "third-level" in category_data:
        return second_level_category

    for count, entity in enumerate(entities):
        if second_level_category[count] not in category_data["third-level"]:
            return []
        third_level = category_data["third-level"][second_level_category[count]].lower()
        entity_lower = entity.lower()
        query = f'The ##{entity_lower}## in the sentence: "{original_sentence}" belong to which entity in the third list: {third_level}?'
        entity_type = generate_response(model2, tokenizer2, query, device).strip().lower()
        entity_categories.append(entity_type)

    return entity_categories

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

def clear_infer_result_dir(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def run_bash_script():
    subprocess.run(['/bin/bash', './extract.sh'], check=True)

def process_json_input(output_file, model2, tokenizer2, device, repeat, limit, category_file_path):
    infer_result_dir = './model/stage1/zeroshot/1b-sft/infer_result/'

    responses_dict = {}
    for filename in os.listdir(infer_result_dir):
        file_path = os.path.join(infer_result_dir, filename)
        if os.path.isfile(file_path) and filename.endswith('.jsonl'):
            with open(file_path, 'r', encoding='utf-8') as f_json:
                for k, line in enumerate(f_json):
                    try:
                        data_json = json.loads(line)
                        query = data_json.get('query', '')
                        response = data_json.get('response', '')
                        if query not in responses_dict:
                            responses_dict[query] = []
                        responses_dict[query].append(response)
                    except json.JSONDecodeError as e:
                        print(f'Error decoding JSON from {file_path}: {e}')

    result_data = {}
    start_time = time.time()
    count = 1

    for query, responses in responses_dict.items():
        if responses:
            entities_list = []
            for response in responses:
                entities = extract_entities_with_positions(query, response)
                entities_list.append(entities)
            merged_entities = merge_entities(entities_list)
            if merged_entities:
                entities_text = [entity['text'] for entity in merged_entities]
                categories = categorize_entities(entities_text, query, model2, tokenizer2, device, category_file_path)
                if not categories:
                    continue
                result_data[f"sentence{count}"] = {
                    "sentence": query,
                    "entity": entities_text,
                    "category": categories
                }
                count += 1
        else:
            print(f"No responses found for query: {query}")

        if limit != -1 and count >= limit:
            break

        with open(output_file, "w", encoding="utf-8") as f_out:
            json.dump(result_data, f_out, indent=4, ensure_ascii=False)

        elapsed_time = time.time() - start_time
        print(f"Processed {count} sentences - Elapsed time: {elapsed_time:.2f} seconds")

def main():
    device = "cuda"
    repeat = 3
    limit = 1000
    local_model_path2 = "./model/classifier/zeroshot/1b-sft"
    output_file = "output.json"
    category_file_path = "./eval/category/category_file_path"

    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("")

    model2, tokenizer2 = load_model_and_tokenizer(local_model_path2, device)

    process_json_input(output_file, model2, tokenizer2, device, repeat, limit, category_file_path)

if __name__ == "__main__":
    main()