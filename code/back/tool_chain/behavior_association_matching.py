from __future__ import annotations

"""
Match behavior / association / temporal / rationality tags based on processed data and case_profile.
Relies on DeepSeek LLM.
"""

import json
from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State


class behavior_association_matching:
    """
    Consume cleaned data + case profile, ask LLM to output structured tags.
    """

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = r"""
你是风控分析师。根据【标注化用户数据 JSON】与【案例画像文本】，输出 4 类标签：
- behavior_tags 行为标签
- association_tags 关联标签（标签组合）
- temporal_tags 时序标签（体现事件先后/演进）
- rationality_tags 合理性标签（指出数据/行为是否合理及原因）

输出要求：
- 只输出 JSON，无多余文字，UTF-8。
- 每个标签项都需 evidence（字段=值或片段）、reason（≤80字）、confidence（高/中/低）。
- 若某类无结果，给空数组。

输出格式：
{{
  "case_id": "{case_id}",
  "behavior_tags": [
    {{
      "tag": "行为标签名称",
      "evidence": ["字段=值", "..."],
      "reason": "简述判断依据",
      "confidence": "高"
    }}
  ],
  "association_tags": [
    {{
      "tags": ["标签A", "标签B"],
      "evidence": ["字段=值", "..."],
      "reason": "组合逻辑",
      "confidence": "中"
    }}
  ],
  "temporal_tags": [
    {{
      "tags": ["事件1", "事件2", "事件3"],
      "evidence": ["字段=值", "..."],
      "reason": "时间顺序或演进说明",
      "confidence": "中"
    }}
  ],
  "rationality_tags": [
    {{
      "tag": "合理性标签名称",
      "evidence": ["字段=值", "..."],
      "reason": "哪里合理/不合理",
      "confidence": "中"
    }}
  ],
  "missing_evidence": ["缺失但重要的字段，可为空数组"]
}}

素材1: 【标注化用户数据 JSON】
{data_json}

素材2: 【案例画像文本】
        {case_profile}
"""

    def analyze(self, state: State, case_id: str = "case_0001") -> State:
        data_json = json.dumps(state.get("data", []), ensure_ascii=False, indent=2)
        case_profile = state.get("case_profile", "")

        prompt = self.prompt_template.format(
            case_id=case_id,
            data_json=data_json,
            case_profile=case_profile,
        )

        content = ""
        if hasattr(self.llm, "stream"):
            try:
                chunks = []
                for chunk in self.llm.stream(prompt):
                    text = getattr(chunk, "content", "") or str(chunk)
                    print(text, end="", flush=True)
                    chunks.append(text)
                print()  # 换行，保证控制台可读
                content = "".join(chunks)
            except Exception:
                response = self.llm.invoke(prompt)
                content = response.content
        else:
            response = self.llm.invoke(prompt)
            content = response.content

        def _strip_code_fence(text: str) -> str:
            t = text.strip()
            if t.startswith("```"):
                lines = t.splitlines()
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                t = "\n".join(lines)
            return t

        def _extract_first_json(text: str):
            """Try to extract the first valid JSON object from messy LLM output."""
            for candidate in (text, _strip_code_fence(text)):
                candidate = candidate.strip()
                # fast path: whole text is json
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass
                # try to find the first {...} block
                start = candidate.find("{")
                end = candidate.rfind("}")
                if start != -1 and end != -1 and end > start:
                    sub = candidate[start : end + 1]
                    try:
                        return json.loads(sub)
                    except json.JSONDecodeError:
                        continue
            return None

        parsed = _extract_first_json(content)

        if parsed is not None:
            state["behavior_tags"] = parsed.get("behavior_tags", [])
            state["association_tags"] = parsed.get("association_tags", [])
            state["temporal_tags"] = parsed.get("temporal_tags", [])
            state["rationality_tags"] = parsed.get("rationality_tags", [])
            state["missing_evidence"] = parsed.get("missing_evidence", [])
            state["behavior_matching_raw"] = parsed
            state["behavior_matching_status"] = "parsed_ok"
        else:
            state["behavior_tags"] = []
            state["association_tags"] = []
            state["temporal_tags"] = []
            state["rationality_tags"] = []
            state["missing_evidence"] = []
            state["behavior_matching_raw"] = content
            state["behavior_matching_status"] = "parse_failed"

        state["response"] = (
            state.get("response", "")
            + "完成behavior_association_matching("
            + state["behavior_matching_status"]
            + ")"
        )
        return state


def _demo():
    demo_state: State = {
        "data": [{"示例字段": "示例值"}],
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
        "case_profile": "案例ID: demo\n---\n- 示例字段=示例值",
        "response": "",
    }
    matcher = behavior_association_matching()
    result = matcher.analyze(demo_state, case_id="demo_case_0001")
    print(json.dumps(result.get("behavior_matching_raw", {}), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _demo()
