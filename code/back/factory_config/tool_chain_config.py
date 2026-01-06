from typing import Dict, Any


class ToolChainConfig:
    """工具链组件配置类，封装单个组件的配置信息"""
    
    def __init__(
        self,
        component_type: str,
        enabled: bool = True,
        priority: int = 0,
        parameters: Dict[str, Any] = None
    ):
        self.component_type = component_type  # 组件类型（对应ToolChainType枚举）
        self.enabled = enabled  # 是否启用该组件
        self.priority = priority  # 组件优先级（用于执行顺序排序）
        self.parameters = parameters or {}  # 组件参数（如超时时间、重试次数等）

    def __str__(self) -> str:
        return (
            f"ToolChainConfig(component_type={self.component_type}, "
            f"enabled={self.enabled}, "
            f"priority={self.priority})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于配置序列化）"""
        return {
            "component_type": self.component_type,
            "enabled": self.enabled,
            "priority": self.priority,
            "parameters": self.parameters
        }