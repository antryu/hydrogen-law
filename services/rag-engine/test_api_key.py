"""
국가법령정보센터 API 키 테스트 스크립트

API 키 발급: https://www.data.go.kr/data/15000115/openapi.do
"""

import os
import sys

def check_api_key():
    """API 키 확인"""
    api_key = os.getenv("LAW_API_KEY")

    if not api_key:
        print("❌ LAW_API_KEY 환경변수가 설정되지 않았습니다.")
        print("\n설정 방법:")
        print("1. 터미널에서: export LAW_API_KEY='your_key_here'")
        print("2. 또는 .env 파일 생성:")
        print("   LAW_API_KEY=your_key_here")
        print("\nAPI 키 발급:")
        print("https://www.data.go.kr/data/15000115/openapi.do")
        return False

    print(f"✅ API 키 확인됨: {api_key[:10]}...{api_key[-5:]}")
    print(f"   전체 길이: {len(api_key)} 문자")
    return True

if __name__ == "__main__":
    if check_api_key():
        print("\n✅ 환경변수 설정 완료!")
        sys.exit(0)
    else:
        print("\n⚠️  API 키를 먼저 설정해주세요.")
        sys.exit(1)
