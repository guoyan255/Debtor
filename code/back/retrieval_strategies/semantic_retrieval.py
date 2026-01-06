from typing import Dict, List, Any, Optional
import time
import threading
from retrieval_strategy import RetrievalStrategy


class SemanticRetrievalStrategy(RetrievalStrategy):
    """基于语义相似度的检索策略"""

    def __init__(self, config: Dict[str, Any]):
        """初始化语义检索策略
        Args:
            config: 配置字典，包含以下键：
                - top_k: 返回的top-k结果数量
                - similarity_threshold: 相似度阈值（低于此值的结果过滤）
                - batch_size: 批量处理大小
                - cache_enabled: 是否启用缓存
                - cache_ttl: 缓存过期时间（秒）
        """
        self.top_k = config.get("top_k", 10)
        self.similarity_threshold = config.get("similarity_threshold", 0.5)
        self.batch_size = config.get("batch_size", 32)
        self.cache_enabled = config.get("cache_enabled", True)
        self.cache_ttl = config.get("cache_ttl", 3600)  # 默认1小时过期
        
        # 缓存相关属性
        self._cache: Dict[str, List[Dict[str, Any]]] = {}  # 缓存键:检索结果
        self._cache_times: Dict[str, float] = {}  # 缓存键:创建时间
        self._lock = threading.Lock()  # 缓存操作锁

    def retrieve(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行语义检索（框架实现，具体逻辑待补充）"""
        # 1. 检查缓存
        cache_key = self._get_cache_key(query, context.get("domain"))
        if self.cache_enabled:
            cached_result = self._get_cached_results(cache_key)
            if cached_result is not None:
                return cached_result
        
        # 2. 实际检索逻辑（待实现）
        # 此处仅为框架，实际需调用嵌入模型计算向量并匹配
        results = []
        
        # 3. 缓存结果
        if self.cache_enabled:
            self._set_cached_results(cache_key, results)
        
        return results

    def _get_cache_key(self, query: str, domain: Optional[str] = None) -> str:
        """生成缓存键（结合查询和领域）"""
        return f"{domain}:{query}" if domain else query

    def _get_cached_results(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """获取缓存结果（带过期检查）"""
        with self._lock:
            if cache_key in self._cache:
                cache_time = self._cache_times[cache_key]
                if time.time() - cache_time < self.cache_ttl:
                    return self._cache[cache_key]
                # 过期缓存清理
                del self._cache[cache_key]
                del self._cache_times[cache_key]
        return None

    def _set_cached_results(self, cache_key: str, results: List[Dict[str, Any]]) -> None:
        """设置缓存结果"""
        with self._lock:
            self._cache[cache_key] = results
            self._cache_times[cache_key] = time.time()

    def get_strategy_info(self) -> Dict[str, Any]:
        """返回策略配置信息"""
        return {
            "strategy_type": "semantic",
            "top_k": self.top_k,
            "similarity_threshold": self.similarity_threshold,
            "batch_size": self.batch_size,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl
        }