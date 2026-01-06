from typing import Dict, Optional, Any
import logging
from collections import defaultdict
from factory_config.config_manager import ConfigManager
from core_abstract.base_model import BaseModel


class ModelManager:
    """模型管理器，负责所有模型的生命周期管理与状态监控"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager  # 配置管理器实例
        self.models: Dict[str, BaseModel] = {}  # 加载的模型字典：{模型名称: 模型实例}
        self.logger = logging.getLogger(__name__)  # 日志器
        self.model_load_times: Dict[str, float] = {}  # 模型加载时间记录
        self.model_usage_stats = defaultdict(int)  # 模型使用统计：{模型名称: 调用次数}

    def load_models(self) -> Dict[str, BaseModel]:
        """加载所有配置中启用的模型（具体实现待补充）"""
        self.logger.info("Starting to load models...")
        # 1. 从配置管理器获取模型配置
        model_configs = self.config_manager.get_model_configs()
        # 2. 遍历配置，加载启用的模型（通过ModelFactory创建）
        for model_name, config in model_configs.items():
            if config.enabled:
                try:
                    # 此处需通过ModelFactory创建模型实例，暂为框架
                    model = None  # 实际应替换为ModelFactory.create_model(...)
                    self.models[model_name] = model
                    self.logger.info(f"Loaded model: {model_name} (type: {config.model_type})")
                except Exception as e:
                    self.logger.error(f"Failed to load model {model_name}: {str(e)}")
        return self.models

    def unload_models(self) -> None:
        """卸载所有已加载的模型（调用模型的unload方法）"""
        self.logger.info("Unloading all models...")
        for model_name, model in self.models.items():
            try:
                model.unload()
                self.logger.info(f"Unloaded model: {model_name}")
            except Exception as e:
                self.logger.error(f"Failed to unload model {model_name}: {str(e)}")
        self.models.clear()
        self.model_load_times.clear()

    def get_model(self, model_name: str) -> Optional[BaseModel]:
        """根据模型名称获取模型实例"""
        model = self.models.get(model_name)
        if model:
            self.model_usage_stats[model_name] += 1  # 记录使用次数
            model.record_usage()  # 调用模型自身的使用记录方法
        return model

    def get_model_stats(self) -> Dict[str, Any]:
        """获取所有模型的状态统计信息"""
        stats = {}
        for model_name, model in self.models.items():
            stats[model_name] = {
                "type": model.model_type,
                "version": model.model_version,
                "is_loaded": model.is_loaded,
                "usage_count": model.usage_count,
                "load_time": self.model_load_times.get(model_name),
                "last_access": model.last_access_time
            }
        return stats

    def health_check(self) -> Dict[str, Any]:
        """检查所有模型的健康状态"""
        health_status = {}
        for model_name, model in self.models.items():
            try:
                # 简单健康检查：模型是否加载
                health_status[model_name] = {
                    "status": "healthy" if model.is_loaded else "unhealthy",
                    "message": "Model loaded successfully" if model.is_loaded else "Model not loaded"
                }
            except Exception as e:
                health_status[model_name] = {
                    "status": "error",
                    "message": str(e)
                }
        return health_status