import json
import re
import os

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def tokenize_with_punctuation(text):
    return re.findall(r'\w+|[^\w\s]', text)

def format_category(category):
    return category.replace(' ', '_')

def convert_to_bio(json_data):
    bio_data = []
    
    for sentence_id, sentence_info in json_data.items():
        sentence = sentence_info['sentence']
        entities = sentence_info['entity']
        categories = sentence_info['category']
        
        tokens = tokenize_with_punctuation(sentence)
        bio_tokens = ['O'] * len(tokens)
        
        for entity, category in zip(entities, categories):
            formatted_category = format_category(category)
            entity_tokens = tokenize_with_punctuation(entity)
            for i in range(len(tokens) - len(entity_tokens) + 1):
                if tokens[i:i+len(entity_tokens)] == entity_tokens:
                    bio_tokens[i] = f'B-{formatted_category}'
                    for j in range(1, len(entity_tokens)):
                        bio_tokens[i+j] = f'I-{formatted_category}'
                    break
        
        bio_data.extend([(token, bio) for token, bio in zip(tokens, bio_tokens)])
        bio_data.append(('', ''))  # Empty line to separate sentences
    
    return bio_data

def write_bio_file(bio_data, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for token, bio in bio_data:
            if token == '' and bio == '':
                file.write('\n')
            else:
                file.write(f'{token} {bio}\n')

def process_file(input_file, output_file):
    json_data = load_json_file(input_file)
    bio_data = convert_to_bio(json_data)
    write_bio_file(bio_data, output_file)
    print(f"Conversion complete. BIO format data written to {output_file}")

def main(input_directory, output_directory):
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Process all JSON files in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            input_file = os.path.join(input_directory, filename)
            output_file = os.path.join(output_directory, os.path.splitext(filename)[0] + '.txt')
            process_file(input_file, output_file)

if __name__ == "__main__":
    input_directory = "./AnythingNER/inbalanced/es/GEIC"
    output_directory = "./AnythingNER/inbalanced/es/BIO"
    main(input_directory, output_directory)