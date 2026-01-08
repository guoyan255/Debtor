from model_components.deepseek_model import DeepSeekLLM
from state import State
import json

class feature_mining:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
你是银行风控领域的职业背债人特征挖掘专家，负责从标准化的用户JSON数据中挖掘核心风险特征，严格遵循以下规则：

【输入数据说明】
输入为用户多维度标准化JSON数据，包含：基础信息、公积金信息、征信信息、运营商信息、百融多头信息。

【特征挖掘规则】
1. 核心特征类型（必须覆盖以下12类）：
   高负债、频繁逾期、多头借贷、公积金断缴、征信查询频繁、短期异地贷款、异常离婚、与中介高频通话、
   异地运营商使用、低学历高负债、婚姻异常+借贷集中、新增借贷爆发式增长；
2. 特征要求：
   - 显性特征：直接匹配阈值的特征（如负债总额>50万→高负债）；
   - 隐性特征：多字段关联的组合特征（如离异<3个月+异地贷款→异常离婚+借贷集中）；
   - 每个特征需包含「特征类型+具体值+风险等级（低/中/高）+理由」；
   - 风险等级标准：
     ✅ 高风险：负债>50万/逾期>10次/多头平台>8个/断缴>6个月/中介通话占比>60%；
     ✅ 中风险：负债20-50万/逾期5-10次/多头平台4-8个/断缴3-6个月/中介通话占比30-60%；
     ✅ 低风险：负债<20万/逾期<5次/多头平台<4个/断缴<3个月/中介通话占比<30%；
3. 约束：仅基于输入数据挖掘，禁止编造特征，无匹配特征则标注为空列表。

【输出格式】（严格JSON格式，无额外文字、无注释）
{{
  "mined_features": [
    {{
      "feature_type": "特征类型",
      "feature_value": "具体特征值",
      "risk_level": "低/中/高",
      "reason": "挖掘理由（字段+数值+判定依据）"
    }}
  ],
  "top_risk_feature": "最高风险特征类型",
  "confidence": 0.0-1.0
}}

【任务】
基于以下用户标准化JSON数据完成特征挖掘：
用户数据：{text}
特征挖掘结果（仅输出JSON）：
        """

    def mine_features(self, state: State) -> dict:
        prompt = self.prompt_template.format(text=state["text"])
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "feature_mining", "response": response.content}