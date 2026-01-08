from model_components.deepseek_model import DeepSeekLLM
from state import State

class risk_score:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
你是银行风控领域的背债人风险评分专家，负责基于“特征命中结果+背债人判定规则”，输出0-100分的量化风险评分，严格遵循以下规则：

【评分核心依据】
1. 基础评分维度：
   - 背债人判定结果：背债人（80-100分）、潜在背债人（40-79分）、非背债人（0-39分）；
   - 特征风险等级：高风险特征（每个+20分）、中风险特征（每个+10分）、低风险特征（每个+5分）；
   - 规则置信度：匹配规则的置信度×100（如置信度0.98→98分权重）。

【评分量化标准（0-100分，越高风险越高）】
1. 背债人（高风险）：
   - 匹配强判定规则（置信度≥0.9）：90-100分；
   - 匹配多条强判定规则：95-100分；
2. 潜在背债人（中风险）：
   - 匹配弱判定规则（置信度0.7-0.9）：60-89分；
   - 仅1个高风险特征：40-59分；
3. 非背债人（低风险）：
   - 匹配排除规则（置信度≥0.9）：0-19分；
   - 仅低风险特征：20-39分。

【评分规则】
1. 评分优先级：判定结果 > 特征数量 > 规则置信度；
2. 分数为整数，仅输出0-100范围内的数字；
3. 评分理由需包含：判定结果、命中特征数量/类型、匹配的规则、分数计算逻辑。

【输出格式要求】
1. 第一行仅输出风险评分（纯数字，0-100）；
2. 第二行起输出评分理由，逻辑清晰、量化说明；
3. 无额外标题、注释，仅保留“分数+理由”。

【输入数据】
{text}

【输出示例】
98
评分理由：用户命中“高负债、频繁逾期”2个高风险特征，匹配强判定规则“高负债 AND 频繁逾期→背债人（置信度0.98）”，判定为背债人，按规则加权计算得98分。

风险评分结果：
        """

    def assess_risk(self, state: State) -> dict:
        prompt = self.prompt_template.format(text=state["text"])
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "risk_score", "response": response.content}