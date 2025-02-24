import json
import random
import unicodedata
from typing import Dict, List, Tuple
from metrics import evaluate_metrics
from pathlib import Path

def read_json_file(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json_file(file_path: str, data: List[Dict]) -> None:
    # 确保输出目录存在
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def read_synonyms(file_path: str) -> Dict[str, str]:
    synonyms = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('---')
            if len(parts) == 2:
                key = normalize_text(parts[0].strip())
                value = parts[1].strip()
                synonyms[key] = value
    return synonyms

def normalize_text(text: str) -> str:
    return unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('ASCII')

def get_category_frequencies(data: List[Dict]) -> Dict[str, int]:
    frequencies = {}
    for item in data:
        answer = item['conversations'][1]['value']
        frequencies[answer] = frequencies.get(answer, 0) + 1
    return frequencies

def adjust_synonym_strategy(metrics: Dict[str, float], frequencies: Dict[str, int]) -> Tuple[float, bool]:
    # 只在必要时进行同义词替换
    if metrics['coefficient_of_variation'] > 2.0:
        # 变异系数过高，减少替换
        replace_prob = 0.2
    else:
        replace_prob = 0.4

    # 根据Gini系数控制处理范围
    if metrics['gini_coefficient'] > 0.6:
        # 不平衡度高，优先处理高频类别
        process_high_frequency = True
    else:
        process_high_frequency = False
        
    return replace_prob, process_high_frequency

def extract_options(user_message: str) -> List[str]:
    options_start = user_message.rfind(':') + 1
    return [opt.strip() for opt in user_message[options_start:].strip('?').split(',')]

def rebuild_user_message(original_message: str, new_options: List[str]) -> str:
    options_start = original_message.rfind(':') + 1
    return original_message[:options_start] + ' ' + ', '.join(new_options) + '?'

def should_replace_with_synonym(word: str, frequencies: Dict[str, int], 
                              process_high_frequency: bool) -> bool:
    frequency = frequencies.get(word, 0)
    median_freq = sorted(frequencies.values())[len(frequencies)//2]
    
    if process_high_frequency:
        # 优先处理高频词
        return frequency > median_freq
    else:
        # 优先处理低频词
        return frequency < median_freq

def replace_with_synonym(word: str, synonyms: Dict[str, str], 
                        frequencies: Dict[str, int], 
                        process_high_frequency: bool) -> str:
    normalized_word = normalize_text(word)
    if normalized_word in synonyms and should_replace_with_synonym(word, frequencies, process_high_frequency):
        return synonyms[normalized_word]
    return word

def process_conversation(conversation: List[Dict], synonyms: Dict[str, str], 
                        replace_prob: float, frequencies: Dict[str, int], 
                        process_high_frequency: bool) -> None:
    if random.random() > replace_prob:
        return
        
    user_message = conversation[0]['value']
    assistant_answer = conversation[1]['value']
    options = extract_options(user_message)
    
    # 替换选项
    new_options = [
        replace_with_synonym(opt, synonyms, frequencies, process_high_frequency)
        for opt in options
    ]
    
    # 替换答案
    new_answer = replace_with_synonym(
        assistant_answer, synonyms, frequencies, process_high_frequency
    )
    
    # 更新对话
    conversation[0]['value'] = rebuild_user_message(user_message, new_options)
    conversation[1]['value'] = new_answer

def process_json(input_file_path: str, output_file_path: str, 
                synonyms_file_path: str, hierarchy_file_path: str) -> None:
    try:
        # 读取数据
        data = read_json_file(input_file_path)
        synonyms = read_synonyms(synonyms_file_path)
        
        # 计算指标和频率
        metrics = evaluate_metrics(input_file_path, hierarchy_file_path)
        frequencies = get_category_frequencies(data)
        
        # 调整策略
        replace_prob, process_high_frequency = adjust_synonym_strategy(metrics, frequencies)
        
        # 处理数据
        for item in data:
            try:
                process_conversation(
                    item['conversations'], 
                    synonyms, 
                    replace_prob,
                    frequencies, 
                    process_high_frequency
                )
            except Exception as e:
                print(f"Error processing conversation: {str(e)}")
                continue
                
        # 写入结果
        write_json_file(output_file_path, data)
        
        # 输出信息
        print(f"Initial metrics: {metrics}")
        print(f"Replace probability: {replace_prob}")
        print(f"Process high frequency: {process_high_frequency}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    input_file_path = 'AnythingNER/dynamic/de/dev1.json'
    output_file_path = 'AnythingNER/dynamic/de/dev2.json'
    synonyms_file_path = 'AnythingNER/dynamic.txt'
    hierarchy_file_path = 'AnythingNER/anythingNER.json'
    process_json(input_file_path, output_file_path, synonyms_file_path, hierarchy_file_path)