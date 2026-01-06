"""
Reflection Level (반영 수준) 메트릭

PAIR 모델 (Min et al., 2022) 기반으로
상담사의 반영(reflection) 수준을 측정합니다.

반영 수준은 0-6까지 7단계로 구분됩니다:
- Level 0: 반영 없음
- Level 1-2: 낮은 수준의 반영
- Level 3-4: 중간 수준의 반영  
- Level 5-6: 높은 수준의 반영

참고: Min, D. J., et al. (2022). "PAIR: Prompt-Aware Margin Ranking 
for Counselor Reflection Scoring in Motivational Interviewing" (EMNLP 2022)
"""

import re
from typing import List, Dict, Optional, Union, Tuple

import numpy as np

# Optional: transformers for model-based scoring
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class ReflectionLevelMetric:
    """
    반영 수준 측정 메트릭
    
    두 가지 모드 지원:
    1. Rule-based: 반영 패턴 기반 휴리스틱 (기본)
    2. Model-based: PAIR 또는 유사 모델 사용 (옵션)
    """
    
    def __init__(self, use_model: bool = False, model_name: Optional[str] = None):
        """
        Args:
            use_model: True면 모델 기반, False면 규칙 기반
            model_name: 사용할 모델 이름 (HuggingFace)
        """
        self.use_model = use_model and TRANSFORMERS_AVAILABLE
        self.model = None
        self.tokenizer = None
        
        if self.use_model and model_name:
            self._load_model(model_name)
        
        # 반영 패턴 정의 (규칙 기반)
        self._init_reflection_patterns()
    
    def _load_model(self, model_name: str) -> None:
        """PAIR 또는 유사 모델 로드"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.eval()
            print(f"Loaded reflection model: {model_name}")
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.use_model = False
    
    def _init_reflection_patterns(self) -> None:
        """반영 패턴 초기화 (규칙 기반 분석용)"""
        
        # Level 6: Complex Reflection (복잡한 반영)
        # - 감정의 깊은 의미 해석, 은유적 표현
        self.complex_patterns = [
            r"it seems like .+ means .+ to you",
            r"what i('m| am) hearing is that .+ feels like",
            r"it sounds like .+ is really about",
            r"beneath .+ there seems to be",
            r"on a deeper level",
            r"what that .+ represents",
            r"the meaning behind",
        ]
        
        # Level 4-5: Reflection of Feeling (감정 반영)
        # - 명시적 또는 암시적 감정 인식
        self.feeling_patterns = [
            r"you('re| are) feeling",
            r"you feel",
            r"you seem",
            r"sounds like you('re| are)",
            r"it sounds like",
            r"that must (be|feel|have been)",
            r"i can (see|hear|sense|imagine) (that |how )?you",
            r"you('re| are) (worried|anxious|scared|afraid|sad|happy|excited|frustrated|angry|upset|disappointed|overwhelmed|stressed|relieved|grateful|proud)",
        ]
        
        # Level 2-3: Simple Reflection (단순 반영)
        # - 내용 반복, 바꿔 말하기
        self.simple_patterns = [
            r"so you",
            r"you('re| are) saying",
            r"you mentioned",
            r"you said",
            r"i hear you",
            r"i understand",
            r"i see",
            r"that('s| is) (hard|difficult|tough|challenging)",
            r"it('s| is) (hard|difficult|tough|challenging)",
        ]
        
        # Level 1: Minimal Response (최소 반응)
        self.minimal_patterns = [
            r"^(ok|okay|i see|right|uh-huh|mm-hmm|yes|yeah|got it)[\.\,\!]?$",
            r"^(tell me more|go on|continue)[\.\,\!]?$",
        ]
        
        # 공감 표현 패턴 (점수 보너스)
        self.empathy_boosters = [
            r"i('m| am) sorry (to hear|that)",
            r"that must (be|have been) (really |very )?(hard|difficult|painful|frustrating)",
            r"i can only imagine",
            r"my heart goes out",
            r"i appreciate you sharing",
            r"thank you for (sharing|telling me|opening up)",
        ]
    
    def _rule_based_score(self, text: str) -> Tuple[int, Dict[str, int]]:
        """
        규칙 기반 반영 수준 점수 계산
        
        Returns:
            Tuple of (score 0-6, pattern_counts dict)
        """
        text_lower = text.lower().strip()
        
        pattern_counts = {
            "complex": 0,
            "feeling": 0,
            "simple": 0,
            "minimal": 0,
            "empathy_booster": 0,
        }
        
        # 패턴 매칭
        for pattern in self.complex_patterns:
            if re.search(pattern, text_lower):
                pattern_counts["complex"] += 1
        
        for pattern in self.feeling_patterns:
            if re.search(pattern, text_lower):
                pattern_counts["feeling"] += 1
        
        for pattern in self.simple_patterns:
            if re.search(pattern, text_lower):
                pattern_counts["simple"] += 1
        
        for pattern in self.minimal_patterns:
            if re.search(pattern, text_lower):
                pattern_counts["minimal"] += 1
        
        for pattern in self.empathy_boosters:
            if re.search(pattern, text_lower):
                pattern_counts["empathy_booster"] += 1
        
        # 점수 계산
        if pattern_counts["complex"] > 0:
            base_score = 5 + min(pattern_counts["complex"], 1)  # 5-6
        elif pattern_counts["feeling"] > 0:
            base_score = 3 + min(pattern_counts["feeling"], 2)  # 3-5
        elif pattern_counts["simple"] > 0:
            base_score = 2 + min(pattern_counts["simple"] - 1, 1)  # 2-3
        elif pattern_counts["minimal"] > 0:
            base_score = 1
        else:
            base_score = 0
        
        # 공감 부스터 적용 (최대 +1)
        if pattern_counts["empathy_booster"] > 0 and base_score < 6:
            base_score = min(base_score + 1, 6)
        
        return base_score, pattern_counts
    
    def _model_based_score(self, context: str, response: str) -> int:
        """모델 기반 반영 수준 점수 계산"""
        if not self.model or not self.tokenizer:
            return self._rule_based_score(response)[0]
        
        try:
            # 입력 준비
            inputs = self.tokenizer(
                context, response,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                # 7-class classification (0-6)
                predicted_level = torch.argmax(outputs.logits, dim=-1).item()
            
            return predicted_level
        except Exception as e:
            print(f"Model inference error: {e}")
            return self._rule_based_score(response)[0]
    
    def compute(
        self, 
        response: str, 
        context: Optional[str] = None
    ) -> Dict[str, Union[int, float, Dict]]:
        """
        반영 수준 점수 계산
        
        Args:
            response: 평가할 응답 텍스트
            context: 이전 대화 맥락 (모델 기반에서 사용)
            
        Returns:
            Dict with:
                - level: 반영 수준 (0-6)
                - normalized_score: 정규화된 점수 (0-1)
                - pattern_counts: 패턴별 매칭 횟수
                - interpretation: 수준 해석
        """
        if self.use_model and context:
            level = self._model_based_score(context, response)
            pattern_counts = {}
        else:
            level, pattern_counts = self._rule_based_score(response)
        
        # 수준 해석
        interpretations = {
            0: "No reflection",
            1: "Minimal response",
            2: "Simple reflection (repetition)",
            3: "Simple reflection (paraphrase)",
            4: "Reflection of feeling (explicit)",
            5: "Reflection of feeling (implicit)",
            6: "Complex reflection (deep meaning)",
        }
        
        return {
            "level": level,
            "normalized_score": level / 6.0,
            "pattern_counts": pattern_counts,
            "interpretation": interpretations.get(level, "Unknown"),
        }
    
    def compute_batch(
        self, 
        responses: List[str],
        contexts: Optional[List[str]] = None
    ) -> Dict[str, Union[float, List[Dict]]]:
        """
        여러 응답의 반영 수준 일괄 계산
        
        Args:
            responses: 평가할 응답 리스트
            contexts: 맥락 리스트 (옵션)
            
        Returns:
            Dict with:
                - mean_level: 평균 반영 수준
                - mean_normalized: 정규화된 평균 (0-1)
                - level_distribution: 수준별 분포
                - individual: 개별 결과 리스트
        """
        if contexts is None:
            contexts = [None] * len(responses)
        
        results = [
            self.compute(resp, ctx) 
            for resp, ctx in zip(responses, contexts)
        ]
        
        levels = [r["level"] for r in results]
        
        # 수준별 분포 계산
        distribution = {i: levels.count(i) / len(levels) for i in range(7)}
        
        return {
            "mean_level": float(np.mean(levels)),
            "mean_normalized": float(np.mean(levels)) / 6.0,
            "std_level": float(np.std(levels)),
            "level_distribution": distribution,
            "individual": results,
        }


# 테스트 코드
if __name__ == "__main__":
    metric = ReflectionLevelMetric(use_model=False)
    
    # 테스트 예시 (낮은 수준 → 높은 수준)
    test_responses = [
        "Ok.",  # Level 1
        "I understand.",  # Level 2
        "So you're saying that work has been stressful.",  # Level 2-3
        "It sounds like you're feeling overwhelmed.",  # Level 4
        "You're feeling frustrated with the situation.",  # Level 4
        "That must be really difficult for you.",  # Level 4-5
        "It seems like this situation means a lot to you, and beneath the frustration, there's a deeper sense of loss.",  # Level 6
    ]
    
    print("\n=== Reflection Level Metric Test ===\n")
    for response in test_responses:
        result = metric.compute(response)
        print(f"Response: {response}")
        print(f"Level: {result['level']} - {result['interpretation']}")
        print(f"Normalized: {result['normalized_score']:.3f}")
        print()

