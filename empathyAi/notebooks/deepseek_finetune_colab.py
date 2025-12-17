# -*- coding: utf-8 -*-
"""
================================================================================
🧠 EmpathyAI - DeepSeek Fine-tuning (Google Colab용)
================================================================================

한국어 공감 수준 분류를 위한 DeepSeek 모델 Fine-tuning

📋 사용 방법:
1. Google Colab 새 노트북 열기
2. 런타임 → 런타임 유형 변경 → GPU (T4) 선택
3. 아래 코드를 셀 단위로 복사하여 실행

================================================================================
"""

# ==============================================================================
# 셀 1: 패키지 설치
# ==============================================================================
"""
# 아래 코드를 Colab 첫 번째 셀에 붙여넣기

!pip install -q transformers==4.44.0
!pip install -q datasets==2.20.0
!pip install -q accelerate==0.33.0
!pip install -q peft==0.12.0
!pip install -q bitsandbytes==0.43.1
!pip install -q trl==0.9.6

print("✅ 패키지 설치 완료!")
"""

# ==============================================================================
# 셀 2: GPU 확인
# ==============================================================================
"""
!nvidia-smi

import torch
print(f"\\n🔥 PyTorch: {torch.__version__}")
print(f"🎮 CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"📊 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
"""

# ==============================================================================
# 셀 3: Google Drive 연결
# ==============================================================================
"""
from google.colab import drive
drive.mount('/content/drive')

import os
WORK_DIR = "/content/drive/MyDrive/EmpathyAI"
os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(f"{WORK_DIR}/data", exist_ok=True)
os.makedirs(f"{WORK_DIR}/models", exist_ok=True)

print(f"📁 작업 디렉토리: {WORK_DIR}")
print("\\n⚠️ Google Drive의 EmpathyAI/data 폴더에 다음 파일을 업로드하세요:")
print("   - opela_empathy_train.jsonl")
print("   - opela_empathy_val.jsonl")
"""

# ==============================================================================
# 셀 4: 데이터 파일 확인
# ==============================================================================
"""
TRAIN_FILE = f"{WORK_DIR}/data/opela_empathy_train.jsonl"
VAL_FILE = f"{WORK_DIR}/data/opela_empathy_val.jsonl"

import os
if os.path.exists(TRAIN_FILE) and os.path.exists(VAL_FILE):
    print("✅ 데이터 파일 확인 완료!")
    !wc -l {TRAIN_FILE} {VAL_FILE}
else:
    print("❌ 데이터 파일이 없습니다! Google Drive에 업로드해주세요.")
"""

# ==============================================================================
# 셀 5: 데이터 로드 및 전처리
# ==============================================================================
"""
import json
from datasets import Dataset

def load_jsonl(path):
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def convert_to_chat_format(sample):
    messages = sample.get('messages', [])
    
    system_content = ""
    user_content = ""
    assistant_content = ""
    
    for msg in messages:
        role = msg.get('role', '')
        content = msg.get('content', '')
        
        if role == 'system':
            system_content = content
        elif role == 'user':
            user_content = content
        elif role == 'assistant':
            assistant_content = content
    
    # ChatML 형식
    text = f'''<|im_start|>system
{system_content}<|im_end|>
<|im_start|>user
{user_content}<|im_end|>
<|im_start|>assistant
{assistant_content}<|im_end|>'''
    
    return {"text": text}

# 데이터 로드
print("📥 데이터 로드 중...")
train_raw = load_jsonl(TRAIN_FILE)
val_raw = load_jsonl(VAL_FILE)

print(f"   Train: {len(train_raw)} samples")
print(f"   Val: {len(val_raw)} samples")

# Dataset 변환
train_data = [convert_to_chat_format(s) for s in train_raw]
val_data = [convert_to_chat_format(s) for s in val_raw]

train_dataset = Dataset.from_list(train_data)
val_dataset = Dataset.from_list(val_data)

print("\\n✅ 데이터셋 준비 완료!")
print(f"\\n📝 샘플:\\n{train_dataset[0]['text'][:500]}...")
"""

# ==============================================================================
# 셀 6: 모델 로드 (4-bit 양자화)
# ==============================================================================
"""
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

MODEL_ID = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"

print(f"🤖 모델: {MODEL_ID}")
print("📥 모델 로드 중... (약 5-10분 소요)")

# 4-bit 양자화 설정
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# 토크나이저
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# 모델 (4-bit)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
)
model.config.use_cache = False

print("\\n✅ 모델 로드 완료!")
print(f"💾 GPU 메모리: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
"""

# ==============================================================================
# 셀 7: LoRA 설정
# ==============================================================================
"""
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

print("\\n✅ LoRA 설정 완료!")
"""

# ==============================================================================
# 셀 8: 학습 설정
# ==============================================================================
"""
from transformers import TrainingArguments
from trl import SFTTrainer

OUTPUT_DIR = f"{WORK_DIR}/models/deepseek-empathy-lora"

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,
    optim="paged_adamw_32bit",
    learning_rate=2e-4,
    weight_decay=0.01,
    bf16=True,
    max_grad_norm=0.3,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    logging_steps=25,
    save_steps=500,
    save_total_limit=3,
    evaluation_strategy="steps",
    eval_steps=500,
    do_eval=True,
    report_to="none",
    group_by_length=True,
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    dataset_text_field="text",
    max_seq_length=512,
    packing=False,
)

print("✅ Trainer 준비 완료!")
print(f"   Epochs: {training_args.num_train_epochs}")
print(f"   Effective batch size: {training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps}")
"""

# ==============================================================================
# 셀 9: 🚀 학습 시작
# ==============================================================================
"""
print("="*50)
print("🚀 Fine-tuning 시작!")
print("="*50)
print("\\n⏱️ 예상 시간: 약 2-4시간 (무료 Colab T4)")
print("💡 런타임 연결이 끊기지 않도록 주의!\\n")

trainer.train()

print("\\n" + "="*50)
print("✅ 학습 완료!")
print("="*50)
"""

# ==============================================================================
# 셀 10: 모델 저장
# ==============================================================================
"""
FINAL_MODEL_PATH = f"{WORK_DIR}/models/deepseek-empathy-final"

trainer.model.save_pretrained(FINAL_MODEL_PATH)
tokenizer.save_pretrained(FINAL_MODEL_PATH)

print(f"\\n💾 모델 저장: {FINAL_MODEL_PATH}")
!ls -la {FINAL_MODEL_PATH}
"""

# ==============================================================================
# 셀 11: 모델 테스트
# ==============================================================================
"""
def predict_empathy(user_text, persona_text):
    system_prompt = '''You are an empathy classifier for Korean persona-user dialogues. Given a USER utterance and the PERSONA's reply, output a JSON object ONLY with the key "empathy_label" whose value is an integer in {0,1,2,3,4}.
Label meanings: 0=not applicable, 1=empathy failure, 2=low empathy, 3=moderate empathy, 4=high active empathy.'''

    user_prompt = f'''Classify the empathy level of the PERSONA's reply.

USER: {user_text}
PERSONA: {persona_text}

Return JSON only.'''

    prompt = f'''<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant
'''

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "<|im_start|>assistant" in response:
        response = response.split("<|im_start|>assistant")[-1]
    
    return response.strip()

# 테스트
test_cases = [
    ("오늘 너무 힘든 하루였어... 회사에서 혼났거든", "에고 정말 힘들었겠다 ㅠㅠ 무슨 일이 있었어?", 4),
    ("점심 뭐 먹었어?", "나는 김치찌개 먹었어 ㅎㅎ", 0),
    ("시험 망친 것 같아 ㅠㅠ", "그래? 나는 잘 본 것 같아", 1),
]

print("🧪 모델 테스트")
print("="*60)
for user, persona, expected in test_cases:
    print(f"\\nUSER: {user}")
    print(f"PERSONA: {persona}")
    print(f"Expected: {expected}")
    print(f"Predicted: {predict_empathy(user, persona)}")
    print("-"*40)
"""

# ==============================================================================
# 셀 12: 전체 평가 (선택)
# ==============================================================================
"""
import re
from tqdm import tqdm
import random

def extract_label(response):
    try:
        match = re.search(r'"empathy_label"\\s*:\\s*(\\d)', response)
        if match:
            return int(match.group(1))
        match = re.search(r'[0-4]', response)
        if match:
            return int(match.group())
    except:
        pass
    return None

def get_gold_label(sample):
    import json
    for msg in reversed(sample.get('messages', [])):
        if msg.get('role') == 'assistant':
            try:
                content = json.loads(msg.get('content', '{}'))
                return content.get('empathy_label')
            except:
                pass
    return None

def get_user_persona(sample):
    for msg in sample.get('messages', []):
        if msg.get('role') == 'user':
            content = msg.get('content', '')
            user_match = re.search(r'USER:\\s*(.+?)\\nPERSONA:', content, re.DOTALL)
            persona_match = re.search(r'PERSONA:\\s*(.+?)\\n', content, re.DOTALL)
            user_text = user_match.group(1).strip() if user_match else ""
            persona_text = persona_match.group(1).strip() if persona_match else ""
            return user_text, persona_text
    return "", ""

# 200개 샘플 평가
EVAL_SAMPLES = 200
random.seed(42)
eval_samples = random.sample(val_raw, min(EVAL_SAMPLES, len(val_raw)))

correct = 0
total = 0

print(f"🔍 {EVAL_SAMPLES}개 샘플 평가...")
for sample in tqdm(eval_samples):
    gold = get_gold_label(sample)
    if gold is None:
        continue
    
    user_text, persona_text = get_user_persona(sample)
    if not user_text:
        continue
    
    response = predict_empathy(user_text, persona_text)
    pred = extract_label(response)
    
    if pred is not None:
        total += 1
        if pred == gold:
            correct += 1

accuracy = correct / total if total > 0 else 0
print(f"\\n📊 결과: {correct}/{total} = {accuracy*100:.2f}%")
"""

print("""
================================================================================
📋 사용 방법 요약
================================================================================

1. Google Colab 접속: https://colab.research.google.com

2. 새 노트북 생성

3. 런타임 → 런타임 유형 변경 → GPU (T4) 선택

4. 위 코드를 셀 단위로 복사하여 실행
   - 각 셀은 """ 로 구분되어 있습니다
   - """ 안의 코드만 Colab 셀에 붙여넣으세요

5. Google Drive에 데이터 업로드:
   - MyDrive/EmpathyAI/data/opela_empathy_train.jsonl
   - MyDrive/EmpathyAI/data/opela_empathy_val.jsonl

6. 학습 완료 후 결과 확인:
   - 모델: MyDrive/EmpathyAI/models/deepseek-empathy-final/

================================================================================
""")

