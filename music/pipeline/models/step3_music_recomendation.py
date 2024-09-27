import pandas as pd
import re

def categorize_places_by_time(trip_data):
    for entry in trip_data:
        for recommendation in entry['recommendations']:
            for day in recommendation['itinerary']:
                places = day['places']
                
                # 식당 및 숙소는 음악 추천 제외
                for place in places:
                    if place['category'] in ['식당', '숙소']:
                        place['new_order'] = None
                    else:
                        place['new_order'] = place['order']
                
                # new_order가 None인 것을 제외하고 정렬, 그리고 new_order를 1부터 순서대로 다시 할당
                places.sort(key=lambda x: (x['new_order'] is None, x['new_order']))
                for i, place in enumerate(places):
                    if place['new_order'] is not None:
                        place['new_order'] = i + 1
                
                count = sum(1 for place in places if place['new_order'] is not None)
                
                # 여행지 개수에 따른 시간대 할당 및 music_bool 추가
                for place in places:
                    place['music_bool'] = place['new_order'] is not None  # 추가된 부분
                    place['placeId'] = place.get('placeId', None)  # 장소별 아이디 추가
                    if count == 1:
                        place['timeOfDay'] = '오후'
                    elif count == 2:
                        place['timeOfDay'] = '오후'
                    elif count == 3:
                        if place['new_order'] == 1:
                            place['timeOfDay'] = '아침'
                        elif place['new_order'] == 2:
                            place['timeOfDay'] = '오후'
                        elif place['new_order'] == 3:
                            place['timeOfDay'] = '밤'
                    elif count == 4:
                        if place['new_order'] == 1:
                            place['timeOfDay'] = '아침'
                        elif place['new_order'] == 4:
                            place['timeOfDay'] = '밤'
                        else:
                            place['timeOfDay'] = '오후'
                    elif count == 5:
                        if place['new_order'] == 1:
                            place['timeOfDay'] = '아침'
                        elif place['new_order'] == 5:
                            place['timeOfDay'] = '밤'
                        else:
                            place['timeOfDay'] = '오후'
    
    return trip_data

def get_music_scores(trip_data, csv_paths):
    # CSV 파일을 데이터 프레임으로 로드
    dfs = {time: pd.read_csv(path, index_col=0) for time, path in csv_paths.items()}
    
    # 여행지에 어울리는 음악 점수를 내뱉는 함수
    for entry in trip_data:
        for recommendation in entry['recommendations']:
            for day in recommendation['itinerary']:
                for place in day['places']:
                    if place['music_bool']:
                        place_id = place['placeId']
                        time_of_day = place['timeOfDay']
                        df = dfs.get(time_of_day)
                        if df is not None:
                            matched_row = None
                            for row_name in df.index:
                                # 행 이름에서 마지막 _숫자 부분을 제거
                                base_name = re.sub(r'_\d+$', '', row_name)
                                if base_name == place_id:
                                    matched_row = row_name
                                    break
                            
                            if matched_row:
                                place['music_scores'] = df.loc[matched_row].to_dict()
                            else:
                                place['music_scores'] = None  # 일치하는 행 이름이 없는 경우
                        else:
                            place['music_scores'] = None
                    else:
                        place['music_scores'] = None
    return trip_data

def set_top_music(trip_data, user_music_list):
    recommended_music = set()  # 이미 추천된 음악을 저장하는 집합

    # 유저가 좋아하는 음악 목록
    valid_music_ids = set(user_music_list['minjung_id'])

    for entry in trip_data:
        for recommendation in entry['recommendations']:
            for day in recommendation['itinerary']:
                for place in day['places']:
                    if place.get('music_scores'):
                        # 내림차순으로 정렬
                        sorted_music = sorted(place['music_scores'].items(), key=lambda x: x[1], reverse=True)
                        
                        # 유저가 좋아하는 음악 목록에 있는 음악 중에서 추천되지 않은 음악 중 가장 높은 점수를 가진 음악 선택
                        top_musicId = None
                        for musicId, score in sorted_music:
                            if musicId in valid_music_ids and musicId not in recommended_music:
                                top_musicId = musicId
                                recommended_music.add(musicId)
                                break
                        
                        place['top_musicId'] = top_musicId
                        # 음악 점수 삭제
                        del place['music_scores']
                    else:
                        place['top_musicId'] = None
                        if 'music_scores' in place:
                            del place['music_scores']
    return trip_data

def add_song_details(trip_data, music_hashtags_data):
    # minjung_id를 인덱스로 하는 딕셔너리 생성
    merged_data_dict = music_hashtags_data.set_index('minjung_id').to_dict('index')
    
    for entry in trip_data:
        for recommendation in entry['recommendations']:
            for day in recommendation['itinerary']:
                for place in day['places']:
                    top_music_id = place.get('top_musicId')
                    if top_music_id and top_music_id in merged_data_dict:
                        song_details = merged_data_dict[top_music_id]
                        place.update({
                            'song_title': song_details['song_title'],
                            'artist_name': song_details['artist_name'],
                            'spotify_id': song_details['spotify_id']
                        })
    
    return trip_data

def reorder_place_keys(trip_data):
    ordered_keys = ['placeName', 'order', 'category', 'placeId', 'new_order', 'timeOfDay', 'music_bool', 'top_musicId', 'song_title', 'artist_name', 'spotify_id', 'duration', 'price']
    
    for entry in trip_data:
        for recommendation in entry['recommendations']:
            for day in recommendation['itinerary']:
                for place in day['places']:
                    reordered_place = {key: place.get(key) for key in ordered_keys}
                    place.clear()
                    place.update(reordered_place)
    
    return trip_data