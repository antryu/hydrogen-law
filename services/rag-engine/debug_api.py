"""
API XML 응답 디버깅 스크립트
원시 XML 응답을 확인하여 파싱 오류 원인 파악
"""

import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))

def test_api_raw():
    """원시 API 응답 확인"""

    api_key = os.getenv("LAW_API_KEY")
    if not api_key:
        print("❌ LAW_API_KEY 환경변수가 설정되지 않았습니다.")
        return

    # 간단한 키워드로 테스트
    keyword = "수소"
    base_url = "http://www.law.go.kr/DRF/lawSearch.do"

    params = {
        "OC": api_key,
        "target": "law",
        "query": keyword,
        "display": "5",
        "type": "XML"
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    print("="*60)
    print(f"API URL: {url[:100]}...")
    print("="*60)

    try:
        # API 호출
        with urllib.request.urlopen(url, timeout=30) as response:
            raw_xml = response.read().decode('utf-8')

            print("\n✅ API 응답 수신 완료")
            print(f"응답 길이: {len(raw_xml)} bytes\n")

            # 첫 50줄만 출력
            lines = raw_xml.split('\n')
            print("="*60)
            print("원시 XML 응답 (처음 50줄):")
            print("="*60)
            for i, line in enumerate(lines[:50], 1):
                print(f"{i:3d} | {line}")

            if len(lines) > 50:
                print(f"\n... ({len(lines) - 50}줄 더 있음)")

            # XML 파일로 저장
            debug_file = "debug_response.xml"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(raw_xml)

            print(f"\n✅ 전체 응답을 '{debug_file}'에 저장했습니다.")

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_raw()
