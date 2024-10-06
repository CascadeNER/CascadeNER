import json
import random
from collections import OrderedDict

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

def remove_duplicate_special_options(options):
    seen_special = False
    unique_options = []
    for opt in options:
        if opt.startswith(('miscellaneous', 'other')):
            if not seen_special:
                unique_options.append(opt)
                seen_special = True
        else:
            unique_options.append(opt)
    return unique_options

def process_conversation(conversation, removal_probs):
    user_message = conversation[0]['value']
    assistant_answer = conversation[1]['value']
    options = extract_options(user_message)
    options = remove_duplicate_special_options(options)
    if len(options) < 3:
        return
    if assistant_answer in options:
        options.remove(assistant_answer)
    new_answer = next((opt for opt in options if opt.startswith(('miscellaneous', 'other'))), 'unknown')
    conversation[1]['value'] = new_answer
    if new_answer == 'unknown' and 'unknown' not in options:
        options.append('unknown')
    max_removable = len(options) - 3
    num_to_remove = min(random.choices(range(4), weights=removal_probs, k=1)[0], max_removable)
    options_to_remove = random.sample([opt for opt in options if opt != new_answer], num_to_remove)
    kept_options = [opt for opt in options if opt not in options_to_remove]
    if new_answer not in kept_options:
        kept_options.append(new_answer)
    random.shuffle(kept_options)
    new_user_message = rebuild_user_message(user_message, kept_options)
    conversation[0]['value'] = new_user_message

def process_json(input_file_path, output_file_path, removal_probs, process_prob):
    data = read_json_file(input_file_path)
    for item in data:
        if random.random() < process_prob:
            try:
                process_conversation(item['conversations'], removal_probs)
            except Exception:
                pass
    write_json_file(output_file_path, data)

if __name__ == "__main__":
    input_file_path = './AnythingNER/dynamic/de/dev3.json'
    output_file_path = './AnythingNER/dynamic/de/dev.json'
    removal_probs = [0.2, 0.3, 0.3, 0.2]
    process_prob = 0.3
    process_json(input_file_path, output_file_path, removal_probs, process_prob)