import json
import os
from pathlib import Path

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_category_structure(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def find_categories(category, category_structure):
    for second, third_list in category_structure['third-level'].items():
        if category in third_list.split(', '):
            third_level = category
            second_level = second
            for first, second_list in category_structure['second-level'].items():
                if second in second_list.split(', '):
                    first_level = first
                    return first_level, second_level, third_level
    
    for first, second_list in category_structure['second-level'].items():
        if category in second_list.split(', '):
            first_level = first
            second_level = category
            return first_level, second_level, category
    
    if category in category_structure['first-level'].split(', '):
        return category, category, category
    
    return 'miscellaneous', 'miscellaneous', 'miscellaneous'

def get_entity_list(level, category, category_structure):
    if level == 'first-level':
        return category_structure['first-level']
    elif level == 'second-level':
        for first, second_list in category_structure['second-level'].items():
            if category in second_list.split(', '):
                return second_list
        return category_structure['second-level'].get(category, '')
    elif level == 'third-level':
        for second, third_list in category_structure['third-level'].items():
            if category in third_list.split(', '):
                return third_list
    return ''

def convert_to_complex_conversation_format(json_data, category_structure):
    conversation_data = []
    
    for sentence_id, sentence_info in json_data.items():
        sentence = sentence_info['sentence']
        entities = sentence_info['entity']
        categories = sentence_info['category']
        
        for i, (entity, category) in enumerate(zip(entities, categories)):
            first_level, second_level, third_level = find_categories(category, category_structure)
            
            for level, category_value in [('first-level', first_level), ('second-level', second_level), ('third-level', third_level)]:
                entity_list = get_entity_list(level, category_value, category_structure)
                
                # Create a copy of the sentence and highlight the current entity
                highlighted_sentence = sentence
                start_index = 0
                entity_positions = []
                for j, e in enumerate(entities):
                    try:
                        index = highlighted_sentence.index(e, start_index)
                        entity_positions.append((index, index + len(e), j))
                        start_index = index + len(e)
                    except ValueError:
                        continue

                # Sort entity positions to handle overlapping entities
                entity_positions.sort(key=lambda x: x[0])

                # Highlight entities in reverse order to avoid index shifting
                for start, end, j in reversed(entity_positions):
                    if j == i:
                        highlighted_sentence = f"{highlighted_sentence[:start]}##{highlighted_sentence[start:end]}##{highlighted_sentence[end:]}"
                    
                user_message = f"The ##{entity}## in the sentence: \"{highlighted_sentence}\" belongs to which entity in the list: {entity_list}?"
                
                conversation_data.append({
                    "conversations": [
                        {"from": "user", "value": user_message},
                        {"from": "assistant", "value": category_value}
                    ]
                })
    
    return conversation_data

def write_json_file(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def process_directory(input_dir, category_structure_file, output_dir):
    category_structure = load_category_structure(category_structure_file)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, f"{filename}")
            
            json_data = load_json_file(input_file)
            conversation_data = convert_to_complex_conversation_format(json_data, category_structure)
            write_json_file(conversation_data, output_file)
            print(f"Processed {filename}. Output written to {output_file}")

def main(input_dir, category_structure_file, output_dir):
    process_directory(input_dir, category_structure_file, output_dir)
    print(f"Conversion complete. All processed files are in {output_dir}")

if __name__ == "__main__":
    input_dir = "./AnythingNER/inbalanced/es/GEIC"
    category_structure_file = "./anythingNER.json"
    output_dir = "./AnythingNER/inbalanced/es/SWIFT/classify"
    main(input_dir, category_structure_file, output_dir)