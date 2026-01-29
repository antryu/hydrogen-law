"""
검색 API 응답 구조 확인
"""

import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

api_key = os.getenv("LAW_API_KEY")

# 공공데이터포털 API로 검색
url = "https://apis.data.go.kr/1170000/law/lawSearchList.do"

params = {
    "serviceKey": api_key,
    "target": "law",
    "query": "수소",
    "numOfRows": 1,  # 1개만
    "pageNo": 1
}

print("="*60)
print("검색 API 응답 구조 확인")
print("="*60)

try:
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(full_url, timeout=30) as response:
        raw_xml = response.read().decode('utf-8')

        print(f"\n원시 XML 응답:")
        print("="*60)
        print(raw_xml)
        print("="*60)

        # XML 파싱
        root = ET.fromstring(raw_xml)

        # 모든 요소 출력
        print(f"\n\nXML 구조 분석:")
        print("="*60)

        def print_element(elem, level=0):
            indent = "  " * level
            text = elem.text.strip() if elem.text and elem.text.strip() else ""
            print(f"{indent}{elem.tag}: {text[:100]}")
            for child in elem:
                print_element(child, level + 1)

        print_element(root)

except Exception as e:
    print(f"❌ 오류: {e}")
    import traceback
    traceback.print_exc()
