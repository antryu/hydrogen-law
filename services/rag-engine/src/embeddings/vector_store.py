"""
ChromaDB 벡터 스토어

개발 환경: ChromaDB (로컬)
프로덕션: Pinecone
"""

from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import numpy as np

from .embedder import KoreanEmbedder
from .chunker import LawChunk


class VectorStore:
    """벡터 데이터베이스 인터페이스"""

    def __init__(
        self,
        collection_name: str = "hydrogen_law",
        persist_directory: str = "./chroma_db",
        embedder: Optional[KoreanEmbedder] = None
    ):
        """
        Args:
            collection_name: 컬렉션 이름
            persist_directory: 데이터 저장 경로
            embedder: 임베딩 모델 (None이면 자동 생성)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # 임베딩 모델
        self.embedder = embedder or KoreanEmbedder()

        # ChromaDB 클라이언트
        print(f"ChromaDB 초기화 중: {persist_directory}")
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # 컬렉션 생성/로드
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "수소 관련 법령 벡터 데이터베이스"}
        )

        print(f"컬렉션 '{collection_name}' 준비 완료")
        print(f"저장된 문서 수: {self.collection.count()}")

    def add_chunks(self, chunks: List[LawChunk]) -> None:
        """
        청크를 벡터 DB에 추가

        Args:
            chunks: 법령 청크 리스트
        """
        if not chunks:
            return

        # 임베딩 생성
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedder.embed_documents(texts)

        # ChromaDB에 저장
        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = [
            {
                "law_id": chunk.law_id,
                "law_name": chunk.law_name,
                "article_number": chunk.article_number,
                "paragraph_number": chunk.paragraph_number,
                "title": chunk.title,
                "chunk_type": chunk.chunk_type,
                **chunk.metadata
            }
            for chunk in chunks
        ]

        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )

        print(f"✅ {len(chunks)}개 청크 추가 완료")

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        벡터 검색

        Args:
            query: 검색 쿼리
            top_k: 반환할 결과 수
            filters: 메타데이터 필터 (예: {"law_name": "수소법"})

        Returns:
            검색 결과 리스트
        """
        # 쿼리 임베딩
        query_embedding = self.embedder.embed_query(query)

        # 검색
        where = None
        if filters:
            where = filters

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where
        )

        # 결과 포맷팅
        formatted_results = []

        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'similarity_score': 1 - results['distances'][0][i] if 'distances' in results else None
                })

        return formatted_results

    def delete_collection(self) -> None:
        """컬렉션 삭제"""
        self.client.delete_collection(name=self.collection_name)
        print(f"컬렉션 '{self.collection_name}' 삭제 완료")

    def reset(self) -> None:
        """데이터베이스 초기화"""
        self.delete_collection()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "수소 관련 법령 벡터 데이터베이스"}
        )
        print("데이터베이스 초기화 완료")

    def get_stats(self) -> Dict:
        """통계 정보 반환"""
        count = self.collection.count()

        return {
            "collection_name": self.collection_name,
            "total_documents": count,
            "embedding_dimension": self.embedder.get_embedding_dimension(),
            "persist_directory": self.persist_directory
        }


# 사용 예시
if __name__ == "__main__":
    from chunker import LawChunker

    # 벡터 스토어 생성
    vector_store = VectorStore(collection_name="hydrogen_law_test")

    # 테스트 데이터
    chunker = LawChunker()

    test_chunks = chunker.chunk_article(
        law_id="001234",
        law_name="수소경제 육성 및 수소 안전관리에 관한 법률",
        article_number="제1조",
        title="목적",
        content="이 법은 수소경제 육성과 수소 안전관리에 필요한 사항을 규정함으로써 수소경제로의 전환을 촉진하고 수소의 안전한 사용을 도모하여 국민경제의 지속가능한 발전과 국민의 안전을 확보하는 것을 목적으로 한다."
    )

    # 청크 추가
    vector_store.add_chunks(test_chunks)

    # 검색
    print("\n=== 검색 테스트 ===")
    results = vector_store.search("수소 안전", top_k=3)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['metadata']['law_name']} {result['metadata']['article_number']}")
        print(f"   유사도: {result['similarity_score']:.3f}")
        print(f"   내용: {result['content'][:100]}...")

    # 통계
    print("\n=== 통계 ===")
    stats = vector_store.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

    # 초기화
    vector_store.reset()
