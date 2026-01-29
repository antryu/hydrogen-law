"""
국가법령정보센터 API 클라이언트

API 문서: https://open.law.go.kr/LSO/openApi/guideList.do
"""

import os
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LawInfo:
    """법령 기본 정보"""
    law_id: str  # 법령일련번호
    law_name: str  # 법령명
    law_type: str  # 법령 구분 (법률/시행령/시행규칙)
    promulgation_date: Optional[str] = None  # 공포일자
    enforcement_date: Optional[str] = None  # 시행일자


class LawAPIClient:
    """국가법령정보센터 API 클라이언트"""

    BASE_URL = "https://apis.data.go.kr/1170000/law"

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: API 인증키 (환경변수 LAW_API_KEY에서 자동 로드)
        """
        self.api_key = api_key or os.getenv("LAW_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API 키가 필요합니다. 환경변수 LAW_API_KEY를 설정하거나 "
                "api_key 파라미터를 전달하세요.\n"
                "API 키 발급: https://www.data.go.kr/data/15000115/openapi.do"
            )

    def search_laws(
        self,
        keyword: str,
        law_type: Optional[str] = None,
        display: int = 100
    ) -> List[LawInfo]:
        """
        법령 검색

        Args:
            keyword: 검색 키워드 (예: "수소")
            law_type: 법령 구분 (법률/대통령령/총리령/부령)
            display: 결과 개수 (최대 100)

        Returns:
            검색된 법령 목록
        """
        url = f"{self.BASE_URL}/lawSearchList.do"

        params = {
            "serviceKey": self.api_key,
            "target": "law",
            "query": keyword,
            "numOfRows": min(display, 100),
            "pageNo": 1
        }

        if law_type:
            params["법령구분"] = law_type

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            return self._parse_search_results(response.text)

        except requests.RequestException as e:
            print(f"법령 검색 실패: {e}")
            return []

    def get_law_detail(self, law_id: str) -> Optional[Dict]:
        """
        법령 상세 정보 조회

        Args:
            law_id: 법령일련번호 (MST)

        Returns:
            법령 상세 정보 (조문, 부칙 등)
        """
        url = f"{self.BASE_URL}/lawService.do"

        params = {
            "OC": self.api_key,
            "target": "law",
            "MST": law_id,
            "type": "XML"
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            return self._parse_law_detail(response.text)

        except requests.RequestException as e:
            print(f"법령 상세 조회 실패 (ID: {law_id}): {e}")
            return None

    def get_enforcement_rules(self, law_name: str) -> List[LawInfo]:
        """
        특정 법률의 시행령, 시행규칙 조회

        Args:
            law_name: 법률명 (예: "수소경제 육성 및 수소 안전관리에 관한 법률")

        Returns:
            시행령, 시행규칙 목록
        """
        # 시행령 검색
        enforcement_decree = self.search_laws(
            keyword=law_name,
            law_type="대통령령"
        )

        # 시행규칙 검색
        enforcement_rules = self.search_laws(
            keyword=law_name,
            law_type="부령"
        )

        return enforcement_decree + enforcement_rules

    def _parse_search_results(self, xml_text: str) -> List[LawInfo]:
        """XML 검색 결과 파싱"""
        laws = []

        try:
            root = ET.fromstring(xml_text)

            for law_elem in root.findall('.//law'):
                law_id = self._get_text(law_elem, '법령일련번호')
                law_name = self._get_text(law_elem, '법령명한글')
                law_type = self._get_text(law_elem, '법령구분명')

                if law_id and law_name:
                    laws.append(LawInfo(
                        law_id=law_id,
                        law_name=law_name,
                        law_type=law_type or "미분류",
                        promulgation_date=self._get_text(law_elem, '공포일자'),
                        enforcement_date=self._get_text(law_elem, '시행일자')
                    ))

        except ET.ParseError as e:
            print(f"XML 파싱 오류: {e}")

        return laws

    def _parse_law_detail(self, xml_text: str) -> Optional[Dict]:
        """XML 법령 상세 파싱"""
        try:
            root = ET.fromstring(xml_text)

            # 기본 정보
            law_info = {
                'law_id': self._get_text(root, '법령일련번호'),
                'law_name': self._get_text(root, '법령명한글'),
                'law_type': self._get_text(root, '법령구분명'),
                'promulgation_date': self._get_text(root, '공포일자'),
                'enforcement_date': self._get_text(root, '시행일자'),
                'articles': []
            }

            # 조문 추출
            for article in root.findall('.//조문'):
                article_info = {
                    'article_number': self._get_text(article, '조문번호'),
                    'title': self._get_text(article, '조문제목'),
                    'content': self._get_text(article, '조문내용'),
                    'paragraphs': []
                }

                # 항 추출
                for paragraph in article.findall('.//항'):
                    paragraph_info = {
                        'paragraph_number': self._get_text(paragraph, '항번호'),
                        'content': self._get_text(paragraph, '항내용')
                    }
                    article_info['paragraphs'].append(paragraph_info)

                law_info['articles'].append(article_info)

            return law_info

        except ET.ParseError as e:
            print(f"XML 파싱 오류: {e}")
            return None

    def _get_text(self, element: ET.Element, tag: str) -> Optional[str]:
        """XML 요소에서 텍스트 추출"""
        elem = element.find(f'.//{tag}')
        return elem.text.strip() if elem is not None and elem.text else None


# 사용 예시
if __name__ == "__main__":
    # API 클라이언트 생성
    client = LawAPIClient()

    # 수소 관련 법률 검색
    print("=== 수소 관련 법률 검색 ===")
    laws = client.search_laws("수소")

    for law in laws[:5]:  # 상위 5개만 출력
        print(f"- {law.law_name} ({law.law_type})")
        print(f"  ID: {law.law_id}")
        print(f"  시행일: {law.enforcement_date}")
        print()

    # 특정 법령 상세 조회 (첫 번째 법령)
    if laws:
        print(f"\n=== {laws[0].law_name} 상세 ===")
        detail = client.get_law_detail(laws[0].law_id)

        if detail:
            print(f"조문 수: {len(detail.get('articles', []))}")

            # 첫 번째 조문 출력
            if detail.get('articles'):
                first_article = detail['articles'][0]
                print(f"\n{first_article['article_number']} {first_article['title']}")
                print(first_article['content'][:200] + "...")
