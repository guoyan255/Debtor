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

案例ID: {case_id}
原始数据信息:
1. 信贷行为数据: 是否征信白户={{0/1}}, 社保客群标签={{数字/负值写null}}, 社保评分={{数字/负值写null}}, 是否重疾客群={{数字/负值写null}}, 当前_未关闭_所有信用卡_所有机构_循环综合额度使用率_取值={{数字/负值写null}}, 当前_未关闭_循环贷_所有机构_授信额度合计_合计={{数字/负值写null}}, 当前_未关闭_贷记卡_所有机构_循环额度使用率_平均={{数字/负值写null}}, 当前_未关闭_贷记卡_所有机构_所有贷款额度使用率_平均={{数字/负值写null}}, 当前_未关闭_所有信用卡_所有机构_单家机构授信额度_平均={{数字/负值写null}}, 1个月内_在册_所有贷款_所有机构_借款金额_合计={{数字/负值写null}}, 1个月内_在册_所有贷款_所有机构_授信金额_最大={{数字/负值写null}}, 6个月内_在册_所有信用卡_所有机构_授信金额_最大={{数字/负值写null}}, 24个月内_在册_所有信用卡_所有机构_授信额度合计_合计={{数字/负值写null}}, 12个月内_在册_所有信用卡_所有机构_负债余额汇总与最大负债额汇总之比_取值={{数字/负值写null}}, 当前_未关闭_所有信用卡_所有机构_余额_合计={{数字/负值写null}}, 当前_未关闭_所有贷款_所有机构_余额_合计={{数字/负值写null}}, 当前_未关闭_所有房贷_所有机构_余额_合计={{数字/负值写null}}, 当前_所有还款状态_消费贷_所有机构_金额_最大={{数字/负值写null}}, 当前_所有还款状态_所有信用卡_所有机构_账户数_计数={{数字/负值写null}}, 当前_所有还款状态_所有贷款_所有机构_账户数_计数={{数字/负值写null}}, 当前_未关闭_小额经营贷_所有机构_账户数_计数={{数字/负值写null}}, 当前_未关闭_小额消费贷_所有机构_账户数_计数={{数字/负值写null}}, 当前_未关闭_所有房贷_所有机构_账户数_计数={{数字/负值写null}}, 当前_所有还款状态_所有信贷_所有机构_开户日期距今月份数_最小={{数字/负值写null}}, 当前_已关闭_所有信贷_所有机构_首笔信贷业务种类_取值={{数字/负值写null}}, 首次信用卡开户时长_取值={{数字/负值写null}}, 首次信贷开户时年龄_取值={{数字/负值写null}}, 首次房贷开户时年龄_取值={{数字/负值写null}}, 首次经营贷开户时年龄_取值={{数字/负值写null}}, 首次消费贷开户时年龄_取值={{数字/负值写null}}, 近6个周期_所有还款状态_所有信贷_所有机构_总逾期次数_合计={{数字/负值写null}}, 近12个周期_所有还款状态_所有信贷_所有机构_总逾期次数_合计={{数字/负值写null}}, 近24个周期_所有还款状态_所有信贷_所有机构_总逾期次数_合计={{数字/负值写null}}, 近60个周期_所有还款状态_所有信贷_所有机构_总逾期次数_合计={{数字/负值写null}}, 最近2年_所有还款状态_所有查询_所有机构_查询日期距今天数_最小={{数字/负值写null}}, 最近2年_所有还款状态_所有查询_所有机构_本人查询数_计数={{数字/负值写null}}, 最近2年_所有还款状态_所有查询_所有机构_查询的日期距今天数_平均={{数字/负值写null}}, 近6个月所有还款状态所有查询所有机构查询次数={{数字/负值写null}}, 12个月内_所有还款状态_所有查询_所有机构_查询次数_计数={{数字/负值写null}}, 12个月内_所有还款状态_信用卡审批 + 贷后_查询间隔天数_平均={{数字/负值写null}}, 12个月内_所有还款状态_所有查询_所有机构_查询间隔天数_平均={{数字/负值写null}}, 1个月内_所有还款状态_所有查询_所有机构_查询次数_计数={{数字/负值写null}}, 3个月内_所有还款状态_所有查询_所有机构_查询次数_计数={{数字/负值写null}}, 6个月内_所有还款状态_所有查询_所有机构_查询次数_计数={{数字/负值写null}}, 7天内_所有还款状态_所有查询_所有机构_查询次数_计数={{数字/负值写null}}, 12个月内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询次数={{数字/负值写null}}, 1个月内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询次数={{数字/负值写null}}, 3个月内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询次数={{数字/负值写null}}, 6个月内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询次数={{数字/负值写null}}, 7天内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询次数={{数字/负值写null}}, 1个月内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询后审批未通过次数与查询次数之比_取值={{数字/负值写null}}, 24个月内_所有还款状态_信用卡审批_所有机构_查询后审批未通过次数与查询次数之比_取值={{数字/负值写null}}, 最近1个月内的查询次数（本人查询）={{数字/负值写null}}, 按身份证号查询，近12个月最大月申请次数={{数字/空值写null}}, 按身份证号查询，近12个月在非银机构申请机构数={{数字/空值写null}}, 按身份证号查询，近6个月最大月申请次数={{数字/空值写null}}, 按身份证号查询，近12个月申请其他的次数={{数字/空值写null}}, 按身份证号查询，近3个月最大月申请次数={{数字/空值写null}}, 按身份证号查询，近3个月在非银机构申请机构数={{数字/空值写null}}, 按身份证号查询，近1个月在非银机构申请机构数={{数字/空值写null}}, 按身份证号查询，近3个月在非银机构-除蚂蚁小贷机构申请机构数={{数字/空值写null}}, 按身份证号查询，近6个月在非银机构申请机构数={{数字/空值写null}}, 按身份证号查询，近7天在非银机构申请次数={{数字/空值写null}}, 按身份证号查询，近7天在非银机构申请机构数={{数字/空值写null}}, 按身份证号查询，近1个月在非银机构申请次数={{数字/空值写null}}, 按身份证号查询，近3个月在非银机构申请次数={{数字/空值写null}}, 按身份证号查询，近6个月在非银机构申请次数={{数字/空值写null}}, 按身份证号查询，近12个月在非银机构申请次数={{数字/空值写null}}
2. 资产行为数据: 购房所属城市={{汉字}}, 近6个月负债月均增长率={{数字/空值写null}}
3. 职业及收入数据: 公司名称={{汉字}}, 公司地址={{省市区合并}}, 公司地址 1={{汉字}}, 公司地址 2={{汉字}}, 公司地址 3={{汉字}}, 不重复单位数量_计数={{数字/负值写null}}, 进入本单位年份距今年数_最小={{数字/负值写null}}, 进入本单位年份距今年数_最大={{数字/负值写null}}, 公积金账户当前状态={{数字/负值写null}}, 当前缴存基数={{数字/负值写null}}, 当月个人缴存比例={{数字/负值写null}}, 当月个人缴存金额={{数字/负值写null}}, 当前账户余额={{数字/负值写null}}, 最近连续缴存月份={{数字/负值写null}}, 累计缴存次数={{数字/负值写null}}, 当前缴存单位名称={{汉字/负值写null}}, 当前缴存单位状态={{数字/负值写null}}, 当月单位缴存比例={{数字/负值写null}}, 当月单位缴存金额={{数字/负值写null}}, 当前单位性质={{数字/负值写null}}, 近12个自然月个人缴存平均比例={{数字/负值写null}}, 近12个自然月单位缴存平均比例={{数字/负值写null}}, 最近一次缴存距今时长（月）={{数字/负值写null}}, 最新公积金账号开户距今时长={{数字/负值写null}}, 最新公积金账号总缴存时长={{数字/负值写null}}, 初次缴存距今时长（月）={{数字/负值写null}}, 个人与单位缴存比例差值={{数字/负值写null}}, 个人与单位缴存金额差值={{数字/负值写null}}, 当月缴存总额（个人+单位）={{数字/负值写null}}, 近1月代发工资收入代发金额平均值={{数字/空值写null}}, 近12个月代发工资收入代发月数占比={{数字/空值写null}}, 近3个月入账金额月度最大金额={{数字/空值写null}}, 近12个月入账最大交易金额={{数字/空值写null}}, 近12个月入账月均金额={{数字/空值写null}}
4. 个人核心数据: 客户号={{数字}}, 证件号={{str}}, 年龄={{数字}}, 性别={{汉字}}, 学历层次={{汉字}}, 婚姻状态={{10/20/30/40/91/99}}, 户籍地址={{省市区合并}}, 户籍地址 1={{汉字}}, 户籍地址 2={{汉字}}, 户籍地址 3={{汉字}}, 家庭地址={{省市区合并}}, 家庭地址 1={{汉字}}, 家庭地址 2={{汉字}}, 家庭地址 3={{汉字}}, 户籍地区是否高风险区域={{0/1}}, 现居地区是否高风险区域={{0/1}}, 设备号={{设备号}}, gps 地址={{省市合并+邮编}}, 申请时 ip 是否在境外={{0/1}}
5. 联系人及通话记录: 手机号={{str}}, 手机是否实名={{0/1}}, 手机状态={{状态}}, 在网时长={{时长}}, 手机号归属地={{汉字}}, 联系人手机号={{str}}, 不重复居住地址数量_计数={{数字/负值写null}}, 居住地址变更间隔_平均={{数字/负值写null}}, 居住地址变更间隔_最小={{数字/负值写null}}, 居住地址变更间隔_最大={{数字/负值写null}}, 手机号变更间隔_平均={{数字/负值写null}}, 手机号变更间隔_最小={{数字/负值写null}}, 手机号变更间隔_最大={{数字/负值写null}}, 手机号变更来源数_计数={{数字/负值写null}}
6. 其他补充数据: 申请编号={{数字}}, 产品类型={{汉字}}, 申请日期={{YYYY/MM/DD}}, 申请时间={{YYYY/MM/DD HH：MM}}, 系统流水号={{str}}, 成为我行客户距今天数={{数字}}

输出要求：
- 先输出“案例ID: {case_id}”，换行后输出“---”。
- 之后逐行输出关键类别摘要，形如：
  - 信贷行为数据: {{概括内容}}
  - 资产行为数据: {{概括内容}}
  - 职业及收入数据: {{概括内容}}
  - 个人核心数据: {{概括内容}}
  - 联系人及社交行为数据: {{概括内容}}
  - 其他补充数据: {{概括内容}}
- 概括内容直接从【标准化用户数据 JSON】提取，保持“字段=值”用逗号分隔；缺失字段写 N/A。
- 不生成风险等级或原因说明；不额外解释。

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
