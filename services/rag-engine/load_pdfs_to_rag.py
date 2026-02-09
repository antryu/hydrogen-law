"""
PDF 파일에서 법령 텍스트 추출 → RAG 저장
"""

import logging
import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(__file__))

from src.embeddings import KoreanEmbedder, LawChunker, LawChunk, VectorStore

try:
    import PyPDF2
except ImportError:
    print("❌ PyPDF2가 설치되지 않았습니다.")
    print("설치: pip install PyPDF2")
    sys.exit(1)


def extract_text_from_pdf(pdf_path: str) -> str:
    """PDF에서 텍스트 추출"""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"   총 {len(pdf_reader.pages)}페이지")

            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                text_parts.append(page_text)

                if page_num % 10 == 0:
                    print(f"   진행: {page_num}/{len(pdf_reader.pages)} 페이지")

            return "\n".join(text_parts)
    except FileNotFoundError:
        logger.error(f"File not found: {pdf_path}")
        return ""
    except PyPDF2.errors.PdfReadError as e:
        logger.error(f"Failed to read PDF {pdf_path}: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error reading {pdf_path}: {e}")
        return ""


def parse_law_text(text: str, law_name: str, law_id: str) -> List[Dict[str, Any]]:
    """법령 텍스트를 조문 단위로 파싱"""

    # 조문 패턴: 제1조, 제2조, 제1조의2 등 (제목이 없는 경우도 포함)
    article_pattern = re.compile(r"제(\d+)조(?:의\d+)?\s*(?:\(([^)]+)\))?")


    articles = []
    seen_articles = set()  # 중복 제거용
    matches = list(article_pattern.finditer(text))

    print(f"\n   발견된 조문: {len(matches)}개")

    for i, match in enumerate(matches):
        article_number = f"제{match.group(1)}조"
        title = match.group(2) or ""

        # 중복 조문 건너뛰기
        article_key = (law_id, article_number)
        if article_key in seen_articles:
            continue

        seen_articles.add(article_key)

        # 조문 내용: 현재 조문부터 다음 조문 전까지
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        content = text[start:end].strip()

        # 너무 짧은 내용 제외
        if len(content) > 10:
            articles.append(
                {
                    "law_id": law_id,
                    "law_name": law_name,
                    "article_number": article_number,
                    "title": title,
                    "content": content[:2000],  # 최대 2000자
                }
            )

    return articles


def main():
    """메인 함수"""

    # PDF 파일 경로
    pdf_dir = Path("/Users/andrew/Thairon/KGS")

    pdf_files = [
        {
            "path": pdf_dir / "고압가스 안전관리법(법률)(제21065호)(20260102).pdf",
            "law_name": "고압가스 안전관리법",
            "law_id": "276461",
            "law_type": "법률",
        },
        {
            "path": pdf_dir
            / "고압가스 안전관리법 시행령(대통령령)(제35803호)(20251001).pdf",
            "law_name": "고압가스 안전관리법 시행령",
            "law_id": "278293",
            "law_type": "시행령",
        },
        {
            "path": pdf_dir
            / "고압가스 안전관리법 시행규칙(산업통상부령)(제00001호)(20251001).pdf",
            "law_name": "고압가스 안전관리법 시행규칙",
            "law_id": "278693",
            "law_type": "시행규칙",
        },
    ]

    print("=" * 60)
    print("PDF → RAG 저장")
    print("=" * 60)

    all_chunks = []

    for pdf_info in pdf_files:
        print(f"\n{'='*60}")
        print(f"📄 {pdf_info['law_name']}")
        print(f"{'='*60}")

        if not pdf_info["path"].exists():
            print(f"❌ 파일 없음: {pdf_info['path']}")
            continue

        # 1. PDF 텍스트 추출
        print(f"\n1️⃣ PDF 텍스트 추출 중...")
        text = extract_text_from_pdf(str(pdf_info["path"]))
        print(f"   ✅ {len(text)} 문자 추출")

        # 2. 조문 파싱
        print(f"\n2️⃣ 조문 파싱 중...")
        articles = parse_law_text(text, pdf_info["law_name"], pdf_info["law_id"])
        print(f"   ✅ {len(articles)}개 조문 파싱 완료")

        # 3. 청킹
        print(f"\n3️⃣ 청킹 중...")
        chunker = LawChunker()

        for article in articles:
            chunks = chunker.chunk_article(
                law_id=article["law_id"],
                law_name=article["law_name"],
                article_number=article["article_number"],
                title=article["title"],
                content=article["content"],
            )
            all_chunks.extend(chunks)

        print(f"   ✅ {len(all_chunks)}개 청크 생성 (누적)")

    # 4. 벡터 DB 저장
    print(f"\n{'='*60}")
    print(f"4️⃣ 벡터 DB 저장 중...")
    print(f"{'='*60}")

    embedder = KoreanEmbedder()
    vector_store = VectorStore(collection_name="hydrogen_law", embedder=embedder)

    # 기존 데이터 삭제
    vector_store.reset()

    # 청크 저장
    vector_store.add_chunks(all_chunks)

    # 통계
    stats = vector_store.get_stats()
    print(f"\n✅ 저장 완료!")
    print(f"   총 문서: {stats['total_documents']}개")
    print(f"   임베딩 차원: {stats['embedding_dimension']}")

    # 5. 검색 테스트
    print(f"\n{'='*60}")
    print(f"5️⃣ 검색 테스트")
    print(f"{'='*60}")

    test_query = "고압가스 제조 허가"
    print(f"\n🔍 쿼리: '{test_query}'")

    results = vector_store.search(test_query, top_k=3)

    for i, result in enumerate(results, 1):
        print(
            f"\n{i}. {result['metadata']['law_name']} {result['metadata']['article_number']}"
        )
        print(f"   제목: {result['metadata']['title']}")
        print(f"   유사도: {result['similarity_score']:.3f}")
        print(f"   내용: {result['content'][:100]}...")


if __name__ == "__main__":
    main()
