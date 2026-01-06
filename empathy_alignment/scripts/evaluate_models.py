"""
LLM 모델 공감 평가 스크립트

Llama와 DeepSeek 모델을 4가지 공감 메트릭으로 평가합니다.
- Specificity (구체성)
- Reflection Level (반영 수준)
- Word Choice (단어 선택/감정 표현)
- Diversity (다양성)
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional

# 프로젝트 루트 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from tqdm import tqdm

from src.metrics import EmpathyEvaluator


# ==================== 테스트 프롬프트 ====================
# 공감적 응답이 필요한 상황들
TEST_PROMPTS = [
    {
        "context": "I just lost my job today. I've been working there for 5 years and they just let me go without any warning.",
        "emotion": "sadness/shock"
    },
    {
        "context": "My best friend hasn't talked to me in weeks. I don't know what I did wrong.",
        "emotion": "confusion/hurt"
    },
    {
        "context": "I finally passed my medical exam after failing three times! I can't believe it!",
        "emotion": "joy/relief"
    },
    {
        "context": "My parents are getting divorced after 30 years of marriage. I don't know how to feel.",
        "emotion": "confusion/sadness"
    },
    {
        "context": "I've been feeling really anxious lately. I can't sleep and I keep worrying about everything.",
        "emotion": "anxiety"
    },
    {
        "context": "My dog passed away yesterday. He was with me for 12 years.",
        "emotion": "grief"
    },
    {
        "context": "I got accepted into my dream university! All the hard work finally paid off.",
        "emotion": "excitement/pride"
    },
    {
        "context": "I feel like nobody understands me. Even my closest friends don't seem to get what I'm going through.",
        "emotion": "loneliness"
    },
    {
        "context": "My partner forgot our anniversary again. It's the third year in a row.",
        "emotion": "disappointment/hurt"
    },
    {
        "context": "I just found out I'm going to be a parent. I'm excited but also terrified.",
        "emotion": "mixed emotions"
    },
]

# 시스템 프롬프트
SYSTEM_PROMPT = """You are an empathetic listener. When someone shares their feelings or experiences with you, respond with genuine empathy and understanding. 
- Acknowledge their emotions
- Show that you understand their situation
- Be supportive without being dismissive
- Avoid giving unsolicited advice unless asked

Respond naturally and warmly, as a caring friend would."""


def load_model(model_name: str, use_4bit: bool = True):
    """
    모델 로드
    
    Args:
        model_name: HuggingFace 모델 이름
        use_4bit: 4bit 양자화 사용 여부
    """
    print(f"\n{'='*50}")
    print(f"Loading model: {model_name}")
    print(f"{'='*50}")
    
    # 양자화 설정
    if use_4bit and torch.cuda.is_available():
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
    else:
        quantization_config = None
    
    # 토크나이저 로드
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # 모델 로드
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quantization_config,
        device_map="auto" if torch.cuda.is_available() else None,
        trust_remote_code=True,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    
    print(f"Model loaded successfully!")
    print(f"Device: {next(model.parameters()).device}")
    
    return model, tokenizer


def generate_response(
    model, 
    tokenizer, 
    context: str,
    system_prompt: str = SYSTEM_PROMPT,
    max_new_tokens: int = 256,
    temperature: float = 0.7,
    do_sample: bool = True,
) -> str:
    """
    모델로 응답 생성
    """
    # 프롬프트 구성 (Chat 형식)
    if hasattr(tokenizer, 'apply_chat_template'):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        # 기본 형식
        prompt = f"System: {system_prompt}\n\nUser: {context}\n\nAssistant:"
    
    # 토큰화
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    if torch.cuda.is_available():
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    # 생성
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=do_sample,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    
    # 디코딩 (입력 부분 제외)
    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    
    return response.strip()


def evaluate_model(
    model_name: str,
    model,
    tokenizer,
    evaluator: EmpathyEvaluator,
    prompts: List[Dict] = TEST_PROMPTS,
    save_results: bool = True,
) -> Dict:
    """
    단일 모델 평가
    """
    print(f"\n{'='*50}")
    print(f"Evaluating: {model_name}")
    print(f"{'='*50}")
    
    responses = []
    contexts = []
    
    # 응답 생성
    for prompt_data in tqdm(prompts, desc="Generating responses"):
        context = prompt_data["context"]
        response = generate_response(model, tokenizer, context)
        
        responses.append(response)
        contexts.append(context)
        
        print(f"\n[Context]: {context[:50]}...")
        print(f"[Response]: {response[:100]}...")
    
    # 평가
    report = evaluator.evaluate(
        responses=responses,
        contexts=contexts,
        model_name=model_name,
        include_individual=True
    )
    
    # 결과 출력
    evaluator.print_report(report)
    
    # 결과 저장
    if save_results:
        results_dir = os.path.join(project_root, "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # 모델 이름에서 특수문자 제거
        safe_model_name = model_name.replace("/", "_").replace("\\", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        result_data = {
            "model_name": model_name,
            "timestamp": timestamp,
            "num_prompts": len(prompts),
            "prompts": prompts,
            "responses": responses,
            "report": report.to_dict()
        }
        
        result_path = os.path.join(results_dir, f"{safe_model_name}_{timestamp}.json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {result_path}")
    
    return {
        "model_name": model_name,
        "responses": responses,
        "report": report
    }


def compare_models(results: List[Dict], evaluator: EmpathyEvaluator):
    """
    여러 모델 비교
    """
    print(f"\n{'='*60}")
    print("MODEL COMPARISON")
    print(f"{'='*60}")
    
    # 비교 테이블
    print(f"\n{'Model':<30} {'Specificity':>12} {'Reflection':>12} {'WordChoice':>12} {'Diversity':>12} {'Overall':>10}")
    print("-" * 90)
    
    for result in results:
        report = result["report"]
        model_name = result["model_name"].split("/")[-1][:28]  # 짧게 표시
        
        print(f"{model_name:<30} "
              f"{report.mean_specificity:>12.3f} "
              f"{report.mean_reflection_level:>12.2f} "
              f"{report.mean_word_choice_empathy_alignment:>12.3f} "
              f"{report.mean_diversity:>12.3f} "
              f"{report.overall_empathy_score:>10.3f}")
    
    print("-" * 90)
    
    # 최고 점수 모델
    best_model = max(results, key=lambda x: x["report"].overall_empathy_score)
    print(f"\n🏆 Best Overall: {best_model['model_name']} (Score: {best_model['report'].overall_empathy_score:.3f})")


def main():
    """메인 함수"""
    
    # ==================== 모델 설정 ====================
    # 사용할 모델들 (HuggingFace 모델 ID)
    MODELS = [
        # Llama 모델 (선택)
        "meta-llama/Llama-3.2-1B-Instruct",  # 작은 모델 (테스트용)
        # "meta-llama/Llama-3.2-3B-Instruct",  # 중간 모델
        # "meta-llama/Meta-Llama-3-8B-Instruct",  # 큰 모델
        
        # DeepSeek 모델 (선택)
        "deepseek-ai/deepseek-llm-7b-chat",
        # "deepseek-ai/DeepSeek-V2-Lite-Chat",
    ]
    
    # GPU 메모리에 따라 모델 선택
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"GPU Memory: {gpu_memory:.1f} GB")
        
        if gpu_memory < 8:
            print("⚠️ Low GPU memory. Using smaller models.")
            MODELS = [
                "meta-llama/Llama-3.2-1B-Instruct",
                "deepseek-ai/deepseek-llm-7b-chat",
            ]
    else:
        print("⚠️ No GPU detected. This may be slow.")
    
    # ==================== 평가 시작 ====================
    evaluator = EmpathyEvaluator()
    results = []
    
    for model_name in MODELS:
        try:
            # 모델 로드
            model, tokenizer = load_model(model_name, use_4bit=True)
            
            # 평가
            result = evaluate_model(
                model_name=model_name,
                model=model,
                tokenizer=tokenizer,
                evaluator=evaluator,
                prompts=TEST_PROMPTS,
            )
            results.append(result)
            
            # 메모리 정리
            del model, tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
        except Exception as e:
            print(f"\n❌ Error with {model_name}: {e}")
            continue
    
    # ==================== 모델 비교 ====================
    if len(results) > 1:
        compare_models(results, evaluator)
    
    print("\n✅ Evaluation complete!")


if __name__ == "__main__":
    main()

