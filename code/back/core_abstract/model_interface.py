from abc import ABC, abstractmethod
from typing import Dict, Any
from model_type import ModelType

class ModelInterface(ABC):
    """模型接口，定义所有模型必须实现的核心方法"""
    @property
    @abstractmethod
    def model_type(self) -> ModelType:
        pass

    @property
    @abstractmethod
    def config(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def load(self) -> None:
        """加载模型"""
        pass

    @abstractmethod
    def unload(self) -> None:
        """卸载模型"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """验证模型配置的有效性"""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息（名称、版本、参数等）"""
        pass