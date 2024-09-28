import pandas as pd
import numpy as np
from step1_genre_selection import process_genre_selection, filter_data_by_genre
from step2_style_selection import process_style_selection, intersection_of_results
from step3_music_recomendation import categorize_places_by_time, get_music_scores, set_top_music, add_song_details, reorder_place_keys

"""
여기 변경
"""
def main_pipeline(genre_selection, genre_openess, style_selection, style_openess, trip_data, music_hashtags_data, csv_paths, music_embeddings, user_preferences_embeddings):
    """
    여기 변경
    """
    # Step 1: 장르 선택
    final_genre_selection = process_genre_selection(genre_selection, genre_openess)
    genre_filtered_data = filter_data_by_genre(final_genre_selection, music_hashtags_data)
    
    # Step 2: 취향 선택
    style_filtered_data  = process_style_selection(style_selection, style_openess, music_hashtags_data, music_embeddings, user_preferences_embeddings)
    intersection_data = intersection_of_results(style_filtered_data, genre_filtered_data)

    # Step 3: 여행지 방문 시간대를 고려한 음악 추천
    categorized_trip_data = categorize_places_by_time(trip_data)
    trip_data_with_music_scores = get_music_scores(categorized_trip_data, csv_paths)
    trip_data_with_top_music = set_top_music(trip_data_with_music_scores, intersection_data)
    trip_data_with_song_details = add_song_details(trip_data_with_top_music, music_hashtags_data)
    trip_data_with_ordered_keys = reorder_place_keys(trip_data_with_song_details)
    
    return trip_data_with_ordered_keys

if __name__ == "__main__":
    # Example usage
    genre_selection = ['발라드', 'POP']
    genre_openess = 5
    style_selection = ['운동']
    style_openess = 1
    trip_data = [
        {
            "recommendations": [
                {
                    "candidates": 1,
                    "itinerary": [
                        {
                            "dayNumber": 1,
                            "places": [
                                {
                                    "placeId": "CONT_000000000500349",
                                    "placeName": "헬로키티아일랜드",
                                    "category": "관광지",
                                    "duration": 120,
                                    "order": 1,
                                    "price": 10000
                                },
                                {
                                    "placeId": "CONT_000000000500477",
                                    "placeName": "천지연폭포",
                                    "category": "역사 유적지",
                                    "duration": 120,
                                    "order": 2,
                                    "price": 3000
                                }
                            ],
                            "travelSegments": [
                                {
                                    "distance": 3.2
                                }
                            ]
                        },
                        {
                            "dayNumber": 2,
                            "places": [
                                {
                                    "placeId": "CONT_000000000500477",
                                    "placeName": "성산일출봉",
                                    "category": "전통 마을",
                                    "duration": 120,
                                    "order": 1,
                                    "price": 0
                                },
                                {
                                    "placeId": "CONT_000000000500477",
                                    "placeName": "거문오름",
                                    "category": "문화시설",
                                    "duration": 120,
                                    "order": 2,
                                    "price": 15000
                                }
                            ],
                            "travelSegments": [
                                {
                                    "distance": 4.7
                                }
                            ]
                        }
                    ]
                },
                {
                    "candidates": 2,
                    "itinerary": [
                        {
                            "dayNumber": 1,
                            "places": [
                                {
                                    "placeId": "CONT_000000000500477",
                                    "placeName": "Namsan Park",
                                    "category": "공원",
                                    "duration": 120,
                                    "order": 1,
                                    "price": 0
                                },
                                {
                                    "placeId": "CONT_000000000500477",
                                    "placeName": "Myeongdong Shopping Street",
                                    "category": "상업지구",
                                    "duration": 120,
                                    "order": 2,
                                    "price": 0
                                }
                            ],
                            "travelSegments": [
                                {
                                    "distance": 2.5
                                }
                            ]
                        },
                        {
                            "dayNumber": 2,
                            "places": [
                                {
                                    "placeId": "CONT_000000000500477",
                                    "placeName": "Insadong",
                                    "category": "전통 문화 거리",
                                    "duration": 120,
                                    "order": 1,
                                    "price": 0
                                },
                                {
                                    "placeId": "CONT_000000000500477",
                                    "placeName": "Cheonggyecheon Stream",
                                    "category": "산책로",
                                    "duration": 120,
                                    "order": 2,
                                    "price": 0
                                }
                            ],
                            "travelSegments": [
                                {
                                    "distance": 3.9
                                }
                            ]
                        },
                        {
                            "dayNumber": 3,
                            "places": [
                                {
                                    "placeId": "CONT_000000000500477",
                                    "placeName": "Hangang Park",
                                    "category": "공원",
                                    "duration": 120,
                                    "order": 1,
                                    "price": 0
                                },
                                {
                                    "placeId": "CONT_000000000500477",
                                    "placeName": "War Memorial of Korea",
                                    "category": "역사 유적지",
                                    "duration": 120,
                                    "order": 2,
                                    "price": 0
                                },
                                {
                                    "placeId": "CONT_000000000500477",
                                    "placeName": "National Museum of Korea",
                                    "category": "박물관",
                                    "duration": 120,
                                    "order": 3,
                                    "price": 3000
                                }
                            ],
                            "travelSegments": [
                                {
                                    "distance": 4.8
                                },
                                {
                                    "distance": 3.3
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]

    csv_paths = {
        '아침': '/root/tripbeats/music/pipeline/data/morning_score_id.csv',
        '오후': '/root/tripbeats/music/pipeline/data/afternoon_score_id.csv',
        '밤': '/root/tripbeats/music/pipeline/data/night_score_id.csv'
    }

    music_embeddings = np.load('/root/tripbeats/music/pipeline/data/music_embeddings.npy') 
    user_preferences_embeddings = np.load('/root/tripbeats/music/pipeline/data/average_embeddings.npy', allow_pickle=True)
    music_hashtags_data = pd.read_csv('/root/tripbeats/music/pipeline/data/music_recommendation_list.csv')

    """
    여기 변경
    """
    result = main_pipeline(genre_selection, genre_openess, style_selection, style_openess, trip_data, music_hashtags_data, csv_paths, music_embeddings, user_preferences_embeddings)
    print(result)
    """
    여기 변경
    """