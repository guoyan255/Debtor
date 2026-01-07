from model_components.deepseek_model import DeepSeekLLM

class feature_matching:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """你是一个特征匹配专家。
        请根据以下描述，判断两个特征是否匹配，并给出理由。
        特征A: {feature_a}
        特征B: {feature_b}
        请输出“匹配”或“不匹配”，并简要说明理由。
        """
    
    def match_features(self, feature_a: str, feature_b: str) -> str:
        prompt = self.prompt_template.format(feature_a=feature_a, feature_b=feature_b)
        response = self.llm.invoke(prompt)
        return response
        
    
