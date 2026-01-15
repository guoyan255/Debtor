from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State

class risk_reporting:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
你是一个金融风控AI，根据风险评分结果生成结构化风险提示报告。
### 角色设定
你是一个专业的金融风控AI系统，负责汇总全链路分析结果，生成最终的《背债风险评估报告》。

### 输入数据源
1. **分析数据全文**：{user_data}
2. **命中风险特征**：{user_features}
3. **风控规则依据**：{user_rules}
4. **风险评分与原因简述**：{user_risk}

### 报告生成逻辑与规则
1. **风险等级判定**：
   - 80-100分：高风险
   - 55-79分：中风险
   - 0-54分：低风险
2. **内容抽取要求**：
   - **用户名**：从“分析数据全文”中提取。
   - **已知特征**：整合“命中风险特征”，必须包含具体的时间、地点或关键行为。
   - **挖掘新特征**：结合“风险评分原因”，标注该用户是否命中了潜在的背债人行为模式。
   - **特征依据**：将“风控规则依据”与具体的数据事实（如通话、入职时间、借贷频率）一一对应。

### 约束要求
- **严禁废话**：输出内容必须以“风险提示报告”开头，以“特征依据”内容结尾。
- **严禁解释**：不要输出“收到”、“好的”或任何分析过程。
- **格式一致**：严格遵循下方示例格式。

---
### 输出格式模板

风险提示报告
用户名：[姓名]
风险等级：[高/中/低]风险（评分[具体分数]分）

命中特征清单：
1. 已知特征：[特征A（时间/行为/数据）；特征B...]
3. 特征规则：- [依据1：数据事实+规则逻辑]; - [依据2：数据事实+规则逻辑]

"""

    def warn_risk(self, state: State) -> dict:
              
      prompt = self.prompt_template.format(user_data=state["analysis_data"],user_features=state["feature"],user_rules=state["rule"],user_risk=state["risk"])
      response = self.llm.invoke(prompt)
      return {"response": state["response"] + "已经执行risk_reporting", "report": response.content}