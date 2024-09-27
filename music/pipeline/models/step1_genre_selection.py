# 음악 장르 유사성 사전 (한국어 기준)
music_genres_similarity = {
    'POP': ['댄스', '록/메탈', 'R&B/Soul', '애시드/퓨전/팝'],
    '댄스': ['POP', '일렉트로니카', 'R&B/Soul', '애시드/퓨전/팝'],
    '랩/힙합': ['R&B/Soul', '일렉트로니카', '댄스', 'POP'],
    '일렉트로니카': ['댄스', 'POP', '애시드/퓨전/팝', '랩/힙합'],
    '발라드': ['R&B/Soul', '포크/블루스', '인디음악', 'POP'],
    'R&B/Soul': ['POP', '댄스', '랩/힙합', '발라드'],
    '록/메탈': ['POP', '인디음악', '포크/블루스', '댄스'],
    '인디음악': ['록/메탈', '포크/블루스', '발라드', 'POP'],
    '성인가요/트로트': ['포크/블루스', '국악', '발라드', 'POP'],
    '포크/블루스': ['발라드', '인디음악', '성인가요/트로트', '블루스'],
    '재즈': ['보컬재즈', '애시드/퓨전/팝', '빅밴드/스윙', 'POP'],
    '국내드라마': ['국내영화', '국외드라마', 'POP', 'R&B/Soul'],
    'J-POP': ['POP', '애니메이션/웹툰', '댄스', '일렉트로니카'],
    '애니메이션/웹툰': ['J-POP', '게임', 'POP', '댄스'],
    '보컬재즈': ['재즈', '애시드/퓨전/팝', '빅밴드/스윙', '클래식'],
    '국외영화': ['국내영화', '국외드라마', 'POP', 'R&B/Soul'],
    '애시드/퓨전/팝': ['POP', '재즈', '일렉트로니카', '보컬재즈'],
    '뉴에이지': ['클래식', '크로스오버', 'POP', '애시드/퓨전/팝'],
    '컨트리': ['포크/블루스', '블루스', 'POP', '록/메탈'],
}

def process_genre_selection(genre_selection, genre_openess):
    """
    선택한 음악 장르와 개방성 수준을 기반으로 유저에게 추천 가능한 최종 장르 목록을 반환한다.

    Args:
        genre_selection (list of str): 선택한 장르 목록
        genre_openess (int): 개방성 수준 (1에서 5까지)

    Returns:
        set: 최종 선택된 장르 목록
    """
    if genre_openess == 5:
        return set(music_genres_similarity.keys())

    final_selection = set(genre_selection)
    if genre_openess > 1:
        additional_genres = set()
        for genre in genre_selection:
            similar_genres = music_genres_similarity.get(genre, [])
            additional_genres.update(similar_genres[:genre_openess-1])
        final_selection.update(additional_genres)

    return final_selection

def filter_data_by_genre(final_selection, music_hashtags_data):
    """
    최종 선택된 장르 목록에 있는 장르를 genre 열에서 1개 이상 가지고 있는 행만 필터링한다.

    Args:
        final_selection (set): 최종 선택된 장르 목록
        file_path (str): CSV 파일 경로

    Returns:
        DataFrame: 장르 기반 추천 가능 음악 데이터
    """
    filtered_data = music_hashtags_data[music_hashtags_data['genre'].apply(lambda x: any(genre in final_selection for genre in eval(x)))]
    return filtered_data[['song_title', 'artist_name', 'like_cnt', 'hashtags', 'generated', 'id', 'genre', 'morning', 'night', 'minjung_id']]