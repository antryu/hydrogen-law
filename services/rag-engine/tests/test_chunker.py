"""LawChunker unit tests"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.embeddings.chunker import LawChunker, LawChunk


class TestLawChunker:
    def setup_method(self):
        self.chunker = LawChunker(max_chunk_size=512, overlap=50)

    def test_short_article_single_chunk(self):
        """Short articles (<512 chars) should produce exactly one chunk"""
        chunks = self.chunker.chunk_article(
            law_id="001",
            law_name="Test Law",
            article_number="제1조",
            title="목적",
            content="이 법은 수소경제 육성에 필요한 사항을 규정한다.",
        )
        assert len(chunks) == 1
        assert chunks[0].chunk_id == "001_제1조"
        assert chunks[0].chunk_type == "article"
        assert chunks[0].metadata["full_article"] is True

    def test_definition_article_detected(self):
        """Articles with definition keywords should be marked as definition type"""
        chunks = self.chunker.chunk_article(
            law_id="001",
            law_name="Test Law",
            article_number="제2조",
            title="정의",
            content="이 법에서 사용하는 용어의 뜻은 다음과 같다.",
        )
        assert chunks[0].chunk_type == "definition"
        assert chunks[0].metadata["is_definition"] is True

    def test_definition_keyword_variants(self):
        """All definition keywords (정의, 용어, 뜻) should be detected"""
        for title in ["정의", "용어의 정리", "뜻"]:
            chunks = self.chunker.chunk_article(
                law_id="001",
                law_name="T",
                article_number="제1조",
                title=title,
                content="짧은 내용",
            )
            assert chunks[0].metadata["is_definition"] is True

    def test_long_article_with_paragraphs(self):
        """Long articles with paragraphs should split by paragraph"""
        long_content = "가" * 600
        paragraphs = [
            {"number": "①", "content": "첫번째 항 내용"},
            {"number": "②", "content": "두번째 항 내용"},
        ]
        chunks = self.chunker.chunk_article(
            law_id="001",
            law_name="Test Law",
            article_number="제3조",
            title="허가",
            content=long_content,
            paragraphs=paragraphs,
        )
        assert len(chunks) == 2
        assert chunks[0].chunk_type == "paragraph"
        assert chunks[0].paragraph_number == "①"
        assert chunks[1].paragraph_number == "②"

    def test_long_article_without_paragraphs_splits_text(self):
        """Long articles without paragraphs should be split into text chunks"""
        long_content = "가" * 1200
        chunks = self.chunker.chunk_article(
            law_id="001",
            law_name="Test Law",
            article_number="제4조",
            title="기준",
            content=long_content,
        )
        assert len(chunks) > 1
        assert all(c.chunk_type == "text_split" for c in chunks)

    def test_table_chunk(self):
        """Table (별표) chunking should work correctly"""
        chunk = self.chunker.chunk_table(
            law_id="001",
            law_name="Test Law",
            table_number="1",
            title="안전기준",
            content="별표 내용",
        )
        assert chunk.chunk_type == "table"
        assert chunk.article_number == "별표1"
        assert chunk.metadata["is_table"] is True

    def test_split_long_text_overlap(self):
        """Text splitting should apply overlap"""
        chunker = LawChunker(max_chunk_size=100, overlap=20)
        text = "가" * 250
        parts = chunker._split_long_text(text)
        assert len(parts) >= 3

    def test_empty_content(self):
        """Empty content should produce a single chunk"""
        chunks = self.chunker.chunk_article(
            law_id="001",
            law_name="Test Law",
            article_number="제1조",
            title="목적",
            content="",
        )
        assert len(chunks) == 1

    def test_non_definition_title(self):
        """Non-definition titles should not be flagged"""
        assert self.chunker._is_definition_article("허가") is False
        assert self.chunker._is_definition_article("벌칙") is False
        assert self.chunker._is_definition_article("") is False
        assert self.chunker._is_definition_article(None) is False
