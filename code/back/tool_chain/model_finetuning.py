from model_components.deepseek_model import DeepSeekLLM
from state import State

class model_finetuning:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """数据特征判别专家。
        """

    def match_features(self, state: State) -> dict:
        prompt = self.prompt_template.format(feature_a=state["text"], feature_b=state["response"])
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "feature_matching", "response": response.content}