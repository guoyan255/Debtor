from __future__ import annotations

"""
基于 data_processing 的清洗结果，调用大模型生成“案例画像”文本。
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict

import pandas as pd

_CUR_DIR = Path(__file__).resolve().parent
_BACK_DIR = _CUR_DIR.parent
if str(_BACK_DIR) not in sys.path:
    sys.path.insert(0, str(_BACK_DIR))

from model_components.deepseek_model import DeepSeekLLM
from tool_chain.data_processing import data_processing
from tool_chain.state import State


class case_formatter:
    """
    产出与截图一致的模板化“案例画像”。
    """

    def __init__(self):
        if os.getenv("LLM_SKIP", "0") == "1":
            self.llm = None
        else:
            self.llm = DeepSeekLLM().llm
        self.processor = data_processing()
        # 只保留 {case_id} 与 {data_json} 供 format，其余花括号全部使用双花括号转义
        self.prompt = r"""
你是一名银行信贷风控分析师，请基于给定的“标准化用户数据 JSON”生成下述模板文本，严格遵循格式。

输出要求：
- 使用流式输出
- 按你理解来对原始数据进行如下分类：1.信贷行为数据 2.资产行为数据 3.职业及收入数据 4.个人核心数据 5.联系人及社交行为数据 6.其他补充数据
- 先输出“案例ID: {case_id}”，换行后输出“--”
- 之后依次输出关键类别摘要，例如：
  - 信贷行为数据: {{示例内容}}
  - 资产行为数据: {{示例内容}}
  - 职业及收入数据: {{示例内容}}
  - 个人核心数据: {{示例内容}}
  - 联系人及社交行为数据: {{示例内容}}
  - 其他补充数据: {{示例内容}}
- 你需要对以下数据进行转换：
  - 1.是否实名：1(=手机号、证件号、姓名均一致；3(证件号、姓名不一致)
  - 2.在网状态（-2=查询异常；1=正常使用；2=停机）
  - 3.在网时长（≤2=查询异常；1=用户当前入网；2=入网(1,2];3=入网(2,6];4=入网(6,12];5=入网(12,24];6=入网(24,+)
  - 4.社保人群标签：1=大病/特困/低保/残疾/失独/低保/失业；2=即将状态暂停/终止；3=有社保记录，但未参保明确数据；4=新农合；5=城镇在职个人社保；6=城镇在职单位社保）
- 示例内容直接从【标准化用户数据 JSON】提取，保持“字段=值”用逗号分隔；过长字段写 N/A。
- 最后你需要生成此案例可能匹配的高风险人群标签,例如跑路贷款、刷单等标签
- 不生成评级等或原因说明；不额外输出。
- 输出为 json格式

【标准化用户数据 JSON】
{data_json}
"""

    def format_from_processed(self, state: State, case_id: str = "case_0001") -> State:
        """
        接收已调用 data_processing 的 state，返回带模板输出的 state。
        """
        if os.getenv("LLM_SKIP", "0") == "1":
            state["case_profile"] = f"[MOCK] case_profile for {case_id}"
            state["response"] = state.get("response", "") + "完成case_formatter(mock)"
            return state

        cleaned_data = state.get("data", [])
        data_json = json.dumps(cleaned_data, ensure_ascii=False, indent=2)
        prompt = self.prompt.format(case_id=case_id, data_json=data_json)

        content = ""
        if hasattr(self.llm, "stream"):
            try:
                chunks = []
                for chunk in self.llm.stream(prompt):
                    text = getattr(chunk, "content", "") or str(chunk)
                    print(text, end="", flush=True)
                    chunks.append(text)
                print()  # 换行，便于阅读
                content = "".join(chunks)
            except Exception:
                response = self.llm.invoke(prompt)
                content = response.content
        else:
            response = self.llm.invoke(prompt)
            content = response.content

        state["case_profile"] = content
        state["response"] = state.get("response", "") + "完成case_template_formatter"
        return state

    def format_from_raw(self, raw_records: List[Dict[str, str]], case_id: str = "case_0001") -> State:
        """
        直接传入原始记录列表 -> 先清洗 -> 模板化输出。
        """
        state: State = {
            "data": raw_records,
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
        processed = self.processor.process_data(state)
        return self.format_from_processed(processed, case_id)


def _demo():
    """
    读取 back/2.csv 作为示例，演示模板输出。
    """
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "2.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"示例文件不存在: {csv_path}")

    try:
        df = pd.read_csv(csv_path, dtype=str, encoding="utf-8", on_bad_lines="warn", engine="python").fillna("")
    except UnicodeDecodeError:
        df = pd.read_csv(
            csv_path,
            dtype=str,
            encoding="gbk",
            encoding_errors="ignore",
            on_bad_lines="warn",
            engine="python",
        ).fillna("")
    records = df.to_dict(orient="records")

    formatter = case_formatter()
    final_state = formatter.format_from_raw(records, case_id="case_demo_0001")
    print(final_state.get("case_profile", "未生成输出"))


if __name__ == "__main__":
    _demo()

# Backward compatibility alias
case_template_formatter = case_formatter
