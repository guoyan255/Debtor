"""
简单测试脚本：读取 bq.json（预处理好的标签 JSONL/JSON 文件），调用 pattern_mining 运行并打印结果。

用法：
    python Debtor/code/back/tool_chain/test_pattern_mining.py --input bq.json --top 20
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_CUR_DIR = Path(__file__).resolve().parent
_BACK_DIR = _CUR_DIR.parent
if str(_BACK_DIR) not in sys.path:
    sys.path.insert(0, str(_BACK_DIR))

from pattern_mining import run_mining, load_cases


def main():
    parser = argparse.ArgumentParser(description="Test pattern_mining with prepared tag file")
    parser.add_argument(
        "--input",
        default="../bq.json",
        help="标签文件，支持 JSONL 或单一 JSON 数组，默认路径 code/back/bq.json",
    )
    parser.add_argument("--top", type=int, default=20, help="每类统计保留 TopN")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.is_absolute():
        in_path = (_CUR_DIR / in_path).resolve()
    if not in_path.exists():
        raise FileNotFoundError(f"未找到输入文件: {in_path}")

    # 兼容单一 JSON 数组与 JSONL
    if in_path.suffix.lower() == ".json":
        try:
            data = json.loads(in_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                cases = data
            else:
                raise ValueError("JSON 文件必须是列表，每个元素为一条案例标签结果")
        except json.JSONDecodeError:
            # 若 json 失败则按 jsonl 读
            cases = load_cases(in_path)
    else:
        cases = load_cases(in_path)

    result = run_mining(cases, top_n=args.top)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
