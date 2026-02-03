from __future__ import annotations

"""
pattern_mining.py

让 LLM 直接读取 behavior_association_matching 的标签结果（JSON / JSONL），
由 LLM 计算出现率、共现率、时序、合理性贡献，输出高区分度模式。
CLI:
    python Debtor/code/back/tool_chain/pattern_mining.py --input results.jsonl --top 20
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

_CUR_DIR = Path(__file__).resolve().parent
_BACK_DIR = _CUR_DIR.parent
if str(_BACK_DIR) not in sys.path:
    sys.path.insert(0, str(_BACK_DIR))

from model_components.deepseek_model import DeepSeekLLM


class pattern_mining:
    """模式挖掘主类：封装数据读取与 LLM 调用。"""

    def __init__(self):
        self.llm = DeepSeekLLM().llm

    # ---------- 数据准备 ---------- #
    def load_cases(self, path: Path) -> List[Dict]:
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

    # ---------- LLM 提示词 ---------- #
    @staticmethod
    def build_llm_prompt(cases: List[Dict], top_n: int) -> str:
        cases_json = json.dumps(cases, ensure_ascii=False, indent=2)
        return f"""
你是模式挖掘分析师。以下是多条 behavior_association_matching 的标签结果（JSON 数组）。
请你基于这些原始标签自行计算并挖掘：
- 你要对行为标签、时序标签、合理性标签的各种组合进行计算，分别得到这些组合的共现率。
- 合理性倾向（合理/不合理的占比或显著模式）。
- 标签共现模式：同时出现且与背债行为强相关的标签组合 (共现率≥70%)
- 时序依赖模式：背债人群中高频出现的行为时序链 (出现率≥60%)
- 合理性异常模式：合理性标签中 "不合理" 项的高频组合 (出现率≥50%)


输出要求：
- 仅依据输入数据计算，不要虚构数字；
- 在标签共现模式中只输出共现率>=70%的数据；在时序依赖模式中只输出出现率>=60%的数据；在合理性异常模式中只输出出现率>=50%的数据；
- 输出 JSON，字段 high_distinctive_patterns（数组）；
- 每个元素字段：pattern_number（标签共现模式从M001开始，时序依赖模式从T001开始，合理性异常模式从R001开始）、type(标签共现模式|时序依赖模式|合理性异常模式)、pattern(字符串或字符串数组)、value(数值或"N/A")、evidence(简述计算依据，如 "12/50 cases = 24%")、reason(≤80字解释为何高区分度/高贡献率)；
- 每类最多保留 Top {top_n}，按数值降序；
- 数据不足时 value 用 "N/A"，reason 说明原因。
- 最后总结输出由以上分析得到的核心结论、隐藏逻辑、未覆盖领域。

输入数据 cases:
{cases_json}
"""

    # ---------- 模式挖掘 ---------- #
    def mine(self, cases: List[Dict], top_n: int = 20) -> Dict:
        prompt = self.build_llm_prompt(cases, top_n)
        resp = self.llm.invoke(prompt)
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


# ------- 模块级便捷函数 ------- #
def load_cases(path: Path) -> List[Dict]:
    return pattern_mining().load_cases(path)


def run_mining(cases: List[Dict], top_n: int = 20) -> Dict:
    return pattern_mining().mine(cases, top_n=top_n)


# ------- CLI ------- #
def main():
    parser = argparse.ArgumentParser(description="挖掘高区分度标签模式（出现率/共现/时序/合理性）")
    parser.add_argument("--input", required=True, help="behavior_association_matching 的 JSON/JSONL 结果文件")
    parser.add_argument("--top", type=int, default=20, help="每类统计保留 TopN")
    args = parser.parse_args()

    in_path = Path(args.input)
    miner = pattern_mining()
    if in_path.suffix.lower() == ".json":
        try:
            data = json.loads(in_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                cases = data
            else:
                raise ValueError("JSON 文件必须是列表，每个元素为一条带标签的 case")
        except json.JSONDecodeError:
            cases = miner.load_cases(in_path)
    else:
        cases = miner.load_cases(in_path)

    result = miner.mine(cases, top_n=args.top)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
