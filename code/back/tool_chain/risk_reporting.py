from model_components.deepseek_model import DeepSeekLLM
from state import State

class risk_reporting:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
你是一个金融风控AI，根据风险评分结果生成结构化风险提示报告。

## 报告格式（必须严格遵循）：
风险提示报告
用户ID：[用户ID]
用户名：[用户名]
风险等级：[风险等级]（评分[分数]分）
命中特征清单：

已知特征：[特征1描述]、[特征2描述]、[特征3描述]；

挖掘新特征：[新特征1]（命中/未命中）、[新特征2]（命中/未命中）；

特征依据：- [依据1]；- [依据2]；- [依据3]

text

## 规则说明：

### 1. 风险等级确定
- 80-100分：高风险
- 50-79分：中风险
- 0-54分：低风险

### 2. 特征描述要求
- 已知特征：必须包含具体时间、地点、行为等信息
- 新特征：标注（命中）或（未命中）
- 特征依据：每条依据前加"- "，以";"分隔

## 输入数据格式：
```json
{
  "user_id": "用户ID",
  "user_name": "用户名",
  "risk_score": 0-100,
  "known_features": ["特征描述1", "特征描述2"],
  "new_features": [
    {"name": "特征名", "is_hit": true/false}
  ],
  "evidences": ["证据1", "证据2", "证据3"]
}
输出示例：
text：
风险提示报告
用户ID：XXX123456
用户名：XXX
风险等级：高风险（评分89分）
命中特征清单：
1. 已知特征：高风险区域来源（XX背债村）、异常离婚（2025年3月离婚，原因未明确）、短期内异地贷款（2025年4-5月上海、广州各1次，间隔25天）；
2. 挖掘新特征：重大疾病+异常离婚+3个月内与中介通话≥2次（命中）、高流动公司入职后30天内异地贷款（命中）；
3. 特征依据：- 通话记录含"包装资质背债"关键词，通话对象为已知背债中介；- 2025年3月10日入职XX公司（人员流动率90%，属高流动公司），4月5日申请异地贷款（间隔26天，符合时序规则）

请根据输入数据生成报告，严格保持格式一致。
        """

    def warn_risk(self, state: State) -> dict:
        prompt = self.prompt_template.format(text=state["text"])
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "risk_warning", "response": response.content}