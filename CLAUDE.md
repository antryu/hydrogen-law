# CLAUDE.md - hydrogen-law-rag

## Project Overview

Hydrogen Law RAG System (수소법률 RAG 시스템) - A RAG-based legal search and compliance system for Korean hydrogen-related laws from the National Law Information Center (국가법령정보센터).

**Key Design Principle**: LLM-minimal approach. 90% of searches use pure vector + BM25 retrieval. LLM is only used for complex interpretation when explicitly requested.

## Tech Stack

- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS 3 (shadcn/ui components)
- **Backend API**: Next.js API routes (apps/web/src/app/api/)
- **RAG Engine**: Python 3.10+ + FastAPI + uvicorn
- **Vector DB**: ChromaDB (dev) / Pinecone (production)
- **Database**: PostgreSQL via Supabase (@supabase/supabase-js)
- **Embeddings**: jhgan/ko-sroberta-multitask (Korean-optimized, 768 dimensions)
- **Search**: Hybrid retrieval (vector 0.7 + BM25 0.3)
- **LLM**: Claude 3.5 Sonnet (optional, for AI summaries only)

## Directory Structure

```
hydrogen-law-rag/
├── apps/
│   ├── web/                  # Next.js frontend + API routes
│   │   ├── src/app/          # App router pages & API
│   │   ├── src/components/   # React components (shadcn/ui)
│   │   ├── src/lib/          # Utilities
│   │   └── src/types/        # TypeScript types
│   ├── api/                  # (Placeholder) Node.js backend
│   ├── mobile/               # (Placeholder) React Native app
│   └── desktop/              # (Placeholder) Desktop app
├── services/
│   └── rag-engine/           # Python RAG service
│       ├── src/
│       │   ├── collectors/   # Law data collectors & parsers
│       │   ├── embeddings/   # Embedder, chunker, vector store
│       │   └── retrieval/    # Hybrid retriever (vector + BM25)
│       ├── main.py           # FastAPI entrypoint
│       ├── load_pdfs_to_rag.py  # PDF ingestion pipeline
│       ├── law_config.yaml   # Law collection configuration
│       └── chroma_db/        # Local ChromaDB data
├── packages/
│   ├── shared-types/         # Shared TypeScript types (@hydrogen-law/shared-types)
│   └── ui-components/        # (Placeholder) Shared UI components
└── scripts/                  # Utility scripts
```

## Commands

### Frontend (apps/web/)
```bash
cd apps/web
npm run dev          # Dev server with Turbopack
npm run build        # Production build
npm run lint         # ESLint
npm run type-check   # TypeScript type checking
```

### RAG Engine (services/rag-engine/)
```bash
cd services/rag-engine
pip install -r requirements.txt         # Install dependencies
uvicorn main:app --reload               # Start FastAPI dev server (port 8000)
python load_pdfs_to_rag.py              # Ingest PDF law documents into ChromaDB
pytest                                  # Run tests
black .                                 # Format Python code
```

### Shared Types (packages/shared-types/)
```bash
cd packages/shared-types
npm run type-check   # TypeScript type checking
```

## Environment Variables

Reference: `services/rag-engine/.env.example`

| Variable | Required | Description |
|----------|----------|-------------|
| `LAW_API_KEY` | Yes | 국가법령정보센터 API key (data.go.kr) |
| `DATABASE_URL` | Yes | PostgreSQL connection string (Supabase) |
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase project URL (frontend) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase anon key (frontend) |
| `PINECONE_API_KEY` | No | Pinecone API key (production only) |
| `ANTHROPIC_API_KEY` | No | Claude API key (optional AI features) |

## Conventions

- **Python**: snake_case, formatted with `black`
- **TypeScript**: camelCase for variables/functions, PascalCase for components
- **Commits**: Conventional Commits (feat/fix/refactor)
- **Korean law structure**: 장(Chapter) > 조(Article) > 항(Paragraph) > 호(Item) > 목(Subitem)
- **Chunking**: Articles < 500 chars = single chunk; longer articles split by paragraph (항)

## Key APIs

### RAG Engine (FastAPI - port 8000)
- `GET /` - Health check
- `POST /search` - Hybrid law search (vector + BM25)
- `POST /compliance/check` - Rule-based compliance check (WIP)
- `POST /ai-summary` - Optional LLM summary (WIP)

### Frontend API Routes (Next.js)
- `POST /api/search` - Search proxy to Supabase

## Testing

```bash
# RAG Engine
cd services/rag-engine
pytest                                  # Unit tests
python test_hybrid_search.py            # Integration search test

# Frontend
cd apps/web
npm run lint && npm run build           # Lint + build check
```

## Law PDFs

The project includes Korean law PDFs (고압가스 안전관리법 and related regulations) at the project root. These are ingested via `load_pdfs_to_rag.py` into ChromaDB for vector search.
