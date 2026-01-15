import pandas as pd
import os
from tool_chain.state import State
from tool_chain.rule_mining import rule_mining  # 确保你的类名和文件名正确
from tool_chain.feature_mining import feature_mining

def run_analysis(file_path: str):
    # --- 1. 读取 CSV 数据 ---
    try:
        # 只读取前 n 条，dtype=str 避免长数字被截断
        df = pd.read_csv(
            file_path,
            nrows=50,
            dtype=str,
            encoding="gbk"
        )
        
        # 将空值填充为空字符串，防止 LLM 处理时报错
        df = df.fillna("")
        
        # 转换为 List[Dict] 格式
        # 结果示例: [{"姓名": "张三", "身份证号": "..."}, {...}]
        user_records = df.to_dict(orient='records')
        
    except Exception as e:
        print(f"读取 CSV 文件失败: {e}")
        return

    # --- 2. 初始化 State ---
    # 按照你定义的 State 结构进行完整初始化
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
        "response": ""
    }

    # --- 3. 调用大模型分析节点 ---
    print(f"正在分析 {len(state['data'])} 条用户数据，寻找隐藏的‘背债人’特征规则...")
    
    miner = rule_mining()
    final_state = miner.mine_rules(state)

    # --- 4. 输出挖掘出的新规则 ---
    print("\n" + "="*30 + " 挖掘结果 " + "="*30)
    if final_state["new_rule"]:
        print(final_state["new_rule"])
    else:
        print("未发现显著新特征或模型未返回结果。")
    print("="*68)


if __name__ == "__main__":
    # 指定你的文件名 1.csv
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "1.csv")
    run_analysis(csv_path)