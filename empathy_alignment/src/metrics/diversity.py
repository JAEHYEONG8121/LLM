"""
Diversity (다양성) 메트릭

Distinct-n (Li et al., 2016) 기반으로
응답의 어휘적 다양성을 측정합니다.

Distinct-n = 고유한 n-gram 수 / 전체 n-gram 수

높은 Distinct-n = 더 다양하고 창의적인 응답
낮은 Distinct-n = 반복적이고 일반적인 응답

참고: Li, J., et al. (2016). "A Diversity-Promoting Objective Function 
for Neural Conversation Models" (NAACL 2016)
"""

import re
from typing import List, Dict, Union, Tuple, Set
from collections import Counter

import numpy as np


class DiversityMetric:
    """
    Distinct-n을 사용한 응답 다양성 측정 메트릭
    
    측정 항목:
    - Distinct-1: 유니그램 다양성
    - Distinct-2: 바이그램 다양성
    - Distinct-3: 트라이그램 다양성 (옵션)
    - Entropy: 토큰 분포 엔트로피
    """
    
    def __init__(self, max_n: int = 3):
        """
        Args:
            max_n: 계산할 최대 n-gram (기본 3)
        """
        self.max_n = max_n
    
    def _tokenize(self, text: str) -> List[str]:
        """간단한 토크나이저"""
        text = text.lower()
        # 단어 및 구두점 추출
        tokens = re.findall(r'\b[a-z]+\b|[.,!?;:]', text)
        return tokens
    
    def _get_ngrams(self, tokens: List[str], n: int) -> List[Tuple[str, ...]]:
        """n-gram 추출"""
        if len(tokens) < n:
            return []
        return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
    
    def _compute_distinct_n(self, tokens: List[str], n: int) -> float:
        """
        Distinct-n 계산
        
        Args:
            tokens: 토큰 리스트
            n: n-gram 크기
            
        Returns:
            Distinct-n 점수 (0-1)
        """
        ngrams = self._get_ngrams(tokens, n)
        
        if not ngrams:
            return 0.0
        
        unique_ngrams = set(ngrams)
        return len(unique_ngrams) / len(ngrams)
    
    def _compute_entropy(self, tokens: List[str]) -> float:
        """
        토큰 분포의 엔트로피 계산
        높은 엔트로피 = 더 균일한 분포 = 더 다양함
        """
        if not tokens:
            return 0.0
        
        counter = Counter(tokens)
        total = len(tokens)
        
        entropy = 0.0
        for count in counter.values():
            prob = count / total
            if prob > 0:
                entropy -= prob * np.log2(prob)
        
        return entropy
    
    def _compute_type_token_ratio(self, tokens: List[str]) -> float:
        """
        Type-Token Ratio (TTR) 계산
        고유 단어 수 / 전체 단어 수
        """
        if not tokens:
            return 0.0
        return len(set(tokens)) / len(tokens)
    
    def compute(self, text: str) -> Dict[str, float]:
        """
        텍스트의 다양성 점수 계산
        
        Args:
            text: 평가할 텍스트
            
        Returns:
            Dict with:
                - distinct_1: Distinct-1 점수
                - distinct_2: Distinct-2 점수
                - distinct_3: Distinct-3 점수 (max_n >= 3인 경우)
                - entropy: 토큰 엔트로피
                - type_token_ratio: TTR
                - token_count: 총 토큰 수
                - unique_tokens: 고유 토큰 수
        """
        tokens = self._tokenize(text)
        
        if not tokens:
            return self._empty_result()
        
        result = {
            "distinct_1": self._compute_distinct_n(tokens, 1),
            "distinct_2": self._compute_distinct_n(tokens, 2),
            "entropy": self._compute_entropy(tokens),
            "type_token_ratio": self._compute_type_token_ratio(tokens),
            "token_count": len(tokens),
            "unique_tokens": len(set(tokens)),
        }
        
        # Distinct-3 이상 추가
        for n in range(3, self.max_n + 1):
            result[f"distinct_{n}"] = self._compute_distinct_n(tokens, n)
        
        # 종합 다양성 점수 (Distinct-1, 2의 가중 평균)
        result["diversity_score"] = (
            0.4 * result["distinct_1"] + 
            0.6 * result["distinct_2"]
        )
        
        return result
    
    def _empty_result(self) -> Dict[str, float]:
        """빈 결과 반환"""
        result = {
            "distinct_1": 0.0,
            "distinct_2": 0.0,
            "entropy": 0.0,
            "type_token_ratio": 0.0,
            "token_count": 0,
            "unique_tokens": 0,
            "diversity_score": 0.0,
        }
        for n in range(3, self.max_n + 1):
            result[f"distinct_{n}"] = 0.0
        return result
    
    def compute_corpus_diversity(self, texts: List[str]) -> Dict[str, float]:
        """
        코퍼스 전체의 다양성 계산
        (개별 텍스트가 아닌 전체 응답 집합의 다양성)
        
        Args:
            texts: 텍스트 리스트
            
        Returns:
            코퍼스 레벨 다양성 메트릭
        """
        all_tokens = []
        all_bigrams: Set[Tuple[str, str]] = set()
        all_trigrams: Set[Tuple[str, str, str]] = set()
        
        for text in texts:
            tokens = self._tokenize(text)
            all_tokens.extend(tokens)
            all_bigrams.update(self._get_ngrams(tokens, 2))
            all_trigrams.update(self._get_ngrams(tokens, 3))
        
        if not all_tokens:
            return {
                "corpus_distinct_1": 0.0,
                "corpus_distinct_2": 0.0,
                "corpus_distinct_3": 0.0,
                "corpus_entropy": 0.0,
                "total_tokens": 0,
                "unique_unigrams": 0,
                "unique_bigrams": 0,
                "unique_trigrams": 0,
            }
        
        # 코퍼스 레벨 Distinct-n
        unigrams = self._get_ngrams(all_tokens, 1)
        bigrams = self._get_ngrams(all_tokens, 2)
        trigrams = self._get_ngrams(all_tokens, 3)
        
        return {
            "corpus_distinct_1": len(set(unigrams)) / len(unigrams) if unigrams else 0.0,
            "corpus_distinct_2": len(set(bigrams)) / len(bigrams) if bigrams else 0.0,
            "corpus_distinct_3": len(set(trigrams)) / len(trigrams) if trigrams else 0.0,
            "corpus_entropy": self._compute_entropy(all_tokens),
            "total_tokens": len(all_tokens),
            "unique_unigrams": len(set(all_tokens)),
            "unique_bigrams": len(all_bigrams),
            "unique_trigrams": len(all_trigrams),
        }
    
    def compute_batch(self, texts: List[str]) -> Dict[str, Union[float, List[Dict]]]:
        """
        여러 텍스트의 다양성 점수 일괄 계산
        
        Args:
            texts: 평가할 텍스트 리스트
            
        Returns:
            Dict with:
                - 개별 텍스트 평균 점수
                - 코퍼스 레벨 다양성
                - 개별 결과
        """
        results = [self.compute(text) for text in texts]
        
        # 개별 평균
        individual_stats = {
            "mean_distinct_1": float(np.mean([r["distinct_1"] for r in results])),
            "mean_distinct_2": float(np.mean([r["distinct_2"] for r in results])),
            "mean_entropy": float(np.mean([r["entropy"] for r in results])),
            "mean_diversity_score": float(np.mean([r["diversity_score"] for r in results])),
            "std_distinct_1": float(np.std([r["distinct_1"] for r in results])),
            "std_distinct_2": float(np.std([r["distinct_2"] for r in results])),
        }
        
        # 코퍼스 레벨 다양성
        corpus_stats = self.compute_corpus_diversity(texts)
        
        return {
            **individual_stats,
            **corpus_stats,
            "individual": results,
        }
    
    def compare_diversity(
        self, 
        responses_a: List[str], 
        responses_b: List[str]
    ) -> Dict[str, float]:
        """
        두 응답 집합의 다양성 비교
        
        Args:
            responses_a: 첫 번째 응답 집합
            responses_b: 두 번째 응답 집합
            
        Returns:
            비교 결과 (양수 = A가 더 다양, 음수 = B가 더 다양)
        """
        stats_a = self.compute_batch(responses_a)
        stats_b = self.compute_batch(responses_b)
        
        return {
            "distinct_1_diff": stats_a["mean_distinct_1"] - stats_b["mean_distinct_1"],
            "distinct_2_diff": stats_a["mean_distinct_2"] - stats_b["mean_distinct_2"],
            "corpus_distinct_1_diff": stats_a["corpus_distinct_1"] - stats_b["corpus_distinct_1"],
            "corpus_distinct_2_diff": stats_a["corpus_distinct_2"] - stats_b["corpus_distinct_2"],
            "entropy_diff": stats_a["mean_entropy"] - stats_b["mean_entropy"],
            "stats_a": stats_a,
            "stats_b": stats_b,
        }


# 테스트 코드
if __name__ == "__main__":
    metric = DiversityMetric()
    
    # 테스트 예시
    test_texts = [
        "I understand how you feel. That must be really difficult for you.",
        "I'm sorry to hear that. I'm sorry you're going through this. I'm sorry.",  # 반복적
        "Your experience sounds challenging. The situation you described involves complex emotions and difficult circumstances that many people struggle with.",  # 다양함
    ]
    
    print("\n=== Diversity Metric Test ===\n")
    for text in test_texts:
        result = metric.compute(text)
        print(f"Text: {text[:60]}...")
        print(f"  Distinct-1: {result['distinct_1']:.3f}")
        print(f"  Distinct-2: {result['distinct_2']:.3f}")
        print(f"  Entropy: {result['entropy']:.3f}")
        print(f"  Diversity Score: {result['diversity_score']:.3f}")
        print()
    
    # 코퍼스 레벨 테스트
    print("=== Corpus Diversity Test ===\n")
    
    # 다양한 응답 집합
    diverse_responses = [
        "I understand how challenging that must be.",
        "It sounds like you're going through a difficult time.",
        "Your feelings are completely valid in this situation.",
        "That's a lot to process. Take your time.",
    ]
    
    # 반복적인 응답 집합
    repetitive_responses = [
        "I'm sorry to hear that.",
        "I'm sorry you're feeling this way.",
        "I'm sorry that happened to you.",
        "I'm sorry to hear about your situation.",
    ]
    
    comparison = metric.compare_diversity(diverse_responses, repetitive_responses)
    print(f"Diverse responses vs Repetitive responses:")
    print(f"  Distinct-1 diff: {comparison['distinct_1_diff']:+.3f}")
    print(f"  Distinct-2 diff: {comparison['distinct_2_diff']:+.3f}")
    print(f"  Corpus Distinct-2 diff: {comparison['corpus_distinct_2_diff']:+.3f}")

