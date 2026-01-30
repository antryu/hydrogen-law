import os
from supabase import create_client

# Get Supabase credentials
supabase_url = "https://ygohwygdwbckgtotlogm.supabase.co"
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_key:
    with open("apps/web/.env.local") as f:
        for line in f:
            if "SUPABASE_SERVICE_ROLE_KEY" in line:
                supabase_key = line.split("=")[1].strip()

supabase = create_client(supabase_url, supabase_key)

# Check how many documents contain "충전"
result = supabase.from_("law_documents") \
    .select("id, content, metadata") \
    .like("content", "%충전%") \
    .execute()

print(f"Total documents containing '충전': {len(result.data)}")
print("\nFirst few documents:")
for i, doc in enumerate(result.data[:5]):
    print(f"\n{i+1}. {doc['id']}")
    print(f"   Law: {doc['metadata'].get('law_name', 'Unknown')}")
    print(f"   Article: {doc['metadata'].get('article_number', 'Unknown')}")
    # Count occurrences
    count = doc['content'].count('충전')
    print(f"   Occurrences of '충전': {count}")

# Now test the search function
search_result = supabase.rpc('search_law_documents', {
    'search_query': '충전',
    'max_results': 10
}).execute()

print(f"\n\nSearch function returned: {len(search_result.data)} results")
for i, doc in enumerate(search_result.data):
    print(f"{i+1}. {doc['id']} - Score: {doc['relevance_score']}")
