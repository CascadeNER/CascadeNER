import json
import random
from collections import OrderedDict
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

def get_category_frequencies(data: List[Dict]) -> Dict[str, int]:
    frequencies = {}
    for item in data:
        answer = item['conversations'][1]['value']
        frequencies[answer] = frequencies.get(answer, 0) + 1
    return frequencies

def calculate_health_score(metrics: Dict[str, float]) -> float:
    return (
        0.4 * metrics['cohesion_score'] +
        0.3 * metrics['normalized_entropy'] +
        0.2 * (1 - metrics['gini_coefficient']) +
        0.1 * (2.5 - min(metrics['coefficient_of_variation'], 2.5)) / 2.5
    )

def adjust_special_strategy(metrics: Dict[str, float], 
                          frequencies: Dict[str, int]) -> Tuple[List[float], float, bool]:
    health_score = calculate_health_score(metrics)
    
    # 根据健康度决定处理策略
    if health_score < 0.4:
        # 数据质量不佳，采取保守策略
        process_prob = 0.2
        removal_probs = [0.1, 0.2, 0.2, 0.5]
        aggressive = False
    else:
        # 数据质量尚可，适度优化
        process_prob = 0.3
        removal_probs = [0.2, 0.3, 0.3, 0.2]
        aggressive = True
    
    # 根据具体指标微调
    if metrics['cohesion_score'] < 0.03:
        process_prob *= 0.8  # 降低处理概率
    if metrics['normalized_entropy'] < 0.75:
        aggressive = False  # 更保守的处理
        
    return removal_probs, process_prob, aggressive

def extract_options(user_message: str) -> List[str]:
    options_start = user_message.rfind(':') + 1
    return [opt.strip() for opt in user_message[options_start:].strip('?').split(',')]

def rebuild_user_message(original_message: str, new_options: List[str]) -> str:
    options_start = original_message.rfind(':') + 1
    return original_message[:options_start] + ' ' + ', '.join(new_options) + '?'

def remove_duplicate_special_options(options: List[str]) -> List[str]:
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

def select_special_answer(options: List[str], frequencies: Dict[str, int], 
                         aggressive: bool) -> str:
    # 寻找特殊选项（miscellaneous或other）
    special_options = [opt for opt in options 
                      if opt.startswith(('miscellaneous', 'other'))]
    
    if not special_options:
        return 'unknown'
    
    if aggressive:
        # 选择频率最低的特殊选项
        return min(special_options, key=lambda x: frequencies.get(x, 0))
    else:
        # 随机选择一个特殊选项
        return random.choice(special_options)

def process_conversation(conversation: List[Dict], removal_probs: List[float],
                        frequencies: Dict[str, int], aggressive: bool) -> None:
    user_message = conversation[0]['value']
    options = extract_options(user_message)
    
    # 处理特殊选项
    options = remove_duplicate_special_options(options)
    if len(options) < 3:
        return
        
    # 选择新的答案
    new_answer = select_special_answer(options, frequencies, aggressive)
    if new_answer == 'unknown' and 'unknown' not in options:
        options.append('unknown')
        
    # 决定要移除的选项数量
    max_removable = len(options) - 3
    num_to_remove = min(
        random.choices(range(4), weights=removal_probs, k=1)[0],
        max_removable
    )
    
    # 选择要保留的选项
    options_to_remove = random.sample(
        [opt for opt in options if opt != new_answer],
        num_to_remove
    )
    kept_options = [opt for opt in options if opt not in options_to_remove]
    
    # 确保新答案在选项中
    if new_answer not in kept_options:
        kept_options.append(new_answer)
        
    # 更新对话
    random.shuffle(kept_options)
    conversation[0]['value'] = rebuild_user_message(user_message, kept_options)
    conversation[1]['value'] = new_answer

def process_json(input_file_path: str, output_file_path: str, 
                hierarchy_file_path: str) -> None:
    try:
        # 读取数据
        data = read_json_file(input_file_path)
        
        # 计算指标和频率
        metrics = evaluate_metrics(input_file_path, hierarchy_file_path)
        frequencies = get_category_frequencies(data)
        
        # 调整策略
        removal_probs, process_prob, aggressive = adjust_special_strategy(
            metrics, frequencies
        )
        
        # 处理数据
        for item in data:
            if random.random() < process_prob:
                try:
                    process_conversation(
                        item['conversations'],
                        removal_probs,
                        frequencies,
                        aggressive
                    )
                except Exception as e:
                    print(f"Error processing conversation: {str(e)}")
                    continue
                    
        # 写入结果
        write_json_file(output_file_path, data)
        
        # 输出信息
        print(f"Initial metrics: {metrics}")
        print(f"Health score: {calculate_health_score(metrics):.4f}")
        print(f"Removal probabilities: {removal_probs}")
        print(f"Process probability: {process_prob}")
        print(f"Aggressive mode: {aggressive}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    input_file_path = 'AnythingNER/dynamic/de/dev3.json'
    output_file_path = 'AnythingNER/dynamic/de/dev.json'
    hierarchy_file_path = 'AnythingNER/anythingNER.json'
    process_json(input_file_path, output_file_path, hierarchy_file_path)