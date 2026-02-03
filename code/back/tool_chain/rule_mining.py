import json
from pathlib import Path

from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State


class rule_mining:
    """
    Rule mining that leverages high-confidence patterns (gxl.json) and newly mined features
    (feature.json) to generate combined risk rules without changing outer code framework.
    """

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = """
你是“背债人”规则挖掘专家，需在保持现有代码框架下，结合高置信度模式与新挖掘特征生成可执行的判定规则。
输入:
- high_confidence_patterns (来自 gxl.json): {patterns}
- mined_features (来自 feature.json): {features}
- user_data (当前样本列表): {user_data}

约束:
1) 规则必须使用“特征组合”或“模式编号组合”，每条至少包含 2 个条件，禁止单个特征直接触发高风险。
2) 按风险降序输出：高风险(触发率>0.8)、中风险(0.5-0.8]、低风险(<0.5)，需给出触发率估计或来源说明。
3) 组合唯一：同一特征/模式组合不能出现在不同风险等级；如存在冲突需合并或取更高风险并说明处理。
4) 输出 JSON，字段: rule_name, logic_expression(AND/OR 组合，用特征名或模式号直写), risk_level("高"/"中"/"低"), trigger_rate(0-1), reasoning(≤80字), evidence(引用的 pattern_number/feature name), confidence(0.8-1.0)。
5) 若数据不足需在 reasoning 中说明“数据不足”并保持 JSON 合法。
"""

    def mine_rules(self, state: State):
        patterns_path = Path(r"E:/bzr/Debtor/code/back/gxl.json")
        features_path = Path(r"E:/bzr/Debtor/code/back/feature.json")

        def _load_high_conf_patterns():
            try:
                data = json.loads(patterns_path.read_text(encoding="utf-8"))
            except (FileNotFoundError, json.JSONDecodeError):
                return []

            raw_patterns = data.get("high_distinctive_patterns", data)
            if not isinstance(raw_patterns, list):
                return []

            high_conf = []
            for item in raw_patterns:
                if not isinstance(item, dict):
                    continue
                score = None
                val = item.get("value")
                if isinstance(val, str) and val.strip().endswith("%"):
                    try:
                        score = float(val.strip().rstrip("%"))
                    except ValueError:
                        score = None
                elif isinstance(val, (int, float)):
                    score = float(val) * 100 if val <= 1 else float(val)

                if score is None:
                    conf = item.get("confidence")
                    if isinstance(conf, (int, float)):
                        score = float(conf) * 100 if conf <= 1 else float(conf)

                if score is None or score >= 80:
                    high_conf.append(item)

            return high_conf or raw_patterns

        def _load_mined_features():
            try:
                data = json.loads(features_path.read_text(encoding="utf-8"))
                mined = data.get("mined_features", data)
                return mined if isinstance(mined, list) else []
            except (FileNotFoundError, json.JSONDecodeError):
                return []

        patterns_payload = _load_high_conf_patterns()
        features_payload = _load_mined_features()

        patterns_str = (
            json.dumps(patterns_payload, ensure_ascii=False, indent=2)
            if isinstance(patterns_payload, (list, dict))
            else "[]"
        )
        features_str = (
            json.dumps(features_payload, ensure_ascii=False, indent=2)
            if isinstance(features_payload, (list, dict))
            else "[]"
        )

        # 将 List[Dict] 转成可读文本
        user_data_str = ""
        for i, d in enumerate(state.get("data", [])):
            user_data_str += f"用户{i+1}: {str(d)}\n"
        if not user_data_str:
            user_data_str = "无"

        # 调用大模型
        prompt = (
            self.prompt_template.replace("{patterns}", patterns_str)
            .replace("{features}", features_str)
            .replace("{user_data}", user_data_str)
        )
        response = self.llm.invoke(prompt)

        # 结果写回 state
        try:
            parsed = json.loads(response.content)
            state["new_rule"] = json.dumps(parsed, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            state["new_rule"] = response.content
        return state
