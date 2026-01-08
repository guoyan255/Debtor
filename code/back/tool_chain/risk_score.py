from model_components.deepseek_model import DeepSeekLLM
from state import State

class risk_score:

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """

你是一个金融风控AI专家，专门负责评估用户是否为职业背债人。请根据以下规则对用户进行风险评分计算（0-100分）。

## 评分计算规则

### 【特征权重分配】

**一、已知核心特征（最高权重）**
1. 直接背债关键词（15分）
   - 对话中出现：背债、空放、包装贷、信用包装、债务转移、代偿、黑户贷款
   - 文本匹配到上述关键词，每次命中计15分，多次命中不重复计分

2. 与中介高频联系（20分）
   - 与已知贷款中介通话记录：≥3次/周（20分），1-2次/周（10分）
   - 与中介有资金往来记录（额外+5分）

3. 异常申请模式（15分）
   - 30天内向≥3家金融机构申请贷款（15分）
   - 7天内向≥2家申请（10分）
   - 申请材料存在明显矛盾（如地址不一致）（额外+8分）

4. 信用历史异常（10分）
   - 近30天征信查询次数≥5次（10分）
   - 有贷后失联历史记录（8分）
   - 存在多头借贷（≥3笔未结清）（6分）

**二、新挖掘特征（中级权重）**
1. 时序行为模式命中（12分）
   - 检测到集中申请模式：7天内≥3次申请动作
   - 非工作时间（20:00-08:00）频繁操作贷款相关事项
   - 贷款获取后立即变更联系方式

2. 关联网络高风险密度（10分）
   - 直接联系的高风险人员≥5人（10分）
   - 二级关联网络中高风险人员≥10人（8分）

3. 地域异常特征（8分）
   - 高频出现在贷款中介聚集区域
   - 活动轨迹与多个贷款机构位置高度重合

4. 设备指纹异常（10分）
   - 同一设备关联≥3个不同用户账号
   - 设备频繁更换网络环境/IP地址

### 【特征组合加成规则】

当以下特征组合同时命中时，增加额外分数：
1. 组合A（中介联系 + 背债关键词）：额外+10分
2. 组合B（异常申请 + 时序模式）：额外+8分  
3. 组合C（3个及以上核心特征同时命中）：额外+15分
4. 组合D（已知特征 + 新特征同时命中）：额外+5分
5. 组合E（关联网络 + 地域异常）：额外+7分

### 【评分计算公式】
总评分 = Σ(单个特征权重分) + Σ(特征组合加成分)
- 上限：100分（超过100分按100分计）
- 下限：0分
- 特征组合加分不重复计算（取最高值）

### 【核心特征验证规则】（二次筛选）

**高风险判定必须同时满足两个条件：**
1. 风险评分 ≥ 80分（基础筛选）
2. 至少命中以下1个核心特征：
   - 核心特征1：与中介高频联系（≥3次/周） + 命中背债关键词
   - 核心特征2：时序行为模式命中（集中申请模式）
   - 核心特征3：3个及以上已知核心特征同时命中
   - 核心特征4：异常申请模式 + 信用历史异常

**注意：**
- 仅评分≥80分但未命中任何核心特征 → 不算高风险，属于"评分虚高"
- 命中核心特征但评分<80分 → 需人工复核

### 【用户数据输入】
请分析以下用户数据：

用户ID：{user_id}
用户名：{user_name}
通讯记录：{communication_records}
贷款申请记录：{loan_applications}
征信查询记录：{credit_inquiries}
地理位置数据：{location_data}
设备信息：{device_info}
关联网络数据：{network_data}
文本内容：{text_content}
.........


### 【输出格式要求】
请严格按照以下JSON格式输出：
```json
{
  "user_id": "输入的user_id",
  "user_name": "输入的user_name",
  "risk_score": 0-100的整数,
  
  "screening_results": {
    "phase1_score_based": {
      "threshold": 80,
      "is_passed": true/false,
      "reason": "评分≥80分/评分<80分"
    },
    "phase2_core_feature": {
      "required": "至少命中1个核心特征",
      "core_features_hit": [
        {
          "core_feature_name": "核心特征名称",
          "is_hit": true/false,
          "evidence": "命中证据"
        }
      ],
      "is_passed": true/false,
      "reason": "命中了X个核心特征/未命中核心特征"
    },
    "final_assessment": {
      "is_high_risk": true/false,
      "assessment": "职业背债人高风险/候选名单（评分虚高）/需人工复核/低风险",
      "reason": "同时满足两个条件/仅满足评分条件/仅满足核心特征条件/均不满足"
    }
  },
  
  "score_breakdown": {
    // 原有的分数拆解...
  },
  
  "risk_classification": {
    "level": "极高风险(90-100)/高风险(80-89)/中风险(50-79)/低风险(0-49)",
    "recommendation": "立即拦截/加强监控/定期观察/正常处理"
  }
}
        """

    def assess_risk(self, state: State) -> dict:
        prompt = self.prompt_template.format(text=state["text"])
        response = self.llm.invoke(prompt)
        return {"text": state["text"] + "risk_score", "response": response.content}