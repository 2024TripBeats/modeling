import pandas as pd
import numpy as np
from geopy.distance import geodesic
import json
from datetime import datetime, timedelta

# 사용자 조건 설정
user_trip_days = 3  # 2박 3일
user_difficulty = [5, 2, 3]  # 각 날짜별 빡센 정도
user_openness = 1  # 개방도
#df: place.csv
# 유사도 딕셔너리 생성: 윤이 코드
similarity_dict = create_similarity_dict(similarity_df, user_preferences)

# 여행 일정 생성 함수
def generate_itinerary(df, similarity_dict, user_difficulty, user_openness, user_days):
    difficulty_map = {
    1: 2,  # 자연관광지
    2: 2,  # 역사
    3: 1,  # 문화시설
    4: 3,  # 상업지구
    5: 5,  # 레저, 스포츠 관련 시설
    6: 5,  # 놀이공원
    7: 2,  # 산책로
    8: 4   # 지역축제
    }

    recommendations = []
    used_lower_similarity_place = False  # 사용자의 개방도에 따른 유사도가 낮은 장소 추천 여부
    
    for day in range(1, user_days + 1):
        day_plan = {
            "dayNumber": day,
            "candidates": []
        }
        
        max_difficulty = user_difficulty[day - 1] * 2 + 2
        total_difficulty = 0
        
        for _ in range(2):  # 각 날에 대해 두 개의 후보 경로 생성
            selected_places = []
            categories = set()
            total_difficulty = 0
            
            # 시작 지점 선택
            start_place = df.sample().iloc[0]
            selected_places.append(start_place)
            total_difficulty += difficulty_map[start_place['VISIT_AREA_TYPE_CD']]
            categories.add(start_place['VISIT_AREA_TYPE_CD'])
            
            travel_segments = []
            
            # 탐욕 알고리즘을 사용하여 경로 생성
            for _ in range(4):
                best_place = None
                best_score = float('inf')
                
                for _, place in df.iterrows():
                    if place['VISIT_AREA_NM'] in [p['VISIT_AREA_NM'] for p in selected_places]:
                        continue
                    distance = geodesic((selected_places[-1]['lat'], selected_places[-1]['lng']), (place['lat'], place['lng'])).km
                    difficulty = difficulty_map[place['VISIT_AREA_TYPE_CD']]
                    if total_difficulty + difficulty > max_difficulty:
                        continue
                    similarity = similarity_dict.get(place['VISIT_AREA_NM'], 0)
                    
                    if not used_lower_similarity_place and similarity < user_openness:
                        used_lower_similarity_place = True
                    else:
                        score = distance + (1 - similarity)
                        if score < best_score:
                            best_score = score
                            best_place = place
                
                if best_place is None:
                    break
                
                selected_places.append(best_place)
                total_difficulty += difficulty_map[best_place['VISIT_AREA_TYPE_CD']]
                categories.add(best_place['VISIT_AREA_TYPE_CD'])
                
                if len(selected_places) > 1:
                    distance = geodesic((selected_places[-2]['lat'], selected_places[-2]['lng']), (selected_places[-1]['lat'], selected_places[-1]['lng'])).km
                    travel_segments.append({"distance": distance})
            
            itinerary = [{"placeId": str(df[df['VISIT_AREA_NM'] == place['VISIT_AREA_NM']].index[0]), "placeName": place['VISIT_AREA_NM'], "duration": 120} for place in selected_places]
            
            day_plan["candidates"].append({
                "itinerary": itinerary,
                "travelSegments": travel_segments
            })
        
        recommendations.append(day_plan)
    
    return {"recommendations": recommendations}

# 여행 일정 생성
itinerary = generate_itinerary(df, similarity_dict, user_difficulty, user_openness, user_trip_days)

