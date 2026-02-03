import json
import os

from tool_chain.rule_mining import rule_mining
from tool_chain.state import State


def run_analysis(gxl_path: str, feature_path: str):
    # --- 1. 读取模式库与已挖掘特征 ---
    def _read_json(path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.loads(f.read())
        except Exception as e:
            print(f"读取 {path} 失败: {e}")
            return default

    gxl_data = _read_json(gxl_path, [])
    patterns = gxl_data.get("high_distinctive_patterns", gxl_data) if isinstance(gxl_data, dict) else gxl_data

    feature_data = _read_json(feature_path, [])
    features = feature_data.get("mined_features", feature_data) if isinstance(feature_data, dict) else feature_data

    # --- 2. 初始化 State（无需用户 CSV，data 置空） ---
    state: State = {
        "data": [],
        "patterns": patterns,
        "features": features,
        "text": "",
        "new_feature": "",
        "new_rule": "",
        "feature": "",
        "feature_matching": "",
        "rule": "",
        "rule_matching": "",
        "report": "",
        "risk": "",
        "response": "",
    }

    # --- 3. 调用规则挖掘 ---
    print(
        f"正在结合 {len(patterns) if isinstance(patterns, list) else 1} 条模式 "
        f"和 {len(features) if isinstance(features, list) else 1} 条特征 生成规则..."
    )
    miner = rule_mining()
    final_state = miner.mine_rules(state)

    # --- 4. 输出规则结果 ---
    print("\n" + "=" * 30 + " 规则挖掘结果 " + "=" * 30)
    if final_state.get("new_rule"):
        print(final_state["new_rule"])
    else:
        print("未发现新规则或模型未返回结果。")
    print("=" * 68)


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    gxl_path = os.path.join(BASE_DIR, "gxl.json")
    feature_path = os.path.join(BASE_DIR, "feature.json")
    run_analysis(gxl_path, feature_path)
