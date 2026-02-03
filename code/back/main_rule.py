import os
import pandas as pd

from tool_chain.rule_mining import rule_mining  # 保持类名与文件名一致
from tool_chain.state import State


def run_analysis(file_path: str):
    # --- 1. 读取 CSV 数据 ---
    try:
        # 优先 UTF-8，失败回退 GBK；保留原有架构，仅增强健壮性
        try:
            df = pd.read_csv(file_path, nrows=50, dtype=str, encoding="utf-8-sig")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, nrows=50, dtype=str, encoding="gbk")

        # 填充缺失，避免 LLM 处理异常
        df = df.fillna("")
        user_records = df.to_dict(orient="records")
    except Exception as e:
        print(f"读取 CSV 失败: {e}")
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

    # --- 3. 调用规则挖掘 ---
    print(f"正在分析 {len(state['data'])} 条用户数据，生成背债人规则...")
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
    # 默认读取同目录下 1.csv，可根据需要替换路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "1.csv")
    run_analysis(csv_path)
