from typing import Dict, List
from typing_extensions import TypedDict


class State(TypedDict):
    
    data: List[Dict]  #输入数据
    analysis_data: str #要分析的用户数据
    text: str #处理后的数据
    new_feature: str #新特征
    new_rule: str #新规则
    feature: str #匹配到的相关特征特征
    feature_matching: str #特征匹配结果
    rule : str #检索出的相关规则
    rule_matching : str #规则匹配结果
    report: str #风险报告
    risk: str #风险评分
    case_profile: str
    response: str #回答
    behavior_tags: List[Dict]  # 行为标签
    association_tags: List[Dict]  # 关联标签
    temporal_tags: List[Dict]  # 时间序标签
    rationality_tags: List[Dict]  # 合理性标签
    missing_evidence: List[str]  # 缺失字段
    behavior_matching_raw: Dict | str  # LLM 原始输出或解析后的对象
    pattern_mining: Dict  # 模式挖掘结果
