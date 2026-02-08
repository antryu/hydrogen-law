"""
수소법률 RAG 엔진 - FastAPI 메인 엔트리포인트

LLM 최소화 접근법:
- 90% 순수 검색 (벡터 + BM25)
- 10% 선택적 LLM (사용자 요청 시만)
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any
import uvicorn

logger = logging.getLogger(__name__)

from src.embeddings import KoreanEmbedder, VectorStore
from src.retrieval import HybridRetriever

# 전역 변수로 검색 엔진 초기화
embedder = None
vector_store = None
retriever = None

app = FastAPI(
    title="수소법률 RAG 엔진",
    description="국가법령정보센터 기반 수소 관련 법률 검색 시스템",
    version="1.0.0",
)

# CORS 설정 (환경변수에서 허용 origin 로드)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# 요청/응답 모델
class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    filters: Optional[Dict[str, Any]] = None

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("검색어를 입력해주세요")
        if len(v) > 500:
            raise ValueError("검색어는 500자를 초과할 수 없습니다")
        return v

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, v: int) -> int:
        return max(1, min(v, 100))


class Article(BaseModel):
    id: str
    law_name: str
    article_number: str
    title: str
    content: str
    highlighted_content: str
    related_articles: List[Dict[str, str]]
    relevance_score: float


class SearchResponse(BaseModel):
    query: str
    total_found: int
    keywords: List[str]
    relevant_laws: List[str]
    articles: List[Article]
    metadata: Dict[str, Any]


class ComplianceRequest(BaseModel):
    business_type: str
    details: Dict[str, Any]


class ComplianceResponse(BaseModel):
    business_type: str
    checklist: List[Dict[str, Any]]
    summary: Dict[str, Any]
    risk_assessment: str
    metadata: Dict[str, Any]


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 검색 엔진 초기화"""
    global embedder, vector_store, retriever

    print("=" * 60)
    print("수소법률 RAG 엔진 시작")
    print("=" * 60)

    # 임베딩 모델 로드
    print("\n1️⃣ 임베딩 모델 로드 중...")
    embedder = KoreanEmbedder()

    # 벡터 DB 로드
    print("2️⃣ 벡터 DB 로드 중...")
    vector_store = VectorStore(collection_name="hydrogen_law", embedder=embedder)

    # BM25 인덱스 구축
    print("3️⃣ 하이브리드 검색 엔진 초기화 중...")
    retriever = HybridRetriever(vector_store)

    stats = vector_store.get_stats()
    total_docs = stats["total_documents"]
    documents = []

    # Batch loading to prevent OOM with large datasets
    batch_size = 500
    offset = 0
    while offset < total_docs:
        result = vector_store.collection.get(
            limit=batch_size,
            offset=offset,
            include=["documents", "metadatas"],
        )
        if not result["documents"]:
            break
        for doc, metadata in zip(result["documents"], result["metadatas"]):
            documents.append(
                {
                    "id": metadata.get("chunk_id", ""),
                    "content": doc,
                    "metadata": metadata,
                }
            )
        offset += batch_size

    retriever.build_bm25_index(documents)

    print(f"\n✅ 초기화 완료!")
    print(f"   문서 수: {stats['total_documents']}개")
    print(f"   임베딩 차원: {stats['embedding_dimension']}")
    print("=" * 60)


@app.get("/")
async def root():
    """헬스 체크"""
    return {
        "status": "healthy",
        "service": "수소법률 RAG 엔진",
        "version": "1.0.0",
        "llm_mode": "minimal (90% search, 10% optional)",
    }


@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "dependencies": {
            "vector_db": "not_initialized",
            "embedding_model": "not_loaded",
            "law_database": "not_connected",
        },
    }


@app.post("/search", response_model=SearchResponse)
async def search_laws(request: SearchRequest):
    """
    법률 검색 (LLM 없이 작동)

    하이브리드 검색:
    - 벡터 검색 (의미 기반)
    - BM25 (키워드 기반)
    """
    global retriever

    if retriever is None:
        raise HTTPException(
            status_code=503, detail="검색 엔진이 아직 초기화되지 않았습니다"
        )

    try:
        # 하이브리드 검색
        results = retriever.search(request.query, top_k=request.top_k)

        # 응답 변환
        articles = []
        for article in results["articles"]:
            articles.append(
                Article(
                    id=article["id"],
                    law_name=article["law_name"],
                    article_number=article["article_number"],
                    title=article["title"],
                    content=article["content"],
                    highlighted_content=article.get(
                        "highlighted_content", article["content"]
                    ),
                    related_articles=article.get("related_articles", []),
                    relevance_score=article["relevance_score"],
                )
            )

        return SearchResponse(
            query=results["query"],
            total_found=results["total_found"],
            keywords=results.get("keywords", []),
            relevant_laws=results.get("relevant_laws", []),
            articles=articles,
            metadata=results["metadata"],
        )

    except (KeyError, ValueError, AttributeError) as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="검색 처리 중 오류가 발생했습니다")
    except Exception as e:
        logger.critical(f"Unexpected search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="시스템 오류가 발생했습니다")


@app.post("/compliance/check", response_model=ComplianceResponse)
async def check_compliance(request: ComplianceRequest):
    """
    컴플라이언스 체크 (규칙 기반, LLM 없음)

    사업 유형별 필수 법령 매칭
    """
    # TODO: 규칙 기반 컴플라이언스 엔진 구현
    raise HTTPException(status_code=501, detail="컴플라이언스 엔진 구현 예정")


@app.post("/ai-summary")
async def ai_summary(request: Dict[str, Any]):
    """
    AI 요약 (선택적 LLM 사용)

    사용자가 명시적으로 요청할 때만 호출
    """
    # TODO: Claude API 통합
    raise HTTPException(status_code=501, detail="AI 요약 구현 예정")


@app.get("/laws")
async def list_laws():
    """수집된 법령 목록 조회"""
    # TODO: DB에서 법령 목록 조회
    return {"total_laws": 0, "laws": []}


@app.get("/laws/{law_id}")
async def get_law_detail(law_id: str):
    """특정 법령 상세 정보"""
    # TODO: DB에서 법령 상세 조회
    raise HTTPException(status_code=404, detail="법령을 찾을 수 없습니다")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
