"""
简单可执行的流水线测试脚本，验证：
data_loader -> data_processing -> case_template_formatter -> behavior_association_matching
按顺序运行，并打印最终的行为/关联标签输出。

运行示例（默认读取 back/2.csv，文件无表头时按 DEFAULT_COLUMNS 映射）：
    python Debtor/code/back/tool_chain/test_behavior_pipeline.py

默认直接使用 DeepSeek，与其他工具保持一致（需正确配置 DEEPSEEK_KEY / DEEPSEEK_URL）。
"""

import json
import sys
from pathlib import Path
from typing import Dict

# 便于脚本直接运行找到同级模块
_CUR_DIR = Path(__file__).resolve().parent
_BACK_DIR = _CUR_DIR.parent
if str(_BACK_DIR) not in sys.path:
    sys.path.insert(0, str(_BACK_DIR))

# ---------------- 导入组件 ---------------- #
from tool_chain.data_loader import data_loader
from tool_chain.data_processing import data_processing
from tool_chain.case_formatter import case_template_formatter
from tool_chain.behavior_association_matching import behavior_association_matching
from tool_chain.state import State


def _initial_state() -> State:
    # 依据 State 类型补全默认字段
    return {
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
        "case_profile": "",
        "response": "",
    }


def run_pipeline(file_path: str = "2.csv", has_header: bool = False, case_id: str = "case_test_0001") -> Dict:
    state: State = _initial_state()

    # 1) 数据加载
    loader = data_loader(file_path=file_path, has_header=has_header)
    state = loader.load_data(state)

    # 2) 数据清洗
    processor = data_processing()
    state = processor.process_data(state)

    # 3) 案例画像生成
    formatter = case_template_formatter()
    state = formatter.format_from_processed(state, case_id=case_id)

    # 4) 行为/关联标签挖掘
    matcher = behavior_association_matching()
    state = matcher.analyze(state, case_id=case_id)

    return state


def main():
    import argparse

    parser = argparse.ArgumentParser(description="测试背债人行为/关联标签流水线")
    parser.add_argument("--file", default="2.csv", help="待处理 CSV 路径（相对 back/）")
    parser.add_argument("--has-header", action="store_true", help="CSV 是否包含表头")
    parser.add_argument("--case-id", default="case_test_0001", help="案例 ID")
    args = parser.parse_args()

    # 解析文件真实路径（默认与 back 同级）
    file_path = args.file
    if not Path(file_path).exists():
        candidate = _BACK_DIR.parent / args.file
        if candidate.exists():
            file_path = str(candidate)

    state = run_pipeline(file_path=file_path, has_header=args.has_header, case_id=args.case_id)

    summary = {
        "response_chain": state.get("response", ""),
        "behavior_tags": state.get("behavior_tags"),
        "association_tags": state.get("association_tags"),
        "raw_output": state.get("behavior_matching_raw"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
