from config import RAGConfig
#查看向量库中所有内容
def fetch_all_rules():
    config = RAGConfig()

    client = config.client
    collection_name = config.collection_name

    all_points = []
    offset = None

    while True:
        points, offset = client.scroll(
            collection_name=collection_name,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False  # 不需要向量本体
        )

        all_points.extend(points)

        if offset is None:
            break

    results = []
    for p in all_points:
        payload = p.payload or {}
        results.append({
            "rule_name": payload.get("rule_name"),
            "logic_expression": payload.get("logic_expression"),
            "risk_verdict": payload.get("risk_verdict")
        })

    return results


if __name__ == "__main__":
    rules = fetch_all_rules()
    print(f"向量库中共有 {len(rules)} 条规则：\n")

    for r in rules:
        print("规则名称:", r["rule_name"])
        print("逻辑表达式:", r["logic_expression"])
        print("风险判定:", r["risk_verdict"])
        print("-" * 50)
