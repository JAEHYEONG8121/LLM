"""
Word Choice (단어 선택과 감정 표현) 메트릭

NRC VAD Lexicon (Mohammad, 2018) 기반으로
단어 선택의 감정적 특성을 측정합니다.

세 가지 차원:
- Valence: 긍정/부정 (0-1, 높을수록 긍정)
- Arousal: 각성 수준 (0-1, 높을수록 각성)
- Dominance: 지배/통제 (0-1, 높을수록 통제감)

추가로 Intensity (감정 강도)도 측정합니다.

참고: Mohammad, S. M. (2018). "Obtaining Reliable Human Ratings of 
Valence, Arousal, and Dominance for 20,000 English Words"
"""

import os
import re
from typing import List, Dict, Optional, Union, Tuple

import numpy as np


class WordChoiceMetric:
    """
    NRC VAD Lexicon을 사용한 단어 선택/감정 표현 메트릭
    
    측정 항목:
    - Valence (V): 쾌/불쾌
    - Arousal (A): 각성 수준
    - Dominance (D): 통제감
    - Intensity: 감정 강도
    """
    
    def __init__(
        self, 
        vad_lexicon_path: Optional[str] = None,
        intensity_lexicon_path: Optional[str] = None
    ):
        """
        Args:
            vad_lexicon_path: NRC VAD Lexicon 파일 경로
            intensity_lexicon_path: NRC Affect Intensity Lexicon 경로
        """
        self.vad_lexicon: Dict[str, Dict[str, float]] = {}
        self.intensity_lexicon: Dict[str, float] = {}
        
        # 렉시콘 로드
        self._load_vad_lexicon(vad_lexicon_path)
        self._load_intensity_lexicon(intensity_lexicon_path)
    
    def _load_vad_lexicon(self, path: Optional[str]) -> None:
        """NRC VAD Lexicon 로드"""
        if path and os.path.exists(path):
            self._load_vad_from_file(path)
        else:
            self._load_default_vad_lexicon()
    
    def _load_vad_from_file(self, path: str) -> None:
        """파일에서 VAD 렉시콘 로드"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                header = f.readline()  # Skip header
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 4:
                        word = parts[0].lower()
                        self.vad_lexicon[word] = {
                            "valence": float(parts[1]),
                            "arousal": float(parts[2]),
                            "dominance": float(parts[3]),
                        }
            print(f"Loaded {len(self.vad_lexicon)} words from VAD lexicon")
        except Exception as e:
            print(f"Error loading VAD lexicon: {e}")
            self._load_default_vad_lexicon()
    
    def _load_default_vad_lexicon(self) -> None:
        """
        기본 샘플 VAD 렉시콘
        실제 연구에서는 NRC VAD Lexicon 다운로드 필요
        https://saifmohammad.com/WebPages/nrc-vad.html
        """
        # 샘플 데이터: {word: {valence, arousal, dominance}}
        self.vad_lexicon = {
            # 긍정적, 높은 각성 단어들
            "happy": {"valence": 0.96, "arousal": 0.74, "dominance": 0.87},
            "excited": {"valence": 0.90, "arousal": 0.85, "dominance": 0.75},
            "joy": {"valence": 0.98, "arousal": 0.78, "dominance": 0.82},
            "love": {"valence": 0.95, "arousal": 0.72, "dominance": 0.70},
            "wonderful": {"valence": 0.94, "arousal": 0.68, "dominance": 0.78},
            "amazing": {"valence": 0.92, "arousal": 0.75, "dominance": 0.72},
            "great": {"valence": 0.88, "arousal": 0.62, "dominance": 0.80},
            "proud": {"valence": 0.85, "arousal": 0.58, "dominance": 0.88},
            "grateful": {"valence": 0.90, "arousal": 0.48, "dominance": 0.65},
            "relieved": {"valence": 0.82, "arousal": 0.35, "dominance": 0.68},
            
            # 긍정적, 낮은 각성 단어들
            "calm": {"valence": 0.78, "arousal": 0.22, "dominance": 0.72},
            "peaceful": {"valence": 0.85, "arousal": 0.18, "dominance": 0.70},
            "relaxed": {"valence": 0.80, "arousal": 0.20, "dominance": 0.68},
            "content": {"valence": 0.75, "arousal": 0.30, "dominance": 0.65},
            
            # 부정적, 높은 각성 단어들
            "angry": {"valence": 0.15, "arousal": 0.85, "dominance": 0.55},
            "furious": {"valence": 0.08, "arousal": 0.92, "dominance": 0.48},
            "scared": {"valence": 0.12, "arousal": 0.88, "dominance": 0.18},
            "terrified": {"valence": 0.05, "arousal": 0.95, "dominance": 0.10},
            "anxious": {"valence": 0.20, "arousal": 0.78, "dominance": 0.25},
            "stressed": {"valence": 0.18, "arousal": 0.82, "dominance": 0.30},
            "frustrated": {"valence": 0.15, "arousal": 0.75, "dominance": 0.35},
            "overwhelmed": {"valence": 0.12, "arousal": 0.80, "dominance": 0.15},
            
            # 부정적, 낮은 각성 단어들
            "sad": {"valence": 0.15, "arousal": 0.32, "dominance": 0.25},
            "depressed": {"valence": 0.08, "arousal": 0.28, "dominance": 0.15},
            "lonely": {"valence": 0.12, "arousal": 0.35, "dominance": 0.20},
            "hopeless": {"valence": 0.05, "arousal": 0.25, "dominance": 0.08},
            "disappointed": {"valence": 0.18, "arousal": 0.42, "dominance": 0.28},
            "tired": {"valence": 0.25, "arousal": 0.15, "dominance": 0.30},
            
            # 중립적 단어들
            "think": {"valence": 0.55, "arousal": 0.45, "dominance": 0.60},
            "know": {"valence": 0.60, "arousal": 0.40, "dominance": 0.65},
            "feel": {"valence": 0.50, "arousal": 0.50, "dominance": 0.50},
            "understand": {"valence": 0.70, "arousal": 0.35, "dominance": 0.65},
            "situation": {"valence": 0.45, "arousal": 0.40, "dominance": 0.45},
            
            # 공감 관련 단어들
            "sorry": {"valence": 0.35, "arousal": 0.45, "dominance": 0.35},
            "care": {"valence": 0.82, "arousal": 0.45, "dominance": 0.55},
            "support": {"valence": 0.78, "arousal": 0.48, "dominance": 0.62},
            "help": {"valence": 0.75, "arousal": 0.52, "dominance": 0.58},
            "comfort": {"valence": 0.80, "arousal": 0.28, "dominance": 0.55},
            "hear": {"valence": 0.58, "arousal": 0.38, "dominance": 0.52},
            "listen": {"valence": 0.62, "arousal": 0.35, "dominance": 0.48},
        }
        print(f"Loaded default sample VAD lexicon with {len(self.vad_lexicon)} words")
        print("Note: For research, download NRC VAD Lexicon from saifmohammad.com")
    
    def _load_intensity_lexicon(self, path: Optional[str]) -> None:
        """NRC Affect Intensity Lexicon 로드"""
        if path and os.path.exists(path):
            self._load_intensity_from_file(path)
        else:
            self._load_default_intensity_lexicon()
    
    def _load_intensity_from_file(self, path: str) -> None:
        """파일에서 Intensity 렉시콘 로드"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        word = parts[0].lower()
                        self.intensity_lexicon[word] = float(parts[1])
            print(f"Loaded {len(self.intensity_lexicon)} words from intensity lexicon")
        except Exception as e:
            print(f"Error loading intensity lexicon: {e}")
            self._load_default_intensity_lexicon()
    
    def _load_default_intensity_lexicon(self) -> None:
        """기본 샘플 Intensity 렉시콘"""
        # 감정 강도: 0 (낮음) ~ 1 (높음)
        self.intensity_lexicon = {
            # 높은 강도
            "ecstatic": 0.95, "furious": 0.92, "terrified": 0.90,
            "overjoyed": 0.88, "devastated": 0.87, "thrilled": 0.85,
            "enraged": 0.88, "horrified": 0.86, "elated": 0.82,
            
            # 중간 강도
            "happy": 0.70, "angry": 0.72, "scared": 0.68,
            "excited": 0.75, "sad": 0.65, "frustrated": 0.70,
            "anxious": 0.68, "grateful": 0.65, "disappointed": 0.62,
            "proud": 0.60, "worried": 0.65, "relieved": 0.58,
            
            # 낮은 강도
            "content": 0.45, "annoyed": 0.48, "nervous": 0.50,
            "pleased": 0.52, "upset": 0.55, "uneasy": 0.45,
            "okay": 0.30, "fine": 0.35, "alright": 0.32,
            
            # 매우 낮은 강도
            "calm": 0.25, "relaxed": 0.28, "neutral": 0.15,
            "indifferent": 0.10,
        }
        print(f"Loaded default sample intensity lexicon with {len(self.intensity_lexicon)} words")
    
    def _tokenize(self, text: str) -> List[str]:
        """간단한 토크나이저"""
        text = text.lower()
        words = re.findall(r'\b[a-z]+\b', text)
        return words
    
    def compute(self, text: str) -> Dict[str, Union[float, Dict]]:
        """
        텍스트의 단어 선택/감정 표현 점수 계산
        
        Args:
            text: 평가할 텍스트
            
        Returns:
            Dict with:
                - valence: 평균 Valence (0-1)
                - arousal: 평균 Arousal (0-1)
                - dominance: 평균 Dominance (0-1)
                - intensity: 평균 감정 강도 (0-1)
                - coverage: 렉시콘 매칭 비율
                - emotion_words: 감정 단어 수
        """
        words = self._tokenize(text)
        
        if not words:
            return self._empty_result()
        
        # VAD 점수 수집
        valence_scores = []
        arousal_scores = []
        dominance_scores = []
        intensity_scores = []
        
        matched_vad = 0
        matched_intensity = 0
        
        for word in words:
            if word in self.vad_lexicon:
                vad = self.vad_lexicon[word]
                valence_scores.append(vad["valence"])
                arousal_scores.append(vad["arousal"])
                dominance_scores.append(vad["dominance"])
                matched_vad += 1
            
            if word in self.intensity_lexicon:
                intensity_scores.append(self.intensity_lexicon[word])
                matched_intensity += 1
        
        # 결과 계산
        result = {
            "valence": float(np.mean(valence_scores)) if valence_scores else 0.5,
            "arousal": float(np.mean(arousal_scores)) if arousal_scores else 0.5,
            "dominance": float(np.mean(dominance_scores)) if dominance_scores else 0.5,
            "intensity": float(np.mean(intensity_scores)) if intensity_scores else 0.0,
            "vad_coverage": matched_vad / len(words) if words else 0.0,
            "intensity_coverage": matched_intensity / len(words) if words else 0.0,
            "word_count": len(words),
            "emotion_words": matched_vad,
        }
        
        # 종합 감정 점수 (VAD 기반)
        # 공감적 응답: 적절한 valence, 중간 arousal, 낮은 dominance
        result["empathy_alignment"] = self._compute_empathy_alignment(
            result["valence"], 
            result["arousal"], 
            result["dominance"]
        )
        
        return result
    
    def _empty_result(self) -> Dict[str, Union[float, Dict]]:
        """빈 결과 반환"""
        return {
            "valence": 0.5,
            "arousal": 0.5,
            "dominance": 0.5,
            "intensity": 0.0,
            "vad_coverage": 0.0,
            "intensity_coverage": 0.0,
            "word_count": 0,
            "emotion_words": 0,
            "empathy_alignment": 0.0,
        }
    
    def _compute_empathy_alignment(
        self, 
        valence: float, 
        arousal: float, 
        dominance: float
    ) -> float:
        """
        공감적 단어 선택 정렬 점수 계산
        
        공감적 응답의 특성:
        - Valence: 상황에 따라 다름 (여기선 중립~긍정 선호)
        - Arousal: 중간 수준 (너무 높지도 낮지도 않음)
        - Dominance: 낮음 (상대방에게 통제권 부여)
        """
        # 이상적인 공감 응답 VAD 프로파일
        ideal_valence = 0.65  # 약간 긍정적
        ideal_arousal = 0.45  # 중간 각성
        ideal_dominance = 0.40  # 낮은 지배성
        
        # 거리 계산 (낮을수록 좋음)
        v_diff = abs(valence - ideal_valence)
        a_diff = abs(arousal - ideal_arousal)
        d_diff = abs(dominance - ideal_dominance)
        
        # 정렬 점수 (1 - 평균 거리)
        alignment = 1.0 - (v_diff + a_diff + d_diff) / 3.0
        
        return max(0.0, min(1.0, alignment))
    
    def compute_distance(
        self, 
        prompt: str, 
        response: str
    ) -> Dict[str, float]:
        """
        프롬프트와 응답 간의 VAD 거리 계산
        (EmPO 논문 방식)
        
        Args:
            prompt: 사용자 입력
            response: 모델 응답
            
        Returns:
            Dict with VAD distances
        """
        prompt_result = self.compute(prompt)
        response_result = self.compute(response)
        
        return {
            "valence_distance": abs(prompt_result["valence"] - response_result["valence"]),
            "arousal_distance": abs(prompt_result["arousal"] - response_result["arousal"]),
            "dominance_distance": abs(prompt_result["dominance"] - response_result["dominance"]),
            "intensity_distance": abs(prompt_result["intensity"] - response_result["intensity"]),
            "prompt_vad": {
                "valence": prompt_result["valence"],
                "arousal": prompt_result["arousal"],
                "dominance": prompt_result["dominance"],
            },
            "response_vad": {
                "valence": response_result["valence"],
                "arousal": response_result["arousal"],
                "dominance": response_result["dominance"],
            },
        }
    
    def compute_batch(self, texts: List[str]) -> Dict[str, Union[float, List[Dict]]]:
        """
        여러 텍스트의 단어 선택 점수 일괄 계산
        
        Args:
            texts: 평가할 텍스트 리스트
            
        Returns:
            Dict with aggregated results
        """
        results = [self.compute(text) for text in texts]
        
        return {
            "mean_valence": float(np.mean([r["valence"] for r in results])),
            "mean_arousal": float(np.mean([r["arousal"] for r in results])),
            "mean_dominance": float(np.mean([r["dominance"] for r in results])),
            "mean_intensity": float(np.mean([r["intensity"] for r in results])),
            "mean_empathy_alignment": float(np.mean([r["empathy_alignment"] for r in results])),
            "std_valence": float(np.std([r["valence"] for r in results])),
            "std_arousal": float(np.std([r["arousal"] for r in results])),
            "individual": results,
        }


# 테스트 코드
if __name__ == "__main__":
    metric = WordChoiceMetric()
    
    # 테스트 예시
    test_texts = [
        "I'm so happy and excited to hear about your wonderful news!",  # 긍정, 높은 각성
        "I understand you're feeling sad and lonely right now.",  # 공감적, 낮은 각성
        "That sounds incredibly frustrating and overwhelming.",  # 부정, 높은 각성
        "I hear you. It's okay to feel this way.",  # 중립적, 공감적
    ]
    
    print("\n=== Word Choice Metric Test ===\n")
    for text in test_texts:
        result = metric.compute(text)
        print(f"Text: {text}")
        print(f"  Valence: {result['valence']:.3f}")
        print(f"  Arousal: {result['arousal']:.3f}")
        print(f"  Dominance: {result['dominance']:.3f}")
        print(f"  Intensity: {result['intensity']:.3f}")
        print(f"  Empathy Alignment: {result['empathy_alignment']:.3f}")
        print()
    
    # 거리 테스트
    print("=== Distance Test ===\n")
    prompt = "I'm feeling really stressed and anxious about my job."
    response = "I understand how stressful that can be. It's natural to feel anxious."
    
    distance = metric.compute_distance(prompt, response)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print(f"Valence Distance: {distance['valence_distance']:.3f}")
    print(f"Arousal Distance: {distance['arousal_distance']:.3f}")

