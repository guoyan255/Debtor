from abc import ABC, abstractmethod
import logging
import time
from typing import Dict, Any, Optional
from model_interface import ModelInterface
from model_type import ModelType

class BaseModel(ModelInterface, ABC):
    """所有模型的抽象基类，实现模型的通用属性和方法"""
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._model_type: Optional[ModelType] = None  # 由子类具体赋值
        self._model_name = config.get("model_name", "unknown")
        self._model_version = config.get("model_version", "1.0.0")
        self._parameters = config.get("parameters", {})
        self._is_loaded = False
        self._logger = logging.getLogger(f"model.{self._model_name}")
        self._creation_time = time.time()
        self._last_access_time = time.time()
        self._usage_count = 0

    @property
    def model_type(self) -> ModelType:
        if not self._model_type:
            raise NotImplementedError("子类必须设置_model_type属性")
        return self._model_type

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def __str__(self) -> str:
        return (f"BaseModel(model_name={self._model_name}, "
                f"model_type={self._model_type}, "
                f"is_loaded={self._is_loaded})")

    def record_usage(self, context: Dict[str, Any] = None) -> None:
        """记录模型使用情况（更新访问时间和使用次数）"""
        self._last_access_time = time.time()
        self._usage_count += 1
        if context:
            self._logger.debug(f"Model used with context: {context}")

    @abstractmethod
    def load(self) -> None:
        pass

    @abstractmethod
    def unload(self) -> None:
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        pass