"""
Quick test runner for the full pipeline:
data_loader -> data_processing -> case_template_formatter.

Usage:
    python Debtor/code/back/main_case_formatter.py

Requirements:
    - 2.csv present under Debtor/code/back/
    - DeepSeek env vars configured for case_template_formatter to call LLM.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import pandas as pd

# Ensure sibling modules are importable when running as a script
_CUR_DIR = Path(__file__).resolve().parent
_BACK_DIR = _CUR_DIR.parent
if str(_BACK_DIR) not in sys.path:
    sys.path.insert(0, str(_BACK_DIR))

from tool_chain.data_loader import data_loader, DEFAULT_COLUMNS
from tool_chain.data_processing import data_processing
from tool_chain.case_formatter import case_template_formatter
from tool_chain.state import State


def _resolve_csv(path_str: str) -> Path:
    """Resolve CSV path: absolute else script dir else parent dir."""
    p = Path(path_str)
    candidates = [p] if p.is_absolute() else [
        (_CUR_DIR / path_str).resolve(),
        (_BACK_DIR / path_str).resolve(),
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(f"CSV 不存在，尝试过: {', '.join(str(c) for c in candidates)}")


def _read_all_rows(file_path: str, has_header: bool) -> List[dict]:
    """Read the whole CSV into a list of dicts."""
    csv_path = _resolve_csv(file_path)
    enc_opts = [("utf-8", None), ("gbk", "ignore")]
    last_err = None
    for enc, enc_err in enc_opts:
        try:
            df = pd.read_csv(
                csv_path,
                dtype=str,
                encoding=enc,
                encoding_errors=enc_err,
                on_bad_lines="warn",
                engine="python",
                header=0 if has_header else None,
            )
            if not has_header:
                cols = DEFAULT_COLUMNS[: len(df.columns)]
                df.columns = cols
            return df.fillna("").to_dict(orient="records")
        except UnicodeDecodeError as e:
            last_err = e
            continue
    raise last_err or UnicodeDecodeError("utf-8/gbk", b"", 0, 0, "无法解码 CSV")


def run_pipeline(file_name: str = "2.csv", case_id_prefix: str = "case", has_header: bool = False) -> List[State]:
    """只处理首行，生成单个 case_profile；默认 CSV 无表头。"""
    rows = _read_all_rows(file_name, has_header=has_header)
    if not rows:
        return []
    row = rows[0]

    processor = data_processing()
    formatter = case_template_formatter()

    state: State = {
        "data": [row],
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
    processed = processor.process_data(state)
    case_id = f"{case_id_prefix}_0001"
    formatted = formatter.format_from_processed(processed, case_id=case_id)
    return [formatted]


def main() -> None:
    results = run_pipeline(has_header=False)  # 默认无表头；如有表头改为 True
    if not results:
        print("未读取到数据行")
        return
    for st in results:
        print("--- CASE PROFILE ---")
        print(st.get("case_profile", "未生成案例画像"))
        print("\n--- PIPELINE STATUS ---")
        print(st.get("response", ""))
        print("\n========================\n")


if __name__ == "__main__":
    main()
