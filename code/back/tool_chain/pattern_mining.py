"""
pattern_mining.py

给定 behavior_association_matching 的 JSONL 结果，统计共现 / 排他 / 时序 / 合理性模式，
并调用大模型挑选“背债人群独有”的高区分度模式。

使用方法：
    python Debtor/code/back/tool_chain/pattern_mining.py --input results.jsonl --top 20

说明：
    - 输入文件为 JSON Lines，每行至少包含:
        case_id, behavior_tags, association_tags, temporal_tags, rationality_tags
      其中 behavior_tags 为对象数组，字段含 tag；association_tags 含 tags(list)；
      temporal_tags 含 tags(list)；rationality_tags 含 tag。
    - 脚本先做简单统计（频次、共现率、排他率），再把摘要交给 DeepSeek LLM，
      让模型根据阈值：共现>70%，时序>60%，排他>50%，合理性异常>50%，筛选高区分度模式。
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

# ensure back/ parent is on sys.path for model_components import
_CUR_DIR = Path(__file__).resolve().parent
_BACK_DIR = _CUR_DIR.parent
if str(_BACK_DIR) not in sys.path:
    sys.path.insert(0, str(_BACK_DIR))

from model_components.deepseek_model import DeepSeekLLM


def load_cases(path: Path) -> List[Dict]:
    cases: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return cases


def extract_tags(case: Dict) -> Dict[str, List[str]]:
    behaviors = [t.get("tag") for t in case.get("behavior_tags", []) if t.get("tag")]
    associations: List[str] = []
    for a in case.get("association_tags", []):
        tags = a.get("tags") or []
        associations.extend([t for t in tags if t])
    temporals: List[str] = []
    for t in case.get("temporal_tags", []):
        tags = t.get("tags") or []
        temporals.extend([v for v in tags if v])
    rationalities = [t.get("tag") for t in case.get("rationality_tags", []) if t.get("tag")]
    return {
        "behavior": behaviors,
        "association": associations,
        "temporal": temporals,
        "rationality": rationalities,
    }


def compute_stats(cases: List[Dict]):
    total = len(cases)
    counts = {
        "behavior": Counter(),
        "association": Counter(),
        "temporal": Counter(),
        "rationality": Counter(),
    }
    co_counts = Counter()

    for case in cases:
        tags = extract_tags(case)
        # 单项频次
        for k, vs in tags.items():
            counts[k].update(set(vs))  # 去重防止同一case重复计数

        # 共现：跨所有类别的标签并集
        flat = set(tags["behavior"] + tags["association"] + tags["temporal"] + tags["rationality"])
        for a, b in combinations(sorted(flat), 2):
            co_counts[(a, b)] += 1

    def rate(c):
        return c / total * 100 if total else 0

    co_rates = {pair: rate(c) for pair, c in co_counts.items()}

    return total, counts, co_rates


def build_llm_prompt(total, counts, co_rates, top_n: int) -> str:
    def top_dict(d: Dict[Tuple[str, str], float], threshold: float):
        return [
            {"pair": list(k), "co_rate": round(v, 2)}
            for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True)
            if v >= threshold
        ][:top_n]

    payload = {
        "total_cases": total,
        "top_behavior": counts["behavior"].most_common(top_n),
        "top_association": counts["association"].most_common(top_n),
        "top_temporal": counts["temporal"].most_common(top_n),
        "top_rationality": counts["rationality"].most_common(top_n),
        "co_occurrence_candidates": top_dict(co_rates, 70.0),
        "temporal_candidates": top_dict(co_rates, 60.0),
    }

    prompt = f"""
你是银行风控模式挖掘专家。根据“统计摘要”筛选并输出【背债人群独有的高区分度模式】。

务必注意：
1) 只使用摘要里出现的标签；同义标签需要先合并再输出（同类、同含义视为同一标签）。
2) 各模式阈值不可更改：
   - 标签共现模式：同时出现且与背债行为强相关的behavior_tags，要求共现率 > 70%
   - 时序依赖模式：背债人案例中高频出现的temporal_tags，共现率 > 60%，并明确事件先后/因果
   - 合理性异常模式：案例中高频出现的rationality tag组合，出现率或共现率 > 50%
3) 避免重复：若模式含义重复或是子集，保留最具概括力的一条。

输出格式（仅 JSON，无额外文本）：
{{
  "high_distinctive_patterns": [
    {{
      "type": "标签共现|时序依赖|合理性异常",
      "pattern": ["标签A", "标签B", "..."],
      "metric": "共现率|出现率|出现率",
      "value": "数字（如 78.5）",
      "evidence": ["简要统计依据，引用摘要中的数值/排名"],
      "reason": "为何能区分背债人群（<=80字）"
    }}
  ]
}}

统计摘要(JSON)：{json.dumps(payload, ensure_ascii=False, indent=2)}
"""
    return prompt


def run_mining(cases: List[Dict], top_n: int = 20) -> Dict:
    total, counts, co_rates = compute_stats(cases)
    prompt = build_llm_prompt(total, counts, co_rates, top_n)
    llm = DeepSeekLLM().llm
    resp = llm.invoke(prompt)
    content = resp.content.strip()
    # best-effort JSON parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        try:
            start = content.find("{")
            end = content.rfind("}")
            return json.loads(content[start : end + 1])
        except Exception:
            return {"high_distinctive_patterns": [], "raw_output": content}


def main():
    parser = argparse.ArgumentParser(description="挖掘高区分度标签模式（共现/时序/排他/合理性）")
    parser.add_argument("--input", required=True, help="behavior_association_matching 的 JSONL 结果文件")
    parser.add_argument("--top", type=int, default=20, help="每类统计保留 TopN")
    args = parser.parse_args()

    in_path = Path(args.input)
    cases = load_cases(in_path)
    result = run_mining(cases, top_n=args.top)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
