from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd

app = FastAPI()

class Place(BaseModel):
    placeId: str
    placeName: str
    duration: int

class PlaceMusicPair(BaseModel):
    placeId: str
    placeName: str
    musicId: str
    musicName: str
    musicArtist: str
    duration: int

class TravelSegmentDto(BaseModel):
    distance: float

class RecommendationCandidateRequestDto(BaseModel):
    itinerary: List[Place]
    travelSegments: List[TravelSegmentDto]

class RecommendationCandidateResponseDto(BaseModel):
    itinerary: List[PlaceMusicPair]
    travelSegments: List[TravelSegmentDto]

class DayRecommendationRequestDto(BaseModel):
    dayNumber: int
    candidates: List[RecommendationCandidateRequestDto]

class DayRecommendationResponseDto(BaseModel):
    dayNumber: int
    candidates: List[RecommendationCandidateResponseDto]

class FinalRecommendationRequestDto(BaseModel):
    recommendations: List[DayRecommendationRequestDto]
    musicGenres: List[str]
    genreOpenness: int
    musicTags: List[str]
    tagOpenness: int

class FinalRecommendationResponseDto(BaseModel):
    recommendations: List[DayRecommendationResponseDto]

# 데이터프레임을 전역 변수로 정의하여 서버 시작 시 한 번만 로드
music_df = pd.read_csv('/root/genre/music_recomendation.csv')

def get_music_info(place_name):
    filtered_df = music_df[music_df['rc_music'] == place_name]
    if not filtered_df.empty:
        row = filtered_df.iloc[0]
        return {
            "musicId": row['id'],
            "musicName": row['rc_music'],
            "musicArtist": row['artist_name'],
            "duration": int(row['duration'])
        }
    return None

@app.post("/music_recommend", response_model=FinalRecommendationResponseDto)
async def music_recommend(request: FinalRecommendationRequestDto):
    # 로그에 요청 데이터를 출력합니다.
    print("Received request:")
    print(request)
    
    recommendations = []

    for day_recommendation in request.recommendations:
        day_response = DayRecommendationResponseDto(
            dayNumber=day_recommendation.dayNumber,
            candidates=[]
        )

        for candidate in day_recommendation.candidates:
            itinerary_with_music = []

            for place in candidate.itinerary:
                music_info = get_music_info(place.placeName)
                if music_info:
                    itinerary_with_music.append(
                        PlaceMusicPair(
                            placeId=place.placeId,
                            placeName=place.placeName,
                            musicId=music_info['musicId'],
                            musicName=music_info['musicName'],
                            musicArtist=music_info['musicArtist'],
                            duration=music_info['duration']
                        )
                    )
                else:
                    # 음악 정보를 찾지 못했을 경우 기본값 설정 (옵션)
                    itinerary_with_music.append(
                        PlaceMusicPair(
                            placeId=place.placeId,
                            placeName=place.placeName,
                            musicId="0",
                            musicName="Unknown",
                            musicArtist="Unknown",
                            duration=0
                        )
                    )

            day_response.candidates.append(
                RecommendationCandidateResponseDto(
                    itinerary=itinerary_with_music,
                    travelSegments=candidate.travelSegments
                )
            )

        recommendations.append(day_response)

    response = FinalRecommendationResponseDto(
        recommendations=recommendations
    )
    
    return response

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
