from model_components.deepseek_model import DeepSeekLLM
from state import State

class risk_score:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """你是一个风险评分专家。
        请根据以下数据描述，评估其风险评分，并给出理由。
        数据描述: {text}
        请输出风险评分，并简要说明理由。
        """

    def assess_risk(self, state: State) -> dict:
        prompt = self.prompt_template.format(text=state["text"])
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "risk_score", "response": response.content}