from typing import Dict, Any
import logging
import time
from core_application.vertical_domain_application import VerticalDomainApplication


class HealthChecker:
    """健康检查器，负责系统整体健康状态监控"""
    
    def __init__(self, application: VerticalDomainApplication):
        self.application = application  # 核心应用实例
        self.logger = logging.getLogger(__name__)  # 日志器
        self.check_interval = 60  # 健康检查间隔（秒）
        self.last_check_time = 0.0  # 上次检查时间
        self.health_status: Dict[str, Any] = {
            "overall": "unknown",
            "components": {},
            "timestamp": 0.0
        }  # 健康状态缓存

    def perform_health_check(self) -> Dict[str, Any]:
        """执行全系统健康检查"""
        current_time = time.time()
        self.logger.info("Performing system health check...")
        
        # 检查各核心组件健康状态
        model_health = self.application.model_manager.health_check()
        tool_health = self.application.tool_chain_manager.health_check()
        resource_health = self._check_resources()
        
        # 汇总整体健康状态
        all_healthy = (
            all(status["status"] == "healthy" for status in model_health.values()) and
            all(status["status"] == "healthy" for status in tool_health.values()) and
            resource_health["status"] == "healthy"
        )
        
        self.health_status = {
            "overall": "healthy" if all_healthy else "degraded",
            "components": {
                "models": model_health,
                "tool_chain": tool_health,
                "resources": resource_health
            },
            "timestamp": current_time
        }
        
        self.last_check_time = current_time
        return self.health_status

    def _check_resources(self) -> Dict[str, Any]:
        """检查系统资源健康状态"""
        resources = self.application.resource_manager.monitor_resources()
        thresholds = self.application.resource_manager.resource_thresholds
        
        # 检查资源是否超过阈值
        cpu_healthy = resources["cpu_usage"] < thresholds["cpu"]
        memory_healthy = resources["memory_usage"] < thresholds["memory"]
        disk_healthy = resources["disk_usage"] < thresholds["disk"]
        
        status = "healthy" if (cpu_healthy and memory_healthy and disk_healthy) else "degraded"
        
        return {
            "status": status,
            "metrics": resources,
            "thresholds": thresholds,
            "message": "Resources within limits" if status == "healthy" else "Resource usage high"
        }