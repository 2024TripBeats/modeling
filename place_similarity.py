import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def recommend_places(similarity_df, user_preference_numbers):
    # 장소와 번호의 매핑 정의
    place_to_number = {
        '안흥지 애련정': 1,
        'KT&G상상마당 홍대': 2,
        '명동난타극장': 3,
        '백운계곡관광지': 4,
        '소래역사관': 5
    }

    number_to_place = {v: k for k, v in place_to_number.items()}

    # 숫자 리스트를 장소 이름 리스트로 변환
    user_preferences = [number_to_place[num] for num in user_preference_numbers]
    
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
