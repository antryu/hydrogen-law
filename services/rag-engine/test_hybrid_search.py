"""
하이브리드 검색 테스트 (벡터 + BM25)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.embeddings import KoreanEmbedder, VectorStore
from src.retrieval import HybridRetriever

def main():
    """하이브리드 검색 테스트"""

    print("="*60)
    print("하이브리드 검색 테스트")
    print("="*60)

    # 1. 벡터 스토어 로드
    print(f"\n1️⃣ 벡터 DB 로드 중...")
    embedder = KoreanEmbedder()
    vector_store = VectorStore(
        collection_name="hydrogen_law",
        embedder=embedder
    )

    stats = vector_store.get_stats()
    print(f"   ✅ {stats['total_documents']}개 문서 로드 완료")

    # 2. 하이브리드 검색기 초기화
    print(f"\n2️⃣ 하이브리드 검색기 초기화 중...")

    retriever = HybridRetriever(vector_store)

    # BM25 인덱스 구축 (벡터 DB의 모든 문서)
    documents = []
    for i in range(stats['total_documents']):
        # ChromaDB에서 문서 가져오기
        result = vector_store.collection.get(
            limit=stats['total_documents'],
            include=['documents', 'metadatas']
        )

        for doc, metadata in zip(result['documents'], result['metadatas']):
            documents.append({
                "id": metadata.get('chunk_id', ''),
                "content": doc,
                "metadata": metadata
            })
        break  # 한 번만 가져오기

    retriever.build_bm25_index(documents)
    print(f"   ✅ BM25 인덱스 구축 완료 ({len(documents)}개 문서)")

    # 3. 검색 테스트
    test_queries = [
        "고압가스 제조 허가",
        "수소충전소 설치 기준",
        "안전검사 주기",
        "고압가스 저장",
        "시설 기준"
    ]

    print(f"\n{'='*60}")
    print(f"3️⃣ 검색 테스트")
    print(f"{'='*60}")

    for query in test_queries:
        print(f"\n🔍 쿼리: '{query}'")
        print("-"*60)

        results = retriever.search(query, top_k=3)

        print(f"검색 결과: {results['total_found']}건")
        print(f"검색 시간: {results['metadata']['search_time_ms']:.2f}ms")
        print(f"LLM 사용: {results['metadata']['llm_used']}")

        for i, article in enumerate(results['articles'], 1):
            print(f"\n  {i}. {article['law_name']} {article['article_number']}")
            print(f"     제목: {article['title']}")
            print(f"     관련도: {article['relevance_score']:.2f}")
            print(f"     내용: {article['content'][:80]}...")

if __name__ == "__main__":
    main()
