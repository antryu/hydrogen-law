"""
ChromaDB에서 Supabase로 데이터 마이그레이션
"""

import os
from supabase import create_client, Client
from src.embeddings import VectorStore

# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ygohwygdwbckgtotlogm.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # 환경 변수에서 가져오기

if not SUPABASE_KEY:
    print("❌ SUPABASE_KEY 환경 변수가 설정되지 않았습니다.")
    print("Supabase Dashboard → Settings → API → anon/public key 복사")
    print("export SUPABASE_KEY='your-key-here'")
    exit(1)

# Supabase 클라이언트
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ChromaDB에서 데이터 가져오기
print("📊 ChromaDB에서 데이터 읽는 중...")
vector_store = VectorStore(collection_name="hydrogen_law")
stats = vector_store.get_stats()
print(f"총 문서: {stats['total_documents']}개")

# 모든 문서 가져오기
result = vector_store.collection.get(
    limit=stats['total_documents'],
    include=['documents', 'metadatas', 'embeddings']
)

print(f"\n🔄 Supabase로 마이그레이션 시작...")

# Supabase에 데이터 삽입
migrated = 0
failed = 0

for i, (doc_id, doc, metadata, embedding) in enumerate(
    zip(result['ids'], result['documents'], result['metadatas'], result['embeddings']),
    1
):
    try:
        # Supabase에 삽입 (embedding을 리스트로 변환)
        data = {
            "id": metadata.get('chunk_id', doc_id),
            "content": doc,
            "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
            "metadata": metadata
        }

        supabase.table("law_documents").upsert(data).execute()
        migrated += 1

        if i % 10 == 0:
            print(f"진행: {i}/{stats['total_documents']} ({migrated} 성공, {failed} 실패)")

    except Exception as e:
        failed += 1
        print(f"❌ 실패 ({doc_id}): {e}")

print(f"\n✅ 마이그레이션 완료!")
print(f"   성공: {migrated}개")
print(f"   실패: {failed}개")
print(f"   총: {stats['total_documents']}개")
