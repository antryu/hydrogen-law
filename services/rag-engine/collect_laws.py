"""
실제 법령 데이터 수집 스크립트

국가법령정보센터 API를 사용하여
고압가스법 + 수소법 수집
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.collectors import LawAPIClient, LawParser
from src.embeddings import KoreanEmbedder, LawChunker, VectorStore

def collect_laws():
    """법령 수집"""
    print("=" * 60)
    print("실제 법령 데이터 수집")
    print("=" * 60)

    # API 클라이언트
    try:
        client = LawAPIClient()
        print(f"\n✅ API 클라이언트 초기화 완료")
    except ValueError as e:
        print(f"\n❌ {e}")
        return None

    # 수집할 법령
    target_laws = [
        {
            "keyword": "수소경제 육성 및 수소 안전관리에 관한 법률",
            "short_name": "수소법"
        },
        {
            "keyword": "고압가스 안전관리",
            "short_name": "고압가스법"
        }
    ]

    all_laws = []

    for target in target_laws:
        print(f"\n{'='*60}")
        print(f"🔍 '{target['keyword']}' 검색 중...")
        print(f"{'='*60}")

        # 검색
        laws = client.search_laws(target["keyword"], display=10)

        if not laws:
            print(f"❌ '{target['keyword']}' 검색 결과 없음")
            continue

        print(f"\n✅ {len(laws)}개 법령 발견:")
        for i, law in enumerate(laws, 1):
            print(f"   {i}. {law.law_name} ({law.law_type})")
            print(f"      ID: {law.law_id}")
            print(f"      시행일: {law.enforcement_date}")

        # 첫 번째 결과 사용
        selected_law = laws[0]
        all_laws.append(selected_law)

        print(f"\n📥 '{selected_law.law_name}' 상세 조회 중...")

        # 상세 정보
        detail = client.get_law_detail(selected_law.law_id)

        if detail:
            articles = detail.get('articles', [])
            print(f"✅ {len(articles)}개 조문 수집 완료")

            # 파싱
            parser = LawParser()
            parsed = parser.parse_from_api_response(detail)

            # 청킹
            chunker = LawChunker()
            all_chunks = []

            for article in parsed.articles[:5]:  # 처음 5개 조문만 테스트
                chunks = chunker.chunk_article(
                    law_id=parsed.law_id,
                    law_name=parsed.law_name,
                    article_number=article.article_number,
                    title=article.title,
                    content=article.content
                )
                all_chunks.extend(chunks)

            print(f"✅ {len(all_chunks)}개 청크 생성")

            # 벡터 DB 저장
            print(f"\n💾 벡터 DB 저장 중...")

            embedder = KoreanEmbedder()
            vector_store = VectorStore(
                collection_name="hydrogen_law_real",
                embedder=embedder
            )

            vector_store.add_chunks(all_chunks)

            print(f"✅ 저장 완료")

    print(f"\n{'='*60}")
    print(f"✅ 법령 수집 완료!")
    print(f"   수집된 법령: {len(all_laws)}개")
    print(f"{'='*60}")

    return all_laws

if __name__ == "__main__":
    collect_laws()
