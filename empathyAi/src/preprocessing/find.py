import pandas as pd

# 파일 로드 (경로는 네가 사용 중인 환경에 맞게 수정!)
df1 = pd.read_csv("oplea_open_data.csv")
df2 = pd.read_csv("open_data_2.csv")

# 각 파일에서 doc_id 컬럼만 뽑기
doc_ids_1 = set(df1["doc_id"].astype(str).unique())
doc_ids_2 = set(df2["doc_id"].astype(str).unique())

# 교집합 구하기
common_doc_ids = sorted(list(doc_ids_1.intersection(doc_ids_2)))

print("총 공통 doc_id 개수:", len(common_doc_ids))
print("일부 샘플:", common_doc_ids[:10])

# 필요하면 파일로 저장
#pd.DataFrame({"doc_id": common_doc_ids}).to_csv("common_doc_ids.csv", index=False)
