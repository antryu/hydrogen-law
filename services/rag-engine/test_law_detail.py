"""
조문 상세 조회 테스트
"""

import os
import urllib.parse
import urllib.request

api_key = os.getenv("LAW_API_KEY")

# 수소법 ID로 상세 조회 테스트
law_id = "276545"  # 수소경제 육성 및 수소 안전관리에 관한 법률

# 엔드포인트 1: 기존 DRF (조문 상세)
url1 = "http://www.law.go.kr/DRF/lawService.do"
params1 = {
    "OC": api_key,
    "target": "law",
    "MST": law_id,
    "type": "XML"
}

print("="*60)
print("테스트 1: 기존 DRF API (lawService.do)")
print("="*60)
print(f"URL: {url1}")
print(f"법령 ID: {law_id}")

try:
    full_url = f"{url1}?{urllib.parse.urlencode(params1)}"
    with urllib.request.urlopen(full_url, timeout=30) as response:
        raw_xml = response.read().decode('utf-8')

        # 처음 30줄만 출력
        lines = raw_xml.split('\n')
        print(f"\n응답 (처음 30줄):")
        print("="*60)
        for i, line in enumerate(lines[:30], 1):
            print(f"{i:3d} | {line}")

        if len(lines) > 30:
            print(f"\n... ({len(lines) - 30}줄 더 있음)")

        # XML 파일로 저장
        with open("law_detail_response.xml", 'w', encoding='utf-8') as f:
            f.write(raw_xml)
        print(f"\n✅ 전체 응답을 'law_detail_response.xml'에 저장")

except Exception as e:
    print(f"❌ 오류: {e}")
