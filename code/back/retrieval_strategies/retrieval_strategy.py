from abc import ABC, abstractmethod
from typing import Dict, List, Any


class RetrievalStrategy(ABC):
    """检索策略抽象接口，定义检索逻辑的规范"""

    @abstractmethod
    def retrieve(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行检索操作
        Args:
            query: 检索查询文本
            context: 检索上下文（可能包含领域、过滤条件等）
        Returns:
            检索结果列表，每个结果为包含文本、分数等信息的字典
        """
        pass

    @abstractmethod
    def get_strategy_info(self) -> Dict[str, Any]:
        """获取检索策略的配置信息
        Returns:
            包含策略类型、参数等信息的字典
        """
        pass