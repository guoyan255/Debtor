from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State
import json
class risk_score:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
### 角色设定
你是一位精通金融反欺诈的资深风控专家，专门识别“职业背债人”风险。你具备从碎片化特征中洞察团伙作案和信用欺诈的敏锐嗅觉。

### 输入数据
1. **用户原始数据**：
{user_data}

2. **命中的风险特征**：
{user_features}

3. **关联的风控规则依据**：
{user_rules}

### 评估任务
请结合上述数据、特征与规则，评估该用户为“职业背债人”的风险程度。
- **风险评分**：0-100分（分值越高代表风险越大，80分以上通常视为极高风险）。
- **评分原因**：基于数据事实、特征逻辑与规则碰撞，简要说明扣分项。

### 约束要求（极其重要）
1. **只允许输出风险评分和评分原因**，禁止输出任何开场白、过程分析或结束语。
2. **严禁废话**，不要解释“根据上述分析...”。
3. **输出格式**必须严格遵循以下模板：
---
风险评分：[具体分值]
评分原因：[1. 原因一；2. 原因二；...]
---
"""

    def assess_risk(self, state: State) -> dict:

      prompt = self.prompt_template.format(user_data=state["analysis_data"],user_features=state["feature"],user_rules=state["rule"])
      response = self.llm.invoke(prompt)
      return {"response": state["response"] + "已经执行risk_score", "risk": response.content}