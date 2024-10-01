from datetime import datetime, timedelta, time
from geopy.distance import geodesic
import random
import pandas as pd
import joblib
import json
from datetime import datetime, timedelta, time
from geopy.distance import geodesic
import random
from sklearn.preprocessing import MinMaxScaler
from pycaret.regression import predict_model
from restaurants_recomm import restaurants_recomm
from cafe_recomm import cafe_recomm
from accom_recom import rank_accommodation
from trip_recom_realll import combined_recommendation
from course import (
    calculate_distance,
    get_coordinates,
    get_place_name,
    is_within_distance,
    select_restaurant,
    select_cafe,
    select_tourist_place,
    determine_start_time,
    generate_day_plan,
    generate_recommendation,
    force_add_restaurant,
    format_itinerary
)


'''
df_tr = pd.read_csv(r"C:\Users\김소민\Desktop\사문\kakao\df.csv")
df_ca =  pd.read_csv(r"C:\Users\김소민\Desktop\사문\kakao\restaurant_df.csv")
df_re = pd.read_csv(r"C:\Users\김소민\Desktop\사문\kakao\cafe_df.csv")
df_ac = pd.read_csv(r"C:\Users\김소민\Desktop\사문\kakao\숙박_처리완.csv")
sim_df = pd.read_csv('/content/similarity_df.csv')
master_visit_all = pd.read_csv('/content/master_visit_all.csv')
model_path = '/content/bayesian_regression.pkl'


#restaurant recomm
rest_survey = {
    "restaurant": [
        "로컬 맛집",
        "뷰가 좋은"
    ],
    "requiredRestText": "삼계탕",
    "cafe": [
        "가성비"
    ]
}

acc_prefer = {"accomodation": [
    "주차시설",
    "20평 ~ 10평",
    "조리 가능"
],
"requiredAccomText": '',
"accompriority": "좋은 품질"}

user_features = {
    'GENDER': [1],
    'AGE_GRP': [20],
    'TRAVEL_STYL_1': [2],
    'TRAVEL_STYL_2': [2],
    'TRAVEL_STYL_3': [2],
    'TRAVEL_STYL_4': [2]
}

input_order = [2, 4, 3, 1, 5]
user_prefer = ['역사유적지']

user_trip_days = 3  # 2박 3일
user_difficulty = [3, 4, 2]  # 각 날짜별 난이도
user_openness = 2  # 개방도 (1~5)
start_time = '오전'  # 여행 시작 시간 (오전 9시)
'''

def main(user_prefer,rest_survey, df_re,df_ca,df_ac,input_order, sim_df, df_tr, model_path, master_visit_all, user_features, user_trip_days, user_difficult):
  rest_df = restaurants_recomm(df_re, rest_survey)
  cafe_df = cafe_recomm(rest_survey, df_ca)
  acco_df = rank_accommodation(acc_prefer,df_ac)
  end_time = '22:00:00'
  max_travel_distance = 10
  max_daily_places = 4 
  
  trip_df = combined_recommendation(input_order, sim_df, df_tr, model_path, master_visit_all, user_prefer, user_features)
  recommendation_result = generate_recommendation(rest_df, cafe_df, acco_df, trip_df, user_trip_days, user_difficulty, start_time_option)
  return recommendation_result

