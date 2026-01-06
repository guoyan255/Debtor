from typing import Dict, Any, Optional, List
import logging
from model_config import ModelConfig
from tool_chain_config import ToolChainConfig


class ConfigManager:
    """配置管理器，负责加载和管理应用所有配置"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file  # 配置文件路径
        self.config: Dict[str, Any] = {}  # 合并后的完整配置
        self.logger = logging.getLogger(__name__)  # 日志器

    def init(self) -> None:
        """初始化配置（加载默认配置 + 外部配置）"""
        self.logger.info("Initializing configuration...")
        # 1. 加载默认配置
        default_config = self._load_default_config()
        # 2. 加载外部配置文件（如指定）
        external_config = self._load_config_from_file() if self.config_file else {}
        # 3. 合并配置（外部配置覆盖默认配置）
        self.config = self._merge_configs(default_config, external_config)
        # 4. 初始化日志配置
        self._setup_logging()
        # 5. 验证配置有效性
        if not self.validate_config():
            raise ValueError("Invalid application configuration")
        self.logger.info("Configuration initialized successfully")

    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置（内置基础配置）"""
        return {
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "models": {},  # 默认模型配置
            "tool_chain": {},  # 默认工具链配置
            "system": {
                "max_threads": 10,
                "cache_enabled": True
            }
        }

    def _load_config_from_file(self) -> Dict[str, Any]:
        """从外部文件加载配置（具体实现待补充，支持JSON/YAML等格式）"""
        if not self.config_file:
            return {}
        self.logger.info(f"Loading configuration from {self.config_file}")
        # 此处仅为框架，实际需实现文件读取逻辑
        return {}

    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """合并基础配置和覆盖配置（递归合并嵌套字典）"""
        merged = base.copy()
        for key, value in override.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _setup_logging(self) -> None:
        """根据配置设置日志系统（待实现）"""
        log_config = self.config.get("logging", {})
        logging.basicConfig(
            level=log_config.get("level", "INFO"),
            format=log_config.get("format", "%(asctime)s - %(levelname)s - %(message)s")
        )

    def get_model_configs(self) -> Dict[str, ModelConfig]:
        """获取所有模型配置（转换为ModelConfig对象）"""
        model_configs = {}
        for name, cfg in self.config.get("models", {}).items():
            model_configs[name] = ModelConfig(
                model_type=cfg.get("model_type"),
                model_name=name,
                parameters=cfg.get("parameters", {}),
                enabled=cfg.get("enabled", True),
                priority=cfg.get("priority", 0)
            )
        return model_configs

    def get_tool_chain_configs(self) -> List[ToolChainConfig]:
        """获取所有工具链组件配置（转换为ToolChainConfig对象）"""
        tool_configs = []
        for cfg in self.config.get("tool_chain", {}).values():
            tool_configs.append(ToolChainConfig(
                component_type=cfg.get("component_type"),
                enabled=cfg.get("enabled", True),
                priority=cfg.get("priority", 0),
                parameters=cfg.get("parameters", {})
            ))
        # 按优先级排序
        return sorted(tool_configs, key=lambda x: x.priority, reverse=True)

    def validate_config(self) -> bool:
        """验证配置的完整性和有效性（待实现）"""
        # 检查必要配置项是否存在
        required_sections = ["models", "tool_chain", "logging"]
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"Missing required config section: {section}")
                return False
        return True

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项（支持点分隔符，如"system.max_threads"）"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value