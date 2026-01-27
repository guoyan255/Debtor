
import sys
import os

# 将项目根目录加入 pyhton path，确保能找到模块
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # d:\Debtor\code\back
sys.path.append(project_root)

from model_components.foundation_model import FoundationModel

def test_foundation_model():
    print("Executing Test for FoundationModel...")
    
    # 1. 模拟配置
    config = {
        "model_name": "gpt-3.5-turbo",
        "api_key": "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", # 这是一个测试key，实际调用时会失败但能验证代码逻辑
        "base_url": "https://api.openai.com/v1",
        "temperature": 0.5
    }
    
    # 2. 实例化模型
    try:
        model = FoundationModel(config)
        print("Model initialized successfully.")
    except Exception as e:
        print(f"FAILED to initialize model: {e}")
        return

    # 3. 测试 generate 方法
    print("Testing generate method...")
    prompt = "Hello, tell me a joke."
    
    # 注意：因为 key 是假的，这里预计会报错，但我们要看报错信息是否来自 OpenAI，
    # 如果报错是 "Incorrect API key provided"，说明我们的 socket/request 逻辑通了。
    response = model.generate(prompt)
    
    print(f"Response received: {response}")

if __name__ == "__main__":
    test_foundation_model()
