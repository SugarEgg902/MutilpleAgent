import os
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
import chromadb
from chromadb.config import Settings
from config import Config


class KnowledgeBase:
    """知识库管理系统，支持文档加载、语义分割、MD5查重"""

    def __init__(self,
                 knowledge_dir: str = "./knowledgeBase",
                 md5_dir: str = "./MD5",
                 chroma_dir: str = "./chroma_kb"):
        self.knowledge_dir = Path(knowledge_dir)
        self.md5_dir = Path(md5_dir)
        self.chroma_dir = Path(chroma_dir)

        # 创建目录
        self.knowledge_dir.mkdir(exist_ok=True)
        self.md5_dir.mkdir(exist_ok=True)
        self.chroma_dir.mkdir(exist_ok=True)

        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )

        # 初始化向量数据库
        self.client = chromadb.Client(Settings(
            persist_directory=Config.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False
        ))
        self.collection = self.client.get_or_create_collection("knowledge_base")

        # 初始化嵌入模型
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v1",
            dashscope_api_key=Config.DASHSCOPE_API_KEY
        )

        print("知识库路径:", self.knowledge_dir.resolve())
    def _compute_md5(self, text: str) -> str:
        """计算文本的MD5哈希值"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _is_duplicate(self, md5_hash: str) -> bool:
        """检查MD5是否已存在"""
        md5_file = self.md5_dir / f"{md5_hash}.json"
        return md5_file.exists()

    def _save_md5(self, md5_hash: str, metadata: Dict[str, Any]):
        """保存MD5记录"""
        md5_file = self.md5_dir / f"{md5_hash}.json"
        with open(md5_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def load_documents(self) -> List[Dict[str, Any]]:
        """从knowledgeBase目录加载所有文档"""
        documents = []
        for file_path in self.knowledge_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.txt', '.md', '.json']:
                try:
                    with open(os.path.abspath(file_path), 'r', encoding='utf-8') as f:
                        content = f.read()

                    documents.append({
                        "content": content,
                        "source": str(file_path.relative_to(self.knowledge_dir)),
                        "file_type": file_path.suffix
                    })
                except Exception as e:
                    print(f"加载文件失败 {file_path}: {e}")

        return documents

    def process_and_store(self, documents: List[Dict[str, Any]]) -> Dict[str, int]:
        """处理文档：分割、查重、存储"""
        stats = {
            "total_chunks": 0,
            "stored_chunks": 0,
            "duplicate_chunks": 0
        }

        for doc in documents:
            # 语义分割
            chunks = self.text_splitter.split_text(doc["content"])
            stats["total_chunks"] += len(chunks)

            for idx, chunk in enumerate(chunks):
                # 计算MD5
                md5_hash = self._compute_md5(chunk)

                # 查重
                if self._is_duplicate(md5_hash):
                    stats["duplicate_chunks"] += 1
                    continue

                # 存储到向量库
                chunk_id = f"{md5_hash}_{idx}"
                metadata = {
                    "source": doc["source"],
                    "file_type": doc["file_type"],
                    "chunk_index": idx,
                    "md5": md5_hash
                }

                try:
                    self.collection.add(
                        documents=[chunk],
                        metadatas=[metadata],
                        ids=[chunk_id]
                    )

                    # 保存MD5记录
                    self._save_md5(md5_hash, {
                        "chunk_id": chunk_id,
                        "source": doc["source"],
                        "chunk_index": idx
                    })

                    stats["stored_chunks"] += 1
                except Exception as e:
                    print(f"存储chunk失败: {e}")

        return stats

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """语义搜索知识库"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })

            return formatted_results
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    def rebuild_index(self):
        """重建知识库索引"""
        print("开始重建知识库索引...")
        documents = self.load_documents()
        print(f"加载了 {len(documents)} 个文档")

        stats = self.process_and_store(documents)
        print(f"处理完成: {stats}")

        return stats
know = KnowledgeBase()
know.rebuild_index()
print(know.search("相关性分析是啥",3))