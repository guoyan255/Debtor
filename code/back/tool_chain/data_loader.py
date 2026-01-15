import csv
import io
import os
from tool_chain.state import State

class data_loader:
    def __init__(self, file_path: str = "2.csv"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(os.path.dirname(base_dir), file_path)
    
    def load_data(self, state: State) -> dict:
        try:
            # --- 修改开始：增加编码兼容性逻辑 ---
            content = ""
            # 优先尝试 UTF-8
            try:
                with open(self.file_path, mode='r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 如果失败，尝试 GBK (常见于 Windows Excel 文件)
                print(f"[警告] UTF-8 读取失败，正在尝试 GBK 编码: {self.file_path}")
                with open(self.file_path, mode='r', encoding='gbk') as f:
                    content = f.read()
            
            # 保存原始文本
            raw_content = content
            
            # 解析 CSV
            f_obj = io.StringIO(content)
            reader = csv.DictReader(f_obj)
            structured_data = [row for row in reader]
            # --- 修改结束 ---

            return {
                "analysis_data": raw_content, 
                "data": structured_data,
                "response": state["response"] + "执行成功data_loader"
            }
        except Exception as e:
            # 打印详细堆栈以便调试
            print(f"致命错误: {e}")
            return {
                # 强烈建议：这里返回特定的错误标记，让后续节点知道出错了
                "analysis_data": "ERROR_DATA_LOAD_FAILED", 
                "response": f"错误：文件读取失败 - {str(e)}"
            }