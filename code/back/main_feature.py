import os
import json
import os

from tool_chain.feature_mining import feature_mining
from tool_chain.state import State


def run_analysis(json_path: str):
    # --- 1. 读取 gxl.json 数据 ---
    try:
        data = json.loads(open(json_path, "r", encoding="utf-8").read())
        if isinstance(data, dict):
            # 优先取 high_distinctive_patterns，否则整个 dict 作为单元素列表
            user_records = data.get("high_distinctive_patterns", data)
            if not isinstance(user_records, list):
                user_records = [user_records]
        elif isinstance(data, list):
            user_records = data
        else:
            user_records = [data]
    except Exception as e:
        print(f"读取 {json_path} 失败: {e}")
        return

    # --- 2. 初始化 State ---
    state: State = {
        "data": user_records,
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

    # --- 3. 调用特征挖掘 ---
    print(f"正在分析 {len(state['data'])} 条模式/特征数据，生成特征...")
    miner = feature_mining()
    final_state = miner.mine_features(state)

    # --- 4. 输出结果 ---
    print("\n" + "=" * 30 + " 特征挖掘结果 " + "=" * 30)
    if final_state.get("new_feature"):
        print(final_state["new_feature"])
    else:
        print("未发现新特征或模型未返回结果。")
    print("=" * 68)


if __name__ == "__main__":
    # 默认读取同目录下 gxl.json，可按需替换路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(BASE_DIR, "gxl.json")
    run_analysis(json_path)
