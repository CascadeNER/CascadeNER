import json
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def extract_options(user_message):
    options_start = user_message.rfind(':') + 1
    return [opt.strip() for opt in user_message[options_start:].strip('?').split(',')]

def rebuild_user_message(original_message, new_options):
    options_start = original_message.rfind(':') + 1
    return original_message[:options_start] + ' ' + ', '.join(new_options) + '?'

def process_conversation(conversation, removal_probs):
    user_message = conversation[0]['value']
    assistant_answer = conversation[1]['value']
    options = extract_options(user_message)
    if len(options) <= 3:
        return
    options.remove(assistant_answer)
    max_removable = len(options) - 2
    if max_removable < 1:
        return
    adjusted_probs = removal_probs[:max_removable] + [0] * (4 - max_removable)
    adjusted_probs = [p / sum(adjusted_probs) for p in adjusted_probs]
    num_to_remove = random.choices(range(1, max_removable + 1), weights=adjusted_probs[:max_removable], k=1)[0]
    num_to_keep = len(options) - num_to_remove
    kept_options = random.sample(options, num_to_keep)
    kept_options.append(assistant_answer)
    random.shuffle(kept_options)
    new_user_message = rebuild_user_message(user_message, kept_options)
    conversation[0]['value'] = new_user_message

def process_json(input_file_path, output_file_path, removal_probs, process_prob):
    data = read_json_file(input_file_path)
    for i, item in enumerate(data):
        if random.random() < process_prob:
            try:
                process_conversation(item['conversations'], removal_probs)
            except Exception as e:
                pass
    write_json_file(output_file_path, data)

if __name__ == "__main__":
    input_file_path = './AnythingNER/dynamic/de/dev2.json'
    output_file_path = './AnythingNER/dynamic/de/dev3.json'
    removal_probs = [0.3, 0.25, 0.25, 0.2]
    process_prob = 0.3
    process_json(input_file_path, output_file_path, removal_probs, process_prob)