

from datetime import datetime, timedelta, time
from geopy.distance import geodesic
import random
import pandas as pd

#데이터 프레임 
# 파일 경로
file_path = r"C:\Users\김소민\Desktop\사문\kakao\df.csv"
trip_df = pd.read_csv(file_path)

df_ca =  pd.read_csv(r"C:\Users\김소민\Desktop\사문\kakao\restaurant_df.csv")
df_re = pd.read_csv(r"C:\Users\김소민\Desktop\사문\kakao\cafe_df.csv")
df_ac = pd.read_csv(r"C:\Users\김소민\Desktop\사문\kakao\숙박_처리완.csv")


#input 파라미터
user_trip_days = 3  # 2박 3일
user_difficulty = [3, 4, 2]  # 각 날짜별 난이도
user_openness = 2  # 개방도 (1~5)
start_time = '09:00:00'  # 여행 시작 시간 (오전 9시)
end_time = '22:00:00'  # 여행 종료 제한 시간 (밤 10시)
max_travel_distance = 10  # 여행지 간 최대 거리 (KM)
max_daily_places = 4  # 하루 최대 여행지 수



#코드 
def calculate_distance(place1, place2):
    coords_1 = get_coordinates(place1)
    coords_2 = get_coordinates(place2)
    if coords_1 is None or coords_2 is None:
        return float('inf')
    return geodesic(coords_1, coords_2).km

def get_coordinates(place):
    if '위도' in place and '경도' in place and pd.notnull(place['위도']) and pd.notnull(place['경도']):
        return (place['위도'], place['경도'])
    elif 'lat' in place and 'lon' in place and pd.notnull(place['lat']) and pd.notnull(place['lon']):
        return (place['lat'], place['lon'])
    elif 'X_COORD' in place and 'Y_COORD' in place and pd.notnull(place['X_COORD']) and pd.notnull(place['Y_COORD']):
        return (place['Y_COORD'], place['X_COORD'])
    else:
        return None

def get_place_name(place):
    if '명칭' in place:
        return place['명칭']
    elif '음식점 이름' in place:
        return place['음식점 이름']
    elif 'tourist_x' in place:
        return place['tourist_x']
    return None

def is_within_distance(last_place, new_place, max_distance):
    distance = calculate_distance(last_place, new_place)
    return distance <= max_distance

def select_restaurant(restaurant_df, last_place, visited_places, max_distance):
    for _, restaurant in restaurant_df.iterrows():
        if get_coordinates(restaurant) is None:
            continue
        if restaurant['id'] not in visited_places and is_within_distance(last_place, restaurant, max_distance):
            return restaurant
    return None

def select_cafe(cafe_df, last_place, visited_places, max_distance):
    for _, cafe in cafe_df.iterrows():
        if get_coordinates(cafe) is None:
            continue
        if cafe['id'] not in visited_places and is_within_distance(last_place, cafe, max_distance):
            return cafe
    return None

def select_tourist_place(trip_df, last_place, visited_places, max_distance, user_difficulty, total_difficulty, categories):
    for _, place in trip_df.iterrows():
        if get_coordinates(place) is None:
            continue
        if place['tourist_id'] not in visited_places and is_within_distance(last_place, place, max_distance):
            difficulty = difficulty_map.get(place['category'], 0)
            if total_difficulty + difficulty <= user_difficulty and place['category'] not in categories:
                return place, difficulty
    return None, 0

from datetime import datetime, timedelta, time

# 첫째날 시작 시간 결정 함수
def determine_start_time(first_day_start):
    if first_day_start == '오전':
        return datetime.strptime("09:00:00", "%H:%M:%S")
    elif first_day_start == '오후':
        return datetime.strptime("14:00:00", "%H:%M:%S")
    elif first_day_start == '밤':
        return datetime.strptime("22:00:00", "%H:%M:%S")

# 하루 일정 생성 함수 (첫째날 특수 처리 포함)
# 하루 일정 생성 함수 (첫째날 특수 처리 포함)
def generate_day_plan(restaurant_df, cafe_df, trip_df, start_datetime, end_time, user_difficulty, visited_places, cafes_added, current_accommodation, max_travel_distance, max_daily_places, is_first_day=False, first_day_start='오전'):
    selected_places = []
    total_difficulty = 0
    current_time = start_datetime
    last_place_type = None
    tourist_places_added = 0
    categories = set()

    # 두 번의 식사 타임 플래그
    lunch_added = False
    dinner_added = False

    # 첫째날 밤인 경우 숙소 하나만 추천
    if is_first_day and first_day_start == '밤':
        selected_places.append({
            'place': current_accommodation,
            'type': '숙소',
            'duration': 0
        })
        visited_places.add(current_accommodation['id'])
        return selected_places, cafes_added

    # 숙소 추가
    selected_places.append({
        'place': current_accommodation,
        'type': '숙소',
        'duration': 0
    })
    last_place = current_accommodation
    visited_places.add(current_accommodation['id'])
    last_place_type = '숙소'
    current_time += timedelta(hours=1)

    while len(selected_places) < max_daily_places and current_time < datetime.combine(current_time.date(), datetime.strptime(end_time, "%H:%M:%S").time()):
        # 11:00-13:00에 점심 식당 추천
        if 11 <= current_time.hour < 13 and not lunch_added:
            restaurant = select_restaurant(restaurant_df, last_place, visited_places, max_travel_distance)
            if restaurant is not None:
                selected_places.append({
                    'place': restaurant,
                    'type': '식당',
                    'duration': 1.5
                })
                visited_places.add(restaurant['id'])
                last_place = restaurant
                last_place_type = '식당'
                current_time += timedelta(hours=1.5)
                lunch_added = True  # 점심 추가 완료 플래그
                continue

        # 17:00-20:00에 저녁 식당 추천
        if 17 <= current_time.hour < 20 and not dinner_added:
            restaurant = select_restaurant(restaurant_df, last_place, visited_places, max_travel_distance)
            if restaurant is not None:
                selected_places.append({
                    'place': restaurant,
                    'type': '식당',
                    'duration': 1.5
                })
                visited_places.add(restaurant['id'])
                last_place = restaurant
                last_place_type = '식당'
                current_time += timedelta(hours=1.5)
                dinner_added = True  # 저녁 추가 완료 플래그
                continue

        # 관광지 추가 (거리 및 시간 준수)
        if tourist_places_added < 4:
            tourist_place, difficulty = select_tourist_place(trip_df, last_place, visited_places, max_travel_distance, user_difficulty, total_difficulty, categories)
            if tourist_place is not None:
                travel_time = timedelta(hours=tourist_place['평균 소요 시간'])
                if current_time + travel_time <= datetime.combine(current_time.date(), datetime.strptime(end_time, "%H:%M:%S").time()) and calculate_distance(last_place, tourist_place) <= max_travel_distance:
                    selected_places.append({
                        'place': tourist_place,
                        'type': tourist_place['category'],
                        'duration': tourist_place['평균 소요 시간']
                    })
                    visited_places.add(tourist_place['tourist_id'])
                    last_place = tourist_place
                    last_place_type = '관광지'
                    current_time += travel_time
                    total_difficulty += difficulty
                    tourist_places_added += 1
                    categories.add(tourist_place['category'])
                    continue

        # 카페 추가
        if cafes_added < 2 and last_place_type != '식당' and random.random() < 0.5:
            cafe = select_cafe(cafe_df, last_place, visited_places, max_travel_distance)
            if cafe is not None:
                selected_places.append({
                    'place': cafe,
                    'type': '카페',
                    'duration': 1.5
                })
                visited_places.add(cafe['id'])
                last_place = cafe
                last_place_type = '카페'
                current_time += timedelta(hours=1.5)
                cafes_added += 1
                continue

        # 더 이상 추가할 장소가 없으면 반복 종료
        break

    # 만약 점심 또는 저녁이 추천되지 않았을 경우 강제로 추가
    if not lunch_added and current_time < datetime.combine(current_time.date(), time(13, 0)):
        restaurant = select_restaurant(restaurant_df, last_place, visited_places, max_travel_distance)
        if restaurant is not None:
            selected_places.append({
                'place': restaurant,
                'type': '식당',
                'duration': 1.5
            })
            visited_places.add(restaurant['id'])
            current_time += timedelta(hours=1.5)
    
    if not dinner_added and current_time < datetime.combine(current_time.date(), time(20, 0)):
        restaurant = select_restaurant(restaurant_df, last_place, visited_places, max_travel_distance)
        if restaurant is not None:
            selected_places.append({
                'place': restaurant,
                'type': '식당',
                'duration': 1.5
            })
            visited_places.add(restaurant['id'])
            current_time += timedelta(hours=1.5)

    # 마지막 숙소 추가
    selected_places.append({
        'place': current_accommodation,
        'type': '숙소',
        'duration': 0
    })

    return selected_places, cafes_added

# 전체 추천 일정 생성
def generate_recommendation(restaurant_df, cafe_df, accommodation_df, trip_df, user_trip_days, user_difficulty, user_openness, first_day_start):
    visited_places = set()
    candidates = []

    for candidate_num in range(2):
        itinerary = []
        cafes_added = 0

        # 데이터프레임 셔플
        restaurant_df = restaurant_df.sample(frac=1).reset_index(drop=True)
        cafe_df = cafe_df.sample(frac=1).reset_index(drop=True)
        trip_df = trip_df.sample(frac=1).reset_index(drop=True)

        current_accommodation = accommodation_df.iloc[candidate_num % len(accommodation_df)]

        for day in range(user_trip_days):
            if day == 0:  # 첫째날 처리
                start_datetime = determine_start_time(first_day_start)
                if first_day_start == '밤':
                    day_plan, cafes_added = generate_day_plan(restaurant_df, cafe_df, trip_df, start_datetime, end_time, user_difficulty[day], visited_places, cafes_added, current_accommodation, max_travel_distance, max_daily_places, is_first_day=True, first_day_start=first_day_start)
                else:
                    day_plan, cafes_added = generate_day_plan(restaurant_df, cafe_df, trip_df, start_datetime, end_time, user_difficulty[day], visited_places, cafes_added, current_accommodation, max_travel_distance, max_daily_places, is_first_day=True)
            else:  # 둘째날 이후 처리
                start_datetime = datetime.strptime("09:00:00", "%H:%M:%S")  # 고정된 9시 시작 시간
                day_plan, cafes_added = generate_day_plan(restaurant_df, cafe_df, trip_df, start_datetime, end_time, user_difficulty[day], visited_places, cafes_added, current_accommodation, max_travel_distance, max_daily_places)

            itinerary.append(day_plan)

        formatted_itinerary = format_itinerary(itinerary)
        candidates.append({"candidates": candidate_num + 1, "itinerary": formatted_itinerary})

    return {"recommendations": candidates}


#화룡 예시]
recommendation_result = generate_recommendation(df_re, df_ca, df_ac, trip_df, user_trip_days, user_difficulty)

# 결과 출력
import json
print(json.dumps(recommendation_result, indent=4, ensure_ascii=False)

