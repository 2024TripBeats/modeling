import pandas as pd

# 음악-여행지 어울림 점수와 음악-시간대 어울림 점수 파일 불러오기
travle_score = pd.read_csv('/root/TripBeats_modeling-repo/music/output/KoSimCSE-roberta/standardized_results.csv')
time_score = pd.read_csv('/root/TripBeats_modeling-repo/music/pipeline/data/merged_data_updated2.csv')

# 시간대 점수 딕셔너리 생성
time_score_dict = time_score.set_index('minjung_id').to_dict('index')

# 음악-여행지 어울림 점수와 음악-시간대 어울림 점수 결합
morning_df = pd.DataFrame(index=travle_score['Unnamed: 0'], columns=travle_score.columns.drop('Unnamed: 0'))
morning_df.index.name = 'placeId' 

afternoon_df = pd.DataFrame(index=travle_score['Unnamed: 0'], columns=travle_score.columns.drop('Unnamed: 0'))
afternoon_df.index.name = 'placeId' 

night_df = pd.DataFrame(index=travle_score['Unnamed: 0'], columns=travle_score.columns.drop('Unnamed: 0'))
night_df.index.name = 'placeId' 

# 오전 점수 계산
for i, row in travle_score.iterrows():
    for key, nested_dict in row.items():
        if key in time_score_dict:
            morning_value = time_score_dict[key]['morning']
            music_scores_value = nested_dict
            combined_value = morning_value * 0.3 + music_scores_value # 음악-여행지 어울림 점수와 음악-시간대 어울림 점수 결합 (가중평균)
            morning_df.at[travle_score.at[i, 'Unnamed: 0'], key] = combined_value

# 오후 점수 계산
for i, row in travle_score.iterrows():
    for key, nested_dict in row.items():
        if key in time_score_dict:
            music_scores_value = nested_dict
            combined_value = music_scores_value # 오후는 시간대 점수 부여 x 
            afternoon_df.at[travle_score.at[i, 'Unnamed: 0'], key] = combined_value

# 밤 점수 계산
for i, row in travle_score.iterrows():
    for key, nested_dict in row.items():
        if key in time_score_dict:
            night_value = time_score_dict[key]['night']
            music_scores_value = nested_dict
            combined_value = night_value * 0.3 + music_scores_value # 음악-여행지 어울림 점수와 음악-시간대 어울림 점수 결합 (가중평균)
            night_df.at[travle_score.at[i, 'Unnamed: 0'], key] = combined_value

# 오전 점수 저장
morning_df.to_csv('/root/TripBeats_modeling-repo/music/pipeline/data/morning_score.csv', index=True)

# 오후 점수 저장
afternoon_df.to_csv('/root/TripBeats_modeling-repo/music/pipeline/data/afternoon_score.csv', index=True) 

# 밤 점수 저장
night_df.to_csv('/root/TripBeats_modeling-repo/music/pipeline/data/night_score.csv', index=True)
