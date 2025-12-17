# EmpathyAI

한국어 대화에서 AI(페르소나)의 공감 수준을 자동으로 분류하는 LLM 파인튜닝 프로젝트

## 📋 프로젝트 개요

OPELA(Open-domain conversations by Personas with Empathy, Long-term memory, and Attractive personality) 데이터셋을 활용하여 두 가지 접근법으로 공감 분류 모델을 개발했습니다:

1. **GPT-4.1 Nano**: OpenAI API를 통한 SFT(Supervised Fine-tuning)
2. **DeepSeek 7B**: Google Colab에서 QLoRA를 활용한 효율적 파인튜닝

### 🏆 주요 성과

| 모델 | 정확도 | 향상 |
|------|--------|------|
| GPT-4.1 Nano (Base) | 15.70% | - |
| GPT-4.1 Nano (Fine-tuned) | 33.49% | +17.79%p |
| **DeepSeek 7B (QLoRA)** | **49.19%** | **+33.49%p** |

## 📁 프로젝트 구조

```
empathyAi/
├── data/                               # 데이터 파일
│   ├── raw/                            # 원본 데이터
│   ├── processed/                      # 전처리된 데이터
│   ├── train_val/                      # 학습/검증 데이터
│   │   ├── opela_empathy_train.jsonl   # 학습 데이터 (13,341개)
│   │   └── opela_empathy_val.jsonl     # 검증 데이터 (1,484개)
│   ├── eval_results.json               # GPT 평가 결과
│   └── deepseek_eval_results.json      # DeepSeek 평가 결과
│
├── src/                                # 소스 코드
│   ├── preprocessing/                  # 데이터 전처리
│   │   ├── change2json.py              # JSON 변환
│   │   ├── data_split.py               # Train/Val 분할
│   │   ├── find.py                     # 데이터 탐색
│   │   └── fusion.py                   # 데이터 통합
│   ├── evaluation/                     # 모델 평가
│   │   └── eval_ft_vs_base.py          # Base vs Fine-tuned 비교 평가
│   ├── analysis/                       # 결과 분석
│   │   └── analyze_results.py          # 평가 결과 분석
│   └── training/                       # 모델 학습
│
├── notebooks/                          # Colab 노트북
│   ├── deepseek_finetune_colab.py      # DeepSeek QLoRA 학습 코드
│   └── COLAB_GUIDE.md                  # Colab 사용 가이드
│
├── scripts/                            # 유틸리티 스크립트
│   ├── generate_final_report_v4.py     # 최종 보고서 생성
│   ├── generate_deepseek_report.py     # DeepSeek 보고서 생성
│   ├── generate_report_pdf.py          # PDF 보고서 (FPDF2)
│   └── generate_report_latex.py        # LaTeX 보고서
│
├── reports/                            # 보고서 및 시각화
│   ├── figures/                        # 그래프 이미지
│   │   ├── accuracy_improvement.png
│   │   ├── confusion_matrix.png
│   │   ├── label_distribution.png
│   │   ├── model_comparison.png
│   │   ├── text_length.png
│   │   └── response_length_by_label.png
│   ├── latex/                          # LaTeX 소스
│   └── EmpathyAI_Final_Report_v4.pdf   # 최종 보고서 (GPT + DeepSeek)
│
├── configs/                            # 설정 파일
│   └── model_config.yaml
│
├── .env                                # 환경 변수 (API 키)
├── requirements.txt                    # 의존성
└── README.md
```

## 🏷️ 공감 레벨 정의

| Level | Label | Description |
|-------|-------|-------------|
| 0 | Not Applicable | 공감이 적용되지 않는 상황 (인사, 정보 교환) |
| 1 | Empathy Failure | 공감 실패 (무시, 부적절한 반응) |
| 2 | Low Empathy | 낮은 수준의 공감 (최소한의 반응) |
| 3 | Moderate Empathy | 중간 수준의 공감 (적절한 감정적 반응) |
| 4 | High Active Empathy | 높은 수준의 적극적 공감 (깊은 이해와 지지) |

## 🚀 사용 방법

### 1. 환경 설정
```bash
pip install -r requirements.txt
```

### 2. GPT 모델 평가 (OpenAI API)

`.env` 파일 생성:
```
OPENAI_API_KEY=your-api-key-here
```

평가 실행:
```bash
python -m src.evaluation.eval_ft_vs_base --dataset data/train_val/opela_empathy_val.jsonl
```

### 3. DeepSeek QLoRA 학습 (Google Colab)

1. `notebooks/COLAB_GUIDE.md` 가이드 참고
2. Google Colab에서 A100/H100 GPU 런타임 선택
3. `notebooks/deepseek_finetune_colab.py` 코드 실행

### 4. 결과 분석
```bash
python -m src.analysis.analyze_results --input data/eval_results.json
```

### 5. 보고서 생성
```bash
python scripts/generate_final_report_v4.py
```

## 📊 데이터셋

- **출처**: OPELA Dataset (Smilegate AI & 서울대학교)
- **전체 샘플**: 14,825개
- **학습 데이터**: 13,341개 (90%)
- **검증 데이터**: 1,484개 (10%)

### 클래스 분포

| Label | Count | Percentage |
|-------|-------|------------|
| 0 (Not Applicable) | 4,167 | 28.1% |
| 1 (Empathy Failure) | 660 | 4.5% |
| 2 (Low Empathy) | 1,806 | 12.2% |
| 3 (Moderate Empathy) | 7,198 | 48.6% |
| 4 (High Active Empathy) | 994 | 6.7% |

## 🔧 모델 정보

### GPT-4.1 Nano (OpenAI API)

| Parameter | Value |
|-----------|-------|
| Base Model | `gpt-4.1-nano-2025-04-14` |
| Fine-tuned Model | `ft:gpt-4.1-nano-2025-04-14:personal::Cn0GL0QT` |
| Training Method | Supervised Fine-tuning (SFT) |
| Epochs | 3 |
| Platform | OpenAI API |

### DeepSeek 7B (QLoRA)

| Parameter | Value |
|-----------|-------|
| Base Model | `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` |
| Parameters | 7 Billion |
| Training Method | QLoRA (4-bit + LoRA) |
| LoRA Rank | 16 |
| LoRA Alpha | 32 |
| Learning Rate | 2e-4 |
| Epochs | 3 |
| Platform | Google Colab (H100 80GB) |
| Training Time | ~3 hours |

## 📈 실험 결과

### 전체 성능 비교

| Metric | GPT Base | GPT FT | DeepSeek | Best Improvement |
|--------|----------|--------|----------|------------------|
| Accuracy | 15.70% | 33.49% | **49.19%** | +33.49%p |
| Macro Precision | 0.2272 | 0.2270 | **0.3067** | +0.0795 |
| Macro Recall | 0.1939 | **0.2326** | 0.2284 | +0.0387 |
| Macro F1 | 0.1452 | **0.2275** | 0.2034 | +0.0823 |
| Correct/Total | 233/1484 | 497/1484 | **730/1484** | +497 |

### 클래스별 F1 Score

| Label | GPT Base | GPT FT | DeepSeek |
|-------|----------|--------|----------|
| 0 | 0.221 | 0.335 | 0.288 |
| 1 | 0.061 | 0.087 | 0.000 |
| 2 | 0.166 | 0.125 | 0.092 |
| 3 | 0.179 | 0.464 | **0.637** |
| 4 | 0.099 | 0.126 | 0.000 |

### 모델 비교 분석

| 측면 | GPT-4.1 Nano FT | DeepSeek QLoRA |
|------|-----------------|----------------|
| **장점** | 소수 클래스 인식 가능 | 최고 정확도 (49.19%) |
| **단점** | API 비용 발생 | 소수 클래스 무시 (1, 4) |
| **비용** | API 크레딧 필요 | 무료 (Colab) |
| **재현성** | 제한적 | 완전 재현 가능 |
| **추천 상황** | 균형 잡힌 분류 필요 시 | 높은 정확도 우선 시 |

### 성능 분석

- **5-class 분류의 본질적 어려움**: 랜덤 베이스라인 20%
- **클래스 불균형 문제**: Label 3이 48.6% 차지
- **DeepSeek 특성**: 다수 클래스(Label 3)에 강하지만 소수 클래스 무시
- **GPT FT 특성**: 더 균형 잡힌 분류, 모든 클래스 인식

### 향후 개선 방향

1. **클래스 단순화**: 5-class → 3-class (Low/Medium/High)
2. **데이터 증강**: 소수 클래스(1, 4) 오버샘플링
3. **앙상블**: GPT + DeepSeek 모델 결합
4. **Class-weighted Loss**: 불균형 보정
5. **LLaMA 3.1 8B**: 추가 모델 비교 실험

## 🛠️ QLoRA 기술 설명

QLoRA(Quantized Low-Rank Adaptation)는 대규모 언어 모델을 효율적으로 파인튜닝하는 기술입니다:

1. **4-bit 양자화**: 모델 가중치를 4비트로 압축 (NF4 형식)
2. **LoRA 어댑터**: 전체 파라미터의 0.5%만 학습
3. **Double Quantization**: 양자화 상수도 양자화하여 추가 메모리 절약

**효과**: 7B 모델 학습에 필요한 GPU 메모리를 28GB → 6GB로 감소

## 📚 참고문헌

- Smilegate AI & Seoul National University (2022). OPELA: Open-domain conversations by Personas with Empathy, Long-term memory, and Attractive personality. [GitHub](https://github.com/smilegate-ai/OPELA)
- Lee, Y. K., et al. (2022). "Feels like I've known you forever": empathy and self-awareness in human open-domain dialogs. PsyArXiv.
- Dettmers, T., et al. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. NeurIPS.
- Hu, E. J., et al. (2021). LoRA: Low-Rank Adaptation of Large Language Models. ICLR.
- DeepSeek AI (2024). DeepSeek-R1: Advancing Reasoning in Large Language Models.

## 📄 라이선스

This project uses the OPELA dataset which is licensed under CC-BY-NC-SA 4.0.
