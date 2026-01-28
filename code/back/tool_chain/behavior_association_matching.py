from __future__ import annotations

"""
基于 case_formatter 输出与标准化 JSON，匹配预定义“行为标签”和“关联标签”，不做自由挖掘。
行为标签列表（固定）：
1. 异地贷款
2. 近期多机构查询贷款
3. 婚姻状况异常（10/30/40/91/99 均为异常码）
4. 近期贷款通过率低
5. 近期新增贷款
6. 近期负债增长
7. 居住地变更频繁
8. 使用境外ip
9. 公司变更频繁
10. 学历低
11. 患有重大疾病
12. 近期逾期频繁
13. 异地户籍
14. 公积金状态异常
15. 职业与收入不符
16. 职业与贷款额度不符
17. 征信评分低

关联标签列表（固定）：
1. 公积金未缴纳 + 贷款次数多
2. 学历低 + 高负债
3. 在网时间短 + 近期多次查询
4. 重大疾病 + 房贷或者车贷
5. 离婚 + 多次申请贷款
"""

import json
from typing import List, Dict


from model_components.deepseek_model import DeepSeekLLM
from tool_chain.state import State


class behavior_association_matching:
    """
    将输入数据与画像文本对照固定标签进行匹配；禁止生成列表外标签。
    """

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.prompt_template = r"""
你是一名银行信贷风控分析师，任务是匹配下列“行为标签”和“关联标签”。
仅可从给定标签中选择，禁止新造标签；必须基于【标准化用户数据 JSON】与【案例画像文本】的明确证据。

行为标签（逐一判定，可多选）：
1. 异地贷款
2. 近期多机构查询贷款
3. 婚姻状况异常（婚姻码 10/30/40/91/99 视为异常）
4. 近期贷款通过率低
5. 近期新增贷款
6. 近期负债增长
7. 居住地变更频繁
8. 使用境外ip
9. 公司变更频繁
10. 学历低
11. 患有重大疾病
12. 近期逾期频繁
13. 异地户籍
14. 公积金状态异常
15. 职业与收入不符
16. 职业与贷款额度不符
17. 征信评分低

关联标签（仅可从下列组合中选择）：
1. 公积金未缴纳 + 贷款次数多
2. 学历低 + 高负债
3. 在网时间短 + 近期多次查询
4. 重大疾病 + 房贷或者车贷
5. 离婚 + 多次申请贷款

输出要求：
- 仅输出 JSON，无额外文字。
- 未找到证据的标签不要输出；证据不足可以给出但 confidence 填 “低”，reason 必须写明缺失字段。
- 每个标签附带 evidence（字段=值或画像片段），reason（≤80 字说明判定依据），confidence（高/中/低）。

输出格式：
{{
  "case_id": "{case_id}",
  "behavior_tags": [
    {{
      "tag": "行为标签名称",
      "evidence": ["字段=值或画像片段", "..."],
      "reason": "简短理由",
      "confidence": "高/中/低"
    }}
  ],
  "association_tags": [
    {{
      "tags": ["标签A", "标签B"],
      "evidence": ["字段=值或画像片段", "..."],
      "reason": "组合逻辑",
      "confidence": "高/中/低"
    }}
  ],
  "missing_evidence": ["缺失但重要的字段或描述，可为空数组"]
}}

素材 1：【标准化用户数据 JSON】
{data_json}

素材 2：【案例画像文本】
{case_profile}
"""

    def analyze(self, state: State, case_id: str = "case_0001") -> State:
        """
        基于 state 中的清洗数据与 case_profile，输出匹配结果。
        结果写回：
            state["behavior_tags"], state["association_tags"], state["behavior_matching_raw"]
            state["response"] 追加执行痕迹。
        """
        data_json = json.dumps(state.get("data", []), ensure_ascii=False, indent=2)
        case_profile = state.get("case_profile", "")

        prompt = self.prompt_template.format(
            case_id=case_id,
            data_json=data_json,
            case_profile=case_profile,
        )

        response = self.llm.invoke(prompt)
        content = response.content

        def _strip_code_fence(text: str) -> str:
            t = text.strip()
            if t.startswith("```"):
                # remove first line fence and possible language hint
                lines = t.splitlines()
                if len(lines) >= 2 and lines[0].startswith("```"):
                    lines = lines[1:]
                # drop trailing fence
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                t = "\n".join(lines)
            return t

        parsed = None
        for candidate in (content, _strip_code_fence(content)):
            try:
                parsed = json.loads(candidate)
                break
            except json.JSONDecodeError:
                continue

        if parsed is not None:
            state["behavior_tags"] = parsed.get("behavior_tags", [])
            state["association_tags"] = parsed.get("association_tags", [])
            state["behavior_matching_raw"] = parsed
        else:
            # 解析失败时保持原文，避免 None
            state["behavior_tags"] = []
            state["association_tags"] = []
            state["behavior_matching_raw"] = content

        state["response"] = state.get("response", "") + "完成behavior_association_matching"
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
        "case_profile": "案例ID: demo\n---\n- 信贷行为数据: 示例字段=示例值",
        "response": "",
    }
    matcher = behavior_association_matching()
    result = matcher.analyze(demo_state, case_id="demo_case_0001")
    print(json.dumps(result.get("behavior_matching_raw", {}), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _demo()
