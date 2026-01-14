import os
from config import RAGConfig
from ingestion import DataIngestor

def run_ingestion():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接出 rule.json 的绝对路径
    rule_file_path = os.path.join(current_dir, "rule.json")
    
    config = RAGConfig(collection_name="risk_rules_collection")
    ingestor = DataIngestor(config=config)
    
    try:
        # 使用计算出的绝对路径
        ingestor.ingest_rules(rule_file_path)
        print("所有规则已成功向量化并存入向量库。")
    except Exception as e:
        print(f"入库失败: {e}")

if __name__ == "__main__":
    run_ingestion()