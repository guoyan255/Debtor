from typing import Dict, Any, Optional
import time
import logging
from management.model_manager import ModelManager
from management.tool_chain_manager import ToolChainManager
from management.health_checker import HealthChecker
from management.resource_manager import ResourceManager
from core_application import RequestProcessor, ApplicationContext

from factory_config.config_manager import ConfigManager
from factory_config.model_config import ModelConfig
from factory_config.tool_chain_config import ToolChainConfig



class VerticalDomainApplication:
    """垂直领域应用核心类，管理整个应用的生命周期和组件"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_manager = ConfigManager(config_file)  # 配置管理器
        self.model_manager: Optional[ModelManager] = None  # 模型管理器
        self.tool_chain_manager: Optional[ToolChainManager] = None  # 工具链管理器
        self.request_processor: Optional[RequestProcessor] = None  # 请求处理器
        self.health_checker: Optional[HealthChecker] = None  # 健康检查器
        self.resource_manager: Optional[ResourceManager] = None  # 资源管理器
        self.is_initialized = False  # 初始化状态
        self.logger = logging.getLogger(__name__)  # 日志器
        self.start_time = 0.0  # 启动时间
        self.last_health_check = 0.0  # 最后健康检查时间
        self.models: Dict[str, Any] = {}  # 加载的模型
        self.tool_chain_components: Dict[str, Any] = {}  # 工具链组件

    def initialize(self) -> None:
        """初始化应用（加载配置、模型、组件）"""
        if self.is_initialized:
            self.logger.warning("Application already initialized")
            return
        
        self.start_time = time.time()
        self.logger.info("Initializing VerticalDomainApplication...")
        
        # 1. 加载配置
        self.config_manager.init()
        
        # 2. 初始化模型管理器
        self.model_manager = ModelManager(self.config_manager)
        self.models = self.model_manager.load_models()
        
        # 3. 初始化工具链管理器
        self.tool_chain_manager = ToolChainManager(self.config_manager)
        self.tool_chain_components = self.tool_chain_manager.initialize_components()
        
        # 4. 初始化请求处理器
        self.request_processor = RequestProcessor(self)
        
        # 5. 初始化健康检查器和资源管理器
        self.health_checker = HealthChecker(self)
        self.resource_manager = ResourceManager(self)
        
        self.is_initialized = True
        self._print_initialization_summary()
        self.logger.info("Application initialized successfully")

    def _print_initialization_summary(self) -> None:
        """打印初始化摘要信息"""
        summary = (
            f"Initialization Summary:\n"
            f"- Models loaded: {len(self.models)}\n"
            f"- Toolchain components: {len(self.tool_chain_components)}\n"
            f"- Initialization time: {time.time() - self.start_time:.2f}s"
        )
        self.logger.info(summary)

    def cleanup(self) -> None:
        """清理应用资源（卸载模型、关闭组件）"""
        if not self.is_initialized:
            self.logger.warning("Application not initialized, nothing to clean up")
            return
        
        self.logger.info("Cleaning up application resources...")
        # 卸载模型
        if self.model_manager:
            self.model_manager.unload_models()
        # 清理工具链组件
        if self.tool_chain_manager:
            self.tool_chain_manager.cleanup_components()
        # 清理其他资源
        self.is_initialized = False
        self.logger.info("Application cleanup completed")

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理用户请求"""
        if not self.is_initialized:
            raise RuntimeError("Application not initialized, call initialize() first")
        
        if not self.request_processor:
            raise RuntimeError("RequestProcessor not initialized")
        
        # 执行健康检查（定期）
        if time.time() - self.last_health_check > 60:  # 每60秒检查一次
            self.health_checker.perform_health_check()
            self.last_health_check = time.time()
        
        return self.request_processor.process_request(request)

    def get_application_info(self) -> Dict[str, Any]:
        """获取应用信息"""
        return {
            "initialized": self.is_initialized,
            "start_time": self.start_time,
            "uptime": self._format_uptime(time.time() - self.start_time),
            "model_count": len(self.models),
            "component_count": len(self.tool_chain_components),
            "last_health_check": self.last_health_check
        }

    def _format_uptime(self, seconds: float) -> str:
        """格式化运行时间为人类可读格式"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def add_user_feedback(self, feedback: Dict[str, Any]) -> bool:
        """添加用户反馈（用于持续学习）"""
        # 待实现：将反馈传递给ContinuousLearningComponent
        return True

    def __enter__(self) -> "VerticalDomainApplication":
        """上下文管理器入口（with语句）"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口（with语句）"""
        self.cleanup()