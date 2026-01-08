import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State
from risk_score import risk_score


def test(self, state: State) -> dict:
        prompt = self.prompt_template
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "b", "response": response.content}
    
if __name__ == "__main__":
    test_data = {
        "user_id": "TEST001",
        "user_name": "张三",
        "communication_records": [
            {"date": "2024-01-05", "contact": "中介A", "content": "背债"},
            {"date": "2024-01-06", "contact": "中介A", "content": "信用包装"}
        ],
        "loan_applications": [
            {"date": "2024-01-10", "institution": "银行A"},
            {"date": "2024-01-12", "institution": "银行B"}
        ],
        "credit_inquiries": 5,
        "text_content": "需要办理背债业务"
    }

    # 调用
    scorer = risk_score()
    result = scorer.assess_risk(test_data)
    print(result["response"])