from config import RAGConfig
from retrieval import DataRetriever

def main():
    config = RAGConfig(collection_name="risk_rules_collection")
    retriever = DataRetriever(config)

    query = "近12个月 多次贷款 公积金 断缴"

    results = retriever.search_rules(query_text=query, top_k=5)

    print(f"查询：{query}\n")
    for r in results:
        print("规则名称:", r["rule_name"])
        print("逻辑表达式:", r["logic_expression"])
        print("风险判定:", r["risk_verdict"])
        print("相似度:", round(r["score"], 4))
        print("-" * 50)

if __name__ == "__main__":
    main()
