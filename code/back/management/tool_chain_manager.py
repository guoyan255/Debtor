from typing import List, Optional, Dict, Any
import logging
from collections import defaultdict
from factory_config.config_manager import ConfigManager
from core_abstract.tool_chain_type import ToolChainType
from core_abstract.tool_chain_component import ToolChainComponent


class ToolChainManager:
    """工具链管理器，负责所有工具链组件的生命周期管理与状态监控"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager  # 配置管理器实例
        self.components: List[ToolChainComponent] = []  # 初始化的组件列表
        self.logger = logging.getLogger(__name__)  # 日志器
        self.component_init_times: Dict[str, float] = {}  # 组件初始化时间记录
        self.component_stats = defaultdict(lambda: {
            "execution_count": 0,
            "error_count": 0,
            "avg_execution_time": 0.0
        })  # 组件统计信息

    def initialize_components(self) -> List[ToolChainComponent]:
        """初始化所有配置中启用的工具链组件（具体实现待补充）"""
        self.logger.info("Initializing tool chain components...")
        # 1. 从配置管理器获取工具链配置
        tool_configs = self.config_manager.get_tool_chain_configs()
        # 2. 遍历配置，初始化启用的组件（通过ToolChainFactory创建）
        for config in tool_configs:
            if config.enabled:
                try:
                    # 此处需通过ToolChainFactory创建组件实例，暂为框架
                    component = None  # 实际应替换为ToolChainFactory.create_component(...)
                    component.initialize()  # 调用组件初始化方法
                    self.components.append(component)
                    self.logger.info(f"Initialized component: {config.component_type}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize component {config.component_type}: {str(e)}")
        return self.components

    def cleanup_components(self) -> None:
        """清理所有已初始化的工具链组件（调用组件的cleanup方法）"""
        self.logger.info("Cleaning up tool chain components...")
        for component in self.components:
            try:
                component.cleanup()
                self.logger.info(f"Cleaned up component: {component.component_type}")
            except Exception as e:
                self.logger.error(f"Failed to cleanup component {component.component_type}: {str(e)}")
        self.components.clear()
        self.component_init_times.clear()

    def get_component(self, component_type: str) -> Optional[ToolChainComponent]:
        """根据组件类型获取第一个匹配的组件实例"""
        for component in self.components:
            if component.component_type == component_type:
                return component
        return None

    def get_components_by_type(self, component_type: ToolChainType) -> List[ToolChainComponent]:
        """根据组件类型枚举获取所有匹配的组件实例"""
        return [
            comp for comp in self.components
            if comp.component_type == component_type
        ]

    def get_component_stats(self) -> Dict[str, Any]:
        """获取所有组件的状态统计信息"""
        stats = {}
        for component in self.components:
            comp_type = component.component_type
            stats[comp_type] = {
                "is_enabled": component.is_enabled,
                "priority": component.priority,
                "execution_count": component.execution_count,
                "error_count": component.error_count,
                "avg_execution_time": component.avg_execution_time,
                "last_execution_time": component.last_execution_time
            }
        return stats

    def health_check(self) -> Dict[str, Any]:
        """检查所有组件的健康状态"""
        health_status = {}
        for component in self.components:
            comp_type = component.component_type
            try:
                # 简单健康检查：组件是否初始化
                health_status[comp_type] = {
                    "status": "healthy" if component.initialized else "unhealthy",
                    "message": "Component initialized" if component.initialized else "Component not initialized"
                }
            except Exception as e:
                health_status[comp_type] = {
                    "status": "error",
                    "message": str(e)
                }
        return health_status