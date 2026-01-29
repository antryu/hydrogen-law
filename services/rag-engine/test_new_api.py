"""
수정된 API 엔드포인트 테스트
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.collectors import LawAPIClient

def test_api():
    """API 연결 테스트"""

    print("="*60)
    print("수정된 API 엔드포인트 테스트")
    print("="*60)

    # API 클라이언트
    try:
        client = LawAPIClient()
        print(f"\n✅ API 클라이언트 초기화 완료")
    except ValueError as e:
        print(f"\n❌ {e}")
        return

    # 간단한 검색
    print(f"\n{'='*60}")
    print(f"🔍 '수소' 검색 중...")
    print(f"{'='*60}")

    laws = client.search_laws("수소", display=5)

    if not laws:
        print(f"❌ 검색 결과 없음")
        return

    print(f"\n✅ {len(laws)}개 법령 발견:\n")
    for i, law in enumerate(laws, 1):
        print(f"{i}. {law.law_name}")
        print(f"   구분: {law.law_type}")
        print(f"   ID: {law.law_id}")
        print(f"   시행일: {law.enforcement_date}\n")

if __name__ == "__main__":
    test_api()
