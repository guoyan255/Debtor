import csv
import io
import os
from typing import List, Optional

from tool_chain.state import State


# 按照用户提供的顺序列出全部字段（无表头时按此映射）
DEFAULT_COLUMNS: List[str] = [
    "客户号", "申请编号", "产品类型", "申请日期", "申请时间", "系统流水号", "证件号", "手机号",
    "公司名称", "公司地址（省市区合并）", "公司地址 1", "公司地址 2", "公司地址 3",
    "家庭地址（省市区合并）", "家庭地址 1", "家庭地址 2", "家庭地址 3",
    "联系人手机号", "成为我行客户距今天数",
    "户籍地址（省市区合并）", "户籍地址 1", "户籍地址 2", "户籍地址 3",
    "手机是否实名", "手机状态", "在网时长", "手机号归属地", "学历层次", "设备号",
    "gps 地址（省市合并）", "申请时 ip 是否在境外", "婚姻状态",
    "公积金账户当前状态", "当前缴存基数", "当月个人缴存比例", "当月个人缴存金额",
    "当前账户余额", "最近连续缴存月份", "累计缴存次数",
    "当前缴存单位名称", "当前缴存单位状态", "当月单位缴存比例", "当月单位缴存金额",
    "当前单位性质", "近 12 个自然月个人缴存平均比例", "近 12 个自然月单位缴存平均比例",
    "最近一次缴存距今时长（月）", "最新公积金账号开户距今时长", "最新公积金账号总缴缴时长",
    "初次缴存距今时长（月）", "个人与单位缴存比例差值", "个人与单位缴存金额差值",
    "当月缴存总额（个人 + 单位）", "社保客群标签", "社保评分", "购房所属城市",
    "是否重疾客群", "是否征信白户",
    "当前_未关闭_所有信用卡_所有机构_循环综合额度使用率_取值",
    "当前_未关闭_循环贷_所有机构_授信额度合计_合计",
    "1 个月内_在册_所有贷款_所有机构_借款金额_合计",
    "当前_未关闭_贷记卡_所有机构_循环额度使用率_平均",
    "当前_所有还款状态_消费贷_所有机构_金额_最大",
    "24 个月内_在册_所有信用卡_所有机构_授信额度合计_合计",
    "当前_未关闭_所有信用卡_所有机构_单家机构授信额度_平均",
    "当前_未关闭_贷记卡_所有机构_所有贷款额度使用率_平均",
    "1 个月内_在册_所有贷款_所有机构_授信金额_最大",
    "6 个月内_在册_所有信用卡_所有机构_授信金额_最大",
    "当前_未关闭_所有信用卡_所有机构_余额_合计",
    "当前_未关闭_所有贷款_所有机构_余额_合计",
    "当前_未关闭_所有房贷_所有机构_余额_合计",
    "当前_所有还款状态_所有信用卡_所有机构_账户数_计数",
    "当前_所有还款状态_所有贷款_所有机构_账户数_计数",
    "当前_所有还款状态_所有信贷_所有机构_开户日期距今月份数_最小",
    "当前_已关闭_所有信贷_所有机构_首笔信贷业务种类_取值",
    "不重复单位数量_计数",
    "进入本单位年份距今年数_最小", "进入本单位年份距今年数_最大",
    "不重复居住地址数量_计数",
    "居住地址变更间隔_平均", "居住地址变更间隔_最小", "居住地址变更间隔_最大",
    "手机号变更间隔_平均", "手机号变更间隔_最小", "手机号变更间隔_最大",
    "手机号变更来源数_计数",
    "1 个月内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询后审批未通过次数与查询次数之比_取值",
    "最近 2 年_所有还款状态_所有查询_所有机构_查询日期距今天数_最小",
    "最近 2 年_所有还款状态_所有查询_所有机构_本人查询数_计数",
    "24 个月内_所有还款状态_信用卡审批_所有机构_查询后审批未通过次数与查询次数之比_取值",
    "首次信用卡开户时长_取值",
    "近 6 个月所有还款状态所有查询所有机构查询次数",
    "最近 2 年_所有还款状态_所有查询_所有机构_查询的日期距今天数_平均",
    "12 个月内_所有还款状态_所有查询_所有机构_查询间隔天数_平均",
    "12 个月内_所有还款状态_信用卡审批 + 贷后_查询间隔天数_平均",
    "12 个月内_在册_所有信用卡_所有机构_负债余额汇总与最大负债额汇总之比_取值",
    "12 个月内_所有还款状态_所有查询_所有机构_查询次数_计数",
    "12 个月内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询次",
    "1 个月内_所有还款状态_所有查询_所有机构_查询次数_计数",
    "1 个月内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询次数",
    "3 个月内_所有还款状态_所有查询_所有机构_查询次数_计数",
    "3 个月内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询次数",
    "6 个月内_所有还款状态_所有查询_所有机构_查询次数_计数",
    "6 个月内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询次数",
    "7 天内_所有还款状态_所有查询_所有机构_查询次数_计数",
    "7 天内_所有还款状态_信用卡审批 + 贷款审批_所有机构_查询次数",
    "当前_未关闭_小额经营贷_所有机构_账户数_计数",
    "当前_未关闭_小额消费贷_所有机构_账户数_计数",
    "当前_未关闭_所有房贷_所有机构_账户数_计数",
    "近 12 个周期_所有还款状态_所有信贷_所有机构_总逾期次数_合计",
    "近 24 个周期_所有还款状态_所有信贷_所有机构_总逾期次数_合计",
    "近 60 个周期_所有还款状态_所有信贷_所有机构_总逾期次数_合计",
    "近 6 个周期_所有还款状态_所有信贷_所有机构_总逾期次数_合计",
    "首次信贷开户时年龄_取值",
    "首次房贷开户时年龄_取值",
    "首次经营贷开户时年龄_取值",
    "首次消费贷开户时年龄_取值",
    "首次信贷开户时年龄_取值",
    "最近 1 个月内的查询次数（本人查询）",
    "按身份证号查询，近 12 个月最大月申请次数",
    "按身份证号查询，近 12 个月在非银机构申请机构数",
    "按身份证号查询，近 6 个月最大月申请次数",
    "按身份证号查询，近 12 个月申请其他的次数",
    "按身份证号查询，近 3 个月最大月申请次数",
    "按身份证号查询，近 3 个月在非银机构申请机构数",
    "按身份证号查询，近 1 个月在非银机构申请机构数",
    "按身份证号查询，近 3 个月在非银机构 - 除蚂蚁小贷机构申请机构数",
    "按身份证号查询，近 6 个月在非银机构申请机构数",
    "按身份证号查询，近 7 天在非银机构申请次数",
    "按身份证号查询，近 7 天在非银机构申请机构数",
    "按身份证号查询，近 1 个月在非银机构申请次数",
    "按身份证号查询，近 3 个月在非银机构申请次数",
    "按身份证号查询，近 6 个月在非银机构申请次数",
    "按身份证号查询，近 12 个月在非银机构申请次数",
    "近 1 月代发工资收入代发金额平均值",
    "近 12 个月代发工资收入代发月数占比",
    "近 6 个月负债月均增长率",
    "近 3 个月入账金额月度最大金额",
    "近 12 个月入账最大交易金额",
    "近 12 个月入账月均金额",
    "年龄",
    "性别",
    "户籍地区是否高风险区域",
    "现居地区是否高风险区域",
]


class data_loader:
    def __init__(
        self,
        file_path: str = "2.csv",
        expected_columns: Optional[List[str]] = None,
        has_header: bool = False,
    ):
        """
        expected_columns: 当 CSV 无表头但列顺序固定时提供字段顺序；默认使用 DEFAULT_COLUMNS
        has_header: True 表示文件有表头；False 表示按顺序映射
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(os.path.dirname(base_dir), file_path)
        self.expected_columns = expected_columns or DEFAULT_COLUMNS
        self.has_header = has_header

    def _read_text(self) -> str:
        """兼容 UTF-8 / GBK 读取整个文件文本"""
        try:
            with open(self.file_path, mode="r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            print(f"[警告] UTF-8 读取失败，正在尝试 GBK 编码: {self.file_path}")
            with open(self.file_path, mode="r", encoding="gbk") as f:
                return f.read()

    def _parse_with_header(self, content: str) -> List[dict]:
        f_obj = io.StringIO(content)
        reader = csv.DictReader(f_obj)
        rows = [row for row in reader]

        # 表头缺失时回退顺序映射
        if not reader.fieldnames or any(h is None or h.strip() == "" for h in reader.fieldnames):
            return self._parse_without_header(content, self.expected_columns)
        return rows

    def _parse_without_header(self, content: str, columns: List[str]) -> List[dict]:
        f_obj = io.StringIO(content)
        reader = csv.reader(f_obj)
        rows: List[dict] = []
        for row in reader:
            if not row:
                continue
            if len(row) < len(columns):
                row = row + [""] * (len(columns) - len(row))
            elif len(row) > len(columns):
                row = row[: len(columns)]
            rows.append({col: val for col, val in zip(columns, row)})
        return rows

    def load_data(self, state: State) -> dict:
        try:
            content = self._read_text()
            raw_content = content

            if self.has_header:
                structured_data = self._parse_with_header(content)
            else:
                structured_data = self._parse_without_header(content, self.expected_columns)

            return {
                "analysis_data": raw_content,
                "data": structured_data,
                "response": state["response"] + "执行成功data_loader",
            }
        except Exception as e:
            print(f"自定义错误: {e}")
            return {
                "analysis_data": "ERROR_DATA_LOAD_FAILED",
                "response": f"错误: 文件读取失败- {str(e)}",
            }
