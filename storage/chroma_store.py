import chromadb
from chromadb.config import Settings
from typing import List, Dict
from config import Config

class ChromaVectorStore:
    def __init__(self):
        self.client = chromadb.Client(Settings(
            persist_directory=Config.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False
        ))
        self.collection = self.client.get_or_create_collection("analysis_knowledge")

    def add_documents(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """添加文档到向量库"""
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query: str, n_results: int = 5) -> Dict:
        """向量检索"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    def add_analysis_result(self, analysis_id: str, content: str, metadata: Dict):
        """存储分析结果用于RAG"""
        self.add_documents(
            documents=[content],
            metadatas=[metadata],
            ids=[analysis_id]
        )
