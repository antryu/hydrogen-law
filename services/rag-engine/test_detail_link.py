"""
법령상세링크 테스트
"""

import os
import urllib.parse
import urllib.request

api_key = os.getenv("LAW_API_KEY")

# 수소법 상세 링크 (OC를 우리 API 키로 변경)
base_url = "http://www.law.go.kr/DRF/lawService.do"

params = {
    "OC": api_key,  # 우리 API 키 사용
    "target": "law",
    "MST": "276545",  # 수소법 일련번호
    "type": "XML",  # XML 형식
    "efYd": "20251001"  # 시행일자
}

print("="*60)
print("법령상세링크 테스트 (OC를 API 키로 변경)")
print("="*60)

try:
    full_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print(f"URL: {full_url[:100]}...")

    with urllib.request.urlopen(full_url, timeout=30) as response:
        raw_xml = response.read().decode('utf-8')

        # 첫 50줄 출력
        lines = raw_xml.split('\n')
        print(f"\n응답 (처음 50줄):")
        print("="*60)

        for i, line in enumerate(lines[:50], 1):
            print(f"{i:3d} | {line}")

        if len(lines) > 50:
            print(f"\n... ({len(lines) - 50}줄 더 있음)")

        # HTML 오류 페이지인지 확인
        if "<!DOCTYPE html" in raw_xml[:200]:
            print("\n❌ HTML 오류 페이지 응답")
        elif "<?xml" in raw_xml[:100]:
            print("\n✅ XML 응답 받음!")

            # 파일로 저장
            with open("law_detail_success.xml", 'w', encoding='utf-8') as f:
                f.write(raw_xml)
            print(f"✅ 'law_detail_success.xml'에 저장")

except Exception as e:
    print(f"❌ 오류: {e}")
    import traceback
    traceback.print_exc()
