"""
필수 법령 데이터 수집 (검증 버전)
1. 고압가스 안전관리법
2. 수소경제 육성 및 수소 안전관리에 관한 법률
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.collectors import LawAPIClient

def collect_both_laws():
    """두 개의 필수 법령 수집"""

    print("="*60)
    print("필수 법령 데이터 수집")
    print("="*60)

    # API 클라이언트
    try:
        client = LawAPIClient()
        print(f"\n✅ API 클라이언트 초기화 완료")
    except ValueError as e:
        print(f"\n❌ {e}")
        return None

    # 수집할 법령
    target_laws = [
        {
            "keyword": "수소경제 육성 및 수소 안전관리에 관한 법률",
            "short_name": "수소법"
        },
        {
            "keyword": "고압가스 안전관리",
            "short_name": "고압가스법"
        }
    ]

    all_laws = []

    for target in target_laws:
        print(f"\n{'='*60}")
        print(f"🔍 '{target['keyword']}' 검색 중...")
        print(f"{'='*60}")

        # 검색
        laws = client.search_laws(target["keyword"], display=10)

        if not laws:
            print(f"❌ '{target['keyword']}' 검색 결과 없음")
            continue

        print(f"\n✅ {len(laws)}개 법령 발견:")
        for i, law in enumerate(laws, 1):
            print(f"   {i}. {law.law_name} ({law.law_type})")
            print(f"      ID: {law.law_id}")
            print(f"      시행일: {law.enforcement_date}")

        # 모든 법령 저장
        all_laws.extend(laws)

    print(f"\n{'='*60}")
    print(f"✅ 법령 검색 완료!")
    print(f"   총 {len(all_laws)}개 법령 발견")
    print(f"{'='*60}")

    return all_laws

if __name__ == "__main__":
    collect_both_laws()
