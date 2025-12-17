# -*- coding: utf-8 -*-
"""
Fine-tuning 모델과 베이스 모델 비교 평가 스크립트
- 검증 결과를 JSON 파일로 저장
- 정확도, Precision, Recall, F1 계산
- 혼동 행렬 생성

사용법:
    python -m src.evaluation.eval_ft_vs_base --dataset data/train_val/opela_empathy_val.jsonl
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI

# ============================================
# 상수 설정
# ============================================
LABEL_SET = [0, 1, 2, 3, 4]
DEFAULT_DATASET = Path("data/train_val/opela_empathy_val.jsonl")
BASE_MODEL = "gpt-4.1-nano-2025-04-14"
FT_MODEL = "ft:gpt-4.1-nano-2025-04-14:personal::Cn0GL0QT"
DEFAULT_OUTPUT = Path("data/eval_results.json")

SYSTEM_PROMPT = (
    "You are an empathy classifier for Korean persona-user dialogues. "
    "Given a USER utterance and the PERSONA's reply, output a JSON object ONLY "
    'with the key "empathy_label" whose value is an integer in {0,1,2,3,4}.\n'
    "Label meanings: 0=not applicable, 1=empathy failure, 2=low empathy, "
    "3=moderate empathy, 4=high active empathy."
)


# ============================================
# OpenAI 클라이언트
# ============================================
def init_client() -> OpenAI:
    """OpenAI 클라이언트 초기화"""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경 변수를 설정해주세요.")
    return OpenAI(api_key=api_key)


# ============================================
# 데이터 로드
# ============================================
def load_samples(path: Path) -> List[Dict[str, Any]]:
    """JSONL 파일에서 샘플 로드"""
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_prompt(sample: Dict[str, Any]) -> str:
    """샘플에서 user 프롬프트 추출"""
    if "messages" in sample:
        for msg in sample["messages"]:
            if msg.get("role") == "user":
                return msg.get("content", "")
    return ""


def get_gold_label(sample: Dict[str, Any]) -> Optional[int]:
    """샘플에서 정답 라벨 추출"""
    if "messages" in sample:
        for msg in reversed(sample["messages"]):
            if msg.get("role") == "assistant":
                try:
                    obj = json.loads(msg.get("content", ""))
                    if isinstance(obj, dict) and "empathy_label" in obj:
                        return int(obj["empathy_label"])
                except:
                    pass
                break
    return sample.get("empathy_label")


# ============================================
# 모델 응답 파싱
# ============================================
JSON_PATTERN = re.compile(r"\{.*\}", flags=re.DOTALL)


def extract_empathy_label(raw_text: Optional[str]) -> Tuple[Optional[int], str]:
    """모델 응답에서 empathy_label 추출"""
    if raw_text is None:
        return None, ""
    
    raw_text = raw_text.strip()
    
    # JSON 직접 파싱 시도
    try:
        obj = json.loads(raw_text)
        if isinstance(obj, dict) and "empathy_label" in obj:
            return int(obj["empathy_label"]), raw_text
    except:
        pass
    
    # 마크다운 코드블록 제거 후 재시도
    cleaned = re.sub(r"^```(json)?", "", raw_text, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    
    match = JSON_PATTERN.search(cleaned)
    if match:
        try:
            obj = json.loads(match.group(0))
            if isinstance(obj, dict) and "empathy_label" in obj:
                return int(obj["empathy_label"]), raw_text
        except:
            pass
    
    # 정규식으로 숫자 추출 시도
    match_num = re.search(r"empathy_label\s*[:=]\s*([0-4])", cleaned)
    if match_num:
        return int(match_num.group(1)), raw_text
    
    return None, raw_text


# ============================================
# 모델 호출
# ============================================
def predict_label(client: OpenAI, model_name: str, prompt: str) -> Tuple[Optional[int], str]:
    """모델에 프롬프트를 전송하고 라벨 예측"""
    resp = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=50,
    )
    
    raw = resp.choices[0].message.content if resp.choices else ""
    return extract_empathy_label(raw)


# ============================================
# 메트릭 계산
# ============================================
def compute_metrics(preds: List[int], labels: List[int], label_set: List[int]) -> Dict:
    """정확도, Precision, Recall, F1 계산"""
    total = len(labels)
    if total == 0:
        return {"accuracy": 0.0, "macro_precision": 0.0, "macro_recall": 0.0, "macro_f1": 0.0}
    
    correct = sum(1 for p, g in zip(preds, labels) if p == g)
    
    per_class = {}
    macro_p, macro_r, macro_f1 = 0.0, 0.0, 0.0
    
    for label in label_set:
        tp = sum(1 for p, g in zip(preds, labels) if p == label and g == label)
        fp = sum(1 for p, g in zip(preds, labels) if p == label and g != label)
        fn = sum(1 for p, g in zip(preds, labels) if p != label and g == label)
        
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}
        macro_p += precision
        macro_r += recall
        macro_f1 += f1
    
    n = len(label_set)
    return {
        "accuracy": correct / total,
        "correct": correct,
        "total": total,
        "macro_precision": macro_p / n,
        "macro_recall": macro_r / n,
        "macro_f1": macro_f1 / n,
        "per_class": per_class,
    }


def compute_confusion_matrix(preds: List[int], labels: List[int], label_set: List[int]) -> Dict:
    """혼동 행렬 생성"""
    matrix = [[0] * len(label_set) for _ in label_set]
    label_to_idx = {l: i for i, l in enumerate(label_set)}
    
    for p, g in zip(preds, labels):
        if p in label_to_idx and g in label_to_idx:
            matrix[label_to_idx[g]][label_to_idx[p]] += 1
    
    return {"labels": label_set, "matrix": matrix}


# ============================================
# 메인 평가 함수
# ============================================
def evaluate(
    samples: List[Dict[str, Any]],
    client: OpenAI,
    base_model: str,
    ft_model: str,
    output_path: Optional[Path] = None,
    limit: Optional[int] = None,
) -> Dict:
    """전체 평가 수행"""
    if limit:
        samples = samples[:limit]
    
    gold_labels = []
    base_preds = []
    ft_preds = []
    predictions = []
    
    total = len(samples)
    print(f"\n총 {total}개 샘플 평가 시작...")
    
    for idx, sample in enumerate(samples, 1):
        gold = get_gold_label(sample)
        if gold is None:
            continue
        
        prompt = build_prompt(sample)
        if not prompt:
            continue
        
        base_pred, _ = predict_label(client, base_model, prompt)
        ft_pred, _ = predict_label(client, ft_model, prompt)
        
        if base_pred is None:
            base_pred = 3  # 기본값
        if ft_pred is None:
            ft_pred = 3
        
        gold_labels.append(gold)
        base_preds.append(base_pred)
        ft_preds.append(ft_pred)
        
        predictions.append({
            "idx": idx,
            "gold": gold,
            "base_pred": base_pred,
            "ft_pred": ft_pred,
        })
        
        if idx % 50 == 0:
            print(f"  진행: {idx}/{total} ({idx/total*100:.1f}%)")
    
    # 메트릭 계산
    base_metrics = compute_metrics(base_preds, gold_labels, LABEL_SET)
    ft_metrics = compute_metrics(ft_preds, gold_labels, LABEL_SET)
    
    base_cm = compute_confusion_matrix(base_preds, gold_labels, LABEL_SET)
    ft_cm = compute_confusion_matrix(ft_preds, gold_labels, LABEL_SET)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "base_model": base_model,
            "ft_model": ft_model,
            "total_samples": len(gold_labels),
            "label_set": LABEL_SET,
        },
        "base_model": {
            "name": base_model,
            "metrics": base_metrics,
            "confusion_matrix": base_cm,
        },
        "ft_model": {
            "name": ft_model,
            "metrics": ft_metrics,
            "confusion_matrix": ft_cm,
        },
        "comparison": {
            "accuracy_diff": ft_metrics["accuracy"] - base_metrics["accuracy"],
            "f1_diff": ft_metrics["macro_f1"] - base_metrics["macro_f1"],
            "base_correct": base_metrics["correct"],
            "ft_correct": ft_metrics["correct"],
            "total": len(gold_labels),
        },
        "predictions": predictions,
    }
    
    # 결과 저장
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n결과 저장: {output_path}")
    
    # 요약 출력
    print("\n" + "=" * 50)
    print("평가 결과 요약")
    print("=" * 50)
    print(f"Base Model 정확도:      {base_metrics['accuracy']*100:.2f}%")
    print(f"Fine-tuned 정확도:      {ft_metrics['accuracy']*100:.2f}%")
    print(f"정확도 향상:            +{(ft_metrics['accuracy']-base_metrics['accuracy'])*100:.2f}%p")
    print(f"Macro F1 향상:          +{(ft_metrics['macro_f1']-base_metrics['macro_f1']):.4f}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Fine-tuned vs Base 모델 평가")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET, help="검증 데이터 경로")
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT, help="결과 저장 경로")
    parser.add_argument("--limit", type=int, default=None, help="평가할 샘플 수 제한")
    args = parser.parse_args()
    
    client = init_client()
    samples = load_samples(args.dataset)
    
    evaluate(
        samples=samples,
        client=client,
        base_model=BASE_MODEL,
        ft_model=FT_MODEL,
        output_path=args.output,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()

