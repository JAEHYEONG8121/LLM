import pandas as pd
import json

INPUT_CSV = "opela_turn_level_empathy.csv"   # 고우니가 만든 턴 단위 CSV
OUTPUT_JSONL = "opela_empathy_ft_v2.jsonl"   # 새로 만들 JSONL 파일 이름

df = pd.read_csv(INPUT_CSV)

system_prompt = (
    "You are an empathy classifier. "
    "Read the following short dialogue turn between a USER and a PERSONA, "
    "then answer ONLY with a single integer in {0,1,2,3,4} that represents "
    "the empathy level of the PERSONA's response."
)

with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
    for _, row in df.iterrows():
        # user / persona 턴 텍스트 안전하게 가져오기 (NaN 방지)
        user_text = str(row.get("user_text_in_turn", "") or "")
        persona_text = str(row.get("persona_text_in_turn", "") or "")
        label = int(row["empathy_label"])

        # 입력 텍스트: USER / PERSONA 구분해서 한 덩어리로
        turn_text = f"USER: {user_text}\nPERSONA: {persona_text}"

        record = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": turn_text},
                {"role": "assistant", "content": str(label)},
            ]
        }

        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print("✅ 변환 완료! 출력 파일:", OUTPUT_JSONL)
