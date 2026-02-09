"""
law_documents.json → Supabase 업로드 스크립트

사용법:
  export SUPABASE_URL='https://your-project.supabase.co'
  export SUPABASE_KEY='your-service-role-key'
  python upload_to_supabase.py
"""

import json
import os
import sys

from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("SUPABASE_URL 또는 SUPABASE_KEY 환경 변수가 설정되지 않았습니다.")
    print()
    print("  export SUPABASE_URL='https://your-project.supabase.co'")
    print("  export SUPABASE_KEY='your-service-role-key'")
    sys.exit(1)

# Load documents
with open(os.path.join(os.path.dirname(__file__), "law_documents.json"), "r", encoding="utf-8") as f:
    documents = json.load(f)

print(f"법률 문서 {len(documents)}개 로드 완료")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

uploaded = 0
failed = 0

for i, doc in enumerate(documents, 1):
    try:
        data = {
            "id": doc["id"],
            "content": doc["content"],
            "metadata": doc["metadata"],
        }
        supabase.table("law_documents").upsert(data).execute()
        uploaded += 1
    except Exception as e:
        failed += 1
        print(f"  실패 ({doc['id']}): {e}")

    if i % 10 == 0 or i == len(documents):
        print(f"  진행: {i}/{len(documents)} (성공: {uploaded}, 실패: {failed})")

print()
print(f"업로드 완료: 성공 {uploaded}개, 실패 {failed}개")

if uploaded > 0:
    print()
    print("Vercel 환경변수를 설정하세요:")
    print(f"  NEXT_PUBLIC_SUPABASE_URL={SUPABASE_URL}")
    print("  SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>")
