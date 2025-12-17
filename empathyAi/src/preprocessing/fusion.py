import pandas as pd
import ast

# 1) 원본 데이터 로드
survey_df = pd.read_csv("oplea_open_data.csv")   # labeler_empathy 있는 파일
chat_df   = pd.read_csv("open_data_2.csv")       # all_chat_by_order 있는 파일

# 2) labeler_empathy 파싱 (문자열 -> 리스트[int])
def parse_empathy_list(s):
    try:
        return ast.literal_eval(s)
    except Exception:
        return None

survey_df["empathy_list"] = survey_df["labeler_empathy"].apply(parse_empathy_list)

# 3) doc_id 기준으로 merge (공통 doc_id만 사용)
merged = pd.merge(
    survey_df[["doc_id", "total_sent", "empathy_list"]],
    chat_df[["doc_id", "total_sent", "all_chat_by_order"]],
    on="doc_id",
    how="inner",
    suffixes=("_label", "_chat")
)

# 4) all_chat_by_order 한 줄씩 파싱해서 utterance 리스트로 변환
def parse_all_chat_by_order(s):
    if not isinstance(s, str):
        return None
    
    utterances = []
    lines = [line for line in s.split("\n") if line.strip()]  # 빈 줄 제거

    for line in lines:
        # 끝에 붙은 "]," 같은 거 정리
        inner = line.strip().strip(",")
        if inner.startswith("[") and inner.endswith("]"):
            inner = inner[1:-1].strip()
        
        # 앞에서부터 콤마 4개까지만 split → 5조각
        parts = inner.split(",", 4)
        if len(parts) < 5:
            # 형식 이상하면 그냥 스킵
            continue
        
        role_raw, name_raw, turn_raw, pause_raw, text_raw = parts

        role = role_raw.strip().strip("'").strip('"')
        name = name_raw.strip().strip("'").strip('"')
        try:
            turn_id = int(turn_raw.strip())
        except ValueError:
            # turn 파싱 안되면 스킵
            continue
        
        try:
            is_pause = int(pause_raw.strip())
        except ValueError:
            is_pause = 0
        
        text = text_raw.strip()
        
        utterances.append({
            "role": role,               # "user" or "persona"
            "name": name,
            "turn_id": turn_id,
            "is_pause": is_pause,
            "text": text,
        })
    
    return utterances

merged["utterances"] = merged["all_chat_by_order"].apply(parse_all_chat_by_order)

# 5) 문장 수가 안 맞는 doc은 버리기
valid_rows = []
for _, row in merged.iterrows():
    utts = row["utterances"]
    emps = row["empathy_list"]
    if utts is None or emps is None:
        continue
    
    # '문장 수 == empathy 라벨 수 == total_sent' 인 샘플만 사용
    if len(utts) == len(emps) == int(row["total_sent_label"]):
        valid_rows.append(row)

valid_df = pd.DataFrame(valid_rows)

print("정렬이 잘 맞는 doc_id 개수:", len(valid_df))

# 6) 각 utterance에 empathy 붙이고, turn 단위로 aggregate
turn_level_rows = []

for _, row in valid_df.iterrows():
    doc_id = row["doc_id"]
    utterances = row["utterances"]
    empathy_list = row["empathy_list"]
    
    # 각 발화에 empathy 라벨 붙이기
    for i, utt in enumerate(utterances):
        utt["empathy_label"] = empathy_list[i]
    
    # turn_id 기준으로 묶기
    turns = {}
    for utt in utterances:
        t = utt["turn_id"]
        turns.setdefault(t, []).append(utt)
    
    # turn별로 user / persona 텍스트와 공감라벨 aggregate
    for turn_id, utts in turns.items():
        user_utts = [u for u in utts if u["role"] == "user" and u["is_pause"] == 0]
        persona_utts = [u for u in utts if u["role"] == "persona" and u["is_pause"] == 0]

        # 둘 다 텍스트가 하나도 없으면 스킵
        if len(user_utts) == 0 and len(persona_utts) == 0:
            continue

        user_text_in_turn = " ".join(u["text"] for u in user_utts)
        persona_text_in_turn = " ".join(u["text"] for u in persona_utts)

        n_user_sents = len(user_utts)
        n_persona_sents = len(persona_utts)

        # 📌 공감 라벨은 "페르소나 발화" 기준으로 집계 (추천)
        persona_emps = [u["empathy_label"] for u in persona_utts]
        if len(persona_emps) == 0:
            # 이 턴에 페르소나 발화가 없으면 건너뛰거나, 필요하면 None으로 둘 수 있음
            continue

        # 방법1: 평균 후 반올림 (continuous 느낌)
        empathy_label = int(round(sum(persona_emps) / len(persona_emps)))
        # 방법2 (선택): empathy_label = max(persona_emps)

        turn_level_rows.append({
            "doc_id": doc_id,
            "turn_id": turn_id,
            "user_text_in_turn": user_text_in_turn,
            "persona_text_in_turn": persona_text_in_turn,
            "empathy_label": empathy_label,
            "n_user_sents": n_user_sents,
            "n_persona_sents": n_persona_sents,
        })

turn_df = pd.DataFrame(turn_level_rows)
turn_df = turn_df.sort_values(["doc_id", "turn_id"]).reset_index(drop=True)

# 7) CSV로 저장
turn_df.to_csv("opela_turn_level_empathy.csv", index=False)
print("저장 완료: opela_turn_level_empathy.csv")
