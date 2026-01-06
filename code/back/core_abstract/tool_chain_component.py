from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, Optional
from tool_chain_type import ToolChainType


class ToolChainComponent(ABC):
    """所有工具链组件的抽象基类，定义组件的生命周期和通用方法"""
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._component_type: Optional[ToolChainType] = None  # 由子类具体赋值
        self._is_enabled = config.get("enabled", True)
        self._priority = config.get("priority", 0)
        self._timeout = config.get("timeout", 30.0)
        self._retry_count = config.get("retry_count", 0)
        self._logger = logging.getLogger(f"toolchain.{self.__class__.__name__}")
        self._initialized = False
        self._execution_count = 0
        self._avg_execution_time = 0.0
        self._error_count = 0
        self._last_execution_time = 0.0

    @property
    def component_type(self) -> ToolChainType:
        if not self._component_type:
            raise NotImplementedError("子类必须设置_component_type属性")
        return self._component_type

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    @abstractmethod
    def initialize(self) -> None:
        """初始化组件（资源分配、连接建立等）"""
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行组件核心逻辑"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """清理组件资源"""
        pass

    def update_metrics(self, execution_time: float, success: bool) -> None:
        """更新组件执行 metrics"""
        self._execution_count += 1
        self._last_execution_time = execution_time
        # 计算平均执行时间（简单滑动平均）
        self._avg_execution_time = (
            (self._avg_execution_time * (self._execution_count - 1) + execution_time)
            / self._execution_count
        )
        if not success:
            self._error_count += 1

    def get_metrics(self) -> Dict[str, Any]:
        """获取组件性能 metrics"""
        return {
            "execution_count": self._execution_count,
            "avg_execution_time": self._avg_execution_time,
            "error_count": self._error_count,
            "last_execution_time": self._last_execution_time,
            "initialized": self._initialized,
            "is_enabled": self._is_enabled
        }

    def __str__(self) -> str:
        return (f"ToolChainComponent(type={self._component_type}, "
                f"initialized={self._initialized}, "
                f"priority={self._priority})")