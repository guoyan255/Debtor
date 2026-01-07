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