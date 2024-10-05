import json
import random
import unicodedata

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def read_synonyms(file_path):
    synonyms = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('---')
            if len(parts) == 2:
                key = normalize_text(parts[0].strip())
                value = parts[1].strip()
                synonyms[key] = value
    return synonyms

def normalize_text(text):
    return unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('ASCII')

def extract_options(user_message):
    options_start = user_message.rfind(':') + 1
    return [opt.strip() for opt in user_message[options_start:].strip('?').split(',')]

def rebuild_user_message(original_message, new_options):
    options_start = original_message.rfind(':') + 1
    return original_message[:options_start] + ' ' + ', '.join(new_options) + '?'

def replace_with_synonym(word, synonyms, should_replace):
    normalized_word = normalize_text(word)
    if normalized_word in synonyms and should_replace:
        return synonyms[normalized_word]
    return word

def process_conversation(conversation, synonyms, replace_prob):
    user_message = conversation[0]['value']
    assistant_answer = conversation[1]['value']
    options = extract_options(user_message)
    unique_words = set(options + [assistant_answer])
    replacement_decisions = {normalize_text(word): random.random() < replace_prob for word in unique_words}
    new_options = [replace_with_synonym(opt, synonyms, replacement_decisions[normalize_text(opt)]) for opt in options]
    new_assistant_answer = replace_with_synonym(assistant_answer, synonyms, replacement_decisions[normalize_text(assistant_answer)])
    new_user_message = rebuild_user_message(user_message, new_options)
    conversation[0]['value'] = new_user_message
    conversation[1]['value'] = new_assistant_answer

def process_json(input_file_path, output_file_path, synonyms_file_path, replace_prob, process_prob):
    data = read_json_file(input_file_path)
    synonyms = read_synonyms(synonyms_file_path)
    for item in data:
        if random.random() < process_prob:
            try:
                process_conversation(item['conversations'], synonyms, replace_prob)
            except Exception:
                pass
    write_json_file(output_file_path, data)

if __name__ == "__main__":
    input_file_path = './AnythingNER/dynamic/de/dev1.json'
    output_file_path = './AnythingNER/dynamic/de/dev2.json'
    synonyms_file_path = './annotator/dynamic.txt'
    replace_prob = 0.5
    process_prob = 0.8
    process_json(input_file_path, output_file_path, synonyms_file_path, replace_prob, process_prob)