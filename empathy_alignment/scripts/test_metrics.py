"""
메트릭 테스트 스크립트

4가지 공감 메트릭이 제대로 작동하는지 테스트합니다.
"""

import sys
import os

# 프로젝트 루트를 path에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.metrics import (
    SpecificityMetric,
    ReflectionLevelMetric,
    WordChoiceMetric,
    DiversityMetric,
    EmpathyEvaluator,
)


def test_specificity():
    """구체성 메트릭 테스트"""
    print("\n" + "=" * 50)
    print("Testing Specificity Metric")
    print("=" * 50)
    
    metric = SpecificityMetric()
    
    test_cases = [
        ("I bought a red apple and a book from the store.", "High specificity"),
        ("I understand your feelings about the situation.", "Medium specificity"),
        ("Something happened and everything is nothing.", "Low specificity"),
    ]
    
    for text, expected in test_cases:
        result = metric.compute(text)
        print(f"\nText: {text}")
        print(f"Expected: {expected}")
        print(f"Score: {result['score']:.3f} (Coverage: {result['coverage']:.1%})")


def test_reflection():
    """반영 수준 메트릭 테스트"""
    print("\n" + "=" * 50)
    print("Testing Reflection Level Metric")
    print("=" * 50)
    
    metric = ReflectionLevelMetric(use_model=False)
    
    test_cases = [
        ("Ok.", "Level 1 - Minimal"),
        ("I understand.", "Level 2 - Simple"),
        ("So you're saying that work has been stressful.", "Level 2-3"),
        ("It sounds like you're feeling overwhelmed.", "Level 4"),
        ("That must be really difficult for you.", "Level 4-5"),
        ("It seems like this situation means a lot to you.", "Level 5-6"),
    ]
    
    for text, expected in test_cases:
        result = metric.compute(text)
        print(f"\nText: {text}")
        print(f"Expected: {expected}")
        print(f"Level: {result['level']} - {result['interpretation']}")


def test_word_choice():
    """단어 선택 메트릭 테스트"""
    print("\n" + "=" * 50)
    print("Testing Word Choice Metric")
    print("=" * 50)
    
    metric = WordChoiceMetric()
    
    test_cases = [
        "I'm so happy and excited to hear your wonderful news!",
        "I understand you're feeling sad and lonely right now.",
        "That sounds incredibly frustrating and overwhelming.",
        "I hear you. It's okay to feel this way.",
    ]
    
    for text in test_cases:
        result = metric.compute(text)
        print(f"\nText: {text}")
        print(f"  Valence: {result['valence']:.3f}")
        print(f"  Arousal: {result['arousal']:.3f}")
        print(f"  Dominance: {result['dominance']:.3f}")
        print(f"  Empathy Alignment: {result['empathy_alignment']:.3f}")


def test_diversity():
    """다양성 메트릭 테스트"""
    print("\n" + "=" * 50)
    print("Testing Diversity Metric")
    print("=" * 50)
    
    metric = DiversityMetric()
    
    test_cases = [
        "I understand how you feel. That must be really difficult for you.",
        "I'm sorry. I'm sorry to hear that. I'm sorry you're going through this.",
        "Your experience sounds challenging and complex with many emotions.",
    ]
    
    for text in test_cases:
        result = metric.compute(text)
        print(f"\nText: {text[:50]}...")
        print(f"  Distinct-1: {result['distinct_1']:.3f}")
        print(f"  Distinct-2: {result['distinct_2']:.3f}")
        print(f"  Diversity Score: {result['diversity_score']:.3f}")


def test_evaluator():
    """통합 평가기 테스트"""
    print("\n" + "=" * 50)
    print("Testing Empathy Evaluator")
    print("=" * 50)
    
    evaluator = EmpathyEvaluator()
    
    test_responses = [
        "I understand how you feel. That must be really difficult.",
        "It sounds like you're going through a challenging time.",
        "I'm sorry to hear that. I'm here for you if you need to talk.",
        "That's a lot to process. Your feelings are completely valid.",
        "I hear you. Sometimes life throws unexpected challenges our way.",
    ]
    
    report = evaluator.evaluate(
        responses=test_responses,
        model_name="Test Model"
    )
    
    evaluator.print_report(report)


def main():
    """모든 테스트 실행"""
    print("\n" + "#" * 60)
    print("EMPATHY METRICS TEST SUITE")
    print("#" * 60)
    
    test_specificity()
    test_reflection()
    test_word_choice()
    test_diversity()
    test_evaluator()
    
    print("\n" + "#" * 60)
    print("ALL TESTS COMPLETED")
    print("#" * 60)


if __name__ == "__main__":
    main()

