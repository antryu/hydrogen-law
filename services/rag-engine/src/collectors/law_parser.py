"""
법령 파서 - 조-항-호-목 계층 구조 추출

한국 법령 문서 구조:
- 편 (Part)
- 장 (Chapter)
- 절 (Section)
- 조 (Article) - 제1조, 제2조
- 항 (Paragraph) - ①, ②, ③
- 호 (Item) - 1., 2., 3.
- 목 (Subitem) - 가., 나., 다.
"""

import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass, field


@dataclass
class LawSubitem:
    """법령 목 (Subitem)"""
    number: str  # 가, 나, 다
    content: str


@dataclass
class LawItem:
    """법령 호 (Item)"""
    number: str  # 1, 2, 3
    content: str
    subitems: List[LawSubitem] = field(default_factory=list)


@dataclass
class LawParagraph:
    """법령 항 (Paragraph)"""
    number: str  # ①, ②, ③
    content: str
    items: List[LawItem] = field(default_factory=list)


@dataclass
class LawArticle:
    """법령 조 (Article)"""
    article_number: str  # 제1조, 제2조
    title: Optional[str]  # 조문 제목
    content: str  # 본문
    paragraphs: List[LawParagraph] = field(default_factory=list)


@dataclass
class LawChapter:
    """법령 장 (Chapter)"""
    chapter_number: str  # 제1장, 제2장
    title: str
    articles: List[LawArticle] = field(default_factory=list)


@dataclass
class ParsedLaw:
    """파싱된 법령 전체"""
    law_name: str
    law_id: str
    chapters: List[LawChapter] = field(default_factory=list)
    articles: List[LawArticle] = field(default_factory=list)  # 장 없이 독립 조문


class LawParser:
    """법령 파서"""

    # 정규식 패턴
    ARTICLE_PATTERN = re.compile(r'제(\d+)조')  # 제1조, 제2조
    PARAGRAPH_PATTERN = re.compile(r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮]')  # 항 번호
    ITEM_PATTERN = re.compile(r'^\d+\.')  # 1., 2., 3.
    SUBITEM_PATTERN = re.compile(r'^[가-힣]\.')  # 가., 나., 다.
    CHAPTER_PATTERN = re.compile(r'제(\d+)장')  # 제1장, 제2장

    def parse_from_api_response(self, api_data: Dict) -> ParsedLaw:
        """
        API 응답 데이터에서 법령 파싱

        Args:
            api_data: law_api_client.get_law_detail() 반환값

        Returns:
            파싱된 법령 구조
        """
        parsed = ParsedLaw(
            law_name=api_data.get('law_name', ''),
            law_id=api_data.get('law_id', '')
        )

        for article_data in api_data.get('articles', []):
            article = self._parse_article(article_data)
            parsed.articles.append(article)

        return parsed

    def parse_from_html(self, html_content: str, law_name: str, law_id: str) -> ParsedLaw:
        """
        HTML에서 법령 파싱

        Args:
            html_content: 법령 HTML 콘텐츠
            law_name: 법령명
            law_id: 법령ID

        Returns:
            파싱된 법령 구조
        """
        soup = BeautifulSoup(html_content, 'lxml')
        parsed = ParsedLaw(law_name=law_name, law_id=law_id)

        # 조문 추출
        articles = soup.find_all('div', class_='article')

        for article_elem in articles:
            article = self._parse_article_from_html(article_elem)
            if article:
                parsed.articles.append(article)

        return parsed

    def _parse_article(self, article_data: Dict) -> LawArticle:
        """API 데이터에서 조문 파싱"""
        article = LawArticle(
            article_number=article_data.get('article_number', ''),
            title=article_data.get('title'),
            content=article_data.get('content', '')
        )

        # 항 파싱
        for paragraph_data in article_data.get('paragraphs', []):
            paragraph = LawParagraph(
                number=paragraph_data.get('paragraph_number', ''),
                content=paragraph_data.get('content', '')
            )
            article.paragraphs.append(paragraph)

        return article

    def _parse_article_from_html(self, article_elem) -> Optional[LawArticle]:
        """HTML 요소에서 조문 파싱"""
        # 조문 번호 추출
        number_elem = article_elem.find('span', class_='article-number')
        if not number_elem:
            return None

        article_number = number_elem.get_text(strip=True)

        # 조문 제목
        title_elem = article_elem.find('span', class_='article-title')
        title = title_elem.get_text(strip=True) if title_elem else None

        # 본문
        content_elem = article_elem.find('div', class_='article-content')
        content = content_elem.get_text(strip=True) if content_elem else ''

        article = LawArticle(
            article_number=article_number,
            title=title,
            content=content
        )

        # 항 추출
        paragraphs = self._extract_paragraphs(content)
        article.paragraphs = paragraphs

        return article

    def _extract_paragraphs(self, content: str) -> List[LawParagraph]:
        """본문에서 항 추출"""
        paragraphs = []
        lines = content.split('\n')

        current_paragraph = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 항 번호 확인
            paragraph_match = self.PARAGRAPH_PATTERN.match(line)

            if paragraph_match:
                # 새 항 시작
                if current_paragraph:
                    paragraphs.append(current_paragraph)

                current_paragraph = LawParagraph(
                    number=paragraph_match.group(),
                    content=line[len(paragraph_match.group()):].strip()
                )
            elif current_paragraph:
                # 현재 항에 내용 추가
                current_paragraph.content += ' ' + line

        # 마지막 항 추가
        if current_paragraph:
            paragraphs.append(current_paragraph)

        return paragraphs

    def extract_references(self, content: str) -> List[str]:
        """
        조문에서 다른 조항 참조 추출

        Args:
            content: 조문 내용

        Returns:
            참조된 조항 목록 (예: ["제1조", "제5조제2항"])
        """
        references = []

        # 제○조 패턴
        article_refs = re.findall(r'제\d+조(?:제\d+항)?(?:제\d+호)?', content)
        references.extend(article_refs)

        return list(set(references))  # 중복 제거

    def is_definition_article(self, article: LawArticle) -> bool:
        """정의 조항 여부 확인"""
        if not article.title:
            return False

        definition_keywords = ['정의', '용어', '뜻']
        return any(keyword in article.title for keyword in definition_keywords)

    def is_penalty_article(self, article: LawArticle) -> bool:
        """벌칙 조항 여부 확인"""
        if not article.title:
            return False

        penalty_keywords = ['벌칙', '과태료', '형', '징역', '벌금']
        return any(keyword in article.title for keyword in penalty_keywords)

    def chunk_article(
        self,
        article: LawArticle,
        max_chunk_size: int = 512
    ) -> List[Dict[str, str]]:
        """
        조문을 청크로 분할

        Args:
            article: 조문
            max_chunk_size: 최대 청크 크기 (문자 수)

        Returns:
            청크 목록
        """
        chunks = []

        # 짧은 조문은 전체를 하나의 청크로
        full_content = f"{article.article_number} {article.title or ''}\n{article.content}"

        if len(full_content) < max_chunk_size:
            chunks.append({
                'article_number': article.article_number,
                'title': article.title,
                'content': full_content,
                'chunk_type': 'full_article'
            })
        else:
            # 긴 조문은 항 단위로 분할
            for paragraph in article.paragraphs:
                chunk_content = f"{article.article_number} {paragraph.number}\n{paragraph.content}"

                chunks.append({
                    'article_number': article.article_number,
                    'paragraph_number': paragraph.number,
                    'content': chunk_content,
                    'chunk_type': 'paragraph'
                })

        return chunks


# 사용 예시
if __name__ == "__main__":
    from law_api_client import LawAPIClient

    # API 클라이언트 생성
    client = LawAPIClient()

    # 법령 검색
    laws = client.search_laws("수소경제")

    if laws:
        # 첫 번째 법령 상세 조회
        detail = client.get_law_detail(laws[0].law_id)

        if detail:
            # 파싱
            parser = LawParser()
            parsed = parser.parse_from_api_response(detail)

            print(f"=== {parsed.law_name} ===")
            print(f"조문 수: {len(parsed.articles)}")

            # 첫 번째 조문 출력
            if parsed.articles:
                article = parsed.articles[0]
                print(f"\n{article.article_number} {article.title}")
                print(f"항 수: {len(article.paragraphs)}")

                # 청킹
                chunks = parser.chunk_article(article)
                print(f"청크 수: {len(chunks)}")
