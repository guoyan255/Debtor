from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from tool_chain.state import State


class data_processing:

    def __init__(self, output_path: Optional[str] = None) -> None:
        # 关键字段缺失判为无效
        self.required_fields = {"客户号", "申请编号", "证件号", "手机号"}
        self.output_path = output_path

        # 精确规则
        self.field_rules: Dict[str, str] = {
            "客户号": "numeric_non_negative",
            "申请编号": "numeric_non_negative",
            "产品类型": "cn_text",
            "申请日期": "date",
            "申请时间": "datetime",
            "系统流水号": "serial_5",
            "证件号": "id_card",
            "手机号": "phone",
            "联系人手机号": "phone",
            "公司名称": "cn_text",
            "公司地址（省市区合并）": "address",
            "公司地址 1": "address",
            "公司地址 2": "address",
            "公司地址 3": "address",
            "家庭地址（省市区合并）": "address",
            "家庭地址 1": "address",
            "家庭地址 2": "address",
            "家庭地址 3": "address",
            "户籍地址（省市区合并）": "address",
            "户籍地址 1": "address",
            "户籍地址 2": "address",
            "户籍地址 3": "address",
            "手机号归属地": "address",
            "gps 地址（省市合并）": "gps_address",
            "手机是否实名": "bool_01",
            "申请时 ip 是否在境外": "bool_01",
            "婚姻状态": "marriage_code",
            "学历层次": "cn_text",
            "成为我行客户距今天数": "numeric_non_negative",
        }

        # “数字，负值为 null” 统一规则
        negative_to_null = [
            "公积金账户当前状态",
            "当前缴存基数",
            "当月个人缴存比例",
            "当月个人缴存金额",
            "当前账户余额",
            "最近连续缴存月份",
            "累计缴存次数",
            "当前缴存单位状态",
            "当月单位缴存比例",
            "当月单位缴存金额",
            "当前单位性质",
            "近 12 个自然月个人缴存平均比例",
            "近 12 个自然月单位缴存平均比例",
            "最近一次缴存距今时长（月）",
            "最新公积金账号开户距今时长",
            "最新公积金账号总缴缴时长",
            "初次缴存距今时长（月）",
            "个人与单位缴存比例差值",
            "个人与单位缴存金额差值",
            "当月缴存总额（个人 + 单位）",
            "社保客群标签",
            "社保评分",
            "是否重疾客群",
            "是否征信白户",
        ]
        for f in negative_to_null:
            self.field_rules[f] = "numeric_non_negative"

        # 通用关键词：含这些词且没有专门规则时，同样负值置空
        self.default_negative_to_null_keywords = [
            "次数",
            "计数",
            "金额",
            "余额",
            "额度",
            "比例",
            "比率",
            "占比",
            "使用率",
            "时长",
            "月份",
            "月数",
            "天数",
            "增长率",
            "合计",
            "取值",
            "最大",
            "平均",
        ]

    # ---------------- 公共入口 ---------------- #
    def process_data(self, state: State) -> Dict[str, Any]:
        cleaned_rows: List[Dict[str, Any]] = []
        standardization_log: List[Dict[str, Any]] = []
        invalid_rows: List[Dict[str, Any]] = []

        for row_idx, row in enumerate(state.get("data", [])):
            cleaned, logs, invalid = self._standardize_record(row)
            cleaned_rows.append(cleaned)
            standardization_log.extend({"row_index": row_idx, **log} for log in logs)
            if invalid:
                invalid_rows.append({"row_index": row_idx, "reasons": invalid})

        payload = {
            "data": cleaned_rows,
            "standardization_log": standardization_log,
            "invalid_rows": invalid_rows,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
        json_str = json.dumps(payload, ensure_ascii=False, indent=2)

        if self.output_path:
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(json_str)

        state["data"] = cleaned_rows
        state["standardization_log"] = standardization_log
        state["invalid_rows"] = invalid_rows
        state["json_payload"] = payload
        state["json_string"] = json_str
        state["text"] = state.get("text", "") + "data_processing"
        state["response"] = state.get("response", "") + "数据清洗完成"
        if self.output_path:
            state["output_json_path"] = self.output_path
        return state

    # ---------------- 单行处理 ---------------- #
    def _standardize_record(
        self, record: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[str]]:
        cleaned: Dict[str, Any] = {}
        logs: List[Dict[str, Any]] = []
        invalid_reasons: List[str] = []

        for field, raw in record.items():
            normalized_value, rule = self._normalize_field(field, raw)
            cleaned[field] = normalized_value
            logs.append(
                {
                    "field": field,
                    "raw_value": raw,
                    "standardized_value": normalized_value,
                    "rule": rule,
                }
            )

        for key in self.required_fields:
            if key in record and cleaned.get(key) in (None, ""):
                invalid_reasons.append(f"{key} 缺失或无效")

        return cleaned, logs, invalid_reasons

    # ---------------- 规则选择 ---------------- #
    def _normalize_field(self, field: str, value: Any) -> Tuple[Any, str]:
        val = self._normalize_missing(value)
        if val is None:
            return None, "空值标准化"

        rule_type = self.field_rules.get(field)
        if rule_type:
            if rule_type == "numeric_non_negative":
                return self._normalize_number(val, allow_negative=False), "非负数字"
            if rule_type == "phone":
                return self._normalize_phone(val), "手机号清洗"
            if rule_type == "id_card":
                return self._normalize_id(val), "证件号格式化"
            if rule_type == "bool_01":
                return self._normalize_bool01(val), "0/1 布尔"
            if rule_type == "marriage_code":
                return self._normalize_marriage(val), "婚姻状态编码"
            if rule_type == "serial_5":
                return self._normalize_serial5(val), "流水号校验"
            if rule_type == "date":
                return self._normalize_datetime(val, date_only=True), "日期解析"
            if rule_type == "datetime":
                return self._normalize_datetime(val), "日期时间解析"
            if rule_type == "address":
                return self._normalize_address(val), "地址去噪"
            if rule_type == "gps_address":
                return self._normalize_gps_address(val), "GPS 地址去噪"
            if rule_type == "cn_text":
                return self._normalize_cn_text(val), "中文文本规范"

        if "证件" in field or "身份证" in field:
            return self._normalize_id(val), "证件号格式化"
        if "手机号" in field or "电话" in field:
            return self._normalize_phone(val), "手机号清洗"
        if "ip" in field.lower():
            return self._normalize_ip(val), "IP 规范化"
        if "日期" in field or ("时间" in field and "时长" not in field):
            return self._normalize_datetime(val), "日期/时间解析"
        if any(k in field for k in ["地址", "地区", "城市", "归属地"]):
            return self._normalize_address(val), "地址去噪"

        if self._looks_like_ratio_field(field):
            non_neg = self._keyword_need_non_negative(field)
            return self._normalize_ratio(val, allow_negative=not non_neg), "比例/使用率转小数"
        if self._looks_like_amount_field(field):
            non_neg = self._keyword_need_non_negative(field)
            return self._normalize_number(val, allow_negative=not non_neg), "金额/额度数值化"
        if self._looks_like_count_field(field):
            non_neg = self._keyword_need_non_negative(field)
            return self._normalize_integer(val, allow_negative=not non_neg), "次数/计数转整数"
        if self._looks_like_duration_field(field):
            non_neg = self._keyword_need_non_negative(field)
            return self._normalize_number(val, allow_negative=not non_neg), "时长/月份/天数转数值"

        return self._normalize_text(val), "文本去空白"

    # ---------------- 具体归一化 ---------------- #
    def _normalize_missing(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        val = str(value).strip()
        if val == "":
            return None
        if val.lower() in {"null", "none", "nan", "na", "n/a", "-", "--", "未填写", "未知"}:
            return None
        return val

    def _normalize_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _normalize_id(self, value: str) -> Optional[str]:
        cleaned = re.sub(r"\s+", "", value).upper()
        cleaned = cleaned.replace("（", "(").replace("）", ")")
        cleaned = cleaned.replace("－", "-").replace("，", ",").replace("。", ".")
        cleaned = cleaned.replace("Ｏ", "0").replace("ｏ", "0").replace("Ｘ", "X")
        cleaned = re.sub(r"[^0-9Xx]", "", cleaned).upper()
        if len(cleaned) in (15, 18):
            return cleaned
        return None

    def _normalize_phone(self, value: str) -> Optional[str]:
        digits = re.sub(r"\D", "", value)
        digits = digits[2:] if digits.startswith("86") and len(digits) > 11 else digits
        if len(digits) == 11:
            return digits
        return None

    def _normalize_bool01(self, value: str) -> Optional[int]:
        v = value.strip()
        if v in {"0", "1"}:
            return int(v)
        return None

    def _normalize_marriage(self, value: str) -> Optional[int]:
        v = re.sub(r"\D", "", value)
        if v in {"10", "20", "30", "40", "91", "99"}:
            return int(v)
        return None

    def _normalize_serial5(self, value: str) -> Optional[str]:
        v = value.strip()
        if re.fullmatch(r"[A-Za-z0-9]+(-[A-Za-z0-9]+){4}", v):
            return v
        return None

    def _normalize_cn_text(self, value: str) -> str:
        cleaned = re.sub(r"[ \t\r\n]+", " ", value)
        return cleaned.strip()

    def _normalize_gps_address(self, value: str) -> str:
        cleaned = re.sub(r"^[0-9]{4,6}", "", value).strip()
        cleaned = cleaned.strip(",， ")
        return self._normalize_address(cleaned)

    def _normalize_ip(self, value: str) -> str:
        return value.strip().lower()

    def _normalize_address(self, value: str) -> str:
        cleaned = re.sub(r"[，,\s]+", " ", value).strip()
        return cleaned

    def _normalize_datetime(self, value: str, date_only: bool = False) -> Optional[str]:
        val = value.strip()
        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M",
            "%Y.%m.%d",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y%m%d",
        ]
        if date_only:
            date_formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y%m%d"]
        for fmt in date_formats:
            try:
                dt = datetime.strptime(val, fmt)
                if not date_only and any(token in fmt for token in ["%H", "%M", "%S"]):
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        if not date_only:
            for fmt in ["%H:%M:%S", "%H:%M"]:
                try:
                    dt = datetime.strptime(val, fmt)
                    return dt.strftime("%H:%M:%S")
                except ValueError:
                    continue
        return None

    def _normalize_number(self, value: str, allow_negative: bool = True) -> Optional[float]:
        text = value.replace(",", "").replace("，", "").replace("元", "").strip()
        multiplier = 1.0
        if "万" in text:
            multiplier = 10000.0
            text = text.replace("万", "")
        if text.endswith("%"):
            try:
                num = float(text.rstrip("%")) / 100.0
            except ValueError:
                return None
        else:
            try:
                num = float(text) * multiplier
            except ValueError:
                numbers = re.findall(r"-?\d+\.?\d*", text)
                if not numbers:
                    return None
                try:
                    num = float(numbers[0]) * multiplier
                except ValueError:
                    return None
        if not allow_negative and num < 0:
            return None
        return num

    def _normalize_integer(self, value: str, allow_negative: bool = True) -> Optional[int]:
        number = self._normalize_number(value, allow_negative=allow_negative)
        if number is None:
            return None
        try:
            return int(round(number))
        except (ValueError, TypeError):
            return None

    def _normalize_ratio(self, value: str, allow_negative: bool = True) -> Optional[float]:
        num = self._normalize_number(value, allow_negative=allow_negative)
        if num is None:
            return None
        if num > 1.0 and "." not in value and "%" not in value:
            return num / 100.0
        return num

    # ---------------- 关键词判定 ---------------- #
    def _keyword_need_non_negative(self, field: str) -> bool:
        if field in self.field_rules and self.field_rules[field] == "numeric_non_negative":
            return True
        return any(k in field for k in self.default_negative_to_null_keywords)

    def _looks_like_amount_field(self, field: str) -> bool:
        keywords = ["金额", "余额", "额度", "收入", "基数", "缴存", "薪资", "差值", "合计"]
        return any(k in field for k in keywords)

    def _looks_like_ratio_field(self, field: str) -> bool:
        keywords = ["比例", "比率", "占比", "使用率"]
        return any(k in field for k in keywords)

    def _looks_like_count_field(self, field: str) -> bool:
        keywords = ["次数", "数量", "账户数", "笔数", "机构数", "月数", "天数"]
        return any(k in field for k in keywords)

    def _looks_like_duration_field(self, field: str) -> bool:
        keywords = ["时长", "月份", "月", "天", "距今", "年数", "间隔", "年龄"]
        return any(k in field for k in keywords)

