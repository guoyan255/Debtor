"""
数据格式化模块
将原始债务人数据按照字段分组方案格式化，生成符合要求的案例结构
"""

import json
import os
from typing import Dict, List, Any


class DataFormatter:
    """数据格式化器，负责将原始数据转换为案例格式"""
    
    def __init__(self, field_groups_path: str = None):
        """
        初始化数据格式化器
        
        Args:
            field_groups_path: 字段分组配置文件路径
        """
        if field_groups_path is None:
            # 默认路径
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            field_groups_path = os.path.join(base_dir, "..", "config", "field_groups.json")
        
        with open(field_groups_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.field_groups = config['field_groups']
    
    def format_data(self, raw_data: Dict[str, Any], case_id: str = None) -> Dict[str, Any]:
        """
        格式化原始数据为案例结构
        
        Args:
            raw_data: 原始数据字典
            case_id: 案例ID，如果为None则自动生成
        
        Returns:
            格式化后的案例数据
        """
        if case_id is None:
            # 使用申请编号或客户号作为案例ID
            case_id = f"Case_{raw_data.get('申请编号', '0000')}"
        
        # 初始化案例结构
        case_data = {
            "案例ID": case_id,
            "原始数据清单": {},
            "原始数据值": raw_data.copy()  # 保存完整原始数据供后续推理使用
        }
        
        # 按分组整理数据
        for group_name, group_config in self.field_groups.items():
            group_fields = group_config['fields']
            group_data = {
                "描述": group_config['description'],
                "字段": []
            }
            
            # 提取该组的字段和值
            for field in group_fields:
                if field in raw_data:
                    value = raw_data[field]
                    # 处理空值
                    if value is None or value == '' or (isinstance(value, (int, float)) and value < 0):
                        value = 'null'
                    group_data["字段"].append({
                        "名称": field,
                        "值": value
                    })
            
            case_data["原始数据清单"][group_name] = group_data
        
        return case_data
    
    def batch_format(self, raw_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量格式化数据
        
        Args:
            raw_data_list: 原始数据列表
        
        Returns:
            格式化后的案例数据列表
        """
        formatted_cases = []
        for idx, raw_data in enumerate(raw_data_list):
            case_id = f"Case_{str(idx+1).zfill(4)}"
            formatted_case = self.format_data(raw_data, case_id)
            formatted_cases.append(formatted_case)
        
        return formatted_cases


if __name__ == "__main__":
    # 测试代码
    formatter = DataFormatter()
    
    # 模拟一条韩磊的数据
    test_data = {
        "申请编号": "202308200001",
        "证件号": "650101199503129012",
        "手机号": "18500185001",
        "申请日期": "2023/8/20",
        "产品类型": "信用贷",
        "学历层次": "高中",
        "公积金账户当前状态": "未缴纳",
        "按身份证号查询，近12个月在非银机构申请次数": 10,
        "在网时长": 8,
        "年龄": 23,
        "近12个月入账月均金额": 136000
    }
    
    formatted = formatter.format_data(test_data, "Case_0001")
    print(json.dumps(formatted, ensure_ascii=False, indent=2))
