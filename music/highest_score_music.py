import pandas as pd

# CSV 파일 읽기
df = pd.read_csv('/root/TripBeats_modeling-repo/music/output/standardized_results_gte-Qwen2-1.5B-instruct.csv', index_col=0)

# 각 행에서 가장 높은 값을 가진 열 이름을 뽑아내기
max_columns = df.idxmax(axis=1)

# 결과를 데이터프레임으로 저장
result_df = pd.DataFrame({
    'travel': df.index,
    'Highest_Music': max_columns
})

# 결과 출력
print(result_df)

# 결과를 CSV 파일로 저장 (선택 사항)
result_df.to_csv('/root/TripBeats_modeling-repo/music/output/highest_music.csv')