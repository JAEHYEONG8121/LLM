# Empathy Alignment 프로젝트: 4가지 공감 평가 메트릭 상세 문서

## 개요

본 문서는 LLM(Large Language Model)의 공감 능력을 평가하기 위한 4가지 핵심 차원의 메트릭 구현에 대해 상세히 설명합니다. 이 메트릭들은 Lee et al. (2024)의 EACL 논문 "A Comparative Multidimensional Analysis of Empathetic Systems"에서 제시된 다차원적 공감 평가 프레임워크를 기반으로 합니다.

## 이론적 배경

### 공감의 다차원적 특성

공감(Empathy)은 단일 점수로 측정하기 어려운 복잡한 다차원적 구조입니다 (Davis, 1983; Cuff et al., 2016). Lee et al. (2024)은 기존 공감 대화 시스템 평가의 한계를 지적하며, 단일 공감 점수 대신 여러 차원에서의 평가가 필요함을 강조했습니다. 그들의 연구에서 21개의 공감 대화 시스템을 분석한 결과, 최근 시스템들이 다음 세 가지 측면에서 부족함을 발견했습니다:

1. **구체성 (Specificity)**: 응답이 일반적이고 진부함
2. **반영 수준 (Reflection Levels)**: 상대방의 감정을 깊이 있게 반영하지 못함
3. **다양성 (Diversity)**: 응답 패턴이 반복적임

본 프로젝트에서는 이 세 가지에 **단어 선택과 감정 표현 (Word Choice)**을 추가하여 총 4가지 차원으로 평가합니다.

---

## 메트릭 1: Specificity (구체성)

### 이론적 기반

구체성 메트릭은 Brysbaert et al. (2014)의 Concreteness Ratings를 기반으로 합니다. 이 연구에서는 약 40,000개의 영어 단어에 대해 1점(매우 추상적)부터 5점(매우 구체적)까지의 구체성 점수를 제공합니다.

**Table 1**

*Concreteness Ratings 예시 (Brysbaert et al., 2014 기반)*

| 단어 | 구체성 점수 | 설명 |
|------|------------|------|
| apple | 5.00 | 매우 구체적 - 감각적으로 경험 가능 |
| house | 4.93 | 매우 구체적 - 물리적 대상 |
| friend | 4.10 | 구체적 - 사람을 지칭 |
| situation | 3.20 | 중간 - 맥락에 따라 다름 |
| idea | 2.50 | 추상적 - 개념적 |
| freedom | 2.10 | 매우 추상적 - 비물리적 개념 |

구체적인 응답은 사용자가 자신의 상황이 이해받고 있다고 느끼게 하며, 추상적이고 일반적인 응답보다 더 공감적으로 인식됩니다 (Truax & Carkhuff, 1964).

### 구현 방법

```python
class SpecificityMetric:
    def compute(self, text: str) -> Dict[str, float]:
        """
        텍스트의 구체성 점수 계산
        
        1. 텍스트를 토큰화
        2. 각 단어의 concreteness 점수 조회
        3. 평균 점수 계산
        
        Returns:
            - score: 평균 구체성 점수 (1-5)
            - coverage: 렉시콘 매칭 비율
        """
        words = self._tokenize(text)
        scores = [self.lexicon[w] for w in words if w in self.lexicon]
        return {"score": np.mean(scores), "coverage": len(scores)/len(words)}
```

### 계산 공식

$$\text{Specificity Score} = \frac{1}{N} \sum_{i=1}^{N} C(w_i)$$

여기서:
- $N$ = 렉시콘에서 매칭된 단어 수
- $C(w_i)$ = 단어 $w_i$의 구체성 점수 (1-5)

### 해석

| 점수 범위 | 해석 |
|----------|------|
| 4.0 - 5.0 | 매우 구체적인 응답 |
| 3.0 - 4.0 | 구체적인 응답 |
| 2.0 - 3.0 | 중간 수준 |
| 1.0 - 2.0 | 추상적인 응답 |

---

## 메트릭 2: Reflection Level (반영 수준)

### 이론적 기반

반영 수준 메트릭은 Min et al. (2022)의 PAIR (Prompt-Aware Margin Ranking) 모델과 상담 심리학의 반영 이론을 기반으로 합니다. 반영(Reflection)은 상담사가 내담자의 말을 되돌려주는 기술로, 공감적 대화의 핵심 요소입니다 (Houck et al., 2012).

**Table 2**

*반영 수준 분류 체계 (Houck et al., 2012; Min et al., 2022 기반)*

| 수준 | 명칭 | 설명 | 예시 |
|------|------|------|------|
| 0 | No Reflection | 반영 없음 | "What happened next?" |
| 1 | Minimal Response | 최소 반응 | "Okay.", "I see." |
| 2 | Simple Reflection (Repetition) | 단순 반복 | "You said you're tired." |
| 3 | Simple Reflection (Paraphrase) | 바꿔 말하기 | "So work has been stressful." |
| 4 | Reflection of Feeling (Explicit) | 명시적 감정 반영 | "You're feeling frustrated." |
| 5 | Reflection of Feeling (Implicit) | 암시적 감정 반영 | "That sounds overwhelming." |
| 6 | Complex Reflection | 복잡한 반영 (깊은 의미 해석) | "It seems like this means a lot to you." |

### 구현 방법

본 구현에서는 규칙 기반(Rule-based) 접근법을 사용하며, 각 수준에 해당하는 언어 패턴을 정규 표현식으로 정의합니다.

```python
class ReflectionLevelMetric:
    def __init__(self):
        # Level 6: Complex Reflection 패턴
        self.complex_patterns = [
            r"it seems like .+ means .+ to you",
            r"beneath .+ there seems to be",
            r"on a deeper level",
        ]
        
        # Level 4-5: Reflection of Feeling 패턴
        self.feeling_patterns = [
            r"you('re| are) feeling",
            r"sounds like you('re| are)",
            r"that must (be|feel|have been)",
        ]
        
        # Level 2-3: Simple Reflection 패턴
        self.simple_patterns = [
            r"so you",
            r"you('re| are) saying",
            r"i understand",
        ]
```

### 계산 방법

```python
def _rule_based_score(self, text: str) -> int:
    """
    패턴 매칭을 통한 반영 수준 결정
    
    1. 복잡한 반영 패턴 확인 → Level 5-6
    2. 감정 반영 패턴 확인 → Level 3-5
    3. 단순 반영 패턴 확인 → Level 2-3
    4. 최소 반응 패턴 확인 → Level 1
    5. 해당 없음 → Level 0
    """
```

### 정규화 점수

$$\text{Normalized Reflection Score} = \frac{\text{Level}}{6}$$

---

## 메트릭 3: Word Choice (단어 선택과 감정 표현)

### 이론적 기반

단어 선택 메트릭은 Mohammad (2018)의 NRC VAD (Valence-Arousal-Dominance) Lexicon을 기반으로 합니다. 이 프레임워크는 Russell (1980)의 차원적 감정 모델에서 유래하며, 감정을 세 가지 독립적인 차원으로 표현합니다.

**Table 3**

*VAD 차원 설명 (Russell, 1980; Mohammad, 2018)*

| 차원 | 영문 | 범위 | 낮은 값 | 높은 값 |
|------|------|------|--------|--------|
| 정서가 (Valence) | V | 0-1 | 부정적, 불쾌 | 긍정적, 유쾌 |
| 각성도 (Arousal) | A | 0-1 | 차분, 이완 | 흥분, 각성 |
| 지배성 (Dominance) | D | 0-1 | 통제받음, 무력 | 통제함, 강력 |

**Table 4**

*감정 단어의 VAD 점수 예시 (NRC VAD Lexicon 기반)*

| 단어 | Valence | Arousal | Dominance | 해석 |
|------|---------|---------|-----------|------|
| happy | 0.96 | 0.74 | 0.87 | 긍정, 각성, 통제 |
| excited | 0.90 | 0.85 | 0.75 | 긍정, 높은 각성 |
| calm | 0.78 | 0.22 | 0.72 | 긍정, 낮은 각성 |
| sad | 0.15 | 0.32 | 0.25 | 부정, 낮은 각성, 무력 |
| angry | 0.15 | 0.85 | 0.55 | 부정, 높은 각성 |
| anxious | 0.20 | 0.78 | 0.25 | 부정, 높은 각성, 무력 |

### 구현 방법

```python
class WordChoiceMetric:
    def compute(self, text: str) -> Dict[str, float]:
        """
        텍스트의 VAD 점수 및 감정 강도 계산
        
        Returns:
            - valence: 평균 정서가 (0-1)
            - arousal: 평균 각성도 (0-1)
            - dominance: 평균 지배성 (0-1)
            - intensity: 감정 강도 (0-1)
            - empathy_alignment: 공감 정렬 점수 (0-1)
        """
```

### 공감 정렬 점수 (Empathy Alignment Score)

공감적 응답의 이상적인 VAD 프로파일을 정의하고, 실제 응답과의 거리를 측정합니다:

$$\text{Empathy Alignment} = 1 - \frac{|V - V_{ideal}| + |A - A_{ideal}| + |D - D_{ideal}|}{3}$$

여기서 이상적인 프로파일은:
- $V_{ideal} = 0.65$ (약간 긍정적)
- $A_{ideal} = 0.45$ (중간 각성)
- $D_{ideal} = 0.40$ (낮은 지배성 - 상대방에게 통제권 부여)

### 거리 계산 (EmPO 방식)

Sotolar et al. (2024)의 EmPO 논문에서 제안한 방식으로, 프롬프트와 응답 간의 VAD 거리를 계산합니다:

```python
def compute_distance(self, prompt: str, response: str) -> Dict[str, float]:
    """
    |score(prompt) - score(response)|
    """
```

---

## 메트릭 4: Diversity (다양성)

### 이론적 기반

다양성 메트릭은 Li et al. (2016)의 Distinct-n 메트릭을 기반으로 합니다. 이 메트릭은 신경망 대화 모델이 생성하는 응답의 다양성을 측정하기 위해 개발되었으며, 많은 대화 시스템 연구에서 표준 메트릭으로 사용됩니다.

**Table 5**

*Distinct-n 메트릭 정의 (Li et al., 2016)*

| 메트릭 | 수식 | 설명 |
|--------|------|------|
| Distinct-1 | $\frac{\text{unique unigrams}}{\text{total unigrams}}$ | 유니그램 다양성 |
| Distinct-2 | $\frac{\text{unique bigrams}}{\text{total bigrams}}$ | 바이그램 다양성 |
| Distinct-3 | $\frac{\text{unique trigrams}}{\text{total trigrams}}$ | 트라이그램 다양성 |

### 구현 방법

```python
class DiversityMetric:
    def _compute_distinct_n(self, tokens: List[str], n: int) -> float:
        """
        Distinct-n 계산
        
        Args:
            tokens: 토큰 리스트
            n: n-gram 크기
            
        Returns:
            고유 n-gram 비율 (0-1)
        """
        ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
        return len(set(ngrams)) / len(ngrams)
```

### 추가 다양성 메트릭

**Table 6**

*구현된 다양성 관련 메트릭*

| 메트릭 | 수식 | 설명 |
|--------|------|------|
| Type-Token Ratio (TTR) | $\frac{\text{unique tokens}}{\text{total tokens}}$ | 어휘 풍부도 |
| Entropy | $-\sum_{i} p_i \log_2(p_i)$ | 토큰 분포 균일성 |
| Corpus Distinct-n | 전체 코퍼스에서의 Distinct-n | 모델 수준 다양성 |

### 종합 다양성 점수

$$\text{Diversity Score} = 0.4 \times \text{Distinct-1} + 0.6 \times \text{Distinct-2}$$

---

## 통합 평가기 (Empathy Evaluator)

### 개요

`EmpathyEvaluator` 클래스는 4가지 메트릭을 통합하여 종합적인 공감 점수를 계산합니다.

### 종합 점수 계산

$$\text{Overall Empathy Score} = \sum_{d \in D} w_d \times s_d$$

여기서:
- $D$ = {Specificity, Reflection, Word Choice, Diversity}
- $w_d$ = 차원 $d$의 가중치 (기본: 0.25)
- $s_d$ = 차원 $d$의 정규화된 점수 (0-1)

**Table 7**

*각 차원의 정규화 방법*

| 차원 | 원본 범위 | 정규화 공식 |
|------|----------|------------|
| Specificity | 1-5 | $s / 5$ |
| Reflection Level | 0-6 | $level / 6$ |
| Word Choice | 0-1 | 그대로 사용 |
| Diversity | 0-1 | 그대로 사용 |

### 사용 예시

```python
from src.metrics import EmpathyEvaluator

evaluator = EmpathyEvaluator()

responses = [
    "I understand how you feel. That must be really difficult.",
    "It sounds like you're going through a challenging time.",
]

report = evaluator.evaluate(responses, model_name="GPT-4")
evaluator.print_report(report)
```

---

## 참고문헌

Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). Concreteness ratings for 40 thousand generally known English word lemmas. *Behavior Research Methods*, 46(3), 904-911. https://doi.org/10.3758/s13428-013-0403-5

Cuff, B. M., Brown, S. J., Taylor, L., & Howat, D. J. (2016). Empathy: A review of the concept. *Emotion Review*, 8(2), 144-153. https://doi.org/10.1177/1754073914558466

Davis, M. H. (1983). Measuring individual differences in empathy: Evidence for a multidimensional approach. *Journal of Personality and Social Psychology*, 44(1), 113-126. https://doi.org/10.1037/0022-3514.44.1.113

Houck, J. M., Moyers, T. B., Miller, W. R., Glynn, L. H., & Hallgren, K. A. (2012). *Motivational Interviewing Skill Code (MISC) 2.5*. Unpublished manual.

Lee, A., Kummerfeld, J. K., An, L., & Mihalcea, R. (2024). A comparative multidimensional analysis of empathetic systems. *Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics (EACL)*, 179-189.

Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A diversity-promoting objective function for neural conversation models. *Proceedings of the 2016 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies*, 110-119. https://doi.org/10.18653/v1/N16-1014

Min, D. J., Pérez-Rosas, V., Resnicow, K., & Mihalcea, R. (2022). PAIR: Prompt-aware margin ranking for counselor reflection scoring in motivational interviewing. *Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing*, 148-158.

Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, and dominance for 20,000 English words. *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics*, 174-184.

Russell, J. A. (1980). A circumplex model of affect. *Journal of Personality and Social Psychology*, 39(6), 1161-1178. https://doi.org/10.1037/h0077714

Sharma, A., Miner, A., Atkins, D., & Althoff, T. (2020). A computational approach to understanding empathy expressed in text-based mental health support. *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)*, 5263-5276.

Sotolar, O., Formanek, V., Debnath, A., Lahnala, A., Welch, C., & Flek, L. (2024). EmPO: Emotion grounding for empathetic response generation through preference optimization. *arXiv preprint arXiv:2406.19071*.

Truax, C. B., & Carkhuff, R. R. (1964). Concreteness: A neglected variable in research in psychotherapy. *Journal of Clinical Psychology*, 20(2), 264-267.

---

*문서 생성일: 2024년 12월 30일*

*프로젝트: Empathy Alignment for Large Language Models*

