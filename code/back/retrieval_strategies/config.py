import os
from llama_index.core import Settings, StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client

class RAGConfig:
    def __init__(self, collection_name="bank_data_collection", storage_path="./qdrant_storage"):
        self.collection_name = collection_name
        self.storage_path = storage_path
        self._setup_settings()
        self.client = qdrant_client.QdrantClient(path=self.storage_path)
        self.vector_store = QdrantVectorStore(
            client=self.client, 
            collection_name=self.collection_name
        )

    def _setup_settings(self):
        """配置全局模型设置"""
        # 如果需要使用其他模型，可以在此处修改
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        # 如果不需要 LLM 生成回答，只需检索，可以不配置 Settings.llm

    def get_storage_context(self):
        """生成存储上下文"""
        return StorageContext.from_defaults(vector_store=self.vector_store)