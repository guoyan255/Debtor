from typing import Dict, Any, List, Tuple, Optional, Deque
from collections import deque
import time
import logging
from .application_context import ApplicationContext
from core_abstract.tool_chain_component import ToolChainComponent
from core_application import VerticalDomainApplication


class RequestProcessor:
    """请求处理器，负责协调工具链组件执行并生成响应"""
    
    def __init__(self, application: VerticalDomainApplication):
        self.application = application  # 关联核心应用实例
        self.logger = logging.getLogger(__name__)  # 日志器
        self.request_counter = 0  # 请求计数器
        self.avg_processing_time = 0.0  # 平均处理时间
        self.error_count = 0  # 错误计数
        self.request_history: Deque[Dict[str, Any]] = deque(maxlen=1000)  # 请求历史（最多1000条）

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理用户请求的主入口"""
        request_id = request.get("request_id", f"req_{int(time.time())}")
        start_time = time.time()
        try:
            # 记录请求开始
            self._record_request_start(request_id, request, start_time)
            
            # 初始化上下文
            context = ApplicationContext()
            context.set("request", request)
            context.set("request_id", request_id)
            
            # 确定组件执行顺序
            components = self.application.tool_chain_manager.get_components_by_type(...)  # 待实现
            execution_order = self._determine_execution_order(context, components, dynamic_routing_enabled=True)
            
            # 按顺序执行组件
            context = self._execute_components_in_order(context, components, execution_order)
            
            # 生成响应
            response = self._generate_response(context, start_time)
            self.request_counter += 1
            self.request_history.append({
                "request_id": request_id,
                "status": "success",
                "processing_time": time.time() - start_time
            })
            return response
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Request {request_id} failed: {str(e)}")
            return self._generate_error_response(e, start_time, request_id)

    def _record_request_start(self, request_id: str, request: Dict[str, Any], start_time: float) -> None:
        """记录请求开始信息"""
        self.logger.info(f"Processing request {request_id} started at {start_time}")

    def _determine_execution_order(
        self, 
        context: ApplicationContext, 
        components: List[ToolChainComponent], 
        dynamic_routing_enabled: bool
    ) -> List[str]:
        """确定工具链组件的执行顺序（待实现动态路由逻辑）"""
        # 暂时返回组件类型列表，实际需根据请求动态计算
        return [comp.component_type.value for comp in components]

    def _execute_components_in_order(
        self, 
        context: ApplicationContext, 
        components: List[ToolChainComponent], 
        execution_order: List[str]
    ) -> ApplicationContext:
        """按顺序执行工具链组件"""
        for component_type in execution_order:
            component = next((c for c in components if c.component_type.value == component_type), None)
            if component:
                context = self._execute_component(component, context)
        return context

    def _execute_component(self, component: ToolChainComponent, context: ApplicationContext) -> ApplicationContext:
        """执行单个工具链组件"""
        component.execute(context.data)  # 调用组件执行方法
        return context

    def _generate_response(self, context: ApplicationContext, start_time: float) -> Dict[str, Any]:
        """生成最终响应（待实现）"""
        processing_time = time.time() - start_time
        # 更新平均处理时间
        self.avg_processing_time = (self.avg_processing_time * (self.request_counter - 1) + processing_time) / self.request_counter
        return {
            "request_id": context.get("request_id"),
            "status": "success",
            "data": context.get("response_data", {}),
            "processing_time": processing_time,
            "token_usage": self._estimate_token_usage("", ""),  # 待实现
            "confidence_score": self._calculate_confidence_score(context)
        }

    def _estimate_token_usage(self, query: str, response: str) -> Dict[str, int]:
        """估算token使用量（待实现）"""
        return {"prompt_tokens": len(query), "completion_tokens": len(response)}

    def _calculate_response_quality(self, response: str) -> float:
        """计算响应质量分数（待实现）"""
        return 0.0  # 占位

    def _calculate_confidence_score(self, context: ApplicationContext) -> float:
        """计算响应置信度（待实现）"""
        return 0.0  # 占位

    def _record_request_complete(self, request_id: str, response: Dict[str, Any], start_time: float) -> None:
        """记录请求完成信息"""
        self.logger.info(f"Request {request_id} completed in {time.time() - start_time}s")

    def _trigger_continuous_learning(self, context: ApplicationContext, response: Dict[str, Any]) -> None:
        """触发持续学习（待实现）"""
        pass

    def _generate_error_response(self, error: Exception, start_time: float, request_id: str) -> Dict[str, Any]:
        """生成错误响应"""
        return {
            "request_id": request_id,
            "status": "error",
            "message": str(error),
            "processing_time": time.time() - start_time
        }

    def get_processor_stats(self) -> Dict[str, Any]:
        """获取处理器统计信息"""
        return {
            "total_requests": self.request_counter,
            "error_rate": self.error_count / max(self.request_counter, 1),
            "avg_processing_time": self.avg_processing_time,
            "history_size": len(self.request_history)
        }