import os
from config import RAGConfig
from ingestion import DataIngestor
from retrieval import DataRetriever

def main():
    # 1. 初始化配置
    config = RAGConfig()
    csv_file = "模拟数据.csv"
    
    # 2. 检查数据库是否已存在，若不存在则进行初始化入库
    if not os.path.exists(config.storage_path):
        ingestor = DataIngestor(config)
        ingestor.ingest_csv(csv_file)
    else:
        print("检测到现有向量数据库，直接加载...")

    # 3. 初始化检索器
    retriever = DataRetriever(config)

    # 4. 循环交互查询
    print("\n=== CSV 向量检索系统已就绪 ===")
    while True:
        user_query = input("\n请输入查询内容 (退出请输入 'exit'): ")
        if user_query.lower() == 'exit':
            break
        
        print(f"正在匹配最相似的3条记录...")
        results = retriever.search(user_query, top_k=3)
        
        if not results:
            print("抱歉，未找到相关匹配数据。")
            continue

        for i, item in enumerate(results):
            print(f"\n[结果 {i+1} | 相似度得分: {item['score']:.4f}]")
            print(f"数据详情: {item['content']}")

if __name__ == "__main__":
    main()