"""
知识库使用示例
演示如何加载、查询和管理知识库
"""
from knowledge.knowledge_base import KnowledgeBase


def main():
    # 初始化知识库
    kb = KnowledgeBase(
        knowledge_dir="./knowledgeBase",
        md5_dir="./MD5",
        chroma_dir="./chroma_kb"
    )

    print("=== 重建知识库索引 ===")
    stats = kb.rebuild_index()
    print(f"处理统计: {stats}")

    print("\n=== 语义搜索测试 ===")
    queries = [
        "如何处理缺失数据？",
        "销售预测方法",
        "数据质量检查"
    ]

    for query in queries:
        print(f"\n查询: {query}")
        results = kb.search(query, n_results=2)

        for i, result in enumerate(results, 1):
            print(f"\n结果 {i}:")
            print(f"  内容: {result['content'][:100]}...")
            print(f"  来源: {result['metadata']['source']}")
            print(f"  距离: {result['distance']:.4f}")


if __name__ == "__main__":
    main()
