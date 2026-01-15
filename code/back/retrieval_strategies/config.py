import os
from llama_index.core import Settings, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client


class RAGConfig:
    def __init__(
        self,
        collection_name: str = "risk_rules_collection",
        storage_path: str = "./qdrant_storage"
    ):
        self.collection_name = collection_name
        self.storage_path = storage_path

        # 1. 配置 Embedding（本地模型，不使用 LLM）
        self._setup_settings()

        # 2. 初始化 Qdrant（本地持久化模式）
        self.client = qdrant_client.QdrantClient(
            path=self.storage_path
        )

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name
        )

    def _setup_settings(self):
        """
        仅配置向量化模型，显式关闭 LLM
        """
        self.local_model_path = r"E:\embeddingmodel\bge-base-zh" 
        
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=self.local_model_path,
            trust_remote_code=True
        )

        # 明确关闭 LLM，防止 llamaindex 任何隐式调用
        Settings.llm = None

    def get_storage_context(self):
        """
        返回 Qdrant 存储上下文
        """
        return StorageContext.from_defaults(
            vector_store=self.vector_store
        )
