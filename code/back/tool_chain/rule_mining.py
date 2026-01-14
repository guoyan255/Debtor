from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State

class rule_mining:

   def __init__(self):
      deepseek_client = DeepSeekLLM()
      self.llm = deepseek_client.llm
      self.prompt_template = """
你是银行高级风控专家与欺诈情报分析师。你的任务是从多组原始用户数据中，通过横向对比发现隐藏的“背债人（职业代理人）”包装模式，并提炼出高价值的新规则。

【背债人典型包装逻辑（供参考）】
1. 突击包装：公积金/社保状态正常但分数较低，或短时间内多头借贷激增。
2. 身份错配：学历与收入严重不符（如高中学历申报高额年薪）。
3. 团伙聚集：不同用户的单位名称雷同（如XX商贸、XX咨询）、户籍地高度集中、申请时间点密集。
4. 异常迁移：居住地、工作地与户籍地跨度巨大，且无合理的职业轨迹。

【你的任务】
1. **模式发现**：对比这多个用户，找出那些“本不该有交集但特征高度相似”的群体共性。
2. **特征提炼**：挖掘原始数据中未直接给出的衍生特征（例如：申请频率/在网时长比率、户籍偏远程度等）。
3. **规则构造**：构造类似“特征A + 特征B + 特征C -> 高风险”的组合逻辑。

【输出要求】
请严格按照以下格式输出挖掘出的新规则（每条规则需包含）：
- [新特征组合]：明确描述多个字段的组合逻辑。
- [风险判定]：背债人 / 潜在背债人。
- [挖掘理由]：从多条数据中发现的具体异常点（如：用户3、7、12均符合此特征）。
- [置信度]：0.0-1.0。

【输入数据】
{user_data}
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
