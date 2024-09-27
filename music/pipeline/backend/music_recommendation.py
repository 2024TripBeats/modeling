from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../models')

from main import main_pipeline
import numpy as np

app = FastAPI()


class Place(BaseModel):
    placeId: str
    placeName: str
    duration: int


class PlaceMusicPair(BaseModel):
    placeId: str
    placeName: str
    musicId: int
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


@app.post("/music_recommend", response_model=FinalRecommendationResponseDto)
async def music_recommend(request: FinalRecommendationRequestDto):
    # 로그에 요청 데이터를 출력합니다.
    print("Received request:")
    print(request)

    # Extract necessary data from the request
    genre_selection = request.musicGenres
    genre_openess = request.genreOpenness
    style_selection = request.musicTags
    style_openess = request.tagOpenness
    trip_data = request.recommendations

    # Load additional data required by main_pipeline
    csv_paths = {
        '아침': '/root/TripBeats_modeling-repo/music/pipeline/data/morning_score_id.csv',
        '오후': '/root/TripBeats_modeling-repo/music/pipeline/data/afternoon_score_id.csv',
        '밤': '/root/TripBeats_modeling-repo/music/pipeline/data/night_score_id.csv'
    }
    music_embeddings = np.load('/root/TripBeats_modeling-repo/music/pipeline/data/music_embeddings.npy') 
    user_preferences_embeddings = np.load('/root/TripBeats_modeling-repo/music/pipeline/data/average_embeddings.npy', allow_pickle=True)
    music_hashtags_data = pd.read_csv('/root/TripBeats_modeling-repo/music/pipeline/data/music_recommendation_list.csv')

    # Call the main_pipeline function
    result = main_pipeline(genre_selection, genre_openess, style_selection, style_openess, trip_data, music_hashtags_data, csv_paths)

    # Process the result to match the response model
    recommendations = []
    for day in result:
        day_response = DayRecommendationResponseDto(
            dayNumber=day['dayNumber'],
            candidates=[
                RecommendationCandidateResponseDto(
                    itinerary=[
                        PlaceMusicPair(
                            placeId=place['placeId'],
                            placeName=place['placeName'],
                            musicId=place['top_musicId'],
                            musicName=place['song_title'],
                            musicArtist=place['artist_name'],
                            duration=place['duration'],
                            price=place['price']
                        ) for place in candidate['itinerary']
                    ],
                    travelSegments=candidate['travelSegments']
                ) for candidate in day['candidates']
            ]
        )
        recommendations.append(day_response)

    response = FinalRecommendationResponseDto(
        recommendations=recommendations
    )

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)