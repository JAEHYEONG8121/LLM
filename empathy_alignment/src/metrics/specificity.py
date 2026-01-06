"""
Specificity (구체성) 메트릭

Concreteness ratings (Brysbaert et al., 2014) 기반으로 
응답이 얼마나 구체적인지 측정합니다.

구체적인 응답 = 높은 점수 (추상적 단어 < 구체적 단어)
예: "thing" (추상적) < "apple" (구체적)
"""

import os
import re
from typing import List, Dict, Optional, Union
from collections import defaultdict

import numpy as np


class SpecificityMetric:
    """
    Concreteness ratings를 사용한 구체성 측정 메트릭
    
    Brysbaert et al. (2014) - "Concreteness ratings for 40 thousand 
    generally known English word lemmas"
    
    점수 범위: 1 (매우 추상적) ~ 5 (매우 구체적)
    """
    
    def __init__(self, lexicon_path: Optional[str] = None):
        """
        Args:
            lexicon_path: Concreteness ratings 파일 경로
                         None이면 기본 경로 사용
        """
        self.lexicon: Dict[str, float] = {}
        self.lexicon_path = lexicon_path
        
        # 렉시콘 로드
        self._load_lexicon()
    
    def _load_lexicon(self) -> None:
        """Concreteness ratings 렉시콘 로드"""
        if self.lexicon_path and os.path.exists(self.lexicon_path):
            self._load_from_file(self.lexicon_path)
        else:
            # 기본 렉시콘 (샘플) - 실제 사용시 전체 파일 필요
            # Brysbaert et al. (2014) 데이터 다운로드 필요
            self._load_default_lexicon()
    
    def _load_from_file(self, path: str) -> None:
        """파일에서 렉시콘 로드 (Brysbaert format)"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                # 헤더 스킵
                header = f.readline()
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        word = parts[0].lower()
                        try:
                            # Conc.M (Mean concreteness rating)
                            concreteness = float(parts[2])
                            self.lexicon[word] = concreteness
                        except ValueError:
                            continue
            print(f"Loaded {len(self.lexicon)} words from concreteness lexicon")
        except Exception as e:
            print(f"Error loading lexicon: {e}")
            self._load_default_lexicon()
    
    def _load_default_lexicon(self) -> None:
        """
        기본 샘플 렉시콘 로드
        실제 연구에서는 전체 Brysbaert 데이터셋을 다운로드해야 함
        https://link.springer.com/article/10.3758/s13428-013-0403-5
        """
        # 샘플 데이터 (구체적 → 추상적 순서 예시)
        self.lexicon = {
            # 매우 구체적 (4.5-5.0)
            "apple": 5.0, "dog": 4.98, "cat": 4.97, "car": 4.95,
            "house": 4.93, "tree": 4.92, "book": 4.89, "table": 4.88,
            "phone": 4.85, "computer": 4.82, "water": 4.80, "food": 4.75,
            "hand": 4.90, "face": 4.85, "eye": 4.88, "door": 4.86,
            
            # 구체적 (4.0-4.5)
            "money": 4.45, "music": 4.20, "weather": 4.15, "friend": 4.10,
            "family": 4.05, "work": 3.95, "home": 4.30, "school": 4.25,
            
            # 중간 (3.0-4.0)
            "problem": 3.50, "situation": 3.20, "experience": 3.15,
            "feeling": 3.10, "moment": 3.05, "reason": 2.95, "way": 2.85,
            "time": 3.30, "life": 3.25, "day": 3.80, "place": 3.75,
            
            # 추상적 (2.0-3.0)
            "idea": 2.50, "hope": 2.30, "love": 2.45, "fear": 2.40,
            "joy": 2.35, "sadness": 2.25, "anger": 2.55, "happiness": 2.20,
            "peace": 2.15, "freedom": 2.10, "truth": 2.05, "justice": 2.00,
            
            # 매우 추상적 (1.0-2.0)
            "thing": 1.95, "something": 1.85, "anything": 1.80,
            "nothing": 1.75, "everything": 1.70, "concept": 1.65,
            "theory": 1.60, "philosophy": 1.55, "essence": 1.50,
            
            # 공감 관련 단어들
            "understand": 2.60, "sorry": 2.70, "glad": 2.65, "proud": 2.55,
            "worried": 2.75, "excited": 2.80, "disappointed": 2.45,
            "frustrated": 2.50, "grateful": 2.40, "anxious": 2.35,
            "overwhelmed": 2.30, "stressed": 2.85, "relieved": 2.90,
        }
        print(f"Loaded default sample lexicon with {len(self.lexicon)} words")
        print("Note: For research, download full Brysbaert et al. (2014) dataset")
    
    def _tokenize(self, text: str) -> List[str]:
        """간단한 토크나이저"""
        # 소문자 변환 및 단어 추출
        text = text.lower()
        words = re.findall(r'\b[a-z]+\b', text)
        return words
    
    def compute(self, text: str) -> Dict[str, float]:
        """
        텍스트의 구체성 점수 계산
        
        Args:
            text: 평가할 텍스트
            
        Returns:
            Dict with:
                - score: 평균 구체성 점수 (1-5)
                - coverage: 렉시콘에서 찾은 단어 비율
                - word_count: 총 단어 수
                - matched_count: 매칭된 단어 수
        """
        words = self._tokenize(text)
        
        if not words:
            return {
                "score": 0.0,
                "coverage": 0.0,
                "word_count": 0,
                "matched_count": 0,
            }
        
        scores = []
        matched_words = []
        
        for word in words:
            if word in self.lexicon:
                scores.append(self.lexicon[word])
                matched_words.append(word)
        
        if not scores:
            return {
                "score": 0.0,
                "coverage": 0.0,
                "word_count": len(words),
                "matched_count": 0,
            }
        
        return {
            "score": float(np.mean(scores)),
            "coverage": len(scores) / len(words),
            "word_count": len(words),
            "matched_count": len(scores),
        }
    
    def compute_batch(self, texts: List[str]) -> Dict[str, Union[float, List[Dict]]]:
        """
        여러 텍스트의 구체성 점수 일괄 계산
        
        Args:
            texts: 평가할 텍스트 리스트
            
        Returns:
            Dict with:
                - mean_score: 전체 평균 점수
                - std_score: 표준편차
                - individual: 개별 결과 리스트
        """
        results = [self.compute(text) for text in texts]
        scores = [r["score"] for r in results if r["score"] > 0]
        
        return {
            "mean_score": float(np.mean(scores)) if scores else 0.0,
            "std_score": float(np.std(scores)) if scores else 0.0,
            "individual": results,
        }


# 테스트 코드
if __name__ == "__main__":
    metric = SpecificityMetric()
    
    # 테스트 예시
    test_texts = [
        "I bought a red apple and a book from the store.",  # 구체적
        "I understand your feelings about the situation.",   # 중간
        "Something happened and I feel like everything is nothing.",  # 추상적
    ]
    
    print("\n=== Specificity Metric Test ===\n")
    for text in test_texts:
        result = metric.compute(text)
        print(f"Text: {text}")
        print(f"Score: {result['score']:.3f} (Coverage: {result['coverage']:.1%})")
        print()

