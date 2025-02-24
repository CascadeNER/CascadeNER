import json
import logging
from pathlib import Path
from metrics import evaluate_metrics
from dynamic1 import main as dynamic1_main
from dynamic2 import process_json as dynamic2_process
from dynamic3 import process_json as dynamic3_process
from dynamic4 import process_json as dynamic4_process

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_directories(base_dir: Path):
    """确保所有必需的目录存在"""
    (base_dir / 'dynamic' / 'de').mkdir(parents=True, exist_ok=True)
    (base_dir / 'balanced' / 'de' / 'SWIFT' / 'classify').mkdir(parents=True, exist_ok=True)

def calculate_final_metrics(json_path: str, hierarchy_path: str):
    """计算最终指标"""
    try:
        metrics = evaluate_metrics(json_path, hierarchy_path)
        logger.info("Final Metrics:")
        logger.info("-" * 50)
        for name, value in metrics.items():
            logger.info(f"{name}: {value:.4f}")
        logger.info("-" * 50)
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")

def run_pipeline():
    try:
        # 获取当前文件的目录路径
        current_dir = Path(__file__).parent.absolute()
        base_dir = current_dir.parent
        
        # 确保目录存在
        ensure_directories(base_dir)
        
        # 定义文件路径
        initial_json = str(base_dir / 'balanced/ja/SWIFT/classify/train.json')
        dev1_json = str(base_dir / 'dynamic/ja/train1.json')
        dev2_json = str(base_dir / 'dynamic/ja/train2.json')
        dev3_json = str(base_dir / 'dynamic/ja/train3.json')
        final_json = str(base_dir / 'dynamic/ja/train.json')
        hierarchy_json = str(base_dir / 'anythingNER.json')
        dynamic_txt = str(base_dir / 'dynamic.txt')

        # Stage 1: 合并处理
        logger.info("Running Stage 1: Merge Processing")
        dynamic1_main(initial_json, dev1_json, hierarchy_json)

        # Stage 2: 同义词替换
        logger.info("Running Stage 2: Synonym Replacement")
        dynamic2_process(dev1_json, dev2_json, dynamic_txt, hierarchy_json)

        # Stage 3: 选项精简
        logger.info("Running Stage 3: Option Reduction")
        dynamic3_process(dev2_json, dev3_json, hierarchy_json)

        # Stage 4: 特殊处理
        logger.info("Running Stage 4: Special Processing")
        dynamic4_process(dev3_json, final_json, hierarchy_json)

        # 计算最终指标
        calculate_final_metrics(final_json, hierarchy_json)
        
        logger.info("Pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        logger.error("Error details:", exc_info=True)

if __name__ == "__main__":
    run_pipeline()