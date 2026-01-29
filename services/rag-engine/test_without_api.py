"""
API 키 없이 테스트 - 샘플 데이터 사용

실제 법령 데이터 구조를 시뮬레이션
"""

import sys
import os

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

from src.embeddings import KoreanEmbedder, LawChunker, LawChunk, VectorStore
from src.retrieval import HybridRetriever

# 샘플 법령 데이터 (실제 법령 구조)
SAMPLE_LAWS = [
    {
        "law_id": "001234",
        "law_name": "수소경제 육성 및 수소 안전관리에 관한 법률",
        "article_number": "제1조",
        "title": "목적",
        "content": "이 법은 수소경제 육성과 수소 안전관리에 필요한 사항을 규정함으로써 수소경제로의 전환을 촉진하고 수소의 안전한 사용을 도모하여 국민경제의 지속가능한 발전과 국민의 안전을 확보하는 것을 목적으로 한다."
    },
    {
        "law_id": "001234",
        "law_name": "수소경제 육성 및 수소 안전관리에 관한 법률",
        "article_number": "제18조",
        "title": "수소충전소의 설치·운영",
        "content": "수소충전소를 설치·운영하려는 자는 산업통상자원부령으로 정하는 바에 따라 시·도지사의 허가를 받아야 한다. 수소충전소의 시설기준 및 기술기준은 산업통상자원부령으로 정한다."
    },
    {
        "law_id": "005678",
        "law_name": "고압가스 안전관리법",
        "article_number": "제3조",
        "title": "정의",
        "content": "이 법에서 사용하는 용어의 뜻은 다음과 같다. 1. 고압가스란 압축·액화 그 밖의 방법으로 처리하여 상용의 온도에서 압력이 대기압을 초과하는 것을 말한다."
    },
    {
        "law_id": "005678",
        "law_name": "고압가스 안전관리법",
        "article_number": "제5조",
        "title": "고압가스 제조의 허가",
        "content": "고압가스를 제조하려는 자는 산업통상자원부령으로 정하는 바에 따라 시·도지사의 허가를 받아야 한다. 제조시설의 안전관리와 검사기준은 대통령령으로 정한다."
    }
]

def test_chunking():
    """청킹 테스트"""
    print("\n=== 1. 청킹 테스트 ===")
    chunker = LawChunker(max_chunk_size=512, overlap=50)

    all_chunks = []
    for law in SAMPLE_LAWS:
        chunks = chunker.chunk_article(
            law_id=law["law_id"],
            law_name=law["law_name"],
            article_number=law["article_number"],
            title=law["title"],
            content=law["content"]
        )
        all_chunks.extend(chunks)

        print(f"✅ {law['article_number']} {law['title']}: {len(chunks)}개 청크")

    print(f"\n총 {len(all_chunks)}개 청크 생성")
    return all_chunks

def test_embedding(chunks):
    """임베딩 테스트"""
    print("\n=== 2. 임베딩 테스트 ===")
    print("한국어 임베딩 모델 로딩 중...")

    embedder = KoreanEmbedder()

    # 테스트 텍스트
    test_texts = [
        "수소충전소 설치 기준",
        "고압가스 안전 관리"
    ]

    embeddings = embedder.embed(test_texts)
    print(f"✅ 임베딩 생성 완료")
    print(f"   차원: {embeddings.shape}")
    print(f"   모델: {embedder.model_name}")

    return embedder

def test_vector_store(chunks, embedder):
    """벡터 스토어 테스트"""
    print("\n=== 3. 벡터 스토어 테스트 ===")

    # 벡터 스토어 생성
    vector_store = VectorStore(
        collection_name="test_hydrogen_law",
        persist_directory="./test_chroma_db",
        embedder=embedder
    )

    # 초기화
    vector_store.reset()

    # 청크 추가
    vector_store.add_chunks(chunks)

    # 통계
    stats = vector_store.get_stats()
    print(f"✅ 벡터 DB 구축 완료")
    print(f"   저장된 문서: {stats['total_documents']}개")
    print(f"   임베딩 차원: {stats['embedding_dimension']}")

    return vector_store

def test_search(vector_store):
    """검색 테스트"""
    print("\n=== 4. 검색 테스트 ===")

    # 테스트 쿼리
    test_queries = [
        "수소충전소 설치 기준",
        "고압가스 안전",
        "수소 제조 허가"
    ]

    for query in test_queries:
        print(f"\n🔍 쿼리: '{query}'")

        results = vector_store.search(query, top_k=3)

        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['metadata']['law_name']} {result['metadata']['article_number']}")
            print(f"      유사도: {result['similarity_score']:.3f}")
            print(f"      내용: {result['content'][:80]}...")

def test_hybrid_search(vector_store, chunks):
    """하이브리드 검색 테스트"""
    print("\n=== 5. 하이브리드 검색 테스트 ===")

    # 하이브리드 검색기
    retriever = HybridRetriever(vector_store)

    # BM25 인덱스 구축
    documents = [
        {
            "id": chunk.chunk_id,
            "content": chunk.content,
            "metadata": {
                "law_name": chunk.law_name,
                "article_number": chunk.article_number,
                "title": chunk.title
            }
        }
        for chunk in chunks
    ]
    retriever.build_bm25_index(documents)

    # 검색
    query = "수소충전소 설치"
    print(f"\n🔍 하이브리드 검색: '{query}'")

    results = retriever.search(query, top_k=3)

    print(f"\n검색 결과: {results['total_found']}건")
    print(f"검색 시간: {results['metadata']['search_time_ms']:.2f}ms")
    print(f"LLM 사용: {results['metadata']['llm_used']}")

    for i, article in enumerate(results['articles'], 1):
        print(f"\n{i}. {article['law_name']} {article['article_number']}")
        print(f"   제목: {article['title']}")
        print(f"   관련도: {article['relevance_score']:.2f}")
        print(f"   내용: {article['content'][:100]}...")

def main():
    """메인 테스트"""
    print("=" * 60)
    print("수소법률 RAG 시스템 - 통합 테스트 (API 키 없음)")
    print("=" * 60)

    try:
        # 1. 청킹
        chunks = test_chunking()

        # 2. 임베딩
        embedder = test_embedding(chunks)

        # 3. 벡터 스토어
        vector_store = test_vector_store(chunks, embedder)

        # 4. 검색
        test_search(vector_store)

        # 5. 하이브리드 검색
        test_hybrid_search(vector_store, chunks)

        print("\n" + "=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)

        print("\n다음 단계:")
        print("1. API 키 발급: https://www.data.go.kr/data/15000115/openapi.do")
        print("2. export LAW_API_KEY='your_key'")
        print("3. 실제 법령 데이터 수집")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
