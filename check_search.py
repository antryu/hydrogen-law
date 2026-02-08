import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables from .env.local if available
load_dotenv("apps/web/.env.local")

# Get Supabase credentials from environment
supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    print(
        "❌ SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY 환경 변수가 설정되지 않았습니다."
    )
    exit(1)

supabase = create_client(supabase_url, supabase_key)

# Check how many documents contain "충전"
result = (
    supabase.from_("law_documents")
    .select("id, content, metadata")
    .like("content", "%충전%")
    .execute()
)

print(f"Total documents containing '충전': {len(result.data)}")
print("\nFirst few documents:")
for i, doc in enumerate(result.data[:5]):
    print(f"\n{i+1}. {doc['id']}")
    print(f"   Law: {doc['metadata'].get('law_name', 'Unknown')}")
    print(f"   Article: {doc['metadata'].get('article_number', 'Unknown')}")
    # Count occurrences
    count = doc["content"].count("충전")
    print(f"   Occurrences of '충전': {count}")

# Now test the search function
search_result = supabase.rpc(
    "search_law_documents", {"search_query": "충전", "max_results": 10}
).execute()

print(f"\n\nSearch function returned: {len(search_result.data)} results")
for i, doc in enumerate(search_result.data):
    print(f"{i+1}. {doc['id']} - Score: {doc['relevance_score']}")
