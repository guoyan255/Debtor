from enum import Enum

class ToolChainType(Enum):
    
    """工具链组件类型枚举，定义系统支持的所有工具链组件类别"""
    AGENT = "agent"
    RAG = "rag"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    RL = "rl"
    MEMORY = "memory"
    SYSTEM_TOOLS = "system_tools"
    ENVIRONMENT = "environment"
    CONTINUOUS_LEARNING = "continuous_learning"
