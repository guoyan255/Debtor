import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State

class test2:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
        你好，DeepSeek！请介绍一下你自己。
        """

    def test(self, state: State) -> dict:
        prompt = self.prompt_template
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "b", "response": response.content}
    
if __name__ == "__main__":
    # 1. 创建实例
    tester = test2()
    
    # 2. 创建state对象（根据State类的实际结构）
    # 假设State需要text字段
    state = {"text": "测试文本: "}
    # 或者如果State是类：state = State(text="测试文本: ")
    
    # 3. 调用test方法
    try:
        result = tester.test(state)
        print("✅ 调用成功！")
        print(f"返回结果: {result}")
        print(f"响应内容: {result.get('response', '无响应')}")
    except Exception as e:
        print(f"❌ 调用失败: {e}")
        import traceback
        traceback.print_exc()