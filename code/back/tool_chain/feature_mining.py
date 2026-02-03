from __future__ import annotations

import json
from pathlib import Path

from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State


class feature_mining:
    """特征挖掘：基于高置信度模式 + 已知特征，生成量化风险特征。"""

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
你是风险特征挖掘专家。直接使用提供的高置信度模式与已知特征，产出可量化的新特征。

输入:
- high_confidence_patterns (JSON): {patterns}
- known_features: {known_features}
- case_data: {user_data}

要求:
1) 所有新特征必须基于 high_confidence_patterns（注明来源 pattern_number/片段）；可对已知特征做量化/拆分/组合，也可新增，但必须有模式支撑。
2) 特征需量化，给出具体阈值/区间，避免模糊表达；若数据不足用 "N/A" 并说明。
3) 每条特征字段: name, metric_def(计算逻辑/公式), threshold(数值或区间), data_source(字段/表/模式引用), linkage(关联的高置信度模式编号), risk_level(低/中/高), reason(≤80字), confidence(0-1)。
4) 输出 JSON，仅含 mined_features 数组，按风险或贡献度降序。
"""

    def mine_features(self, state: State) -> dict:
        # 加载高置信度模式
        patterns_path = Path(r"E:/bzr/Debtor/code/back/gxl.json")
        try:
            patterns_data = json.loads(patterns_path.read_text(encoding="utf-8"))
            patterns_payload = patterns_data.get("high_distinctive_patterns", patterns_data)
        except FileNotFoundError:
            patterns_payload = []
        except json.JSONDecodeError:
            patterns_payload = patterns_path.read_text(encoding="utf-8", errors="ignore")

        if isinstance(patterns_payload, (list, dict)):
            patterns_str = json.dumps(patterns_payload, ensure_ascii=False, indent=2)
        else:
            patterns_str = str(patterns_payload)

        known_features = [
            "离婚",
            "在网时间短",
            "大量负债",
            "近期多次查询贷款",
            "患有重大疾病",
            "收入与职业不符",
            "公积金账户异常",
            "社保评分低",
            "户籍地为高风险地区",
            "居住城市为高风险区",
            "学历低",
        ]
        known_features_str = "，".join(known_features)

        # 将 state.data 转为易读文本
        user_data_str = ""
        for i, d in enumerate(state.get("data", [])):
            user_data_str += f"用户{i + 1}: {d}\n"
        if not user_data_str:
            user_data_str = "无"

        prompt = self.prompt_template.format(
            patterns=patterns_str,
            known_features=known_features_str,
            user_data=user_data_str,
        )

        response = self.llm.invoke(prompt)

        # 解析 LLM 输出
        try:
            feature_result = json.loads(response.content)
            state["new_feature"] = json.dumps(feature_result, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            state["new_feature"] = response.content

        return state
