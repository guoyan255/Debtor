from typing import Dict, Type, Any, Optional
from core_abstract.tool_chain_component import ToolChainComponent  


class ToolChainFactory:
    """工具链工厂类，负责注册和创建工具链组件实例"""
    
    # 组件注册表：{组件类型字符串: 组件类}
    _component_registry: Dict[str, Type[ToolChainComponent]] = {}

    @staticmethod
    def register_component(component_type: str, component_class: Type[ToolChainComponent]) -> None:
        """
        注册工具链组件类
        :param component_type: 组件类型（对应ToolChainType枚举值）
        :param component_class: 组件类（必须继承自ToolChainComponent）
        """
        if not issubclass(component_class, ToolChainComponent):
            raise TypeError(f"Component class {component_class.__name__} must inherit from ToolChainComponent")
        if component_type in ToolChainFactory._component_registry:
            raise ValueError(f"Component type {component_type} already registered")
        ToolChainFactory._component_registry[component_type] = component_class

    @staticmethod
    def create_component(component_type: str, config: Dict[str, Any]) -> ToolChainComponent:
        """
        创建工具链组件实例
        :param component_type: 组件类型（对应已注册的类型）
        :param config: 组件配置参数
        :return: 组件实例
        """
        component_class = ToolChainFactory._component_registry.get(component_type)
        if not component_class:
            raise ValueError(f"Component type {component_type} not registered")
        # 调用组件类的初始化方法
        return component_class(config)

    @staticmethod
    def get_registered_components() -> Dict[str, Type[ToolChainComponent]]:
        """获取所有已注册的组件类型"""
        return ToolChainFactory._component_registry.copy()