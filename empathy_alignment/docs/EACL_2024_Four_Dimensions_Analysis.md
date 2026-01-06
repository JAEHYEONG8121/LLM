# A Comparative Multidimensional Analysis of Empathetic Systems 논문 분석

> **Preference Definition과 연계한 4가지 핵심 차원 분석**

---

## 목차

1. [구체성 (Specificity)](#1-구체성-specificity)
2. [반영 수준 (Reflection Level)](#2-반영-수준-reflection-level)
3. [단어 선택과 감정 표현 (Word Choice)](#3-단어-선택과-감정-표현-word-choice)
4. [다양성 (Diversity)](#4-다양성-diversity)
5. [데이터셋 추천](#5-데이터셋-추천)

---

## 1. 구체성 (Specificity)

### 📖 왜 중요한가?

**정의**: 일반적이고 추상적인 말을 하는 정도 vs 구체적이고 개인화된 말을 하는 정도

**심리 치료 이론의 근거**:
- Truax and Carkhuff (1964)의 "concreteness" 개념에서 나옴
- 치료사가 구체적으로 말할수록 환자는 더 공감을 느낌

**3가지 이점**:

| 이점 | 설명 | 예시 |
|------|------|------|
| **감정적 거리감 줄임** | 구체적 언급이 더 친밀감 형성 | ❌ "그건 정말 힘들겠네요" → ✅ "당신이 말한 그 상황에서, 당신은 버려진 느낌을 받으셨군요" |
| **더 정확한 이해** | 치료사가 환자의 **특정 감정**을 정확히 파악하고 있다는 신호 | - |
| **행동 변화 유도** | 구체적인 반응이 클라이언트를 자신의 문제에 더 집중하게 함 | - |

### 🔬 측정 방법: NIDF (Normalized Inverse Document Frequency)

**수학 공식**:

```
NIDF(w) = log(R / c_w)

R = 데이터셋의 전체 문서 수 (예: 5,255개의 상담 응답)
c_w = 단어 w가 나타난 문서 수
```

**핵심 개념**:
```
구체성 점수 = 그 답변에서 사용된 "특이한 단어들의 점수"의 평균
즉, 자주 안 나오는 단어를 많이 쓸수록 높은 점수
```

**구체 예시**:

```
데이터셋 전체 5,255개 답변 중...

✅ 구체적인 답변 (높은 NIDF):
"당신이 말한 '약속 파기' 때문에 실망했다는 게 정말 그럴 것 같아요"
→ "약속 파기", "실망" 같은 특이한 단어 사용 = 높은 점수

❌ 추상적인 답변 (낮은 NIDF):
"정말 힘드시겠네요"
→ "정말", "힘들다" = 너무 흔한 단어 = 낮은 점수
```

### 📊 실험 결과

```
NIDF 점수 (높을수록 좋음):

인간 답변:           0.20 ⭐⭐⭐⭐⭐ (기준점)
CARE 시스템:         0.15 ⭐⭐⭐⭐
SEEK 시스템:         0.14 ⭐⭐⭐⭐
EmpatheticDialogue:  0.12 ⭐⭐⭐

결론: 모든 AI가 인간보다 덜 구체적임 ❌
```

**논문의 분석**:
- 대부분의 시스템이 기본 데이터셋(EmpatheticDialogue)과 **0.005 이하의 차이**만 보임
- 심지어 **4개 시스템은 기본 데이터셋보다도 더 나쁨**
- **왜?** → 반복되는 일반적인 구조만 학습한 것

---

## 2. 반영 수준 (Reflection Level)

### 📖 왜 중요한가?

**정의**: 상대방이 말한 것을 얼마나 **깊이 있게 이해하고 되돌려주는가**

**치료 이론의 근거**:
- Houck et al. (2012)의 "reflection" 개념
- 심리 치료의 필수 기술

### 3가지 반영 수준

```
1️⃣ 단순 반영 (Simple Reflection) - 가장 기본적
   클라이언트: "내 친구가 나를 무시했어요"
   치료사: "당신의 친구가 당신을 무시했다는 거네요"
   → 말한 것을 그대로 돌려줌 (이해한다는 신호)

2️⃣ 복잡한 반영 (Complex Reflection) - 더 높은 수준 ⭐⭐⭐
   클라이언트: "내 친구가 나를 무시했어요"
   치료사: "당신의 친구가 무시한 것이 당신에게 얼마나 깊은
            상처를 주었는지 느껴집니다. 그래서 당신은 이제
            그 우정을 다시 생각해보고 있는 거군요"
   → 표현되지 않은 감정과 의미까지 반영
```

**비교 예시**:

| 유형 | 예시 |
|------|------|
| 단순 반영 | "당신이 슬프다는 거군요" |
| 복잡 반영 | "당신이 슬픈 것은 당신이 중요하다고 생각하던 사람을 잃었기 때문이고, 그 상실이 당신의 자존감에도 영향을 미치고 있는 것 같네요" |

### 🔬 측정 방법: PAIR 모델

**PAIR란?**
- RoBERTa라는 AI 모델 기반
- 대조 학습(Contrastive Learning)으로 훈련됨
- 0~1 사이의 점수로 반영 수준을 측정

**작동 원리**:

```
입력: "당신이 슬프다는 거군요"
 ↓
PAIR 모델: "이건 단순 반영이다"
 ↓
출력: 0.35점 (복잡함이 낮음)

입력: "당신이 슬픈 것은... 자존감 때문인 것 같네요"
 ↓
PAIR 모델: "이건 복잡한 반영이다"
 ↓
출력: 0.75점 (복잡함이 높음)
```

### 📊 실험 결과

```
PAIR 점수 (높을수록 좋음, 0~0.4 범위):

결론: 모든 AI (1개 제외)가 인간보다 낮은 반영 수준 ❌
```

**흥미로운 발견**:
- 인간 답변도 점수가 매우 낮음 (0.4 이하)
- **→ 복잡한 반영은 정말 어려운 과제**
- AI가 인간처럼 배우는 것만으로는 한계

**논문의 제안**:

```
현재 방법: "인간 데이터를 더 많이 주면 AI도 잘할 것"
문제: 데이터 자체가 복잡한 반영이 부족함

해결책: "다른 방식의 학습 방법이 필요"
        → 강화 학습, 인간 피드백 등
```

---

## 3. 단어 선택과 감정 표현 (Word Choice)

### 📖 왜 중요한가?

**개념**:

```
"저는 당신의 슬픔을 이해합니다"
vs
"저는 당신의 절망적인 슬픔, 그 깊고 어두운 감정을 이해합니다"

→ 두 번째가 더 "고에너지" 표현
```

### 🔬 측정 방법: 3가지 차원

#### 1) 감정 강도 (Emotion Intensity)

```
약함 ←────────────→ 강함
짜증나다 ←────────→ 분노하다
우울하다 ←────────→ 절망하다

도구: NRC 감정 강도 사전 (NRC-EIL)
- 10,000개 단어의 강도를 0~1 사이로 정량화
```

#### 2) 긍정/부정 정도 (Valence)

```
부정적 ←────────────→ 긍정적
-1          0           +1
불행       중립        행복
```

#### 3) 에너지 수준 (Arousal)

```
저에너지 ←────────────→ 고에너지
졸음/침착 ←────────────→ 흥분/활발
```

### 예시

```
클라이언트: "내 할머니가 돌아가셨어요"
(부정적 감정, 높은 감정 강도, 중간~낮은 에너지)

좋은 AI 답변: "당신의 할머니를 잃은 슬픔과
               그 깊은 상실감을 느낍니다"
(클라이언트 감정과 일치하는 강도와 톤)

나쁜 AI 답변: "오, 정말 재밌겠는데요!"
(긍정적, 고에너지 → 완전히 안 맞음)
```

### 📊 실험 결과

```
측정 방법: |클라이언트 감정 강도 - AI 답변 감정 강도|
값이 작을수록 좋음 (클라이언트와 일치)

감정 강도:
├── 인간:       거의 0에 가까움 (완벽히 일치)
├── CARE:       약간의 차이
└── MoEL/MIME:  오래된 시스템이 오히려 더 나음 ✓

긍정/부정(Valence):
├── 인간:       정확히 맞춤
└── SEEK:       약간의 차이

에너지(Arousal):
├── 인간:       정확히 일치
└── 최신 시스템: 격차 증가 ❌
```

**충격적인 발견**:

```
예상: 최신 AI → 더 나은 감정 표현
실제: 최신 AI → 더 나쁜 감정 표현 ❌

왜?
- 최신 AI는 더 안전하고 중립적인 답변 생성 경향
- "안전성"을 추구하다 보니 감정 표현이 약해짐
- 예: "당신이 힘드신 것 같아요" (너무 뻔함)
```

---

## 4. 다양성 (Diversity)

### 📖 왜 중요한가?

**문제 상황**:

```
"내 고양이가 아파요"
AI: "정말 안타깝네요" ✅ (한 번만 봤을 때 좋음)

"내 아버지가 돌아가셨어요"
AI: "정말 안타깝네요" ❌ (똑같은 답변!)

"내 면접을 망쳤어요"
AI: "정말 안타깝네요" ❌❌❌ (반복!)

→ 하나의 샘플만 평가하면 이 반복이 보이지 않음
```

### 🔬 측정 방법: Response-Trie (응답 트라이)

> 이 부분이 **논문의 가장 혁신적인 부분**입니다!

**개념**: 응답들의 패턴을 시각화하고 반복을 찾는 새로운 방법

#### Step 1: 응답 수집

```
AI가 5,255개 질문에 대해 생성한 답변들:
"I am so sorry to hear that"
"I am so sorry, stay strong"
"I am so sorry to hear the news"
"I am so sorry to hear that you lost someone"
"I understand you're feeling sad"
...
```

#### Step 2: "접기" (Folding) - 반복되는 패턴 찾기

```
공식: H(구간) = 구간의 길이 × 구간이 나타난 횟수

예시:
"I am so sorry" → 길이 4, 나타난 횟수 3 → 점수 12 ⭐⭐⭐ (높음)
"to hear" → 길이 2, 나타난 횟수 2 → 점수 4
```

**가장 자주 반복되는 부분을 찾아서 대체**:

```
원본:
"I am so sorry to hear that"
"I am so sorry, stay strong"
"I am so sorry to hear the news"
      ↓↓↓ 접기
<span_1>을 "I am so sorry"로 정의
      ↓↓↓
"<span_1> to hear that"
"<span_1>, stay strong"
"<span_1> to hear the news"
```

**계속 반복** (더 큰 패턴 찾기):

```
"<span_1> to hear that"
"<span_1> to hear the news"
      ↓↓↓ 두 번째 접기
<span_2> = "<span_1> to hear"로 정의

결과:
"<span_2> that"
"<span_1>, stay strong"
"<span_2> the news"

... 이 과정을 반복 (더 이상 반복이 없을 때까지)
```

#### Step 3: 트리 구조 만들기

```
최종 "템플릿"들:
"<span_2> that"           (템플릿 1)
"<span_1>, stay strong"   (템플릿 2)
"<span_2> the news"       (템플릿 3)

이를 트리(Tree) 구조로 변환:
         ROOT
        /  |  \
     <span> <span> ...
      /\      |
     that news strong
      |        |
     EOS      EOS

(각 경로가 하나의 답변을 나타냄)
```

#### Step 4: 다양성 지표 계산

| 지표 | 설명 | 인간 | MIME | MoEL |
|------|------|------|------|------|
| **템플릿 개수** | 많을수록 좋음 | 5,201개 (99%) | 4,719개 | 984개 ❌ |
| **스팬 노드 비율** | 낮을수록 좋음 | 13.1% | 26.73% | 53.7% ❌ |
| **압축률** | 높을수록 좋음 | 60.35% | - | - |
| **시작 단어 다양성** | 높을수록 좋음 | - | - | - |

### 📊 실험 결과

```
어떤 시스템이 생성한 답변들:
"I'm so sorry to hear that"
"I'm so sorry to hear that you're feeling this way"
"I'm so sorry to hear about that"
"I'm so sorry to hear that you're going through this"
"I'm so sorry, that's really tough"
...

→ "I'm so sorry"라는 기본 구조만 반복!
→ 한 샘플로는 이게 안 보임
→ 다양성 지표가 발견함 ✓
```

---

## 5. 데이터셋 추천

### 4가지 차원과 8가지 데이터셋 매칭

위 논문에서 제시하는 4가지 핵심 차원은 empathy-alignment에 아주 적합한 preference definition이 될 수 있습니다.

3가지 최신 LLM(ChatGPT-5.2, Opus 4.5, Gemini 3)에게 어떤 데이터셋이 가장 적합할지 추천을 받은 결과, **모든 모델이 EPITOME을 1순위로 추천**했습니다.

---

### 🏆 1순위: EPITOME

> **Empathy를 '다차원적 개념'으로 alignment하기 위한 최적 데이터셋**

#### 논문 4차원과의 매핑

| EPITOME 기제 | 강도 | EACL 차원 | 활용 |
|--------------|------|-----------|------|
| **Emotional Reaction** | 0/1/2 | Emotional Alignment (Word Choice) | 감정 반응 적절성 reward |
| **Interpretation** | 0/1/2 | Reflection Level | 깊은 이해 reward |
| **Exploration** | 0/1/2 | Specificity | 구체적 탐색 reward |

#### 장점

| 장점 | 설명 |
|------|------|
| **Fine-grained** | 3가지 기제 × 3단계 강도 = 27가지 조합 |
| **이론 기반** | 심리상담 이론(Sharma et al., 2020) 기반 |
| **Rationale 포함** | 왜 그 점수인지 근거 문장 제공 → XAI 가능 |
| **검증된 품질** | 임상 심리 전문가 자문, 훈련된 annotator |
| **적절한 규모** | 6,400개 라벨링 → DPO 학습에 충분 |

#### 차원별 분석

- **Specificity**: 추상적 위로 ❌ → 사용자의 **구체적 경험에 대한 언급 여부 자체를 라벨링**
- **Reflection**: Emotional Reaction / Interpretation / Exploration → 논문이 말하는 *simple vs complex reflection*과 정확히 대응
- **Word Choice**: 감정 반응의 **질적 차이**를 문장 단위로 주석
- **Diversity**: 완벽하진 않지만 "공감 유형 분산"은 확보

---

### 🥈 2순위: ESConv

> **행동·전략 기반 empathy alignment에 최적**

#### 8가지 지원 전략

| ESConv 전략 | EACL 차원 | 활용 |
|-------------|-----------|------|
| Question | Specificity | 상황 탐색 능력 |
| Restatement | Simple Reflection | 단순 반영 |
| Reflection | Complex Reflection | 복잡 반영 |
| Self-disclosure | Emotional Connection | 감정적 연결 |
| Affirmation | Emotional Reaction | 감정 반응 |
| Providing Info | Cognitive Support | 인지적 지원 |
| Suggestion | Action-oriented | 행동 지향 |
| 전략 분포 | Diversity | 다양한 전략 사용 |

---

### 🥉 3순위: EmpatheticDialogues

> **대규모 벤치마크 (주의 필요)**

#### 장점

| 장점 | 설명 |
|------|------|
| 대규모 | 25,000 대화, 100,000 발화 |
| 32개 감정 | Emotional Alignment에 최적 |
| 완전 공개 | 연구/상업 모두 가능 |
| 벤치마크 표준 | EACL 논문도 이 데이터로 실험 |

#### ⚠️ 한계 (논문이 직접 비판)

- Specificity ❌
- Reflection ❌
- Diversity ❌
- "I'm sorry to hear that" 학습 최적화됨

> **Empathy alignment용으로는 단독 사용 비추천**

---

### 🎯 최종 추천: 데이터셋 조합 전략

```
┌─────────────────────────────────────────────────────────────────┐
│                    권장 조합                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   EPITOME (core alignment)                                      │
│   + ESConv (behavior grounding)                                 │
│   + OPELA (diversity & naturalness, 한국어)                     │
│                                                                 │
│   이 조합은:                                                    │
│   - 논문이 지적한 generic / repetitive / shallow empathy        │
│     문제를 거의 모두 회피                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. 구현 코드 예시

### EPITOME Preference 활용

```python
class EPITOMEPreference:
    """
    EPITOME의 3가지 기제를 Multi-signal로 활용
    """

    def __init__(self):
        self.mechanisms = {
            "emotional_reaction": {
                "eacl_dimension": "emotional_alignment",
                "scale": [0, 1, 2],  # 없음 / 약함 / 강함
                "weight": 0.3,
            },
            "interpretation": {
                "eacl_dimension": "reflection_level",
                "scale": [0, 1, 2],
                "weight": 0.35,
            },
            "exploration": {
                "eacl_dimension": "specificity",
                "scale": [0, 1, 2],
                "weight": 0.35,
            },
        }

    def compute_empathy_score(self, sample):
        """
        3가지 기제의 가중 합으로 종합 공감 점수 계산
        """
        total = 0
        for mech, config in self.mechanisms.items():
            score = sample[mech]  # 0, 1, or 2
            normalized = score / 2  # [0, 1]
            total += normalized * config["weight"]
        return total  # [0, 1]

    def create_preference_pair(self, response_a, response_b):
        """
        두 응답의 공감 점수 차이로 preference pair 생성
        """
        score_a = self.compute_empathy_score(response_a)
        score_b = self.compute_empathy_score(response_b)

        if score_a > score_b:
            return {
                "chosen": response_a,
                "rejected": response_b,
                "margin": score_a - score_b,
                "dimension_margins": {
                    "emotional": response_a["emotional_reaction"] - response_b["emotional_reaction"],
                    "interpretation": response_a["interpretation"] - response_b["interpretation"],
                    "exploration": response_a["exploration"] - response_b["exploration"],
                }
            }
        return None
```

---

## 참고문헌

- Lee, A., Kummerfeld, J. K., An, L., & Mihalcea, R. (2024). A Comparative Multidimensional Analysis of Empathetic Systems. *EACL 2024*.
- Truax, C. B., & Carkhuff, R. R. (1964). Concreteness: A neglected variable in research in psychotherapy.
- Houck, J. M., et al. (2012). Motivational interviewing skill code.
- Sharma, A., et al. (2020). A computational approach to understanding empathy expressed in text-based mental health support. *EMNLP 2020*.
- Min, D. J., et al. (2022). PAIR: Prompt-aware margin ranking for counselor reflection scoring. *EMNLP 2022*.

---

*문서 생성일: 2024년 12월*

