"""
웹 스크래핑으로 법령 조문 수집
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.law.go.kr/%EB%B2%95%EB%A0%B9/%EA%B3%A0%EC%95%95%EA%B0%80%EC%8A%A4%EC%95%88%EC%A0%84%EA%B4%80%EB%A6%AC%EB%B2%95"

print("="*60)
print("고압가스안전관리법 웹 스크래핑")
print("="*60)

try:
    # 페이지 가져오기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.encoding = 'utf-8'

    print(f"\n✅ 페이지 다운로드 완료 ({len(response.text)} bytes)")

    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # HTML 구조 확인을 위해 일부 출력
    print("\n" + "="*60)
    print("HTML 구조 샘플:")
    print("="*60)

    # 본문 영역 찾기
    # 가능한 선택자들
    selectors = [
        'div.law_content',
        'div.lawcontent',
        'div#lawContent',
        'div.contbox',
        'article',
        'div.jo_article',
        'div[class*="article"]',
        'div[class*="jo"]'
    ]

    content_found = False
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            print(f"\n✅ 발견: '{selector}' - {len(elements)}개")
            content_found = True

            # 첫 번째 요소의 텍스트 일부 출력
            first_text = elements[0].get_text()[:500]
            print(f"첫 번째 요소 내용:\n{first_text}\n")

    if not content_found:
        # 전체 텍스트에서 "제1조" 찾기
        if "제1조" in response.text:
            print("\n✅ '제1조' 텍스트 발견 - 조문이 페이지에 있음")

            # 전체 텍스트의 일부 저장
            with open("law_page_full.html", 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("✅ 전체 HTML을 'law_page_full.html'에 저장")

            # "제1조" 주변 텍스트 출력
            idx = response.text.find("제1조")
            print(f"\n'제1조' 주변 HTML:\n{response.text[idx-200:idx+500]}")
        else:
            print("\n❌ 조문을 찾을 수 없음")

            # 페이지 타이틀 확인
            title = soup.find('title')
            if title:
                print(f"페이지 제목: {title.text}")

except Exception as e:
    print(f"❌ 오류: {e}")
    import traceback
    traceback.print_exc()
