import json
import random
from typing import List, Dict, Set
from metrics import evaluate_metrics
from pathlib import Path

class ClassificationHierarchy:
    def __init__(self, hierarchy_json):
        self.hierarchy = hierarchy_json
        self.first_level = self.hierarchy["first-level"].split(", ")
        self.second_level = self.hierarchy["second-level"]
        self.third_level = self.hierarchy["third-level"]
        self.reverse_mapping = self._create_reverse_mapping()
        self.forward_mapping = self._create_forward_mapping()

    def _create_reverse_mapping(self):
        mapping = {}
        for first, second_list in self.second_level.items():
            for second in second_list.split(", "):
                mapping[second] = first
                if second in self.third_level:
                    for third in self.third_level[second].split(", "):
                        mapping[third] = second
        return mapping

    def _create_forward_mapping(self):
        mapping = {}
        # 一级到二级的映射
        for first, second_list in self.second_level.items():
            mapping[first] = second_list.split(", ")
        # 二级到三级的映射
        for second, third_list in self.third_level.items():
            mapping[second] = third_list.split(", ")
        return mapping

    def get_parent_category(self, category: str) -> str:
        return self.reverse_mapping.get(category, category)

    def get_child_categories(self, category: str) -> List[str]:
        return self.forward_mapping.get(category, [])

    def get_siblings(self, category: str) -> List[str]:
        parent = self.get_parent_category(category)
        if parent == category:  # 如果是顶级类别
            return self.first_level
        return self.forward_mapping.get(parent, [])

def load_classification_hierarchy(file_path: str) -> ClassificationHierarchy:
    with open(file_path, 'r', encoding='utf-8') as file:
        hierarchy_json = json.load(file)
    return ClassificationHierarchy(hierarchy_json)

def extract_list(value: str) -> List[str]:
    return value.split('list: ')[1].strip('?').split(', ')

def get_category_frequencies(data: List[Dict]) -> Dict[str, int]:
    frequencies = {}
    for item in data:
        answer = item['conversations'][1]['value']
        frequencies[answer] = frequencies.get(answer, 0) + 1
    return frequencies

def find_related_categories(category: str, hierarchy: ClassificationHierarchy) -> Set[str]:
    related = set()
    
    # 添加同级类别
    siblings = hierarchy.get_siblings(category)
    related.update(siblings)
    
    # 添加父类别
    parent = hierarchy.get_parent_category(category)
    if parent != category:
        related.add(parent)
    
    # 添加子类别
    children = hierarchy.get_child_categories(category)
    related.update(children)
    
    return related

def select_types_to_add(response: str, other_types: List[str], 
                       hierarchy: ClassificationHierarchy) -> List[str]:
    types_to_add = [response]
    if not other_types:
        return types_to_add

    # 找到与答案相关的类别
    related_categories = find_related_categories(response, hierarchy)
    
    # 过滤并排序其他类型
    priority_types = []
    normal_types = []
    
    for t in other_types:
        if t in related_categories:
            priority_types.append(t)
        else:
            normal_types.append(t)
    
    # 选择要添加的类型
    num_to_add = min(2, len(other_types))
    if priority_types:
        # 优先从相关类别中选择
        selected = random.sample(priority_types, min(num_to_add, len(priority_types)))
        if len(selected) < num_to_add and normal_types:
            # 如果还需要更多，从普通类别中补充
            selected.extend(random.sample(normal_types, 
                                      min(num_to_add - len(selected), len(normal_types))))
        types_to_add.extend(selected)
    else:
        # 如果没有相关类别，随机选择
        types_to_add.extend(random.sample(other_types, min(num_to_add, len(other_types))))
    
    return types_to_add

def merge_lists(original_list: List[str], new_types: List[str], 
               hierarchy: ClassificationHierarchy) -> List[str]:
    # 移除新类型的父类别
    filtered_list = [item for item in original_list 
                    if not any(hierarchy.get_parent_category(new_type) == item 
                             for new_type in new_types)]
    
    # 合并列表
    merged = set(filtered_list + new_types)
    
    # 移除被其他类别包含的父类别
    final_list = [item for item in merged 
                 if not any(hierarchy.get_parent_category(other) == item 
                           for other in merged if other != item)]
    
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

def merge_classifications(data: List[Dict], hierarchy: ClassificationHierarchy, 
                        merge_probability: float) -> List[Dict]:
    merged_data = []
    for i in range(0, len(data), 3):
        group = data[i:i+3]
        if len(group) < 2:
            merged_data.extend(group)
            continue

        if random.random() < merge_probability:
            try:
                first_list = extract_list(group[0]['conversations'][0]['value'])
                second_list = extract_list(group[1]['conversations'][0]['value'])
                response = group[1]['conversations'][1]['value']
                other_types = [t for t in second_list if t != response]
                
                types_to_add = select_types_to_add(response, other_types, hierarchy)
                merged_list = merge_lists(first_list, types_to_add, hierarchy)
                
                merged_data.append(create_merged_conversation(group, merged_list))
                if len(group) > 2:
                    merged_data.append(group[2])
            except Exception as e:
                print(f"Error merging conversation: {str(e)}")
                merged_data.extend(group)
        else:
            merged_data.extend(group)
    
    return merged_data

def main(input_file_path: str, output_file_path: str, hierarchy_file_path: str) -> None:
    try:
        # 读取数据和层次结构
        hierarchy = load_classification_hierarchy(hierarchy_file_path)
        data = read_json_file(input_file_path)
        
        # 获取初始指标
        metrics = evaluate_metrics(input_file_path, hierarchy_file_path)
        
        # 根据指标调整合并概率
        base_prob = 0.4
        if metrics['cohesion_score'] < 0.04:
            merge_probability = min(0.6, base_prob * 1.5)  # 内聚度低时增加合并概率
        else:
            merge_probability = base_prob
        
        # 执行合并
        merged_data = merge_classifications(data, hierarchy, merge_probability)
        
        # 写入结果
        write_json_file(merged_data, output_file_path)
        
        print(f"Initial metrics: {metrics}")
        print(f"Merge probability: {merge_probability}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def read_json_file(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json_file(data: List[Dict], file_path: str) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    input_file_path = 'DynamicNER/balanced/de/SWIFT/classify/dev.json'
    output_file_path = 'DynamicNER/dynamic/de/dev1.json'
    hierarchy_file_path = 'DynamicNER/DynamicNER.json'
    main(input_file_path, output_file_path, hierarchy_file_path)