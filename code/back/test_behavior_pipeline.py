"""
Simple CLI to run the behavior pipeline.
Supports two modes:
  - stream (default): read CSV row by row, emit one JSON line per row
  - batch: keep previous one-shot behavior (single summary)

Pipeline steps: data_loader -> data_processing -> case_template_formatter -> behavior_association_matching

Example:
    python Debtor/code/back/test_behavior_pipeline.py --file 2.csv --mode stream --limit 3
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Iterator
from datetime import datetime
import time

_CUR_DIR = Path(__file__).resolve().parent
_BACK_DIR = _CUR_DIR.parent
if str(_BACK_DIR) not in sys.path:
    sys.path.insert(0, str(_BACK_DIR))

from tool_chain.data_loader import data_loader
from tool_chain.data_processing import data_processing
from tool_chain.case_formatter import case_template_formatter
from tool_chain.behavior_association_matching import behavior_association_matching
from tool_chain.state import State


def _initial_state() -> State:
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


def run_pipeline(
    file_path: str = "2.csv",
    has_header: bool = False,
    case_id: str = "case_test_0001",
) -> Dict:
    state: State = _initial_state()

    loader = data_loader(file_path=file_path, has_header=has_header)
    state = loader.load_data(state)

    processor = data_processing()
    state = processor.process_data(state)

    formatter = case_template_formatter()
    state = formatter.format_from_processed(state, case_id=case_id)

    matcher = behavior_association_matching()
    state = matcher.analyze(state, case_id=case_id)

    return state


def stream_pipeline(
    file_path: str = "2.csv",
    has_header: bool = False,
    case_prefix: str = "case_stream",
    start_index: int = 1,
    limit: int | None = None,
) -> Iterator[Dict]:
    """
    Iterate CSV rows, processing each independently.
    """
    base_state: State = _initial_state()
    loader = data_loader(file_path=file_path, has_header=has_header)
    loaded = loader.load_data(base_state)
    rows = loaded.get("data", [])

    processor = data_processing()
    formatter = case_template_formatter()
    matcher = behavior_association_matching()

    for idx, row in enumerate(rows, start=start_index):
        if limit is not None and idx - start_index >= limit:
            break

        start_ts = time.perf_counter()

        state = _initial_state()
        state["analysis_data"] = loaded.get("analysis_data", "")
        state["data"] = [row]
        state["response"] = loaded.get("response", "")

        case_id = f"{case_prefix}_{idx:04d}"
        state = processor.process_data(state)
        state = formatter.format_from_processed(state, case_id=case_id)
        state = matcher.analyze(state, case_id=case_id)

        elapsed = round(time.perf_counter() - start_ts, 3)
        finished_at = datetime.now().isoformat(timespec="seconds")

        yield {
            "case_id": case_id,
            "behavior_tags": state.get("behavior_tags"),
            "association_tags": state.get("association_tags"),
            "temporal_tags": state.get("temporal_tags"),
            "rationality_tags": state.get("rationality_tags"),
            "elapsed_seconds": elapsed,
            "finished_at": finished_at,
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run behavior pipeline in stream (default) or batch mode."
    )
    parser.add_argument("--file", default="2.csv", help="CSV path (relative to back/ by default)")
    parser.add_argument("--has-header", action="store_true", help="CSV has header row")
    parser.add_argument("--case-id", default="case_test_0001", help="Case ID prefix")
    parser.add_argument(
        "--mode",
        choices=["stream", "batch"],
        default="stream",
        help="stream: per-row output; batch: single aggregated run",
    )
    parser.add_argument("--limit", type=int, default=None, help="Max rows to process (stream mode)")
    parser.add_argument("--offset", type=int, default=0, help="Skip first N rows before processing")
    args = parser.parse_args()

    file_path = args.file
    if not Path(file_path).exists():
        candidate = _BACK_DIR.parent / args.file
        if candidate.exists():
            file_path = str(candidate)

    if args.mode == "stream":
        for summary in stream_pipeline(
            file_path=file_path,
            has_header=args.has_header,
            case_prefix=args.case_id,
            start_index=args.offset + 1,
            limit=args.limit,
        ):
            print(json.dumps(summary, ensure_ascii=False), flush=True)
    else:
        state = run_pipeline(file_path=file_path, has_header=args.has_header, case_id=args.case_id)
        summary = {
            "behavior_tags": state.get("behavior_tags"),
            "association_tags": state.get("association_tags"),
            "temporal_tags": state.get("temporal_tags"),
            "rationality_tags": state.get("rationality_tags"),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
