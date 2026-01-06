from typing import Dict, Type, Any, Optional
from core_abstract.base_model import BaseModel 


class ModelFactory:
    """模型工厂类，负责注册和创建模型实例"""
    
    # 模型注册表：{模型类型字符串: 模型类}
    _model_registry: Dict[str, Type[BaseModel]] = {}

    @staticmethod
    def register_model(model_type: str, model_class: Type[BaseModel]) -> None:
        """
        注册模型类
        :param model_type: 模型类型（对应ModelType枚举值）
        :param model_class: 模型类（必须继承自BaseModel）
        """
        if not issubclass(model_class, BaseModel):
            raise TypeError(f"Model class {model_class.__name__} must inherit from BaseModel")
        if model_type in ModelFactory._model_registry:
            raise ValueError(f"Model type {model_type} already registered")
        ModelFactory._model_registry[model_type] = model_class

    @staticmethod
    def create_model(model_type: str, config: Dict[str, Any]) -> BaseModel:
        """
        创建模型实例
        :param model_type: 模型类型（对应已注册的类型）
        :param config: 模型配置参数
        :return: 模型实例
        """
        model_class = ModelFactory._model_registry.get(model_type)
        if not model_class:
            raise ValueError(f"Model type {model_type} not registered")
        # 调用模型类的初始化方法
        return model_class(config)

    @staticmethod
    def get_registered_models() -> Dict[str, Type[BaseModel]]:
        """获取所有已注册的模型类型"""
        return ModelFactory._model_registry.copy()