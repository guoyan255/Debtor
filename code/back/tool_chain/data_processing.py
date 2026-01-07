from model_components.deepseek_model import DeepSeekLLM
from state import State

class data_processing:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """你是一个数据处理专家。
        请根据以下描述，对数据进行处理，并给出理由。
        数据: {data}
        请输出处理后的数据，并简要说明理由。
        """

    def process_data(self, state: State) -> dict:
        prompt = self.prompt_template.format(data=state["data"])
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "data_processing", "response": response.content}
        
    
