from llama_index.core import VectorStoreIndex
from llama_index.readers.file import PandasCSVReader

class DataIngestor:
    def __init__(self, config):
        self.config = config

    def ingest_csv(self, file_path):
        print(f"正在读取文件并进行向量化: {file_path}...")
        
        # 1. 使用 PandasCSVReader 加载 CSV
        reader = PandasCSVReader()
        documents = reader.load_data(file_path=file_path)
        
        # 2. 构建索引并保存到 Qdrant
        storage_context = self.config.get_storage_context()
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context
        )
        print(f"入库成功！共处理 {len(documents)} 条数据。")
        return index