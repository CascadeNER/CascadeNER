import argparse
from pathlib import Path
from metrics import evaluate_metrics

def main():
    parser = argparse.ArgumentParser(description='Evaluate metrics for a JSON file')
    parser.add_argument('json_path', type=str, help='Path to the JSON file to evaluate')
    parser.add_argument('--hierarchy', type=str, default='anythingNER.json',
                        help='Path to the hierarchy JSON file (default: anythingNER.json)')
    
    args = parser.parse_args()
    
    # 确保文件存在
    json_path = Path(args.json_path)
    hierarchy_path = Path(args.hierarchy)
    
    if not json_path.exists():
        print(f"Error: JSON file not found at {json_path}")
        return
    
    if not hierarchy_path.exists():
        print(f"Error: Hierarchy file not found at {hierarchy_path}")
        return
        
    try:
        # 评估指标
        metrics = evaluate_metrics(str(json_path), str(hierarchy_path))
        
        # 打印结果
        print("\nMetrics Evaluation Results:")
        print("-" * 30)
        for metric_name, value in metrics.items():
            print(f"{metric_name}: {value:.4f}")
            
    except Exception as e:
        print(f"Error evaluating metrics: {str(e)}")

if __name__ == "__main__":
    main()