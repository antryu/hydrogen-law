"""LawAPIClient unit tests (no actual API calls)"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.collectors.law_api_client import LawAPIClient, LawInfo
import pytest


class TestLawAPIClientInit:
    def test_raises_without_api_key(self):
        """Should raise ValueError when no API key is provided"""
        # Ensure env var is not set
        os.environ.pop("LAW_API_KEY", None)
        with pytest.raises(ValueError, match="API 키가 필요합니다"):
            LawAPIClient()

    def test_accepts_explicit_key(self):
        """Should accept an explicit api_key parameter"""
        client = LawAPIClient(api_key="test-key")
        assert client.api_key == "test-key"


class TestParseSearchResults:
    def setup_method(self):
        self.client = LawAPIClient(api_key="test-key")

    def test_parse_valid_xml(self):
        """Should parse valid law search XML"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <response>
            <law>
                <법령일련번호>12345</법령일련번호>
                <법령명한글>수소경제법</법령명한글>
                <법령구분명>법률</법령구분명>
                <공포일자>20240101</공포일자>
                <시행일자>20240301</시행일자>
            </law>
        </response>"""
        result = self.client._parse_search_results(xml)
        assert len(result) == 1
        assert result[0].law_id == "12345"
        assert result[0].law_name == "수소경제법"
        assert result[0].law_type == "법률"

    def test_parse_empty_response(self):
        """Should return empty list for no results"""
        xml = "<response></response>"
        result = self.client._parse_search_results(xml)
        assert result == []

    def test_parse_error_response(self):
        """Should return empty list on API error"""
        xml = "<error><message>Invalid key</message></error>"
        result = self.client._parse_search_results(xml)
        assert result == []

    def test_skip_incomplete_entries(self):
        """Should skip entries missing required fields"""
        xml = """<response>
            <law>
                <법령일련번호>12345</법령일련번호>
            </law>
            <law>
                <법령일련번호>67890</법령일련번호>
                <법령명한글>완전한 법률</법령명한글>
                <법령구분명>법률</법령구분명>
            </law>
        </response>"""
        result = self.client._parse_search_results(xml)
        assert len(result) == 1
        assert result[0].law_id == "67890"

    def test_parse_invalid_xml(self):
        """Should return empty list for invalid XML"""
        result = self.client._parse_search_results("not xml at all")
        assert result == []

    def test_missing_law_type_defaults(self):
        """Should default to '미분류' when law type is missing"""
        xml = """<response>
            <law>
                <법령일련번호>11111</법령일련번호>
                <법령명한글>타입없는법</법령명한글>
            </law>
        </response>"""
        result = self.client._parse_search_results(xml)
        assert len(result) == 1
        assert result[0].law_type == "미분류"


class TestParseLawDetail:
    def setup_method(self):
        self.client = LawAPIClient(api_key="test-key")

    def test_parse_detail_with_articles(self):
        """Should parse law detail with articles"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <law>
            <법령일련번호>12345</법령일련번호>
            <법령명한글>수소경제법</법령명한글>
            <법령구분명>법률</법령구분명>
            <조문>
                <조문번호>제1조</조문번호>
                <조문제목>목적</조문제목>
                <조문내용>이 법은 수소경제를 육성한다.</조문내용>
            </조문>
        </law>"""
        result = self.client._parse_law_detail(xml)
        assert result is not None
        assert result["law_name"] == "수소경제법"
        assert len(result["articles"]) == 1
        assert result["articles"][0]["title"] == "목적"

    def test_parse_invalid_xml_returns_none(self):
        """Should return None for invalid XML"""
        result = self.client._parse_law_detail("broken xml")
        assert result is None


class TestGetText:
    def setup_method(self):
        self.client = LawAPIClient(api_key="test-key")

    def test_extracts_text(self):
        """Should extract text from XML element"""
        import xml.etree.ElementTree as ET

        root = ET.fromstring("<root><name>  hello  </name></root>")
        assert self.client._get_text(root, "name") == "hello"

    def test_returns_none_for_missing(self):
        """Should return None for missing element"""
        import xml.etree.ElementTree as ET

        root = ET.fromstring("<root></root>")
        assert self.client._get_text(root, "missing") is None
