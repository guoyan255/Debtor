import json
from llama_index.core import VectorStoreIndex, Document
from llama_index.readers.file import PandasCSVReader

class DataIngestor:
    def __init__(self, config):
        self.config = config

    def ingest_csv(self, file_path):
        """处理 CSV 用户数据"""
        print(f"正在读取文件并进行向量化: {file_path}...")
        reader = PandasCSVReader()
        documents = reader.load_data(file_path=file_path)
        
        storage_context = self.config.get_storage_context()
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context
        )
        print(f"CSV 数据入库成功！共处理 {len(documents)} 条数据。")
        return index

    def ingest_rules(self, file_path):
        """
        专门处理 rule.json 规则文件
        """
        print(f"正在解析规则文件: {file_path}...")
        
        try:
            # 1. 加载并解析 JSON 文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            rules_list = data.get("rules", [])
            documents = []
            
            for rule in rules_list:
                # 2. 构建语义文本：将 JSON 字段提取出来拼接成一段自然语言，便于向量检索匹配
                text_content = (
                    f"规则名称: {rule.get('rule_name')}\n"
                    f"风险判定: {rule.get('risk_verdict')}\n"
                    f"逻辑表达式: {rule.get('logic_expression')}"
                )
                
                # 3. 构建元数据：保留结构化信息，方便后续在检索结果中直接引用字段
                metadata = {
                    "rule_name": rule.get("rule_name"),
                    "logic_expression": rule.get("logic_expression"),
                    "risk_verdict": rule.get("risk_verdict")
                }
                
                # 4. 封装为 LlamaIndex 的 Document 对象
                doc = Document(text=text_content, metadata=metadata)
                documents.append(doc)

            # 5. 调用 config 获取 Qdrant 存储上下文并构建索引
            storage_context = self.config.get_storage_context()
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context
            )
            print(f"规则库构建成功！已成功将 {len(documents)} 条规则存入 Qdrant。")
            return index
            
        except json.JSONDecodeError:
            print("错误：rule.json 格式非法，请检查括号或引号。")
        except Exception as e:
            print(f"入库过程中发生错误: {e}")