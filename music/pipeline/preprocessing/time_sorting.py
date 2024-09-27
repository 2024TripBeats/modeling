import pandas as pd

# CSV 파일을 읽어옵니다.
df = pd.read_csv('/root/TripBeats_modeling-repo/music/pipeline/preprocessing/combined_results.csv')

# 인덱스를 문자열로 변환합니다.
df.index = df.index.astype(str)

# 값을 내림차순으로 정렬합니다.
df2 = df.iloc[20, :].apply(pd.to_numeric, errors='coerce').dropna().sort_values(ascending=False)

# 첫 행의 값을 프린트합니다.
print(df2.head(20))
