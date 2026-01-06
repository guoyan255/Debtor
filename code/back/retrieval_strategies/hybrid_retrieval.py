from typing import Dict, List, Any, Optional
import time
import threading
from retrieval_strategy import RetrievalStrategy
from semantic_retrieval import SemanticRetrievalStrategy
from keyword_retrieval import KeywordRetrievalStrategy


class HybridRetrievalStrategy(RetrievalStrategy):
    """混合检索策略（结合语义检索和关键词检索）"""

    def __init__(self, config: Dict[str, Any]):
        """初始化混合检索策略
        Args:
            config: 配置字典，包含以下键：
                - semantic_weight: 语义检索结果权重（0-1）
                - keyword_weight: 关键词检索结果权重（0-1）
                - top_k: 最终返回的top-k结果数量
                - relevancy_threshold: 最低相关性阈值
                - semantic_strategy_config: 语义检索子策略配置
                - keyword_strategy_config: 关键词检索子策略配置
                - cache_enabled: 是否启用缓存
                - cache_ttl: 缓存过期时间（秒）
        """
        self.semantic_weight = config.get("semantic_weight", 0.7)
        self.keyword_weight = config.get("keyword_weight", 0.3)
        self.top_k = config.get("top_k", 10)
        self.relevancy_threshold = config.get("relevancy_threshold", 0.3)
        
        # 初始化子策略
        self.semantic_strategy = SemanticRetrievalStrategy(
            config.get("semantic_strategy_config", {})
        )
        self.keyword_strategy = KeywordRetrievalStrategy(
            config.get("keyword_strategy_config", {})
        )
        
        # 缓存相关属性
        self.cache_enabled = config.get("cache_enabled", True)
        self.cache_ttl = config.get("cache_ttl", 3600)
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        self._cache_times: Dict[str, float] = {}
        self._lock = threading.Lock()

    def retrieve(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行混合检索（框架实现，具体逻辑待补充）"""
        # 1. 检查缓存
        cache_key = self._get_cache_key(query, context.get("domain"))
        if self.cache_enabled:
            cached_result = self._get_cached_results(cache_key)
            if cached_result is not None:
                return cached_result
        
        # 2. 分别执行子策略检索
        semantic_results = self.semantic_strategy.retrieve(query, context)
        keyword_results = self.keyword_strategy.retrieve(query, context)
        
        # 3. 融合结果（待实现）
        # 此处仅为框架，实际需基于权重融合分数并排序
        fused_results = self._fuse_results(semantic_results, keyword_results)
        
        # 4. 缓存结果
        if self.cache_enabled:
            self._set_cached_results(cache_key, fused_results)
        
        return fused_results

    def _fuse_results(self, semantic_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """融合语义检索和关键词检索结果（待实现）"""
        # 示例逻辑框架：合并结果并按加权分数排序
        fused = []
        # ... 实际融合逻辑 ...
        return fused[:self.top_k]  # 截断到top_k

    def _get_cache_key(self, query: str, domain: Optional[str] = None) -> str:
        """生成缓存键"""
        return f"{domain}:{query}" if domain else query

    def _get_cached_results(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """获取缓存结果（带过期检查）"""
        with self._lock:
            if cache_key in self._cache:
                cache_time = self._cache_times[cache_key]
                if time.time() - cache_time < self.cache_ttl:
                    return self._cache[cache_key]
                # 清理过期缓存
                del self._cache[cache_key]
                del self._cache_times[cache_key]
        return None

    def _set_cached_results(self, cache_key: str, results: List[Dict[str, Any]]) -> None:
        """设置缓存结果"""
        with self._lock:
            self._cache[cache_key] = results
            self._cache_times[cache_key] = time.time()

    def get_strategy_info(self) -> Dict[str, Any]:
        """返回策略配置信息（包含子策略信息）"""
        return {
            "strategy_type": "hybrid",
            "semantic_weight": self.semantic_weight,
            "keyword_weight": self.keyword_weight,
            "top_k": self.top_k,
            "relevancy_threshold": self.relevancy_threshold,
            "semantic_strategy": self.semantic_strategy.get_strategy_info(),
            "keyword_strategy": self.keyword_strategy.get_strategy_info(),
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl
        }