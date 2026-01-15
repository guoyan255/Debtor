from risk_graph import risk_graph
from tool_chain.state import State
import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


graph = risk_graph()

workflow = graph.get_graph()

app = workflow.compile()

initial_state = {
        "data": [],
        "analysis_data": "",
        "text": "",
        "new_feature": "",
        "new_rule": "",
        "feature": "",
        "feature_matching": "",
        "rule": "",
        "rule_matching": "",
        "report": "",
        "risk": "",
        "response": "开始启动风控流水线..."
    }

final_state = app.invoke(initial_state)


# 打印输出结果
print("\n" + "="*30 + " 任务执行结果 " + "="*30)
    
print("\n【1. 最终风险报告 (Report)】")
print(final_state.get("report", "未生成报告"))

print("\n【2. 风险评分原因 (Risk)】")
print(final_state.get("risk", "未生成评分"))

print("\n【3. 系统执行日志 (Response)】")
print(final_state.get("response", "无响应信息"))
    
print("\n" + "="*74)

try:
    # 强制让 Python 认为程序已经结束，不再打印后续的垃圾回收错误
    os._exit(0) 
except:
    pass