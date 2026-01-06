from typing import Dict, Any


class ModelConfig:
    """模型配置类，封装单个模型的配置信息"""
    
    def __init__(
        self,
        model_type: str,
        model_name: str,
        parameters: Dict[str, Any] = None,
        enabled: bool = True,
        priority: int = 0
    ):
        self.model_type = model_type  # 模型类型（对应ModelType枚举）
        self.model_name = model_name  # 模型名称
        self.parameters = parameters or {}  # 模型参数（如温度、最大token等）
        self.enabled = enabled  # 是否启用该模型
        self.priority = priority  # 模型优先级（用于多模型选择）

    def __str__(self) -> str:
        return (
            f"ModelConfig(model_type={self.model_type}, "
            f"model_name={self.model_name}, "
            f"enabled={self.enabled}, "
            f"priority={self.priority})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于配置序列化）"""
        return {
            "model_type": self.model_type,
            "model_name": self.model_name,
            "parameters": self.parameters,
            "enabled": self.enabled,
            "priority": self.priority
        }