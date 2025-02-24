import json
import random
import logging
from typing import Dict, List, Tuple
from metrics import evaluate_metrics
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_json_file(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json_file(file_path: str, data: List[Dict]) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def get_category_frequencies(data: List[Dict]) -> Dict[str, int]:
    frequencies = {}
    for item in data:
        answer = item['conversations'][1]['value']
        frequencies[answer] = frequencies.get(answer, 0) + 1
    return frequencies

def extract_options(user_message: str) -> List[str]:
    options_start = user_message.rfind(':') + 1
    return [opt.strip() for opt in user_message[options_start:].strip('?').split(',')]

def rebuild_user_message(original_message: str, new_options: List[str]) -> str:
    options_start = original_message.rfind(':') + 1
    return original_message[:options_start] + ' ' + ', '.join(new_options) + '?'

def process_conversation(conversation: List[Dict], frequencies: Dict[str, int]) -> None:
    try:
        user_message = conversation[0]['value']
        assistant_answer = conversation[1]['value']
        options = extract_options(user_message)
        
        # 如果选项太少，不处理
        if len(options) <= 3:
            return
            
        # 确保答案在选项中
        if assistant_answer not in options:
            options.append(assistant_answer)
            
        # 计算要保留的选项数（至少保留3个选项）
        current_size = len(options)
        min_keep = 3
        if current_size <= min_keep:
            return
            
        # 确定要保留的选项数量（在3到当前数量之间随机）
        num_to_keep = random.randint(min_keep, current_size)
        
        # 始终保留答案
        kept_options = [assistant_answer]
        other_options = [opt for opt in options if opt != assistant_answer]
        
        # 随机选择其他选项
        additional_keeps = num_to_keep - 1  # 减1是因为已经保留了答案
        if additional_keeps > 0 and other_options:
            kept_options.extend(random.sample(other_options, min(additional_keeps, len(other_options))))
        
        # 打乱选项顺序
        random.shuffle(kept_options)
        
        # 更新对话
        conversation[0]['value'] = rebuild_user_message(user_message, kept_options)
        
    except Exception as e:
        logger.error(f"Error in process_conversation: {str(e)}")
        raise

def process_json(input_file_path: str, output_file_path: str, hierarchy_file_path: str) -> None:
    try:
        # 读取数据
        data = read_json_file(input_file_path)
        
        # 计算指标和频率
        metrics = evaluate_metrics(input_file_path, hierarchy_file_path)
        frequencies = get_category_frequencies(data)
        
        # 处理概率基于指标调整
        base_prob = 0.3
        if metrics['normalized_entropy'] < 0.8:
            process_prob = base_prob * 0.8
        else:
            process_prob = base_prob
        
        # 处理数据
        for item in data:
            if random.random() < process_prob:
                try:
                    process_conversation(item['conversations'], frequencies)
                except Exception as e:
                    logger.error(f"Error processing conversation: {str(e)}")
                    continue
        
        # 写入结果
        write_json_file(output_file_path, data)
        
        # 输出信息
        logger.info(f"Initial metrics: {metrics}")
        logger.info(f"Process probability: {process_prob}")
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    input_file_path = 'AnythingNER/dynamic/de/dev2.json'
    output_file_path = 'AnythingNER/dynamic/de/dev3.json'
    hierarchy_file_path = 'AnythingNER/anythingNER.json'
    process_json(input_file_path, output_file_path, hierarchy_file_path)