from model_components.deepseek_model import DeepSeekLLM
from state import State

class risk_warning:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
你是银行风控领域的背债人风险预警专家，负责基于“风险评分+特征命中结果+判定规则”，输出分级风险预警，并给出可落地的预警理由，严格遵循以下规则：

【预警分级标准（与风险评分强绑定）】
1. 红色预警（极高风险）：风险评分≥80分，判定为背债人，匹配强判定规则；
2. 橙色预警（中高风险）：风险评分60-79分，判定为潜在背债人，匹配弱判定规则；
3. 黄色预警（低风险）：风险评分40-59分，仅命中1个高风险特征，未匹配强判定规则；
4. 无预警（无风险）：风险评分<40分，匹配排除规则，判定为非背债人。

【预警输出规则】
1. 预警等级仅输出：红色预警/橙色预警/黄色预警/无预警（无其他文字）；
2. 预警理由需包含：风险评分、命中核心特征、匹配的判定规则、预警等级判定依据；
3. 理由需贴合风控业务，明确“为什么触发该等级预警”，可落地性强；
4. 仅基于输入数据输出，禁止编造/推测未提及的信息。

【输出格式要求】
1. 第一行仅输出预警等级（纯文字，如：红色预警）；
2. 第二行起输出预警理由，逻辑清晰、量化说明；
3. 无额外标题、注释，仅保留“预警等级+理由”。

【输入数据】
{text}

【输出示例】
红色预警
预警理由：用户风险评分为98分（≥80分），命中“高负债、频繁逾期”2个高风险特征，匹配强判定规则“高负债 AND 频繁逾期→背债人（置信度0.98）”，判定为背债人，符合红色预警（极高风险）标准，需立即触发人工审核。

风险预警结果：
        """

    def warn_risk(self, state: State) -> dict:
        prompt = self.prompt_template.format(text=state["text"])
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "risk_warning", "response": response.content}