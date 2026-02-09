# v1.1 변경사항 및 검증 보고서

## 변경사항 요약

### 1. 검색 실패 수정 (fix)
- **문제**: 다중 키워드 검색 (예: "수소 안전")이 0건 반환
- **원인**: SQL `LIKE '%수소 안전%'`로 전체 문자열을 하나의 패턴으로 검색
- **해결**: 키워드를 분리하여 개별 검색 후 결과 병합, 다중 매칭 문서에 점수 부스트
- **파일**: `apps/web/src/app/api/search/route.ts`, `services/rag-engine/search_function.sql`

### 2. 일치율(%) 표시 삭제
- **변경**: 검색 결과 카드에서 relevance_score % 배지 제거
- **이유**: LIKE 기반 검색의 점수가 실제 관련도를 정확히 반영하지 않음
- **파일**: `apps/web/src/components/SearchResults.tsx`

### 3. 더보기/상세보기 버튼 추가
- **변경**: 긴 검색 결과(300자 초과)는 접힌 상태로 표시, "상세보기" 버튼 클릭 시 전체 내용 표시
- **UX**: 그라데이션 오버레이로 잘림 표시, "접기"/"상세보기" 토글
- **파일**: `apps/web/src/components/SearchResults.tsx` (ArticleCard 컴포넌트)

### 4. 법령 업로드 페이지 (feat)
- **URL**: `/upload`
- **기능**: PDF 업로드 → 자동 파싱 → 청킹 → 임베딩 → ChromaDB + Supabase 저장
- **파이프라인**: PDF 텍스트 추출 → 조문 파싱(제N조 패턴) → 512자 청킹 → ko-sroberta 임베딩 → DB 저장 → BM25 인덱스 재구축
- **네비게이션**: 헤더에 "법령 업로드" 링크 추가

#### 새로 생성된 파일
| 파일 | 설명 |
|------|------|
| `apps/web/src/app/upload/page.tsx` | 업로드 페이지 UI |
| `apps/web/src/app/api/upload/route.ts` | 업로드 API 프록시 (Next.js → RAG 엔진) |

#### 수정된 파일
| 파일 | 변경 내용 |
|------|-----------|
| `services/rag-engine/main.py` | `/upload` 엔드포인트 추가 (PDF 처리 + Supabase 저장) |
| `apps/web/src/app/layout.tsx` | 헤더에 업로드 링크, 로고 클릭 홈 이동 |

#### 업로드 데이터 흐름
```
[사용자] PDF 파일 선택 + 법령명 입력
    ↓
[프론트엔드] /upload 페이지 → POST /api/upload (FormData)
    ↓
[Next.js API] FormData 전달 → POST RAG_ENGINE_URL/upload
    ↓
[RAG 엔진] PyPDF2 텍스트 추출
    ↓
[RAG 엔진] 제N조 패턴 파싱 (regex)
    ↓
[RAG 엔진] LawChunker 512자 청킹
    ↓
[RAG 엔진] ko-sroberta 768차원 임베딩
    ↓
[RAG 엔진] ChromaDB 저장 + Supabase upsert
    ↓
[RAG 엔진] BM25 인덱스 재구축
    ↓
[프론트엔드] 결과 표시 (파싱된 조문 수, 청크 수, Supabase 저장 수)
```

---

## 코드 검증 보고서

### 검증 항목 및 결과

#### 1. 검색 파이프라인 무결성 - PASS
- 키워드 분리 로직 정상 (공백/콤마 구분)
- 다중 키워드 병합 로직 정상 (Map으로 중복 제거, 점수 합산)
- 점수 정규화 정상 (0-100 범위, maxScore 기반)
- 응답 형식이 TypeScript 타입과 일치

#### 2. 업로드 파이프라인 무결성 - PASS
- PDF → 텍스트 추출 → 조문 파싱 → 청킹 → 임베딩 → 저장 흐름 정상
- Supabase 저장 형식이 스키마와 일치 (id, content, embedding, metadata JSONB)
- 임시 파일 정리 (finally 블록에서 unlink)

#### 3. 프론트엔드-백엔드 계약 - PASS
- 검색 응답 형식: SearchResponse 타입과 일치
- 업로드 응답 형식: UploadResult 인터페이스와 일치
- DOMPurify 사용하여 XSS 방지

#### 4. 파싱 로직 일관성 - FIXED
- **이전**: `load_pdfs_to_rag.py`와 `main.py`의 regex 패턴 불일치
  - `load_pdfs_to_rag.py`: `r"제(\d+)조\s*\(([^)]+)\)"` (제목 필수)
  - `main.py`: `r"제(\d+)조(?:의\d+)?\s*(?:\(([^)]+)\))?"` (제목 선택)
- **수정**: `load_pdfs_to_rag.py`의 패턴을 `main.py`와 동일하게 변경

#### 5. SQL 함수 호환성 - PASS
- `search_law_documents` 함수의 입출력 형식이 API route와 일치
- 다중 키워드 OR 검색 지원 (SQL 함수 업데이트 완료)
- LIKE 와일드카드 이스케이프 적용

### 발견된 이슈 및 조치

| 이슈 | 심각도 | 상태 | 조치 |
|------|--------|------|------|
| 파싱 regex 패턴 불일치 | HIGH | 수정완료 | load_pdfs_to_rag.py 패턴 통일 |
| 하드코딩된 기본 법령명 | MEDIUM | 수정완료 | "(법령명 없음)"으로 변경 |
| Supabase JSONB 쿼리 방식 | MEDIUM | 수정완료 | `.contains()` → `.filter('metadata->>law_id', 'eq', ...)` |
| 프론트엔드가 벡터 검색 미사용 | LOW | 알려진 이슈 | 현재 LIKE 기반, 향후 hybrid_search 전환 권장 |

### 빌드 및 테스트 결과
- TypeScript 타입 체크: PASS
- Next.js 프로덕션 빌드: PASS
- Vitest 단위 테스트: 17/17 PASS
- ESLint: WARNING만 (미사용 import, 기능에 영향 없음)

---

## 사전 요구사항

### 업로드 기능 사용을 위한 요구사항

1. **RAG 엔진 실행**
   ```bash
   cd services/rag-engine
   pip install -r requirements.txt
   uvicorn main:app --reload  # port 8000
   ```

2. **환경 변수 설정**
   ```bash
   # RAG 엔진 (.env)
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-key-here

   # Next.js (.env.local)
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   RAG_ENGINE_URL=http://localhost:8000  # 기본값
   ```

3. **Supabase SQL 함수 배포**
   - `services/rag-engine/search_function.sql` → Supabase SQL Editor에서 실행
   - `services/rag-engine/supabase_schema.sql` → 테이블 및 인덱스 생성

---

## 향후 개선 사항

1. **하이브리드 검색 전환**: 현재 LIKE 기반 → `hybrid_search_law_documents` RRF 기반 전환
2. **업로드 배치 처리**: 여러 PDF 동시 업로드 지원
3. **법령 관리 페이지**: 업로드된 법령 목록 조회 및 삭제
4. **검색 필터**: 법령별, 조문 유형별 필터링
