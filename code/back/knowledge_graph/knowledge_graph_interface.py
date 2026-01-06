from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from model_components.knowledge_graph_model import KnowledgeGraphModel

class KnowledgeGraphInterface(ABC):
    """知识图谱核心操作接口（抽象基类），定义实体和关系的管理规范"""

    @abstractmethod
    def add_entity(self, entity_id: str, entity_type: str, attributes: Dict[str, Any]) -> None:
        """添加实体
        Args:
            entity_id: 实体唯一标识
            entity_type: 实体类型
            attributes: 实体属性键值对
        """
        pass

    @abstractmethod
    def add_relation(self, source_id: str, target_id: str, relation_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """添加关系
        Args:
            source_id: 源实体ID
            target_id: 目标实体ID
            relation_type: 关系类型
            attributes: 关系属性键值对（可选）
        """
        pass

    @abstractmethod
    def query_entities(self, entity_type: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """查询实体
        Args:
            entity_type: 实体类型（可选，过滤特定类型）
            attributes: 属性过滤条件（可选）
        Returns:
            符合条件的实体列表
        """
        pass

    @abstractmethod
    def query_relations(self, source_id: Optional[str] = None, target_id: Optional[str] = None, relation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """查询关系
        Args:
            source_id: 源实体ID（可选）
            target_id: 目标实体ID（可选）
            relation_type: 关系类型（可选）
        Returns:
            符合条件的关系列表
        """
        pass

    @abstractmethod
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """执行自定义查询（如SPARQL、Cypher等）
        Args:
            query: 查询语句
        Returns:
            查询结果列表
        """
        pass

    @abstractmethod
    def get_entity_neighbors(self, entity_id: str, max_depth: int = 1) -> Dict[str, Any]:
        """获取实体的邻居节点（关系网络）
        Args:
            entity_id: 实体ID
            max_depth: 最大查询深度（默认1层）
        Returns:
            包含邻居实体和关系的字典
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """关闭知识图谱连接（释放资源）"""
        pass