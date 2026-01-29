"""
한국어 임베딩 모델

모델: jhgan/ko-sroberta-multitask
- 한국어 특화 sentence transformer
- 768차원 벡터
- 의미 검색에 최적화
"""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import torch


class KoreanEmbedder:
    """한국어 임베딩 생성기"""

    def __init__(
        self,
        model_name: str = "jhgan/ko-sroberta-multitask",
        device: str = "cpu",
        batch_size: int = 32
    ):
        """
        Args:
            model_name: 임베딩 모델명
            device: 'cpu' 또는 'cuda'
            batch_size: 배치 크기
        """
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size

        print(f"임베딩 모델 로딩 중: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        print(f"모델 로드 완료 (device: {device})")

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        텍스트를 임베딩 벡터로 변환

        Args:
            texts: 단일 텍스트 또는 텍스트 리스트

        Returns:
            임베딩 벡터 (shape: [n_texts, 768])
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=len(texts) > 10,
            convert_to_numpy=True
        )

        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """
        검색 쿼리 임베딩 (단일 벡터 반환)

        Args:
            query: 검색 쿼리

        Returns:
            임베딩 벡터 (shape: [768])
        """
        return self.embed(query)[0]

    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """
        문서 임베딩 (배치 처리)

        Args:
            documents: 문서 리스트

        Returns:
            임베딩 벡터 (shape: [n_docs, 768])
        """
        return self.embed(documents)

    def get_embedding_dimension(self) -> int:
        """임베딩 차원 반환"""
        return self.model.get_sentence_embedding_dimension()

    def similarity(self, text1: str, text2: str) -> float:
        """
        두 텍스트 간 코사인 유사도 계산

        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트

        Returns:
            유사도 (-1 ~ 1)
        """
        embeddings = self.embed([text1, text2])

        # 코사인 유사도
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )

        return float(similarity)


# 사용 예시
if __name__ == "__main__":
    embedder = KoreanEmbedder()

    # 단일 텍스트 임베딩
    text = "수소충전소 설치 기준"
    embedding = embedder.embed_query(text)
    print(f"텍스트: {text}")
    print(f"임베딩 차원: {embedding.shape}")
    print(f"벡터 샘플: {embedding[:5]}")

    # 유사도 계산
    text1 = "수소충전소 안전 기준"
    text2 = "수소 저장소 안전 규정"
    text3 = "커피 맛집 추천"

    sim12 = embedder.similarity(text1, text2)
    sim13 = embedder.similarity(text1, text3)

    print(f"\n'{text1}' vs '{text2}': {sim12:.3f}")
    print(f"'{text1}' vs '{text3}': {sim13:.3f}")
