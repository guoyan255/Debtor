from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State

class rule_mining:

   def __init__(self):
      deepseek_client = DeepSeekLLM()
      self.llm = deepseek_client.llm
      self.prompt_template = """
### 角色定位
你是银行反欺诈策略专家。你的核心任务是利用**已知的风险特征**和**原始用户数据**，构建能够精准识别“职业背债人”的**组合规则**。

### 任务背景
我们已经确认了以下高风险特征，现在的目标是将这些“单点特征”进行逻辑组合（AND/OR逻辑），找出那些“单看某一点尚可解释，但组合在一起极不合理”的背债模式。

### 1. 已挖掘的基础特征（已知条件）
以下特征已确认为风险指标，请基于这些积木构建规则：
[
  {{
    "feature_type": "公积金断缴",
    "feature_value": "公积金账户状态为'未缴纳'或'冻结'",
    "risk_level": "高"
  }},
  {{
    "feature_type": "多头借贷",
    "feature_value": "近12个月申请贷款次数=5-6次",
    "risk_level": "中"
  }},
  {{
    "feature_type": "低学历高负债",
    "feature_value": "学历为高中/中专 且 近12个月申请贷款次数>=4次",
    "risk_level": "中"
  }},
  {{
    "feature_type": "新增借贷爆发式增长",
    "feature_value": "近12个月申请贷款次数>=4次",
    "risk_level": "中"
  }},
  {{
    "feature_type": "异地运营商使用",
    "feature_value": "手机在网时长<6个月",
    "risk_level": "中"
  }}
]

### 2. 原始用户数据
{user_data}

### 规则构建指南
背债人通常具有“包装出的完美外壳”和“无法掩盖的底层矛盾”。请遵循以下逻辑构建规则：
1. **矛盾性组合**：例如 [低学历高负债] + [公积金断缴] -> 说明收入证明造假，且资金链已断裂。
2. **时序性组合**：例如 [异地运营商使用] + [新增借贷爆发式增长] -> 说明是近期专门为了骗贷购置的手机号。
3. **资质与行为不符**：典型底层群体被包装成优质客户后“杀鸡取卵”。

### 输出要求
请输出严格的 JSON 格式，包含一个规则列表 `rules`。每条规则必须包含：
- `rule_name`: 规则名称（如：断缴期突击借贷规则）。
- `logic_expression`: 逻辑表达式（如：公积金断缴 AND 多头借贷 > 5）。
- `risk_verdict`: 判定结果（高风险背债人 / 疑似背债人）。
- `hit_users`: 原始数据中命中该规则的用户编号（如：用户1, 用户3）。
- `reasoning`: 为什么这个组合能判定为背债人（深度业务逻辑解释）。
- `confidence`: 置信度 (0.8 - 1.0)。

### 输出示例
{{
    "rules": [
        {{
            "rule_name": "空壳包装突击规则",
            "logic_expression": "公积金状态异常 AND 手机在网<6个月 AND 借贷次数>4",
            "risk_verdict": "高风险背债人",
            "hit_users": ["用户2"],
            "reasoning": "用户公积金异常说明无稳定收入来源，却使用新手机号在短期内疯狂借贷，符合中介包装‘白户’进行最后一波收割的特征。",
            "confidence": 0.95
        }}
    ]
}}
"""

   ''' def mine_rules(self, state: State) -> dict:
        prompt = self.prompt_template.format(text=state["text"])
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "rule_mining", "response": response.content}'''
    
   def mine_rules(self, state: State):
      # 将 List[Dict] 转换为更易读的文本格式
      user_data_str = ""
      for i, d in enumerate(state["data"]):
         user_data_str += f"用户{i+1}: {str(d)}\n"
        
      # 调用大模型
      response = self.llm.invoke(self.prompt_template.format(user_data=user_data_str))
        
      # 将结果存入 state
      state["new_rule"] = response.content
      return state
