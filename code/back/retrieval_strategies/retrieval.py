from llama_index.core import VectorStoreIndex

class DataRetriever:
    def __init__(self, config):
        self.config = config
        # 从现有的向量库加载索引
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.config.vector_store
        )

    def search(self, query_text, top_k=3):
        """执行检索并返回格式化结果"""
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query_text)
        
        results = []
        for node in nodes:
            results.append({
                "content": node.text,
                "score": node.score
            })
        return results