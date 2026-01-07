from model_components.deepseek_model import DeepSeekLLM
from state import State

class feature_mining:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """你是一个特征挖掘专家。
        请根据以下数据描述，挖掘出有价值的特征，并给出理由。
        数据描述: {text}
        请输出挖掘出的特征，并简要说明理由。
        """

    def mine_features(self, state: State) -> dict:
        prompt = self.prompt_template.format(text=state["text"])
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "feature_mining", "response": response.content}