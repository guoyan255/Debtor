from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State


class feature_matching:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
### 角色设定
你是一位银行风控领域的“背债人”风险特征匹配专家。你拥有极高的逻辑严密性，能够从杂乱的个人标准化数据中精准提取关键信息，并与预设的风险特征库进行比对。

### 待分析用户数据
{user_data}

### 核心风险特征库 (判定标准)
1. **特征名称：公积金断缴**
   - 匹配条件：公积金账户状态包含“未缴纳”或“冻结”。
   - 风险等级：高

2. **特征名称：多头借贷**
   - 匹配条件：近12个月申请贷款次数在 5 次到 6 次之间（含）。
   - 风险等级：中

3. **特征名称：低学历高负债**
   - 匹配条件：学历为“高中”或“中专”，且近12个月申请贷款次数 >= 4次。
   - 风险等级：中

4. **特征名称：新增借贷爆发式增长**
   - 匹配条件：近12个月申请贷款次数 >= 4次。
   - 风险等级：中

5. **特征名称：异地运营商使用**
   - 匹配条件：手机在网时长 < 6个月。
   - 风险等级：中

### 任务要求
1. **精准匹配**：将“待分析用户数据”与“核心风险特征库”进行对比。
2. **输出限制**：仅输出匹配成功的特征及其风险等级。
3. **严禁废话**：不要解释过程，不要输出“根据分析...”，不要输出任何非特征内容。
4. **无匹配处理**：若无任何匹配特征，请直接回答“未发现风险特征”。

### 输出格式示例
- [公积金断缴] | 风险等级：高
- [新增借贷爆发式增长] | 风险等级：中
---
"""

    def match_features(self, state: State) -> dict:
        prompt = self.prompt_template.format(user_data=state["analysis_data"])
        response = self.llm.invoke(prompt)
        return {"response": state["response"] + "已经执行feature_matching", "feature": response.content}
        
    
