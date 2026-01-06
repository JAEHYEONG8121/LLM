"""
통합 공감 평가기 (Empathy Evaluator)

4가지 핵심 차원을 통합하여 LLM의 공감 능력을 종합 평가합니다:
1. Specificity (구체성)
2. Reflection Level (반영 수준)
3. Word Choice (단어 선택/감정 표현)
4. Diversity (다양성)

사용법:
    evaluator = EmpathyEvaluator()
    results = evaluator.evaluate(responses)
    evaluator.print_report(results)
"""

import json
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime

import numpy as np

from .specificity import SpecificityMetric
from .reflection import ReflectionLevelMetric
from .word_choice import WordChoiceMetric
from .diversity import DiversityMetric


@dataclass
class EmpathyScore:
    """개별 응답의 공감 점수"""
    specificity: float
    reflection_level: float
    word_choice_valence: float
    word_choice_arousal: float
    word_choice_dominance: float
    word_choice_intensity: float
    word_choice_empathy_alignment: float
    diversity_distinct_1: float
    diversity_distinct_2: float
    diversity_score: float
    
    # 종합 점수
    overall_score: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class EmpathyReport:
    """전체 평가 리포트"""
    # 메타데이터
    timestamp: str
    num_samples: int
    model_name: Optional[str]
    
    # 차원별 평균 점수
    mean_specificity: float
    mean_reflection_level: float
    mean_word_choice_empathy_alignment: float
    mean_diversity: float
    
    # 차원별 상세 통계
    specificity_stats: Dict[str, float]
    reflection_stats: Dict[str, float]
    word_choice_stats: Dict[str, float]
    diversity_stats: Dict[str, float]
    
    # 종합 점수
    overall_empathy_score: float
    
    # 개별 결과 (옵션)
    individual_scores: Optional[List[EmpathyScore]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.individual_scores:
            result["individual_scores"] = [s.to_dict() for s in self.individual_scores]
        return result
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class EmpathyEvaluator:
    """
    통합 공감 평가기
    
    4가지 차원을 모두 측정하고 종합 점수를 계산합니다.
    """
    
    def __init__(
        self,
        specificity_lexicon_path: Optional[str] = None,
        vad_lexicon_path: Optional[str] = None,
        intensity_lexicon_path: Optional[str] = None,
        use_reflection_model: bool = False,
        reflection_model_name: Optional[str] = None,
        weights: Optional[Dict[str, float]] = None,
    ):
        """
        Args:
            specificity_lexicon_path: Concreteness ratings 파일 경로
            vad_lexicon_path: NRC VAD Lexicon 파일 경로
            intensity_lexicon_path: NRC Affect Intensity Lexicon 경로
            use_reflection_model: 반영 수준에 모델 사용 여부
            reflection_model_name: 반영 수준 모델 이름
            weights: 차원별 가중치 (기본: 균등)
        """
        # 메트릭 초기화
        self.specificity_metric = SpecificityMetric(specificity_lexicon_path)
        self.reflection_metric = ReflectionLevelMetric(
            use_model=use_reflection_model,
            model_name=reflection_model_name
        )
        self.word_choice_metric = WordChoiceMetric(
            vad_lexicon_path=vad_lexicon_path,
            intensity_lexicon_path=intensity_lexicon_path
        )
        self.diversity_metric = DiversityMetric()
        
        # 가중치 설정 (기본: 균등)
        self.weights = weights or {
            "specificity": 0.25,
            "reflection": 0.25,
            "word_choice": 0.25,
            "diversity": 0.25,
        }
    
    def evaluate_single(
        self, 
        response: str,
        context: Optional[str] = None
    ) -> EmpathyScore:
        """
        단일 응답 평가
        
        Args:
            response: 평가할 응답
            context: 대화 맥락 (옵션)
            
        Returns:
            EmpathyScore 객체
        """
        # 각 차원 평가
        spec_result = self.specificity_metric.compute(response)
        refl_result = self.reflection_metric.compute(response, context)
        word_result = self.word_choice_metric.compute(response)
        div_result = self.diversity_metric.compute(response)
        
        # 정규화된 점수 (0-1 범위)
        spec_score = spec_result["score"] / 5.0 if spec_result["score"] > 0 else 0.0
        refl_score = refl_result["normalized_score"]
        word_score = word_result["empathy_alignment"]
        div_score = div_result["diversity_score"]
        
        # 종합 점수 계산
        overall = (
            self.weights["specificity"] * spec_score +
            self.weights["reflection"] * refl_score +
            self.weights["word_choice"] * word_score +
            self.weights["diversity"] * div_score
        )
        
        return EmpathyScore(
            specificity=spec_result["score"],
            reflection_level=refl_result["level"],
            word_choice_valence=word_result["valence"],
            word_choice_arousal=word_result["arousal"],
            word_choice_dominance=word_result["dominance"],
            word_choice_intensity=word_result["intensity"],
            word_choice_empathy_alignment=word_result["empathy_alignment"],
            diversity_distinct_1=div_result["distinct_1"],
            diversity_distinct_2=div_result["distinct_2"],
            diversity_score=div_result["diversity_score"],
            overall_score=overall,
        )
    
    def evaluate(
        self,
        responses: List[str],
        contexts: Optional[List[str]] = None,
        model_name: Optional[str] = None,
        include_individual: bool = True,
    ) -> EmpathyReport:
        """
        여러 응답 일괄 평가
        
        Args:
            responses: 평가할 응답 리스트
            contexts: 대화 맥락 리스트 (옵션)
            model_name: 모델 이름 (메타데이터용)
            include_individual: 개별 결과 포함 여부
            
        Returns:
            EmpathyReport 객체
        """
        if contexts is None:
            contexts = [None] * len(responses)
        
        # 개별 평가
        individual_scores = [
            self.evaluate_single(resp, ctx)
            for resp, ctx in zip(responses, contexts)
        ]
        
        # 차원별 통계 계산
        specificity_values = [s.specificity for s in individual_scores]
        reflection_values = [s.reflection_level for s in individual_scores]
        word_choice_values = [s.word_choice_empathy_alignment for s in individual_scores]
        diversity_values = [s.diversity_score for s in individual_scores]
        overall_values = [s.overall_score for s in individual_scores]
        
        # 코퍼스 레벨 다양성
        corpus_diversity = self.diversity_metric.compute_corpus_diversity(responses)
        
        # 리포트 생성
        report = EmpathyReport(
            timestamp=datetime.now().isoformat(),
            num_samples=len(responses),
            model_name=model_name,
            
            mean_specificity=float(np.mean(specificity_values)),
            mean_reflection_level=float(np.mean(reflection_values)),
            mean_word_choice_empathy_alignment=float(np.mean(word_choice_values)),
            mean_diversity=float(np.mean(diversity_values)),
            
            specificity_stats={
                "mean": float(np.mean(specificity_values)),
                "std": float(np.std(specificity_values)),
                "min": float(np.min(specificity_values)) if specificity_values else 0.0,
                "max": float(np.max(specificity_values)) if specificity_values else 0.0,
            },
            reflection_stats={
                "mean": float(np.mean(reflection_values)),
                "std": float(np.std(reflection_values)),
                "level_distribution": {
                    i: sum(1 for v in reflection_values if v == i) / len(reflection_values)
                    for i in range(7)
                },
            },
            word_choice_stats={
                "mean_valence": float(np.mean([s.word_choice_valence for s in individual_scores])),
                "mean_arousal": float(np.mean([s.word_choice_arousal for s in individual_scores])),
                "mean_dominance": float(np.mean([s.word_choice_dominance for s in individual_scores])),
                "mean_intensity": float(np.mean([s.word_choice_intensity for s in individual_scores])),
                "mean_empathy_alignment": float(np.mean(word_choice_values)),
            },
            diversity_stats={
                "mean_distinct_1": float(np.mean([s.diversity_distinct_1 for s in individual_scores])),
                "mean_distinct_2": float(np.mean([s.diversity_distinct_2 for s in individual_scores])),
                "corpus_distinct_1": corpus_diversity["corpus_distinct_1"],
                "corpus_distinct_2": corpus_diversity["corpus_distinct_2"],
                "corpus_entropy": corpus_diversity["corpus_entropy"],
            },
            
            overall_empathy_score=float(np.mean(overall_values)),
            
            individual_scores=individual_scores if include_individual else None,
        )
        
        return report
    
    def compare_models(
        self,
        model_results: Dict[str, List[str]],
        contexts: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        여러 모델의 응답 비교
        
        Args:
            model_results: {모델이름: 응답리스트} 딕셔너리
            contexts: 공통 맥락 리스트 (옵션)
            
        Returns:
            모델 간 비교 결과
        """
        reports = {}
        for model_name, responses in model_results.items():
            reports[model_name] = self.evaluate(
                responses, 
                contexts, 
                model_name=model_name,
                include_individual=False
            )
        
        # 비교 테이블 생성
        comparison = {
            "models": list(model_results.keys()),
            "metrics": {
                "specificity": {m: r.mean_specificity for m, r in reports.items()},
                "reflection_level": {m: r.mean_reflection_level for m, r in reports.items()},
                "word_choice": {m: r.mean_word_choice_empathy_alignment for m, r in reports.items()},
                "diversity": {m: r.mean_diversity for m, r in reports.items()},
                "overall": {m: r.overall_empathy_score for m, r in reports.items()},
            },
            "reports": {m: r.to_dict() for m, r in reports.items()},
        }
        
        # 순위 계산
        for metric in comparison["metrics"]:
            scores = comparison["metrics"][metric]
            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            comparison["metrics"][metric]["ranking"] = [m for m, _ in ranked]
        
        return comparison
    
    def print_report(self, report: EmpathyReport) -> None:
        """리포트 출력"""
        print("\n" + "=" * 60)
        print("EMPATHY EVALUATION REPORT")
        print("=" * 60)
        
        print(f"\nModel: {report.model_name or 'Unknown'}")
        print(f"Timestamp: {report.timestamp}")
        print(f"Samples: {report.num_samples}")
        
        print("\n" + "-" * 40)
        print("DIMENSION SCORES (Mean)")
        print("-" * 40)
        
        print(f"  Specificity:        {report.mean_specificity:.3f} / 5.0")
        print(f"  Reflection Level:   {report.mean_reflection_level:.2f} / 6.0")
        print(f"  Word Choice:        {report.mean_word_choice_empathy_alignment:.3f} / 1.0")
        print(f"  Diversity:          {report.mean_diversity:.3f} / 1.0")
        
        print("\n" + "-" * 40)
        print("OVERALL EMPATHY SCORE")
        print("-" * 40)
        print(f"  {report.overall_empathy_score:.3f} / 1.0")
        
        print("\n" + "-" * 40)
        print("DETAILED STATISTICS")
        print("-" * 40)
        
        print("\n[Specificity]")
        stats = report.specificity_stats
        print(f"  Mean: {stats['mean']:.3f}, Std: {stats['std']:.3f}")
        print(f"  Range: [{stats['min']:.3f}, {stats['max']:.3f}]")
        
        print("\n[Reflection Level]")
        stats = report.reflection_stats
        print(f"  Mean: {stats['mean']:.2f}, Std: {stats['std']:.2f}")
        
        print("\n[Word Choice]")
        stats = report.word_choice_stats
        print(f"  Valence:   {stats['mean_valence']:.3f}")
        print(f"  Arousal:   {stats['mean_arousal']:.3f}")
        print(f"  Dominance: {stats['mean_dominance']:.3f}")
        print(f"  Intensity: {stats['mean_intensity']:.3f}")
        
        print("\n[Diversity]")
        stats = report.diversity_stats
        print(f"  Distinct-1: {stats['mean_distinct_1']:.3f}")
        print(f"  Distinct-2: {stats['mean_distinct_2']:.3f}")
        print(f"  Corpus Distinct-2: {stats['corpus_distinct_2']:.3f}")
        
        print("\n" + "=" * 60)
    
    def save_report(self, report: EmpathyReport, path: str) -> None:
        """리포트를 JSON 파일로 저장"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(report.to_json())
        print(f"Report saved to: {path}")


# 테스트 코드
if __name__ == "__main__":
    evaluator = EmpathyEvaluator()
    
    # 테스트 응답들
    test_responses = [
        "I understand how you feel. That must be really difficult.",
        "It sounds like you're going through a challenging time. Your feelings are completely valid.",
        "I'm sorry to hear that. I'm here for you if you need to talk.",
        "That's a lot to process. It seems like beneath all this, there's a deeper sense of loss.",
        "I hear you. Sometimes life throws unexpected challenges our way.",
    ]
    
    # 평가 실행
    report = evaluator.evaluate(
        responses=test_responses,
        model_name="Test Model"
    )
    
    # 리포트 출력
    evaluator.print_report(report)

