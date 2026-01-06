# -*- coding: utf-8 -*-
"""
전체 Lexicon을 적용한 Baseline Evaluation 노트북 생성
"""

import json
import os

def create_notebook():
    cells = []
    
    # Cell 1: Title
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '# 🎯 Empathy Alignment: Baseline Model Evaluation\n',
            '\n',
            '이 노트북에서는 **Llama-3.1-8B**와 **DeepSeek-7B** 모델을 4가지 공감 메트릭으로 평가합니다.\n',
            '\n',
            '## 4가지 평가 차원\n',
            '1. **Specificity (구체성)**: Brysbaert et al. (2014) - **40,000 단어 Lexicon**\n',
            '2. **Reflection Level (반영 수준)**: PAIR Model (Min et al., 2022)\n',
            '3. **Word Choice (단어 선택)**: NRC VAD Lexicon (Mohammad, 2018) - **20,000 단어 Lexicon**\n',
            '4. **Diversity (다양성)**: Distinct-n (Li et al., 2016)'
        ]
    })
    
    # Cell 2: Section 1 header
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['---\n', '## 1. 환경 설정']
    })
    
    # Cell 3: GPU check
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': ['# GPU 확인\n', '!nvidia-smi']
    })
    
    # Cell 4: Install packages
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            '# 필요한 패키지 설치\n',
            '!pip install -q transformers accelerate bitsandbytes\n',
            '!pip install -q torch\n',
            '!pip install -q huggingface_hub\n',
            '!pip install -q tqdm pandas matplotlib requests'
        ]
    })
    
    # Cell 5: Mount Drive
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            '# Google Drive 마운트\n',
            'from google.colab import drive\n',
            'drive.mount("/content/drive")\n',
            '\n',
            '# 프로젝트 경로 설정\n',
            'PROJECT_PATH = "/content/drive/MyDrive/empathy_alignment"\n',
            '\n',
            '# 필요한 폴더 생성\n',
            'import os\n',
            'os.makedirs(f"{PROJECT_PATH}/data", exist_ok=True)\n',
            'os.makedirs(f"{PROJECT_PATH}/data/lexicons", exist_ok=True)\n',
            'os.makedirs(f"{PROJECT_PATH}/models", exist_ok=True)\n',
            'os.makedirs(f"{PROJECT_PATH}/results", exist_ok=True)\n',
            '\n',
            'print(f"Project path: {PROJECT_PATH}")\n',
            'print("Folders created!")'
        ]
    })
    
    # Cell 6: HuggingFace login
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            '# HuggingFace 로그인 (Llama 모델 접근을 위해 필요)\n',
            '# https://huggingface.co/settings/tokens 에서 토큰 발급\n',
            '# https://huggingface.co/meta-llama 에서 Llama 라이센스 동의 필요\n',
            'from huggingface_hub import login\n',
            'login()'
        ]
    })
    
    # Cell 7: Section 2 - Lexicon Download
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '---\n',
            '## 2. Lexicon 데이터 다운로드\n',
            '\n',
            '### 필요한 데이터:\n',
            '- **Brysbaert Concreteness Ratings**: 40,000 영어 단어의 구체성 점수\n',
            '- **NRC VAD Lexicon**: 20,000 영어 단어의 Valence-Arousal-Dominance 점수'
        ]
    })
    
    # Cell 8: Download Concreteness
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            'import requests\n',
            'import os\n',
            '\n',
            'LEXICON_PATH = f"{PROJECT_PATH}/data/lexicons"\n',
            '\n',
            '# ========== Brysbaert Concreteness Ratings 다운로드 ==========\n',
            '# 출처: https://github.com/ArtsEngine/concreteness-ratings\n',
            '# 원본 논문: Brysbaert et al. (2014)\n',
            '\n',
            'CONCRETENESS_URL = "https://raw.githubusercontent.com/ArtsEngine/concreteness-ratings/master/Concreteness_ratings_Brysbaert_et_al_BRM.txt"\n',
            'CONCRETENESS_FILE = f"{LEXICON_PATH}/concreteness_ratings.txt"\n',
            '\n',
            'if not os.path.exists(CONCRETENESS_FILE):\n',
            '    print("Downloading Brysbaert Concreteness Ratings (40,000 words)...")\n',
            '    response = requests.get(CONCRETENESS_URL)\n',
            '    with open(CONCRETENESS_FILE, "w", encoding="utf-8") as f:\n',
            '        f.write(response.text)\n',
            '    print(f"[OK] Saved to {CONCRETENESS_FILE}")\n',
            'else:\n',
            '    print(f"[OK] Concreteness file already exists: {CONCRETENESS_FILE}")\n',
            '\n',
            '# 파일 확인\n',
            'with open(CONCRETENESS_FILE, "r", encoding="utf-8") as f:\n',
            '    lines = f.readlines()\n',
            'print(f"Total lines: {len(lines)}")\n',
            'print(f"Header: {lines[0].strip()}")\n',
            'print(f"Sample: {lines[1].strip()}")'
        ]
    })
    
    # Cell 9: Download VAD
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            '# ========== NRC VAD Lexicon 다운로드 ==========\n',
            '# 출처: https://saifmohammad.com/WebPages/nrc-vad.html\n',
            '# 원본 논문: Mohammad (2018)\n',
            '\n',
            'VAD_FILE = f"{LEXICON_PATH}/NRC-VAD-Lexicon.txt"\n',
            '\n',
            '# NRC VAD Lexicon 대체 다운로드 (GitHub mirror)\n',
            'VAD_URL = "https://raw.githubusercontent.com/bagustris/nrc_vad_lexicon/main/NRC-VAD-Lexicon.txt"\n',
            '\n',
            'if not os.path.exists(VAD_FILE):\n',
            '    print("Downloading NRC VAD Lexicon (20,000 words)...")\n',
            '    try:\n',
            '        response = requests.get(VAD_URL)\n',
            '        if response.status_code == 200:\n',
            '            with open(VAD_FILE, "w", encoding="utf-8") as f:\n',
            '                f.write(response.text)\n',
            '            print(f"[OK] Saved to {VAD_FILE}")\n',
            '        else:\n',
            '            print(f"[WARNING] Could not download VAD Lexicon. Status: {response.status_code}")\n',
            '            print("Please download manually from: https://saifmohammad.com/WebPages/nrc-vad.html")\n',
            '    except Exception as e:\n',
            '        print(f"[ERROR] {e}")\n',
            '        print("Please download manually from: https://saifmohammad.com/WebPages/nrc-vad.html")\n',
            'else:\n',
            '    print(f"[OK] VAD file already exists: {VAD_FILE}")\n',
            '\n',
            '# 파일 확인\n',
            'if os.path.exists(VAD_FILE):\n',
            '    with open(VAD_FILE, "r", encoding="utf-8") as f:\n',
            '        lines = f.readlines()\n',
            '    print(f"Total lines: {len(lines)}")\n',
            '    print(f"Sample: {lines[0].strip()}")\n',
            '    print(f"Sample: {lines[1].strip()}")'
        ]
    })
    
    # Cell 10: Section 3 - Metrics
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['---\n', '## 3. 메트릭 코드 정의 (Full Lexicon 버전)']
    })
    
    # Cell 11: Imports
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            'import re\n',
            'import numpy as np\n',
            'from typing import List, Dict, Optional, Tuple\n',
            'from collections import Counter\n',
            'from dataclasses import dataclass, asdict\n',
            'from datetime import datetime\n',
            'import json\n',
            '\n',
            'print("[OK] Imports ready")'
        ]
    })
    
    # Cell 12: Specificity Metric
    specificity_code = '''# ========== Specificity Metric (Full Lexicon: 40,000 words) ==========
class SpecificityMetric:
    """
    구체성 메트릭 - Brysbaert et al. (2014) Concreteness Ratings 기반
    
    40,000개 영어 단어에 대한 구체성 점수 (1-5점)
    - 5점: 매우 구체적 (감각적으로 경험 가능) - e.g., apple, dog, car
    - 1점: 매우 추상적 (개념적) - e.g., freedom, truth, idea
    
    Reference:
    Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). 
    Concreteness ratings for 40 thousand generally known English word lemmas.
    Behavior Research Methods, 46(3), 904-911.
    """
    
    def __init__(self, lexicon_path: str = None):
        self.lexicon = {}
        if lexicon_path:
            self.load_lexicon(lexicon_path)
        else:
            self._load_fallback_lexicon()
    
    def load_lexicon(self, filepath: str):
        """Brysbaert Concreteness Ratings 파일 로드"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # 헤더 스킵 (첫 줄)
            for line in lines[1:]:
                parts = line.strip().split("\\t")
                if len(parts) >= 3:
                    word = parts[0].lower().strip()
                    try:
                        # Conc.M 컬럼 (평균 구체성 점수)
                        score = float(parts[2])
                        self.lexicon[word] = score
                    except (ValueError, IndexError):
                        continue
            
            print(f"[OK] Loaded {len(self.lexicon):,} words from Concreteness Lexicon")
        except FileNotFoundError:
            print(f"[WARNING] File not found: {filepath}")
            self._load_fallback_lexicon()
    
    def _load_fallback_lexicon(self):
        """파일이 없을 경우 기본 샘플 lexicon 사용"""
        self.lexicon = {
            "apple": 5.0, "dog": 4.98, "cat": 4.97, "car": 4.95, "house": 4.93,
            "tree": 4.92, "book": 4.89, "table": 4.88, "phone": 4.85, "computer": 4.82,
            "water": 4.80, "food": 4.75, "hand": 4.90, "face": 4.85, "eye": 4.88,
            "money": 4.45, "music": 4.20, "weather": 4.15, "friend": 4.10, "family": 4.05,
            "work": 3.95, "home": 4.30, "school": 4.25, "problem": 3.50, "situation": 3.20,
            "experience": 3.15, "feeling": 3.10, "moment": 3.05, "reason": 2.95, "way": 2.85,
            "time": 3.30, "life": 3.25, "day": 3.80, "place": 3.75, "idea": 2.50,
            "hope": 2.30, "love": 2.45, "fear": 2.40, "joy": 2.35, "sadness": 2.25,
            "anger": 2.55, "happiness": 2.20, "peace": 2.15, "freedom": 2.10, "truth": 2.05,
            "thing": 1.95, "something": 1.85, "anything": 1.80, "nothing": 1.75,
            "understand": 2.60, "sorry": 2.70, "glad": 2.65, "proud": 2.55, "worried": 2.75,
            "excited": 2.80, "disappointed": 2.45, "frustrated": 2.50, "grateful": 2.40,
            "anxious": 2.35, "overwhelmed": 2.30, "stressed": 2.85, "relieved": 2.90,
        }
        print(f"[WARNING] Using fallback lexicon ({len(self.lexicon)} words)")
    
    def compute(self, text: str) -> Dict:
        """텍스트의 구체성 점수 계산"""
        words = re.findall(r"\\b[a-z]+\\b", text.lower())
        if not words:
            return {"score": 0.0, "coverage": 0.0, "matched_words": 0, "total_words": 0}
        
        scores = [self.lexicon[w] for w in words if w in self.lexicon]
        if not scores:
            return {"score": 0.0, "coverage": 0.0, "matched_words": 0, "total_words": len(words)}
        
        return {
            "score": float(np.mean(scores)),
            "coverage": len(scores) / len(words),
            "matched_words": len(scores),
            "total_words": len(words)
        }

# Lexicon 로드
CONCRETENESS_FILE = f"{PROJECT_PATH}/data/lexicons/concreteness_ratings.txt"
specificity_metric = SpecificityMetric(CONCRETENESS_FILE)

# 테스트
test_result = specificity_metric.compute("I understand how you feel about losing your dog.")
print(f"Test result: {test_result}")'''
    
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': specificity_code.split('\n')
    })
    
    # Cell 13: Reflection Metric
    reflection_code = '''# ========== Reflection Level Metric ==========
class ReflectionLevelMetric:
    """
    반영 수준 메트릭 - PAIR Model (Min et al., 2022) 및 MISC 2.5 (Houck et al., 2012) 기반
    
    7단계 반영 수준 (0-6):
    - Level 0: 반영 없음
    - Level 1-2: Simple Reflection (단순 반복/확인)
    - Level 3-4: Feeling Reflection (감정 인식 및 반영)
    - Level 5-6: Complex Reflection (깊은 의미/감정 탐색)
    
    References:
    - Min, S., et al. (2022). PAIR: Prompt-aware margin ranking for counselor reflection generation. ACL.
    - Houck, J. M., et al. (2012). Motivational Interviewing Skill Code (MISC) 2.5.
    """
    
    def __init__(self):
        # Complex Reflection 패턴 (Level 5-6)
        self.complex_patterns = [
            r"it seems like .+ means .+ to you",
            r"beneath .+ there seems to be",
            r"on a deeper level",
            r"what that .+ represents",
            r"i sense that .+ is really about",
            r"there\\'s something .+ underneath",
            r"it sounds like .+ goes beyond",
            r"what i\\'m hearing is .+ and also",
            r"the .+ seems connected to",
            r"i wonder if .+ is related to",
        ]
        
        # Feeling Reflection 패턴 (Level 3-4)
        self.feeling_patterns = [
            r"you(\\'re| are) feeling",
            r"you feel",
            r"you seem",
            r"sounds like you(\\'re| are)",
            r"it sounds like",
            r"that must (be|feel|have been)",
            r"i can (see|hear|sense|imagine) (that |how )?you",
            r"you sound",
            r"it seems like you",
            r"you appear to be",
            r"i get the sense that you",
            r"what i hear is that you",
            r"you\\'re experiencing",
            r"that sounds (really |very )?(hard|difficult|painful|frustrating|overwhelming)",
            r"it must (be|feel) (so |really |very )?(hard|difficult|painful)",
        ]
        
        # Simple Reflection 패턴 (Level 1-2)
        self.simple_patterns = [
            r"so you",
            r"you(\\'re| are) saying",
            r"you mentioned",
            r"i hear you",
            r"i understand",
            r"i see",
            r"that(\\'s| is) (hard|difficult|tough|challenging)",
            r"you said",
            r"you told me",
            r"you shared",
            r"right,",
            r"okay,",
            r"i get it",
            r"i hear what you",
            r"that makes sense",
        ]
        
        # Empathy Booster 패턴 (추가 점수)
        self.empathy_boosters = [
            r"i(\\'m| am) (so |really |truly )?sorry (to hear|that|for)",
            r"that must (be|have been) (really |very |so )?(hard|difficult|painful|devastating|heartbreaking)",
            r"i can only imagine",
            r"thank you for (sharing|telling|trusting|opening up)",
            r"i appreciate you (sharing|telling|trusting)",
            r"that takes (courage|strength|a lot)",
            r"i\\'m here for you",
            r"you\\'re not alone",
            r"i care about",
            r"my heart goes out to you",
            r"i can\\'t imagine how (hard|difficult|painful)",
        ]
    
    def compute(self, response: str, context: Optional[str] = None) -> Dict:
        """응답의 반영 수준 계산"""
        text = response.lower().strip()
        
        counts = {"complex": 0, "feeling": 0, "simple": 0, "booster": 0}
        
        for p in self.complex_patterns:
            if re.search(p, text):
                counts["complex"] += 1
        
        for p in self.feeling_patterns:
            if re.search(p, text):
                counts["feeling"] += 1
        
        for p in self.simple_patterns:
            if re.search(p, text):
                counts["simple"] += 1
        
        for p in self.empathy_boosters:
            if re.search(p, text):
                counts["booster"] += 1
        
        # 레벨 계산
        if counts["complex"] > 0:
            level = 5 + min(counts["complex"], 1)  # 5-6
        elif counts["feeling"] > 0:
            level = 3 + min(counts["feeling"], 2)  # 3-5
        elif counts["simple"] > 0:
            level = 1 + min(counts["simple"], 1)   # 1-2
        else:
            level = 0
        
        # Booster로 레벨 상향 (최대 6)
        if counts["booster"] > 0 and level < 6:
            level = min(level + 1, 6)
        
        return {
            "level": level,
            "normalized_score": level / 6.0,
            "counts": counts
        }

reflection_metric = ReflectionLevelMetric()

# 테스트
test_result = reflection_metric.compute("I\\'m so sorry to hear that. It sounds like you\\'re feeling really overwhelmed right now.")
print(f"Test result: {test_result}")'''
    
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': reflection_code.split('\n')
    })
    
    # Cell 14: Word Choice Metric
    word_choice_code = '''# ========== Word Choice Metric (Full Lexicon: 20,000 words) ==========
class WordChoiceMetric:
    """
    단어 선택 메트릭 - NRC VAD Lexicon (Mohammad, 2018) 기반
    
    20,000개 영어 단어에 대한 VAD 점수:
    - Valence (V): 감정의 긍정/부정 (0-1)
    - Arousal (A): 감정의 각성 수준 (0-1)
    - Dominance (D): 통제감/지배력 (0-1)
    
    공감적 응답의 이상적 VAD 프로필:
    - Valence: 0.65 (중간-긍정적, 희망 제공)
    - Arousal: 0.45 (중간-낮음, 차분한 톤)
    - Dominance: 0.40 (중간-낮음, 비지배적 태도)
    
    Reference:
    Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, 
    and dominance for 20,000 English words. ACL.
    """
    
    IDEAL_VALENCE = 0.65
    IDEAL_AROUSAL = 0.45
    IDEAL_DOMINANCE = 0.40
    
    def __init__(self, lexicon_path: str = None):
        self.vad_lexicon = {}
        if lexicon_path:
            self.load_lexicon(lexicon_path)
        else:
            self._load_fallback_lexicon()
    
    def load_lexicon(self, filepath: str):
        """NRC VAD Lexicon 파일 로드"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line in lines:
                parts = line.strip().split("\\t")
                if len(parts) >= 4:
                    word = parts[0].lower().strip()
                    try:
                        v = float(parts[1])  # Valence
                        a = float(parts[2])  # Arousal
                        d = float(parts[3])  # Dominance
                        self.vad_lexicon[word] = {"v": v, "a": a, "d": d}
                    except (ValueError, IndexError):
                        continue
            
            print(f"[OK] Loaded {len(self.vad_lexicon):,} words from VAD Lexicon")
        except FileNotFoundError:
            print(f"[WARNING] File not found: {filepath}")
            self._load_fallback_lexicon()
    
    def _load_fallback_lexicon(self):
        """파일이 없을 경우 기본 샘플 lexicon 사용"""
        self.vad_lexicon = {
            "happy": {"v": 0.96, "a": 0.74, "d": 0.87},
            "excited": {"v": 0.90, "a": 0.85, "d": 0.75},
            "joy": {"v": 0.98, "a": 0.78, "d": 0.82},
            "love": {"v": 0.95, "a": 0.72, "d": 0.70},
            "grateful": {"v": 0.90, "a": 0.48, "d": 0.65},
            "relieved": {"v": 0.82, "a": 0.35, "d": 0.68},
            "calm": {"v": 0.78, "a": 0.22, "d": 0.72},
            "angry": {"v": 0.15, "a": 0.85, "d": 0.55},
            "scared": {"v": 0.12, "a": 0.88, "d": 0.18},
            "anxious": {"v": 0.20, "a": 0.78, "d": 0.25},
            "stressed": {"v": 0.18, "a": 0.82, "d": 0.30},
            "frustrated": {"v": 0.15, "a": 0.75, "d": 0.35},
            "overwhelmed": {"v": 0.12, "a": 0.80, "d": 0.15},
            "sad": {"v": 0.15, "a": 0.32, "d": 0.25},
            "lonely": {"v": 0.12, "a": 0.35, "d": 0.20},
            "disappointed": {"v": 0.18, "a": 0.42, "d": 0.28},
            "understand": {"v": 0.70, "a": 0.35, "d": 0.65},
            "sorry": {"v": 0.35, "a": 0.45, "d": 0.35},
            "care": {"v": 0.82, "a": 0.45, "d": 0.55},
            "support": {"v": 0.78, "a": 0.48, "d": 0.62},
            "help": {"v": 0.75, "a": 0.52, "d": 0.58},
            "comfort": {"v": 0.80, "a": 0.28, "d": 0.55},
            "hear": {"v": 0.58, "a": 0.38, "d": 0.52},
            "feel": {"v": 0.50, "a": 0.50, "d": 0.50},
        }
        print(f"[WARNING] Using fallback VAD lexicon ({len(self.vad_lexicon)} words)")
    
    def compute(self, text: str) -> Dict:
        """텍스트의 VAD 점수 및 공감 정렬도 계산"""
        words = re.findall(r"\\b[a-z]+\\b", text.lower())
        if not words:
            return {
                "valence": 0.5, "arousal": 0.5, "dominance": 0.5,
                "empathy_alignment": 0.0, "coverage": 0.0,
                "matched_words": 0, "total_words": 0
            }
        
        v_scores, a_scores, d_scores = [], [], []
        for w in words:
            if w in self.vad_lexicon:
                v_scores.append(self.vad_lexicon[w]["v"])
                a_scores.append(self.vad_lexicon[w]["a"])
                d_scores.append(self.vad_lexicon[w]["d"])
        
        if not v_scores:
            return {
                "valence": 0.5, "arousal": 0.5, "dominance": 0.5,
                "empathy_alignment": 0.0, "coverage": 0.0,
                "matched_words": 0, "total_words": len(words)
            }
        
        v = np.mean(v_scores)
        a = np.mean(a_scores)
        d = np.mean(d_scores)
        
        # Empathy alignment: 이상적 VAD와의 거리 기반
        distance = (abs(v - self.IDEAL_VALENCE) + 
                   abs(a - self.IDEAL_AROUSAL) + 
                   abs(d - self.IDEAL_DOMINANCE)) / 3.0
        alignment = max(0.0, min(1.0, 1.0 - distance))
        
        return {
            "valence": float(v),
            "arousal": float(a),
            "dominance": float(d),
            "empathy_alignment": float(alignment),
            "coverage": len(v_scores) / len(words),
            "matched_words": len(v_scores),
            "total_words": len(words)
        }

# Lexicon 로드
VAD_FILE = f"{PROJECT_PATH}/data/lexicons/NRC-VAD-Lexicon.txt"
word_choice_metric = WordChoiceMetric(VAD_FILE)

# 테스트
test_result = word_choice_metric.compute("I\\'m sorry to hear that. I understand how difficult this must be for you.")
print(f"Test result: {test_result}")'''
    
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': word_choice_code.split('\n')
    })
    
    # Cell 15: Diversity Metric
    diversity_code = '''# ========== Diversity Metric ==========
class DiversityMetric:
    """
    다양성 메트릭 - Distinct-n (Li et al., 2016) 기반
    
    - Distinct-1: 고유 unigram 비율 (단어 수준 다양성)
    - Distinct-2: 고유 bigram 비율 (구문 수준 다양성)
    - Diversity Score: 0.4 * D1 + 0.6 * D2 (종합 점수)
    
    Reference:
    Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016).
    A diversity-promoting objective function for neural conversation models. NAACL-HLT.
    """
    
    def compute(self, text: str) -> Dict:
        """개별 텍스트의 다양성 계산"""
        tokens = re.findall(r"\\b[a-z]+\\b|[.,!?]", text.lower())
        if not tokens:
            return {"distinct_1": 0.0, "distinct_2": 0.0, "diversity_score": 0.0, "token_count": 0}
        
        # Distinct-1
        d1 = len(set(tokens)) / len(tokens)
        
        # Distinct-2
        bigrams = [tuple(tokens[i:i+2]) for i in range(len(tokens)-1)]
        d2 = len(set(bigrams)) / len(bigrams) if bigrams else 0.0
        
        # 종합 점수
        diversity_score = 0.4 * d1 + 0.6 * d2
        
        return {
            "distinct_1": float(d1),
            "distinct_2": float(d2),
            "diversity_score": float(diversity_score),
            "token_count": len(tokens)
        }
    
    def compute_corpus(self, texts: List[str]) -> Dict:
        """전체 코퍼스의 다양성 계산"""
        all_tokens = []
        for t in texts:
            all_tokens.extend(re.findall(r"\\b[a-z]+\\b|[.,!?]", t.lower()))
        
        if not all_tokens:
            return {"corpus_distinct_1": 0.0, "corpus_distinct_2": 0.0, "total_tokens": 0}
        
        d1 = len(set(all_tokens)) / len(all_tokens)
        bigrams = [tuple(all_tokens[i:i+2]) for i in range(len(all_tokens)-1)]
        d2 = len(set(bigrams)) / len(bigrams) if bigrams else 0.0
        
        return {
            "corpus_distinct_1": float(d1),
            "corpus_distinct_2": float(d2),
            "total_tokens": len(all_tokens),
            "unique_tokens": len(set(all_tokens))
        }

diversity_metric = DiversityMetric()

# 테스트
test_result = diversity_metric.compute("I understand how you feel. That must be really hard for you.")
print(f"Test result: {test_result}")'''
    
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': diversity_code.split('\n')
    })
    
    # Cell 16: Evaluator
    evaluator_code = '''# ========== Empathy Evaluator (통합 평가기) ==========
@dataclass
class EmpathyReport:
    """공감 평가 리포트"""
    model_name: str
    num_samples: int
    mean_specificity: float
    mean_reflection_level: float
    mean_word_choice: float
    mean_diversity: float
    overall_score: float
    details: Dict = None
    
    def to_dict(self):
        return asdict(self)

class EmpathyEvaluator:
    """4가지 메트릭을 통합한 공감 평가기"""
    
    def __init__(self, spec_metric, refl_metric, word_metric, div_metric):
        self.spec = spec_metric
        self.refl = refl_metric
        self.word = word_metric
        self.div = div_metric
    
    def evaluate_single(self, response: str, context: str = None) -> Dict:
        """단일 응답 평가"""
        return {
            "specificity": self.spec.compute(response),
            "reflection": self.refl.compute(response, context),
            "word_choice": self.word.compute(response),
            "diversity": self.div.compute(response)
        }
    
    def evaluate(self, responses: List[str], contexts: List[str] = None,
                 model_name: str = "Unknown") -> EmpathyReport:
        """다중 응답 평가"""
        if contexts is None:
            contexts = [None] * len(responses)
        
        spec_scores, refl_scores, word_scores, div_scores = [], [], [], []
        detailed_results = []
        
        for resp, ctx in zip(responses, contexts):
            result = self.evaluate_single(resp, ctx)
            spec_scores.append(result["specificity"]["score"])
            refl_scores.append(result["reflection"]["level"])
            word_scores.append(result["word_choice"]["empathy_alignment"])
            div_scores.append(result["diversity"]["diversity_score"])
            detailed_results.append(result)
        
        corpus_div = self.div.compute_corpus(responses)
        
        mean_spec = np.mean(spec_scores)
        mean_refl = np.mean(refl_scores)
        mean_word = np.mean(word_scores)
        mean_div = np.mean(div_scores)
        
        # Overall score (정규화 후 평균)
        overall = (0.25 * (mean_spec / 5.0) + 
                   0.25 * (mean_refl / 6.0) + 
                   0.25 * mean_word + 
                   0.25 * mean_div)
        
        return EmpathyReport(
            model_name=model_name,
            num_samples=len(responses),
            mean_specificity=float(mean_spec),
            mean_reflection_level=float(mean_refl),
            mean_word_choice=float(mean_word),
            mean_diversity=float(mean_div),
            overall_score=float(overall),
            details={
                "corpus_distinct_1": corpus_div["corpus_distinct_1"],
                "corpus_distinct_2": corpus_div["corpus_distinct_2"],
                "spec_std": float(np.std(spec_scores)),
                "refl_std": float(np.std(refl_scores)),
                "word_std": float(np.std(word_scores)),
                "div_std": float(np.std(div_scores)),
                "spec_coverage": float(np.mean([r["specificity"]["coverage"] for r in detailed_results])),
                "word_coverage": float(np.mean([r["word_choice"]["coverage"] for r in detailed_results])),
            }
        )
    
    def print_report(self, report: EmpathyReport):
        """리포트 출력"""
        print("\\n" + "="*65)
        print("📊 EMPATHY EVALUATION REPORT")
        print("="*65)
        print(f"Model: {report.model_name}")
        print(f"Samples: {report.num_samples}")
        print("-"*65)
        print(f"  📐 Specificity:        {report.mean_specificity:.3f} / 5.0  (coverage: {report.details[\\"spec_coverage\\"]:.1%})")
        print(f"  🪞 Reflection Level:   {report.mean_reflection_level:.2f} / 6.0")
        print(f"  💬 Word Choice:        {report.mean_word_choice:.3f} / 1.0  (coverage: {report.details[\\"word_coverage\\"]:.1%})")
        print(f"  🎨 Diversity:          {report.mean_diversity:.3f} / 1.0")
        print("-"*65)
        print(f"  🎯 OVERALL SCORE:      {report.overall_score:.3f} / 1.0")
        print("="*65)

# 평가기 초기화
evaluator = EmpathyEvaluator(specificity_metric, reflection_metric, word_choice_metric, diversity_metric)
print("[OK] EmpathyEvaluator ready!")'''
    
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': evaluator_code.split('\n')
    })
    
    # Cell 17: Test prompts section
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['---\n', '## 4. 테스트 프롬프트 정의']
    })
    
    # Cell 18: Test prompts
    test_prompts_code = '''# 공감적 응답이 필요한 상황들 (10가지)
TEST_PROMPTS = [
    {"context": "I just lost my job today. I\\'ve been working there for 5 years and they just let me go without any warning.", "emotion": "sadness/shock"},
    {"context": "My best friend hasn\\'t talked to me in weeks. I don\\'t know what I did wrong.", "emotion": "confusion/hurt"},
    {"context": "I finally passed my medical exam after failing three times! I can\\'t believe it!", "emotion": "joy/relief"},
    {"context": "My parents are getting divorced after 30 years of marriage. I don\\'t know how to feel.", "emotion": "confusion/sadness"},
    {"context": "I\\'ve been feeling really anxious lately. I can\\'t sleep and I keep worrying about everything.", "emotion": "anxiety"},
    {"context": "My dog passed away yesterday. He was with me for 12 years.", "emotion": "grief"},
    {"context": "I got accepted into my dream university! All the hard work finally paid off.", "emotion": "excitement/pride"},
    {"context": "I feel like nobody understands me. Even my closest friends don\\'t seem to get what I\\'m going through.", "emotion": "loneliness"},
    {"context": "My partner forgot our anniversary again. It\\'s the third year in a row.", "emotion": "disappointment/hurt"},
    {"context": "I just found out I\\'m going to be a parent. I\\'m excited but also terrified.", "emotion": "mixed emotions"},
]

SYSTEM_PROMPT = """You are an empathetic listener. When someone shares their feelings or experiences with you, respond with genuine empathy and understanding.
- Acknowledge their emotions
- Show that you understand their situation
- Be supportive without being dismissive
- Avoid giving unsolicited advice unless asked

Respond naturally and warmly, as a caring friend would."""

print(f"[OK] Loaded {len(TEST_PROMPTS)} test prompts")
print(f"Emotions covered: {[p[\\"emotion\\"] for p in TEST_PROMPTS]}")'''
    
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': test_prompts_code.split('\n')
    })
    
    # Cell 19: Model functions section
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['---\n', '## 5. 모델 로드 및 응답 생성 함수']
    })
    
    # Cell 20: Model functions
    model_functions_code = '''import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
import gc

def load_model(model_name: str):
    """모델 로드 (H100/A100에서는 양자화 불필요)"""
    print(f"\\n{\\"=\\"*50}")
    print(f"Loading: {model_name}")
    print(f"{\\"=\\"*50}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    
    print(f"[OK] Model loaded! Device: {next(model.parameters()).device}")
    return model, tokenizer

def generate_response(model, tokenizer, context: str, max_new_tokens: int = 256) -> str:
    """응답 생성"""
    if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": context}]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        prompt = f"System: {SYSTEM_PROMPT}\\n\\nUser: {context}\\n\\nAssistant:"
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens, temperature=0.7,
            do_sample=True, top_p=0.9, pad_token_id=tokenizer.pad_token_id
        )
    
    return tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()

def cleanup():
    """GPU 메모리 정리"""
    gc.collect()
    torch.cuda.empty_cache()
    print("[CLEAN] GPU memory cleaned!")

print("[OK] Functions ready!")'''
    
    cells.append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': model_functions_code.split('\n')
    })
    
    # Cell 21-26: Llama evaluation
    cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': ['---\n', '## 6. Llama-3.1-8B 평가']})
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 
                  'source': ['# Llama 모델 로드\n', 'LLAMA_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"\n', 'llama_model, llama_tokenizer = load_model(LLAMA_MODEL)']})
    
    llama_gen_code = '''# Llama 응답 생성
llama_responses = []
llama_contexts = []

print("Generating Llama responses...")
for prompt_data in tqdm(TEST_PROMPTS):
    context = prompt_data["context"]
    response = generate_response(llama_model, llama_tokenizer, context)
    llama_responses.append(response)
    llama_contexts.append(context)
    print(f"\\n[Context]: {context[:50]}...")
    print(f"[Response]: {response[:100]}...")'''
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': llama_gen_code.split('\n')})
    
    llama_eval_code = '''# Llama 평가
llama_report = evaluator.evaluate(llama_responses, llama_contexts, LLAMA_MODEL)
evaluator.print_report(llama_report)

# 결과 저장
with open(f"{PROJECT_PATH}/results/llama_evaluation.json", "w") as f:
    json.dump({
        "model": LLAMA_MODEL,
        "responses": llama_responses,
        "contexts": llama_contexts,
        "report": llama_report.to_dict()
    }, f, indent=2)
print(f"[OK] Saved to {PROJECT_PATH}/results/llama_evaluation.json")'''
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': llama_eval_code.split('\n')})
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 
                  'source': ['# Llama 메모리 정리\n', 'del llama_model, llama_tokenizer\n', 'cleanup()']})
    
    # Cell 27-32: DeepSeek evaluation
    cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': ['---\n', '## 7. DeepSeek-7B 평가']})
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 
                  'source': ['# DeepSeek 모델 로드\n', 'DEEPSEEK_MODEL = "deepseek-ai/deepseek-llm-7b-chat"\n', 'deepseek_model, deepseek_tokenizer = load_model(DEEPSEEK_MODEL)']})
    
    deepseek_gen_code = '''# DeepSeek 응답 생성
deepseek_responses = []
deepseek_contexts = []

print("Generating DeepSeek responses...")
for prompt_data in tqdm(TEST_PROMPTS):
    context = prompt_data["context"]
    response = generate_response(deepseek_model, deepseek_tokenizer, context)
    deepseek_responses.append(response)
    deepseek_contexts.append(context)
    print(f"\\n[Context]: {context[:50]}...")
    print(f"[Response]: {response[:100]}...")'''
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': deepseek_gen_code.split('\n')})
    
    deepseek_eval_code = '''# DeepSeek 평가
deepseek_report = evaluator.evaluate(deepseek_responses, deepseek_contexts, DEEPSEEK_MODEL)
evaluator.print_report(deepseek_report)

# 결과 저장
with open(f"{PROJECT_PATH}/results/deepseek_evaluation.json", "w") as f:
    json.dump({
        "model": DEEPSEEK_MODEL,
        "responses": deepseek_responses,
        "contexts": deepseek_contexts,
        "report": deepseek_report.to_dict()
    }, f, indent=2)
print(f"[OK] Saved to {PROJECT_PATH}/results/deepseek_evaluation.json")'''
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': deepseek_eval_code.split('\n')})
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 
                  'source': ['# DeepSeek 메모리 정리\n', 'del deepseek_model, deepseek_tokenizer\n', 'cleanup()']})
    
    # Cell 33-36: Comparison
    cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': ['---\n', '## 8. 모델 비교']})
    
    comparison_code = '''import pandas as pd
import matplotlib.pyplot as plt

# 비교 테이블
comparison = pd.DataFrame({
    "Model": ["Llama-3.1-8B", "DeepSeek-7B"],
    "Specificity": [llama_report.mean_specificity, deepseek_report.mean_specificity],
    "Reflection": [llama_report.mean_reflection_level, deepseek_report.mean_reflection_level],
    "Word Choice": [llama_report.mean_word_choice, deepseek_report.mean_word_choice],
    "Diversity": [llama_report.mean_diversity, deepseek_report.mean_diversity],
    "Overall": [llama_report.overall_score, deepseek_report.overall_score],
})

print("\\n" + "="*70)
print("📊 MODEL COMPARISON")
print("="*70)
print(comparison.to_string(index=False))
print("="*70)'''
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': comparison_code.split('\n')})
    
    radar_code = '''# 레이더 차트
categories = ["Specificity\\n(norm)", "Reflection\\nLevel", "Word\\nChoice", "Diversity"]
N = len(categories)

llama_scores = [llama_report.mean_specificity/5, llama_report.mean_reflection_level/6,
                llama_report.mean_word_choice, llama_report.mean_diversity]
deepseek_scores = [deepseek_report.mean_specificity/5, deepseek_report.mean_reflection_level/6,
                   deepseek_report.mean_word_choice, deepseek_report.mean_diversity]

angles = [n / N * 2 * np.pi for n in range(N)]
angles += angles[:1]
llama_scores += llama_scores[:1]
deepseek_scores += deepseek_scores[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
ax.plot(angles, llama_scores, "o-", linewidth=2, label="Llama-3.1-8B", color="#2E86AB")
ax.fill(angles, llama_scores, alpha=0.25, color="#2E86AB")
ax.plot(angles, deepseek_scores, "o-", linewidth=2, label="DeepSeek-7B", color="#E94F37")
ax.fill(angles, deepseek_scores, alpha=0.25, color="#E94F37")

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, size=12)
ax.set_ylim(0, 1)
ax.set_title("Empathy Evaluation: Llama vs DeepSeek", size=14, fontweight="bold", pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

plt.tight_layout()
plt.savefig(f"{PROJECT_PATH}/results/comparison_radar.png", dpi=150, bbox_inches="tight")
plt.show()
print(f"\\n[OK] Chart saved!")'''
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': radar_code.split('\n')})
    
    final_code = '''# 최종 결과 저장
final_result = {
    "date": datetime.now().isoformat(),
    "models": [LLAMA_MODEL, DEEPSEEK_MODEL],
    "llama": llama_report.to_dict(),
    "deepseek": deepseek_report.to_dict(),
    "winner": LLAMA_MODEL if llama_report.overall_score > deepseek_report.overall_score else DEEPSEEK_MODEL,
    "lexicon_info": {
        "concreteness_words": len(specificity_metric.lexicon),
        "vad_words": len(word_choice_metric.vad_lexicon)
    }
}

with open(f"{PROJECT_PATH}/results/baseline_comparison.json", "w") as f:
    json.dump(final_result, f, indent=2)

print("\\n" + "="*60)
print("🏆 EVALUATION COMPLETE!")
print("="*60)
print(f"Winner: {final_result[\\"winner\\"].split(\\"/\\")[-1]}")
print(f"Llama Overall: {llama_report.overall_score:.3f}")
print(f"DeepSeek Overall: {deepseek_report.overall_score:.3f}")
print(f"Results saved to: {PROJECT_PATH}/results/")
print("="*60)'''
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': final_code.split('\n')})
    
    # Cell 37-38: Response samples
    cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': ['---\n', '## 9. 응답 샘플 확인']})
    
    samples_code = '''# 응답 비교
print("\\n" + "="*80)
print("📝 RESPONSE SAMPLES")
print("="*80)

for i in range(min(3, len(TEST_PROMPTS))):
    print(f"\\n--- Prompt {i+1} ({TEST_PROMPTS[i][\\"emotion\\"]}) ---")
    print(f"Context: {TEST_PROMPTS[i][\\"context\\"]}")
    print(f"\\n🦙 [Llama]: {llama_responses[i]}")
    print(f"\\n🔷 [DeepSeek]: {deepseek_responses[i]}")
    print("-"*80)'''
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': samples_code.split('\n')})
    
    # Cell 39-40: Lexicon info
    cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': ['---\n', '## 10. Lexicon 정보 확인']})
    
    lexicon_info_code = '''# Lexicon 통계
print("="*60)
print("📚 LEXICON STATISTICS")
print("="*60)
print(f"Concreteness Lexicon: {len(specificity_metric.lexicon):,} words")
print(f"VAD Lexicon: {len(word_choice_metric.vad_lexicon):,} words")
print("="*60)

# 샘플 단어 확인
print("\\n[Concreteness Samples]")
sample_words = ["dog", "love", "freedom", "understand", "happy"]
for w in sample_words:
    if w in specificity_metric.lexicon:
        print(f"  {w}: {specificity_metric.lexicon[w]:.2f}")

print("\\n[VAD Samples]")
for w in sample_words:
    if w in word_choice_metric.vad_lexicon:
        vad = word_choice_metric.vad_lexicon[w]
        print(f"  {w}: V={vad[\\"v\\"]:.2f}, A={vad[\\"a\\"]:.2f}, D={vad[\\"d\\"]:.2f}")'''
    cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': lexicon_info_code.split('\n')})
    
    # Create notebook
    notebook = {
        'cells': cells,
        'metadata': {
            'accelerator': 'GPU',
            'colab': {'gpuType': 'A100', 'provenance': []},
            'kernelspec': {'display_name': 'Python 3', 'name': 'python3'}
        },
        'nbformat': 4,
        'nbformat_minor': 0
    }
    
    # Save
    os.makedirs('notebooks', exist_ok=True)
    with open('notebooks/01_evaluate_baseline_models.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print('[OK] Created: notebooks/01_evaluate_baseline_models.ipynb')
    print(f'Total cells: {len(cells)}')

if __name__ == '__main__':
    create_notebook()

