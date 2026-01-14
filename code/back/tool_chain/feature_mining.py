from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State
import json

class feature_mining:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
你是银行风控领域资深的职业背债人特征挖掘专家，核心任务是从**已知背债人用户数据**中挖掘其核心风险特征，需尽可能全面、细致地提取所有显性和隐性特征，为后续规则挖掘提供完整依据。

【输入数据说明】
输入为多组背债人用户的多维度标准化数据，包含：基础信息、公积金信息、征信信息、运营商信息、百融多头信息。

【特征挖掘核心要求】
1. 必须覆盖但不限于以下12类核心特征（尽可能挖掘每类下的细分特征）：
   高负债、频繁逾期、多头借贷、公积金断缴、征信查询频繁、短期异地贷款、异常离婚、与中介高频通话、
   异地运营商使用、低学历高负债、婚姻异常+借贷集中、新增借贷爆发式增长；
2. 特征分类（全部挖掘，不遗漏）：
   - 显性特征：直接可匹配阈值的特征（如负债总额>50万→高负债、多头借贷平台数=10→多头借贷）；
   - 隐性特征：多字段关联的组合特征（如离异<3个月+异地贷款+多头平台>8个→异常离婚+借贷集中+高风险）；
3. 每个特征需明确「特征名称+具体值+风险等级（低/中/高）+挖掘理由」，风险等级严格按以下标准判定：
   ✅ 高风险：负债>50万/逾期>10次/多头平台>8个/公积金断缴>6个月/中介通话占比>60%；
   ✅ 中风险：负债20-50万/逾期5-10次/多头平台4-8个/公积金断缴3-6个月/中介通话占比30-60%；
   ✅ 低风险：负债<20万/逾期<5次/多头平台<4个/公积金断缴<3个月/中介通话占比<30%；
4. 约束：仅基于输入的背债人数据挖掘，禁止编造特征；需尽可能多的输出特征（无上限），无匹配特征则标注为空列表。

【输出格式】（严格JSON格式，无任何额外文字、注释、换行，确保可直接解析）
{{
  "mined_features": [
    {{
      "feature_type": "特征类型（需归属到12类核心特征中）",
      "feature_value": "具体特征值（如：负债总额=60万、离异2个月+异地贷款）",
      "risk_level": "低/中/高",
      "reason": "挖掘理由（需关联具体用户数据，如：用户1/3/5的负债总额均>50万，符合高负债高风险标准）"
    }}
  ],
  "top_risk_feature": "最高风险特征类型（如：高负债）",
  "confidence": 0.0-1.0（特征挖掘结果的置信度）
}}

【任务】
基于以下背债人用户数据，全面、无遗漏地挖掘所有相关风险特征：
用户数据：{user_data}
"""

    def mine_features(self, state: State) -> dict:
        # 将 List[Dict] 转换为更易读的文本格式
      user_data_str = ""
      for i, d in enumerate(state["data"]):
         user_data_str += f"用户{i+1}: {str(d)}\n"
      prompt = self.prompt_template.format(user_data=user_data_str)
      response = self.llm.invoke(prompt)
      # 将挖掘出的特征结果存入state的new_feature字段
      try:
          # 尝试解析JSON（可选：确保输出格式合规，也可直接存原始响应）
          feature_result = json.loads(response.content)
          state["new_feature"] = json.dumps(feature_result, ensure_ascii=False, indent=2)
      except json.JSONDecodeError:
          # 若解析失败，直接存储原始响应（避免流程中断）
          state["new_feature"] = response.content
        
      return state


      #return {"text": state["text"] + "feature_mining", "response": response.content}