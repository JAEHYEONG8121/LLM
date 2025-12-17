# 🧠 DeepSeek Fine-tuning on Google Colab (무료)

## 📋 준비물

1. **Google 계정**
2. **데이터 파일** (Google Drive에 업로드)
   - `opela_empathy_train.jsonl`
   - `opela_empathy_val.jsonl`

---

## 🚀 시작하기

### Step 1: Google Colab 열기

👉 [Google Colab 새 노트북 열기](https://colab.research.google.com/#create=true)

### Step 2: GPU 설정

1. 메뉴 → **런타임** → **런타임 유형 변경**
2. **하드웨어 가속기** → **T4 GPU** (또는 A100) 선택
3. **저장**

### Step 3: 데이터 업로드

Google Drive에 폴더 생성 후 파일 업로드:
```
MyDrive/
└── EmpathyAI/
    └── data/
        ├── opela_empathy_train.jsonl
        └── opela_empathy_val.jsonl
```

---

## 📝 Colab 코드 (셀별로 복사)

### 셀 1: 패키지 설치 (CUDA 12.x 호환)
```python
# CUDA 12.x 호환 버전으로 설치
!pip uninstall -y bitsandbytes triton -q
!pip install bitsandbytes>=0.44.0 --no-cache-dir
!pip install triton==3.0.0

# 나머지 패키지
!pip install -q transformers>=4.45.0
!pip install -q datasets==2.20.0
!pip install -q accelerate>=0.34.0
!pip install -q peft==0.12.0
!pip install -q trl>=0.10.0

print("✅ 설치 완료! 런타임을 다시 시작하세요.")
```

⚠️ **설치 후 런타임 → 세션 다시 시작**

---

### 셀 2: GPU 확인
```python
!nvidia-smi

import torch
print(f"CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
else:
    print("❌ GPU 설정 필요! 런타임 → 런타임 유형 변경 → T4 GPU")
```

---

### 셀 3: Google Drive 연결
```python
from google.colab import drive
drive.mount('/content/drive')

import os
WORK_DIR = "/content/drive/MyDrive/EmpathyAI"
os.makedirs(f"{WORK_DIR}/data", exist_ok=True)
os.makedirs(f"{WORK_DIR}/models", exist_ok=True)

TRAIN_FILE = f"{WORK_DIR}/data/opela_empathy_train.jsonl"
VAL_FILE = f"{WORK_DIR}/data/opela_empathy_val.jsonl"

# 파일 확인
if os.path.exists(TRAIN_FILE):
    print("✅ 데이터 파일 확인!")
else:
    print("❌ 데이터를 업로드해주세요!")
```

---

### 셀 4: 데이터 로드
```python
import json
from datasets import Dataset

def load_jsonl(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def convert_format(sample):
    msgs = sample.get('messages', [])
    sys_c, user_c, asst_c = "", "", ""
    for m in msgs:
        if m['role'] == 'system': sys_c = m['content']
        elif m['role'] == 'user': user_c = m['content']
        elif m['role'] == 'assistant': asst_c = m['content']
    
    return {"text": f"<|im_start|>system\n{sys_c}<|im_end|>\n<|im_start|>user\n{user_c}<|im_end|>\n<|im_start|>assistant\n{asst_c}<|im_end|>"}

train_raw = load_jsonl(TRAIN_FILE)
val_raw = load_jsonl(VAL_FILE)

train_dataset = Dataset.from_list([convert_format(s) for s in train_raw])
val_dataset = Dataset.from_list([convert_format(s) for s in val_raw])

print(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}")
```

---

### 셀 5: 모델 로드 (4-bit 양자화)
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

MODEL_ID = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
model.config.use_cache = False

print(f"✅ 모델 로드 완료! GPU: {torch.cuda.memory_allocated()/1024**3:.1f}GB")
```

---

### 셀 6: LoRA 설정
```python
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
    task_type=TaskType.CAUSAL_LM,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

---

### 셀 7: 학습 설정
```python
from transformers import TrainingArguments
from trl import SFTTrainer

training_args = TrainingArguments(
    output_dir=f"{WORK_DIR}/models/deepseek-lora",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,
    optim="paged_adamw_32bit",
    learning_rate=2e-4,
    bf16=True,
    logging_steps=50,
    save_steps=500,
    eval_strategy="steps",
    eval_steps=500,
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    processing_class=tokenizer,
)

print("✅ Trainer 준비 완료!")
```

---

### 셀 8: 🚀 학습 시작
```python
print("="*50)
print("🚀 Fine-tuning 시작!")
print("="*50)
print("\n⏱️ 예상 시간: 약 2-4시간 (T4 GPU)")
print("💡 런타임 연결 유지 필수!\n")

trainer.train()

print("\n" + "="*50)
print("✅ 학습 완료!")
print("="*50)
```

---

### 셀 9: 모델 저장
```python
SAVE_PATH = f"{WORK_DIR}/models/deepseek-empathy-final"
trainer.model.save_pretrained(SAVE_PATH)
tokenizer.save_pretrained(SAVE_PATH)
print(f"💾 저장 완료: {SAVE_PATH}")
```

---

### 셀 10: 테스트
```python
def predict(user_text, persona_text):
    system = 'You are an empathy classifier. Output JSON with "empathy_label" (0-4).'
    user = f"USER: {user_text}\nPERSONA: {persona_text}\nReturn JSON only."
    
    prompt = f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n"
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=50, temperature=0.1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True).split("assistant")[-1]

# 테스트
print(predict("오늘 너무 힘들었어 ㅠㅠ", "에고 무슨 일 있었어?"))
print(predict("점심 뭐 먹었어?", "나는 김치찌개~"))
```

---

## ⏱️ 예상 시간

| 단계 | 시간 |
|------|------|
| 패키지 설치 | 2-3분 |
| 모델 다운로드 | 5-10분 |
| **학습 (3 epochs)** | **2-4시간** |
| 평가 | 10-30분 |

---

## 💡 팁

1. **런타임 연결 유지**: 브라우저 탭을 활성 상태로 유지
2. **중간 저장**: 학습 중 500 step마다 자동 저장됨
3. **이어서 학습**: 중단 시 checkpoint에서 재시작 가능

---

## 🔧 문제 해결

| 에러 | 해결책 |
|------|--------|
| `nvidia-smi: command not found` | 런타임 → 런타임 유형 변경 → GPU 선택 |
| `CUDA: False` | 런타임 재시작 |
| `numpy.dtype size changed` | 런타임 재시작 후 셀 2부터 실행 |
| `unexpected keyword argument` | 패키지 버전 업그레이드 (셀 1 재실행) |

---

## 📊 예상 결과

| 모델 | 정확도 |
|------|--------|
| GPT-4.1 Nano (Base) | 15.70% |
| GPT-4.1 Nano (Fine-tuned) | 33.49% |
| **DeepSeek 7B (QLoRA)** | **~45%** (예상) |
