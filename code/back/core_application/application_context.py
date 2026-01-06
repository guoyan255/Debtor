from typing import Dict, Any
import threading
import time


class ApplicationContext:
    """应用上下文类，存储请求处理过程中的所有数据和状态"""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}  # 上下文数据存储
        self.lock = threading.Lock()  # 线程安全锁
        self.creation_time = time.time()  # 创建时间
        self.last_access_time = time.time()  # 最后访问时间
        self.request_count = 0  # 请求计数

    def set(self, key: str, value: Any) -> None:
        """设置上下文键值对（线程安全）"""
        with self.lock:
            self.data[key] = value
            self.last_access_time = time.time()

    def get(self, key: str, default: Any = None) -> Any:
        """获取上下文值（线程安全）"""
        with self.lock:
            self.last_access_time = time.time()
            return self.data.get(key, default)

    def update(self, data: Dict[str, Any]) -> None:
        """批量更新上下文数据（线程安全）"""
        with self.lock:
            self.data.update(data)
            self.last_access_time = time.time()

    def clear(self) -> None:
        """清空上下文数据（线程安全）"""
        with self.lock:
            self.data.clear()
            self.last_access_time = time.time()
            self.request_count = 0

    def get_context_stats(self) -> Dict[str, Any]:
        """获取上下文统计信息"""
        with self.lock:
            return {
                "creation_time": self.creation_time,
                "last_access_time": self.last_access_time,
                "data_size": len(self.data),
                "request_count": self.request_count,
                "uptime_seconds": time.time() - self.creation_time
            }

    def __str__(self) -> str:
        return f"ApplicationContext(keys={list(self.data.keys())}, stats={self.get_context_stats()})"