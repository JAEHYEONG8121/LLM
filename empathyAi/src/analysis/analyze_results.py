# -*- coding: utf-8 -*-
"""
평가 결과 분석 스크립트
- 클래스 불균형 분석
- 오분류 패턴 분석
- 성능 개선 시뮬레이션 (3-class, 인접 라벨 허용)

사용법:
    python -m src.analysis.analyze_results --input data/eval_results.json
"""

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

import numpy as np


def load_results(path: Path) -> Dict:
    """평가 결과 JSON 로드"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_class_imbalance(predictions: List[Dict]) -> Dict:
    """클래스 불균형 분석"""
    gold_labels = [p["gold"] for p in predictions if p["gold"] is not None]
    label_counts = Counter(gold_labels)
    total = len(gold_labels)
    
    distribution = {}
    for label in sorted(label_counts.keys()):
        count = label_counts[label]
        distribution[label] = {
            "count": count,
            "percentage": count / total * 100 if total > 0 else 0,
        }
    
    return {
        "total_samples": total,
        "distribution": distribution,
        "majority_class": max(label_counts, key=label_counts.get) if label_counts else None,
        "minority_classes": [l for l, c in label_counts.items() if c / total < 0.1] if total > 0 else [],
    }


def analyze_misclassification(confusion_matrix: Dict, threshold: int = 20) -> List[Dict]:
    """주요 오분류 패턴 분석"""
    labels = confusion_matrix["labels"]
    matrix = confusion_matrix["matrix"]
    
    patterns = []
    for i, true_label in enumerate(labels):
        row_sum = sum(matrix[i])
        for j, pred_label in enumerate(labels):
            if i != j and matrix[i][j] >= threshold:
                patterns.append({
                    "true_label": true_label,
                    "pred_label": pred_label,
                    "count": matrix[i][j],
                    "percentage": matrix[i][j] / row_sum * 100 if row_sum > 0 else 0,
                })
    
    return sorted(patterns, key=lambda x: x["count"], reverse=True)


def simulate_simplified_classes(predictions: List[Dict]) -> Dict:
    """3-class 단순화 시뮬레이션"""
    def simplify(label):
        if label in [0, 1]:
            return 0  # Low/None
        elif label in [2, 3]:
            return 1  # Medium
        else:
            return 2  # High
    
    correct_5class = 0
    correct_3class = 0
    correct_adjacent = 0
    total = 0
    
    for p in predictions:
        gold = p.get("gold")
        ft_pred = p.get("ft_pred")
        
        if gold is None or ft_pred is None:
            continue
        
        total += 1
        
        if gold == ft_pred:
            correct_5class += 1
        
        if simplify(gold) == simplify(ft_pred):
            correct_3class += 1
        
        if abs(gold - ft_pred) <= 1:
            correct_adjacent += 1
    
    return {
        "total": total,
        "accuracy_5class": correct_5class / total if total > 0 else 0,
        "accuracy_3class": correct_3class / total if total > 0 else 0,
        "accuracy_adjacent": correct_adjacent / total if total > 0 else 0,
    }


def print_analysis_report(results: Dict):
    """분석 결과 출력"""
    predictions = results.get("predictions", [])
    ft_metrics = results.get("ft_model", {}).get("metrics", {})
    base_metrics = results.get("base_model", {}).get("metrics", {})
    ft_cm = results.get("ft_model", {}).get("confusion_matrix", {})
    
    print("=" * 70)
    print("EmpathyAI 평가 결과 분석")
    print("=" * 70)
    
    # 1. 기본 성능
    print("\n[1] 모델 성능 비교")
    print("-" * 50)
    print(f"{'메트릭':<20} {'Base Model':<15} {'Fine-tuned':<15}")
    print("-" * 50)
    print(f"{'Accuracy':<20} {base_metrics.get('accuracy', 0)*100:>12.2f}% {ft_metrics.get('accuracy', 0)*100:>12.2f}%")
    print(f"{'Macro Precision':<20} {base_metrics.get('macro_precision', 0):>12.4f}  {ft_metrics.get('macro_precision', 0):>12.4f}")
    print(f"{'Macro Recall':<20} {base_metrics.get('macro_recall', 0):>12.4f}  {ft_metrics.get('macro_recall', 0):>12.4f}")
    print(f"{'Macro F1':<20} {base_metrics.get('macro_f1', 0):>12.4f}  {ft_metrics.get('macro_f1', 0):>12.4f}")
    
    # 2. 클래스 불균형
    imbalance = analyze_class_imbalance(predictions)
    print("\n[2] 클래스 불균형 분석")
    print("-" * 50)
    print(f"{'Label':<10} {'Count':<10} {'Percentage':<15} {'비고'}")
    print("-" * 50)
    for label, stats in imbalance["distribution"].items():
        note = ""
        if stats["percentage"] > 40:
            note = "*** 다수 클래스"
        elif stats["percentage"] < 10:
            note = "*** 소수 클래스"
        print(f"{label:<10} {stats['count']:<10} {stats['percentage']:>10.1f}%     {note}")
    
    # 3. 오분류 패턴
    if ft_cm:
        patterns = analyze_misclassification(ft_cm)
        print("\n[3] 주요 오분류 패턴 (Fine-tuned Model)")
        print("-" * 50)
        print(f"{'실제':<10} {'예측':<10} {'개수':<10} {'비율'}")
        print("-" * 50)
        for p in patterns[:8]:
            print(f"{p['true_label']:<10} {p['pred_label']:<10} {p['count']:<10} {p['percentage']:.1f}%")
    
    # 4. 단순화 시뮬레이션
    sim = simulate_simplified_classes(predictions)
    print("\n[4] 클래스 단순화 시뮬레이션")
    print("-" * 50)
    print(f"원래 5-class 정확도:    {sim['accuracy_5class']*100:.2f}%")
    print(f"3-class 단순화 정확도:  {sim['accuracy_3class']*100:.2f}%  (+{(sim['accuracy_3class']-sim['accuracy_5class'])*100:.2f}%p)")
    print(f"±1 인접 허용 정확도:    {sim['accuracy_adjacent']*100:.2f}%  (+{(sim['accuracy_adjacent']-sim['accuracy_5class'])*100:.2f}%p)")
    
    # 5. 개선 제안
    print("\n" + "=" * 70)
    print("[5] 성능 개선 제안")
    print("=" * 70)
    print("""
1. 클래스 단순화: 5-class → 3-class (Low/Medium/High)
2. 데이터 증강: 소수 클래스 오버샘플링
3. 모델 업그레이드: GPT-4.1 Mini/Standard 사용
4. 프롬프트 개선: Few-shot 예시 추가
""")


def main():
    parser = argparse.ArgumentParser(description="평가 결과 분석")
    parser.add_argument("--input", "-i", type=Path, default=Path("data/eval_results.json"))
    args = parser.parse_args()
    
    results = load_results(args.input)
    print_analysis_report(results)


if __name__ == "__main__":
    main()

