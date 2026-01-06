from enum import Enum


class ModelType(Enum):

    """模型类型枚举，定义系统支持的所有模型类别"""
    FOUNDATION = "foundation"
    ASSISTANT = "assistant"
    REASONING = "reasoning"
    EMBEDDING = "embedding"
    RERANKER = "reranker"
    OCR = "ocr"
    SPEECH = "speech"
    CUSTOM = "custom"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    FEEDBACK_ANALYZER = "feedback_analyzer"