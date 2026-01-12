import os
from config import RAGConfig


'''
这个脚本会检查你在 config.py 中定义的本地存储路径，如果存在，则逐条打印出所有存储的数据详情。
'''


def dump_all_data():
    # 1. 初始化配置并获取客户端
    config = RAGConfig()
    
    # 2. 检查本地目录是否存在
    if not os.path.exists(config.storage_path):
        print(f"❌ 未发现本地数据库目录: {config.storage_path}")
        return

    print(f"✅ 发现数据库，正在连接到集合: {config.collection_name}...")

    try:
        # 3. 使用 scroll API 获取所有数据记录
        # scroll 返回一个元组: (list_of_points, next_page_offset)
        points, _ = config.client.scroll(
            collection_name=config.collection_name,
            limit=100,      # 一次读取的数量
            with_payload=True, # 必须为 True 才能看到原始 CSV 文字内容
            with_vectors=False # 如果不需要看原始向量数值，设为 False
        )

        if not points:
            print("󱞪 集合中没有任何数据。")
            return

        print(f"\n--- 数据库全量内容（共计 {len(points)} 条记录）---")
        
        for point in points:
            print("-" * 50)
            print(f"ID: {point.id}")
            # payload 中存储了 LlamaIndex 转换后的文本内容
            content = point.payload.get("_node_content", "无内容")
            # 尝试获取 LlamaIndex 格式化后的文本
            text = point.payload.get("text", "无文本字段")
            
            print(f"内容摘要: {text}")
            # 如果你想看完整的原始元数据，可以打印 point.payload
            
    except Exception as e:
        print(f"❌ 读取数据时发生错误: {e}")

if __name__ == "__main__":
    dump_all_data()