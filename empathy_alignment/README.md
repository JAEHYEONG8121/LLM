# Empathy Alignment

LLM을 공감적으로 정렬하기 위한 연구 프로젝트

## 연구 목표

Base LLM (Llama, DeepSeek 등)을 4가지 공감 차원에서 평가하고, 
SFT + DPO를 통해 공감적 응답 생성 능력을 향상시킵니다.

## 4가지 평가 메트릭

| 메트릭 | 설명 | 측정 방법 | 데이터 소스 |
|--------|------|----------|-------------|
| **Specificity** | 응답의 구체성 | Concreteness ratings | Brysbaert et al. (2014) - 40,000 words |
| **Reflection Level** | 감정 반영 수준 (0-6) | 패턴 기반 탐지 | PAIR model (Min et al., 2022) |
| **Word Choice** | 단어 선택/감정 표현 | VAD 공감 정렬 점수 | NRC VAD Lexicon v2.1 - 55,000 words |
| **Diversity** | 응답 다양성 | Distinct-1, Distinct-2 | Li et al. (2016) |

## 연구 파이프라인

```
Phase 1: Baseline Evaluation ✅ 완료
├── Llama-3.1-8B-Instruct 평가
├── DeepSeek-7B-Chat 평가
└── 4가지 메트릭으로 비교 분석

Phase 2: SFT (Supervised Fine-Tuning) 🔜 예정
├── EPITOME 데이터셋 준비
├── LoRA 기반 효율적 학습
└── SFT 모델 평가

Phase 3: DPO (Direct Preference Optimization) 🔜 예정
├── 4가지 메트릭 기반 선호 쌍 생성
├── DPO 학습
└── 최종 모델 평가

Phase 4: Comparison & Analysis 🔜 예정
└── Base vs SFT vs SFT+DPO 비교
```

## Baseline 평가 결과 (2026-01-06)

### 모델 비교

| 메트릭 | Llama-3.1-8B | DeepSeek-7B | 차이 |
|--------|--------------|-------------|------|
| Specificity | 2.436 | 2.427 | +0.009 |
| Reflection Level | **4.80** | 2.70 | **+2.10** |
| Word Choice | 0.921 | 0.929 | -0.008 |
| Diversity | 0.819 | 0.834 | -0.015 |
| **Overall Score** | **0.757** | 0.674 | **+0.082** |

### 주요 발견

- **Llama-3.1-8B**가 Overall Score 0.757로 DeepSeek-7B (0.674)보다 우수
- 특히 **Reflection Level**에서 큰 차이 (4.80 vs 2.70)
  - Llama가 "It sounds like you're feeling...", "That must be..." 등 감정 반영 표현을 더 많이 사용
- Word Choice와 Diversity는 두 모델이 비슷한 수준

## 프로젝트 구조

```
empathy_alignment/
├── src/
│   ├── metrics/              # 4가지 평가 메트릭
│   │   ├── specificity.py    # Brysbaert Concreteness
│   │   ├── reflection.py     # PAIR Model 패턴
│   │   ├── word_choice.py    # NRC VAD Lexicon
│   │   ├── diversity.py      # Distinct-n
│   │   └── evaluator.py      # 통합 평가기
│   ├── data/                 # 데이터 처리
│   ├── training/             # SFT, DPO 학습
│   └── evaluation/           # 통합 평가
├── data/
│   └── lexicons/             # Lexicon 파일
│       ├── concreteness_ratings.txt    # 40,000 words
│       └── NRC-VAD-Lexicon-v2.1.txt    # 55,000 words
├── results/                  # 실험 결과
│   ├── llama_evaluation.json
│   ├── deepseek_evaluation.json
│   ├── baseline_comparison.json
│   └── comparison_radar.png
├── docs/                     # 문서
│   ├── metrics_documentation.md
│   ├── metrics_documentation_APA.pdf
│   └── baseline_experiment_report_APA.pdf
├── notebooks/                # 실험 노트북
│   └── 01_evaluate_baseline_models.ipynb
├── scripts/                  # 실행 스크립트
└── requirements.txt
```

## 문서

| 문서 | 설명 |
|------|------|
| `docs/metrics_documentation.md` | 4가지 메트릭 상세 설명 (한글) |
| `docs/metrics_documentation_APA.pdf` | 메트릭 문서 PDF (APA 형식) |
| `docs/baseline_experiment_report_APA.pdf` | Baseline 실험 보고서 (APA 형식) |

## 참고 논문

- Lee et al. (2024) "A Comparative Multidimensional Analysis of Empathetic Systems" (EACL 2024)
- Sotolar et al. (2024) "EmPO: Emotion Grounding for Empathetic Response Generation through Preference Optimization"
- Sharma et al. (2020) "EPITOME: A Computational Approach to Understanding Empathy"
- Brysbaert et al. (2014) "Concreteness ratings for 40 thousand generally known English word lemmas"
- Mohammad (2018) "Obtaining Reliable Human Ratings of Valence, Arousal, and Dominance"
- Li et al. (2016) "A Diversity-Promoting Objective Function for Neural Conversation Models"

## 설치

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt')"
```

## 사용법

### Baseline 평가 실행 (Google Colab)

1. `notebooks/01_evaluate_baseline_models.ipynb`를 Google Colab에서 실행
2. HuggingFace 토큰 설정 (Llama 접근용)
3. 전체 셀 실행 → 결과 자동 저장

### 메트릭 테스트

```python
from src.metrics import EmpathyEvaluator

evaluator = EmpathyEvaluator()
result = evaluator.evaluate_response(
    context="I just lost my job today.",
    response="I'm so sorry to hear that. That must be really difficult."
)
print(f"Overall Score: {result['overall_score']:.3f}")
```

## License

MIT License
