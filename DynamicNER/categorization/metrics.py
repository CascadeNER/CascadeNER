import json
import math
import numpy as np
from collections import Counter
from typing import List, Dict, Tuple

class MetricsEvaluator:
    def __init__(self, hierarchy_path: str):
        """
        初始化评估器
        Args:
            hierarchy_path: 分类层次结构文件路径
        """
        self.hierarchy = self._load_hierarchy(hierarchy_path)
        
    def _load_hierarchy(self, file_path: str) -> Dict:
        """加载分类层次结构"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _extract_categories(self, data: List[Dict]) -> List[str]:
        """从数据中提取所有分类"""
        categories = []
        for item in data:
            try:
                message = item['conversations'][0]['value']
                answer = item['conversations'][1]['value']
                categories.append(answer)
            except (KeyError, IndexError):
                continue
        return categories
    
    def calculate_cohesion_score(self, categories: List[str]) -> float:
        """
        计算类别内聚度
        基于层次结构计算类别间的关系紧密程度
        """
        if not categories:
            return 0.0
            
        total_pairs = 0
        cohesive_pairs = 0
        
        for i in range(len(categories)):
            for j in range(i + 1, len(categories)):
                cat1, cat2 = categories[i], categories[j]
                total_pairs += 1
                
                # 检查是否在同一分支
                for first_level in self.hierarchy['first-level'].split(', '):
                    if first_level in self.hierarchy['second-level']:
                        second_levels = self.hierarchy['second-level'][first_level].split(', ')
                        if cat1 in second_levels and cat2 in second_levels:
                            cohesive_pairs += 1
                            break
                        
                        # 检查第三层
                        for second_level in second_levels:
                            if second_level in self.hierarchy['third-level']:
                                third_levels = self.hierarchy['third-level'][second_level].split(', ')
                                if cat1 in third_levels and cat2 in third_levels:
                                    cohesive_pairs += 1
                                    break
        
        return cohesive_pairs / total_pairs if total_pairs > 0 else 0.0
    
    def calculate_normalized_entropy(self, categories: List[str]) -> float:
        """
        计算归一化熵
        评估类别分布的均匀程度
        """
        if not categories:
            return 0.0
            
        counter = Counter(categories)
        total = len(categories)
        
        entropy = 0
        for count in counter.values():
            p = count / total
            entropy -= p * math.log2(p)
            
        max_entropy = math.log2(len(counter))
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def calculate_gini_coefficient(self, categories: List[str]) -> float:
        """
        计算Gini系数
        评估类别分布的不平衡程度
        """
        if not categories:
            return 0.0
            
        counter = Counter(categories)
        values = sorted(counter.values())
        total = sum(values)
        
        if total == 0:
            return 0.0
            
        cumsum = np.cumsum(values)
        n = len(values)
        
        return (n + 1 - 2 * np.sum(cumsum) / total) / n if n > 0 else 0.0
    
    def calculate_coefficient_of_variation(self, categories: List[str]) -> float:
        """
        计算变异系数
        评估类别频率的离散程度
        """
        if not categories:
            return 0.0
            
        counter = Counter(categories)
        values = list(counter.values())
        
        mean = np.mean(values)
        std = np.std(values)
        
        return std / mean if mean > 0 else 0.0
    
    def evaluate_file(self, file_path: str) -> Dict[str, float]:
        """
        评估文件中的所有指标
        Args:
            file_path: JSON文件路径
        Returns:
            包含所有指标的字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return {}
            
        categories = self._extract_categories(data)
        
        metrics = {
            'cohesion_score': self.calculate_cohesion_score(categories),
            'normalized_entropy': self.calculate_normalized_entropy(categories),
            'gini_coefficient': self.calculate_gini_coefficient(categories),
            'coefficient_of_variation': self.calculate_coefficient_of_variation(categories)
        }
        
        return metrics

def evaluate_metrics(json_path: str, hierarchy_path: str) -> Dict[str, float]:
    """
    便捷函数用于评估单个文件
    """
    evaluator = MetricsEvaluator(hierarchy_path)
    return evaluator.evaluate_file(json_path)

if __name__ == "__main__":
    # 示例使用
    hierarchy_path = 'annotator/anythingNER.json'
    json_path = 'AnythingNER/dynamic/de/dev.json'
    
    metrics = evaluate_metrics(json_path, hierarchy_path)
    print("Evaluation Results:")
    for metric_name, value in metrics.items():
        print(f"{metric_name}: {value:.4f}")