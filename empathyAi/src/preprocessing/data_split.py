import json
import random
from collections import defaultdict

INPUT_JSONL = "opela_empathy_ft_sft.jsonl"
TRAIN_JSONL = "opela_empathy_train.jsonl"
VAL_JSONL = "opela_empathy_val.jsonl"

random.seed(42)

# 1) 전체 샘플 읽어서 라벨(0~4)별로 묶기
label_to_samples = defaultdict(list)

with open(INPUT_JSONL, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        obj = json.loads(line)

        # 마지막 assistant 메시지의 content(=JSON 문자열)에서 empathy_label 추출
        label = None
        for m in reversed(obj.get("messages", [])):
            if m.get("role") == "assistant":
                try:
                    content = m.get("content", "")
                    label_json = json.loads(content)  # e.g. {"empathy_label": 3}
                    label = str(label_json["empathy_label"])  # "0"~"4"
                except Exception:
                    label = None
                break

        if label is None:
            continue

        label_to_samples[label].append(obj)

# 라벨 분포 출력
print("=== Label distribution (total) ===")
for lbl in sorted(label_to_samples.keys(), key=lambda x: int(x)):
    print(f"Label {lbl}: {len(label_to_samples[lbl])} samples")

# 2) 각 라벨별로 9:1로 나눠서 합치기 (stratified split)
train_samples = []
val_samples = []

for lbl, lst in label_to_samples.items():
    random.shuffle(lst)
    split_idx = int(len(lst) * 0.9)

    # 라벨이 너무 적어서 val이 0이 되는 걸 최소한 방지하고 싶으면 아래 2줄을 옵션으로 켜세요.
    # if len(lst) >= 2 and split_idx == len(lst):
    #     split_idx = len(lst) - 1

    train_samples.extend(lst[:split_idx])
    val_samples.extend(lst[split_idx:])

print("\n=== Split sizes ===")
print("Total train:", len(train_samples))
print("Total val:", len(val_samples))

# 3) 다시 한 번 전체 셔플 (섞어서 순서 랜덤)
random.shuffle(train_samples)
random.shuffle(val_samples)

# 4) JSONL 저장
with open(TRAIN_JSONL, "w", encoding="utf-8") as f:
    for s in train_samples:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")

with open(VAL_JSONL, "w", encoding="utf-8") as f:
    for s in val_samples:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")

print("\n✅ Stratified split done. Saved to:")
print("  -", TRAIN_JSONL)
print("  -", VAL_JSONL)

# (선택) 저장된 파일 라벨 분포도 다시 확인
def count_labels(path: str):
    counts = defaultdict(int)
    with open(path, "r", encoding="utf-8") as rf:
        for line in rf:
            obj = json.loads(line)
            label = None
            for m in reversed(obj.get("messages", [])):
                if m.get("role") == "assistant":
                    try:
                        label_json = json.loads(m.get("content", ""))
                        label = str(label_json["empathy_label"])
                    except Exception:
                        label = None
                    break
            if label is not None:
                counts[label] += 1
    return counts

train_counts = count_labels(TRAIN_JSONL)
val_counts = count_labels(VAL_JSONL)

print("\n=== Label distribution (train) ===")
for lbl in sorted(train_counts.keys(), key=lambda x: int(x)):
    print(f"Label {lbl}: {train_counts[lbl]}")

print("\n=== Label distribution (val) ===")
for lbl in sorted(val_counts.keys(), key=lambda x: int(x)):
    print(f"Label {lbl}: {val_counts[lbl]}")
