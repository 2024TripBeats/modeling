import pandas as pd

# CSV 파일 읽기
df = pd.read_csv('/root/TripBeats_modeling-repo/music/output/KoSimCSE-roberta/standardized_results.csv', index_col=0)

# 각 행에서 가장 높은 값을 가진 열 이름을 뽑아내기
max_columns = df.idxmax(axis=1)

# 결과를 데이터프레임으로 저장
result_df = pd.DataFrame({
    'travel': df.index,
    'Highest_Music': max_columns
})

# result_df index 초기화
result_df.reset_index(drop=True, inplace=True)

# 'tourist' 열을 추가할 CSV 파일 읽기
tourist_df = pd.read_csv('/root/TripBeats_modeling-repo/music/data/visitjeju_tourist_v3.csv', usecols=['tourist'])

# 기존 result_df에 'tourist' 열을 concat
result_df = pd.concat([result_df, tourist_df['tourist']], axis=1)


# 결과를 CSV 파일로 저장 (선택 사항)
result_df.to_csv('/root/TripBeats_modeling-repo/music/pipeline/preprocessing/music_list.csv')