import json
import random
from typing import List, Dict

class ClassificationHierarchy:
    def __init__(self, hierarchy_json):
        self.hierarchy = hierarchy_json
        self.first_level = self.hierarchy["first-level"].split(", ")
        self.second_level = self.hierarchy["second-level"]
        self.third_level = self.hierarchy["third-level"]
        self.reverse_mapping = self._create_reverse_mapping()

    def _create_reverse_mapping(self):
        mapping = {}
        for first, second_list in self.second_level.items():
            for second in second_list.split(", "):
                mapping[second] = first
                if second in self.third_level:
                    for third in self.third_level[second].split(", "):
                        mapping[third] = second
        return mapping

    def get_parent_category(self, category):
        return self.reverse_mapping.get(category, category)

def load_classification_hierarchy(file_path: str) -> ClassificationHierarchy:
    with open(file_path, 'r', encoding='utf-8') as file:
        hierarchy_json = json.load(file)
    return ClassificationHierarchy(hierarchy_json)

def extract_list(value: str) -> List[str]:
    return value.split('list: ')[1].strip('?').split(', ')

def select_types_to_add(response: str, other_types: List[str]) -> List[str]:
    types_to_add = [response]
    max_additional = min(3, len(other_types))
    probabilities = [0.2, 0.2, 0.3, 0.3]
    num_to_add = random.choices(range(max_additional + 1), 
                                weights=probabilities[:max_additional + 1], k=1)[0]
    if num_to_add > 0:
        types_to_add.extend(random.sample(other_types, num_to_add))
    return types_to_add

def merge_lists(original_list: List[str], new_types: List[str], hierarchy: ClassificationHierarchy) -> List[str]:
    filtered_list = [item for item in original_list if not any(hierarchy.get_parent_category(new_type) == item for new_type in new_types)]
    merged = set(filtered_list + new_types)
    final_list = [item for item in merged if not any(hierarchy.get_parent_category(other) == item for other in merged if other != item)]
    return sorted(final_list)

def create_merged_conversation(group: List[Dict], merged_list: List[str]) -> Dict:
    original_value = group[0]['conversations'][0]['value']
    original_list = extract_list(original_value)
    new_value = original_value.replace(
        ': ' + ', '.join(original_list),
        ': ' + ', '.join(merged_list)
    )
    return {
        'conversations': [
            {'from': 'user', 'value': new_value},
            {'from': 'assistant', 'value': group[1]['conversations'][1]['value']}
        ]
    }

def merge_classifications(data: List[Dict], hierarchy: ClassificationHierarchy, merge_probability: float) -> List[Dict]:
    merged_data = []
    for i in range(0, len(data), 3):
        group = data[i:i+3]
        if random.random() < merge_probability:
            first_list = extract_list(group[0]['conversations'][0]['value'])
            second_list = extract_list(group[1]['conversations'][0]['value'])
            response = group[1]['conversations'][1]['value']
            other_types = [t for t in second_list if t != response]
            types_to_add = select_types_to_add(response, other_types)
            merged_list = merge_lists(first_list, types_to_add, hierarchy)
            merged_data.append(create_merged_conversation(group, merged_list))
            merged_data.append(group[2])
        else:
            merged_data.extend(group)
    return merged_data

def read_json_file(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json_file(data: List[Dict], file_path: str) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

def main(input_file_path: str, output_file_path: str, hierarchy_file_path: str, merge_probability: float) -> None:
    try:
        hierarchy = load_classification_hierarchy(hierarchy_file_path)
        input_data = read_json_file(input_file_path)
        merged_data = merge_classifications(input_data, hierarchy, merge_probability)
        write_json_file(merged_data, output_file_path)
        # print(f"Merging complete. Output written to '{output_file_path}'.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    input_file_path = './AnythingNER/balanced/de/SWIFT/classify/dev.json'
    output_file_path = './AnythingNER/dynamic/de/dev1.json'
    hierarchy_file_path = './annotator/anythingNER.json'
    merge_probability = 0.4
    main(input_file_path, output_file_path, hierarchy_file_path, merge_probability)