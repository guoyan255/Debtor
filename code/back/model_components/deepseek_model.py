from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
import os
from core_abstract.model_type import ModelType


class DeepSeekLLM:
    """
    DeepSeek 大模型客户端封装类
    用于便捷地初始化和调用 DeepSeek 模型
    """
    
    def __init__(self):
        """初始化方法：加载环境变量并创建 ChatDeepSeek 实例"""
        # 加载 .env 文件中的环境变量
        load_dotenv()
        
        # 获取环境变量，并做非空校验
        self.DEEPSEEK_KEY = os.getenv('DEEPSEEK_KEY')
        self.DEEPSEEK_URL = os.getenv('DEEPSEEK_URL')
        self.model_type = ModelType.FOUNDATION
        
        if not self.DEEPSEEK_KEY:
            raise ValueError("环境变量 DEEPSEEK_KEY 未配置，请检查 .env 文件")
        if not self.DEEPSEEK_URL:
            raise ValueError("环境变量 DEEPSEEK_URL 未配置，请检查 .env 文件")
        
        # 初始化 DeepSeek 客户端
        self.llm = self._init_llm()
    
    def _init_llm(self):
        """私有方法：创建并返回 ChatDeepSeek 实例"""
        return ChatDeepSeek(
            model="deepseek-chat",
            base_url=self.DEEPSEEK_URL,
            api_key=self.DEEPSEEK_KEY,
            # 可根据需要添加其他参数，比如温度、最大令牌数等
        )
    