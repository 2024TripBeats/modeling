import pandas as pd
from sklearn.preprocessing import MinMaxScaler

#  user_preferences: 선호 순서의 장소 이름 리스트
def recommend_places(similarity_df, user_preferences):
    # 가중치 정의
    weights = [1.0, 0.8, 0.5, 0.1, 0.05]
    score_dict = {place: weights[i] for i, place in enumerate(user_preferences)}

    # 각 장소의 총 점수를 계산
    total_scores = similarity_df.apply(lambda row: sum(score_dict.get(col, 0) * row[col] for col in user_preferences), axis=1)

    # Min-Max 스케일링
    scaler = MinMaxScaler()
    total_scores_scaled = scaler.fit_transform(total_scores.values.reshape(-1, 1)).flatten()
    
    # 스케일링된 스코어와 장소를 딕셔너리로 묶기
    recommendations_dict = dict(zip(total_scores.index, total_scores_scaled))
    
    # 스케일링된 점수에 따라 내림차순으로 정렬
    recommendations_dict = dict(sorted(recommendations_dict.items(), key=lambda item: item[1], reverse=True))
    
    return recommendations_dict
