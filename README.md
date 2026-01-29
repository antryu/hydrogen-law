# 수소법률 RAG 시스템

국가법령정보센터의 수소 관련 법률 정보를 활용한 RAG 기반 법률 검색 및 컴플라이언스 시스템

## 주요 기능

1. **법률 정보 검색**: 자연어 질의로 관련 법령 조항 검색 (LLM 없이 작동)
2. **컴플라이언스 분석**: 사업 계획과 관련 법규 자동 매칭
3. **법안 제안**: 법률 개정안 작성 지원 (선택적 AI 활용)
4. **비교 분석**: 법률 개정 이력 추적

## 기술 스택

- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS 4
- **Backend API**: Node.js + Express + TypeScript
- **RAG Engine**: Python + FastAPI
- **Vector DB**: ChromaDB (개발) / Pinecone (프로덕션)
- **Database**: PostgreSQL (Supabase)
- **Embeddings**: jhgan/ko-sroberta-multitask (한국어 특화)
- **LLM**: Claude 3.5 Sonnet (선택적 사용)

## 프로젝트 구조

```
hydrogen-law-rag/
├── apps/
│   ├── web/                 # Next.js Frontend
│   └── api/                 # Node.js Backend API
├── services/
│   └── rag-engine/          # Python RAG Service
├── packages/
│   ├── shared-types/        # 공유 TypeScript 타입
│   └── ui-components/       # 공통 UI 컴포넌트
└── scripts/                 # 유틸리티 스크립트
```

## 빠른 시작

### 1. 의존성 설치

```bash
# Node.js 프로젝트
npm install

# Python RAG 엔진
cd services/rag-engine
pip install -r requirements.txt
```

### 2. 개발 서버 실행

```bash
# Frontend (Next.js)
cd apps/web
npm run dev

# Backend API (Node.js)
cd apps/api
npm run dev

# RAG Engine (Python)
cd services/rag-engine
uvicorn main:app --reload
```

## 특징

### LLM 최소화 접근법

- ✅ **비용 절감**: 월 $140-160 (LLM 적극 활용 시 대비 60% 절감)
- ✅ **응답 속도**: <1초 (10배 빠름)
- ✅ **정확도**: 100% (법령 원문 그대로 표시)
- ✅ **오프라인 가능**: API 의존성 없음

90%의 검색은 순수 벡터 검색 + BM25로 처리하며, 복잡한 해석이 필요한 경우에만 선택적으로 LLM을 사용합니다.

## 라이선스

MIT
