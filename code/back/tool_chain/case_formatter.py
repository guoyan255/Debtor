from __future__ import annotations

"""
基于 data_processing 的清洗结果，调用大模型生成与示例图片一致的“案例画像”文本。
运行示例：
    python Debtor/code/back/tool_chain/case_template_formatter.py
需要配置 .env 中的 DEEPSEEK_KEY 与 DEEPSEEK_URL。
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

import pandas as pd

# 便于脚本直接运行找到同级模块
_CUR_DIR = Path(__file__).resolve().parent
_BACK_DIR = _CUR_DIR.parent
if str(_BACK_DIR) not in sys.path:
    sys.path.insert(0, str(_BACK_DIR))

from model_components.deepseek_model import DeepSeekLLM
from tool_chain.data_processing import data_processing
from tool_chain.state import State


class case_template_formatter:
    """
    产出与截图一致的模板化“案例画像”。
    """

    def __init__(self):
        deepseek_client = DeepSeekLLM()
        self.llm = deepseek_client.llm
        self.processor = data_processing()
        # 注意：只保留 {case_id} 与 {data_json} 供 format，其余花括号全部使用双花括号转义
        self.prompt = r"""
你是一名银行信贷风控分析师，请基于给定的“标准化用户数据 JSON”生成下述模板文本，严格遵循格式。


输出要求：
- 采用流式输出
- 按你的理解来对原始数据进行以下分类：1.信贷行为数据 2.资产行为数据 3.职业及收入数据 4.个人核心数据 5.联系人及社交行为数据 6.其他补充数据
- 先输出“案例ID: {case_id}”，换行后输出“---”。
- 之后逐行输出关键类别摘要，形如：
  - 信贷行为数据: {{概括内容}}
  - 资产行为数据: {{概括内容}}
  - 职业及收入数据: {{概括内容}}
  - 个人核心数据: {{概括内容}}
  - 联系人及社交行为数据: {{概括内容}}
  - 其他补充数据: {{概括内容}}
- 你需要对以下数据进行转换：
  - 1.是否实名（0：手机号、证件号、姓名均一致；3：证件号、姓名不一致）
  - 2.在网状态（-2：查询异常；1：正常使用；2：停机）
  - 3.在网时长（-2：查询异常；1：用户当月入网；2：入网[1,2];3：入网[2,6];4：入网[6,12];5：入网[12,24];6：入网[24,+)）
  - 4.社保客群标签（1：大病/特困/五保户/重残/低收入/医疗救助/农民工/低保/失业；2：缴保状态暂停、终止；3：有全民参保记录，但无参保明细数据；4：新农合；5：城镇职工个人缴保；6：城镇职工单位缴保）
  
- 概括内容直接从【标准化用户数据 JSON】提取，保持“字段=值”用逗号分隔；缺失字段写 N/A。
- 最后你需要生成该案例可能匹配到的背债人特征,例如异地贷款、离婚等特征
- 不生成风险等级或原因说明；不额外解释。
- 输出为json格式

【标准化用户数据 JSON】
{data_json}
"""

    def format_from_processed(self, state: State, case_id: str = "case_0001") -> State:
        """
        接收已调用 data_processing 的 state，返回带模板输出的 state。
        """
        # 仅向大模型提供清洗后的主体数据，避免包含 standardization_log 等冗余字段导致重复描述
        cleaned_data = state.get("data", [])
        data_json = json.dumps(cleaned_data, ensure_ascii=False, indent=2)
        prompt = self.prompt.format(case_id=case_id, data_json=data_json)
        response = self.llm.invoke(prompt)
        state["case_profile"] = response.content
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

    formatter = case_template_formatter()
    final_state = formatter.format_from_raw(records, case_id="case_demo_0001")
    print(final_state.get("case_profile", "未生成输出"))


if __name__ == "__main__":
    _demo()
