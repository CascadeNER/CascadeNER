import json
import os

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def convert_to_conversation_format(json_data):
    conversation_data = []
    
    for sentence_id, sentence_info in json_data.items():
        sentence = sentence_info['sentence']
        entities = sentence_info['entity']
        
        # Create a copy of the sentence for marking entities
        marked_sentence = sentence
        
        # Sort entities by length in descending order to handle nested entities correctly
        sorted_entities = sorted(entities, key=len, reverse=True)
        
        # Mark entities in the sentence
        for entity in sorted_entities:
            marked_sentence = marked_sentence.replace(entity, f'##{entity}##')
        
        conversation = {
            "conversations": [
                {
                    "from": "user",
                    "value": sentence
                },
                {
                    "from": "assistant",
                    "value": marked_sentence
                }
            ]
        }
        
        conversation_data.append(conversation)
    
    return conversation_data

def write_json_file(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def process_file(input_file, output_file):
    json_data = load_json_file(input_file)
    conversation_data = convert_to_conversation_format(json_data)
    write_json_file(conversation_data, output_file)
    print(f"Conversion complete. New JSON format written to {output_file}")

def main(input_directory, output_directory):
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Process all JSON files in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            input_file = os.path.join(input_directory, filename)
            output_file = os.path.join(output_directory, filename)
            process_file(input_file, output_file)

if __name__ == "__main__":
    input_directory = "./AnythingNER/inbalanced/es/GEIC"
    output_directory = "./AnythingNER/inbalanced/es/SWIFT/extract"
    main(input_directory, output_directory)