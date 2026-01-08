from model_components.deepseek_model import DeepSeekLLM
from state import State
import json

class feature_matching:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
你是银行风控领域的背债人风险特征匹配专家，负责基于预处理后（data_processing输出）的个人360度标准化JSON数据，精准匹配核心风险特征并输出命中结果，严格遵循以下规则：

【核心规则】
1. 数据读取规则：仅从输入JSON的「standardized_data」字段中读取标准化数据，忽略其他字段（如raw_csv_data、standardization_log）；
2. 字段取值规则：严格按JSON层级读取字段值（如公积金断缴时长：standardized_data→公积金信息→断缴时长（月））；
3. 空值处理：字段值为null/未知时，视为不满足该特征的判定条件；
4. 数值判定：严格按阈值比较，仅支持数字类型比较（非数字值视为不满足）。

【背债人核心风险特征库（基于标准化JSON字段）】
### 1. 基础风险特征（单字段判定）
- 高负债：standardized_data.征信信息.负债总额（元） > 500000
- 频繁逾期：standardized_data.征信信息.逾期次数 > 10 或 standardized_data.征信信息.逾期最长天数 > 90
- 多头借贷：standardized_data.百融多头信息.多头借贷平台数 > 8 或 standardized_data.百融多头信息.近1个月新增借贷次数 > 5
- 公积金断缴：standardized_data.公积金信息.断缴时长（月） > 6
- 征信查询频繁：standardized_data.征信信息.信贷查询次数（近3个月） > 20
- 低学历高负债：standardized_data.学历 ∈ ["小学","初中","高中"] 且 standardized_data.征信信息.负债总额（元） > 300000

### 2. 行为风险特征（多字段组合判定）
- 短期异地贷款：
  ① standardized_data.运营商信息.是否异地使用 = "是" 
  ② standardized_data.百融多头信息.近1个月新增借贷次数 > 3
  ③ standardized_data.地址 包含 "异地" 或 与常用地址不一致（无常用地址时仅需满足①+②）
- 异常离婚：
  ① standardized_data.婚姻状况 = "离异" 
  ② 离异时间 ≤ 6个月（无离异时间时仅需满足①+③）
  ③ standardized_data.征信信息.负债总额（元） > 0 且 环比增长 > 50%（无环比数据时仅需满足①）
- 异地运营商使用：
  ① standardized_data.运营商信息.是否异地使用 = "是" 
  ② standardized_data.运营商信息.在网时长（月） < 12

### 3. 区域风险特征
- 高风险区域来源：standardized_data.地址 ∈ ["广东省深圳市","浙江省杭州市","江苏省苏州市"]

【特征匹配要求】
1. 仅基于输入JSON的standardized_data字段做匹配，禁止使用外部信息/推测；
2. 多条件特征需满足「尽可能多的子条件」（无对应字段时跳过该子条件）；
3. 命中特征名称需和特征库完全一致（如“高负债”而非“负债过高”）；
4. 输出仅保留“特征命中结果”，无任何额外文字、说明、注释。

【输出格式】
- 命中特征：命中：特征1、特征2、特征3（特征名与特征库完全一致，用中文顿号分隔）
- 无命中特征：未命中任何风险特征

【输入数据】
预处理后的个人360度标准化JSON数据：{standardized_json}

特征命中结果：
        """

    def match_features(self, state: State) -> dict:
        prompt = self.prompt_template.format(feature_a=state["text"], feature_b=state["response"])
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "feature_matching", "response": response.content}
        
    
