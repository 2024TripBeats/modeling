import numpy as np
import faiss
import pandas as pd
import time

# 총 연산 시간을 측정하기 위해 시작 시간 기록
start_time_total = time.time()

# 유저 취향 해시태그 사전
categories = {
    "기분전환": ["신나는비트", "활기찬리듬", "긍정에너지", "업비트댄스", "모닝커피"],
    "힐링": ["자연의소리", "따뜻한위로", "잔잔한멜로디", "마음의안정", "평화로운시간"],
    "드라이브": ["도로의리듬", "시원한바람", "끝없는여정", "노을속풍경", "자유로운기분"],
    "사랑": ["달달한멜로디", "따뜻한감정", "감미로운사랑노래", "첫사랑의기억", "로맨틱한순간"],
    "추억": ["옛날생각", "아련한감정", "흑백사진속", "잊을수없는기억", "추억속음악"],
    "위로": ["따뜻한손길", "마음을어루만지는", "희망을주는음악", "감정의힐링", "어려운시간을이겨내는"],
    "감성": ["깊은감정", "감성에잠기는", "달콤한피아노", "낭만적인멜로디", "마음에닿는"],
    "스트레스해소": ["에너지가넘치는", "강렬한비트", "분출하는감정", "리듬에몸을맡겨", "신나는댄스"],
    "휴식": ["편안한저녁", "따뜻한커피한잔", "느린템포", "느긋한시간", "조용한밤"],
    "운동": ["힘이솟는비트", "에너지충전", "강렬한리듬", "피트니스음악", "운동에집중"],
    "이별": ["슬픈멜로디", "눈물의노래", "이별의아픔", "지난사랑의기억", "고독한밤"],
    "공부": ["집중을돕는음악", "배경음악", "차분한멜로디", "생산성향상", "조용한시간"],
    "몽환": ["꿈속을걷는듯한", "신비로운분위기", "초현실적인사운드", "환상적인세계", "비현실적인음악"],
    "비오는날": ["빗소리와함께", "촉촉한감성", "따뜻한차한잔", "잔잔한피아노", "차분한시간"],
    "트렌디": ["최신곡", "핫한비트", "감각적인리듬", "모던사운드", "지금유행하는음악"],
    "설렘": ["두근거리는기대", "첫만남의설렘", "달콤한멜로디", "가슴뛰는순간", "기분좋은기대감"],
    "여유": ["느린템포", "편안한시간", "따뜻한햇살", "일상의소소함", "마음의평온"],
    "기대감": ["설레는기다림", "기분좋은예감", "앞으로의희망", "밝은미래", "희망찬비트"],
    "분노": ["폭발하는감정", "격렬한리듬", "강렬한사운드", "화난감정풀어내기", "어두운비트"],
    "아픔": ["슬픔을담은멜로디", "상처를어루만지는", "감정의깊이", "잊지못한상처", "눈물의음악"],
    "웅장함": ["거대한오케스트라", "장엄한사운드", "에픽한음악", "감동적인음악", "영화같은장면"],
}

# 카테고리 정수 라벨링
category_to_int = {}
for i, category in enumerate(categories.keys()):
    category_to_int[category] = i


def process_style_selection(selected_categories, style_openess, data, embeddings, average_category_embeddings):
    """
    선택된 카테고리에 대해 처리하고, 합집합 minjung_id를 포함하는 filtered_data를 반환합니다.
    
    Args:
        selected_categories (list): 처리할 카테고리 이름들의 리스트
        style_openess (int): 취향 개방도(1~5 사이 정수)
        data (pd.DataFrame): 장르 필터링된 음악 데이터프레임
        embeddings (np.array): 임베딩 벡터
        
    Returns:
        pd.DataFrame: 취향 필터링된 음악 데이터프레임
    """

    words_with_ids = [(row['minjung_id'], hashtag) for _, row in data.iterrows() for hashtag in row['generated'].replace('#', '').split()]
    # 데이터프레임의 각 행에서 해시태그를 추출하여 리스트로 변환
    words = [hashtag for _, hashtag in words_with_ids]
    # 중복 제거된 해시태그 개수 계산
    unique_words_count = len(set(words))

    # FAISS 인덱스 생성 및 추가
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    final_minjung_ids = set()

    if style_openess == 5:
        return data

    # k 값 설정
    if style_openess == 1:
        k = int(unique_words_count * 0.005)
    elif style_openess == 2:
        k = int(unique_words_count * 0.05)
    elif style_openess == 3:
        k = int(unique_words_count * 0.075)
    elif style_openess == 4:
        k = int(unique_words_count * 0.1)
    else:
        raise ValueError("style_openess must be an integer between 1 and 5.")
    
    for category in selected_categories:
        if category not in categories:
            print(f"{category}는 존재하지 않는 카테고리입니다.")
            continue

        # 카테고리 임베딩 벡터 추출
        if isinstance(average_category_embeddings, np.ndarray):
            average_category_embeddings = {str(i): avg for i, avg in enumerate(average_category_embeddings)}

        query_vector = average_category_embeddings[str(category_to_int[category])]

        # 벡터 정규화
        faiss.normalize_L2(query_vector)

        # 쿼리 벡터와 인덱스 차원 맞추기
        query_dim = query_vector.shape[1]
        index_dim = index.d

        if query_dim < index_dim:
            # 쿼리 벡터 패딩
            padding = np.zeros((query_vector.shape[0], index_dim - query_dim))
            query_vector = np.hstack((query_vector, padding))
        elif query_dim > index_dim:
            # 쿼리 벡터 트리밍
            query_vector = query_vector[:, :index_dim]

        # 초기 배수 설정
        initial_multiplier = 100  # 초기 배수
        max_multiplier = 1000  # 최대 배수

        unique_words = set()
        current_multiplier = initial_multiplier

        while len(unique_words) < k and current_multiplier <= max_multiplier:
            current_k_search = k * current_multiplier
            distances, indices = index.search(query_vector, current_k_search)
            
            for idx in indices[0]:
                word = words[idx]
                unique_words.add(word)
                final_minjung_ids.add(words_with_ids[idx][0])
                if len(unique_words) == k:
                    break
            else:
                current_multiplier += 1
                continue
            break

        # 최종적으로 추천 가능한 음악 개수가 k보다 작으면 오류 발생
        if len(unique_words) < k:
            raise ValueError(f"배수 {current_multiplier}까지 검색한 후에 {len(unique_words)}개의 고유 단어만 찾았습니다.")

        # print(f"카테고리 '{category}'에서 선택된 단어 개수: {len(unique_words)}")
    
    # 최종 minjung_id로 필터링
    filtered_data = data[data['minjung_id'].isin(final_minjung_ids)]
    # print(f"최종적으로 추천 가능한 음악 개수: {len(filtered_data)}")
    
    return filtered_data

# process_style_selection의 결과값과 genre_selection의 결과값의 교집합을 추출
def intersection_of_results(style_filtered_data, genre_filtered_data):
    """
    process_style_selection과 process_genre_selection의 결과값을 받아 두 결과값의 교집합을 추출하고, 
    그 교집합을 포함하는 데이터프레임을 반환합니다.

    Args:
        style_filtered_data (pd.DataFrame): process_style_selection의 결과값
    """
    # 두 데이터프레임의 minjung_id 열을 추출
    style_minjung_ids = set(style_filtered_data['minjung_id'])
    genre_minjung_ids = set(genre_filtered_data['minjung_id'])
    
    # 두 집합의 교집합 추출
    common_minjung_ids = style_minjung_ids.intersection(genre_minjung_ids)
    # print(f"최종적으로 추천 가능한 음악 개수: {len(common_minjung_ids)}")
    # 교집합을 포함하는 데이터프레임 반환
    return style_filtered_data[style_filtered_data['minjung_id'].isin(common_minjung_ids)]