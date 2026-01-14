from llama_index.core import VectorStoreIndex

class DataRetriever:
    def __init__(self, config):
        self.config = config
        # 从现有的向量库加载索引
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.config.vector_store
        )

    def search_rules(self, query_text, top_k=3):
        """
        纯检索逻辑：只返回最匹配的规则内容和元数据
        """
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query_text)

        results = []
        for node in nodes:
            results.append({
                "rule_name": node.metadata.get("rule_name"),
                "logic_expression": node.metadata.get("logic_expression"),
                "risk_verdict": node.metadata.get("risk_verdict"),
                "score": node.score,
                # ✅ 关键修复点
                "full_text": node.get_content()
            })
        return results
