from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from models.main import main_pipeline
import numpy as np

app = FastAPI()


class Place(BaseModel):
    placeId: str
    placeName: str
    category: str
    duration: int
    order: int
    new_order: Optional[int]
    timeOfDay: str
    music_bool: bool
    top_musicId: Optional[str]
    song_title: Optional[str]
    artist_name: Optional[str]
    spotify_id: Optional[int]
    price: int


class PlaceMusicPair(BaseModel):
    placeId: str
    placeName: str
    category: str
    duration: int
    order: int
    new_order: Optional[int]
    timeOfDay: str
    music_bool: bool
    musicId: Optional[str]
    musicName: Optional[str]
    musicArtist: Optional[str]
    spotify_id: Optional[int]
    duration: int
    price: int


class TravelSegmentDto(BaseModel):
    distance: float


class RecommendationCandidateRequestDto(BaseModel):
    itinerary: List[Place]
    travelSegments: List[TravelSegmentDto]


class RecommendationCandidateResponseDto(BaseModel):
    dayNumber: int
    places: List[PlaceMusicPair]
    travelSegments: List[TravelSegmentDto]


class DayRecommendationRequestDto(BaseModel):
    dayNumber: int
    candidates: List[RecommendationCandidateRequestDto]


class DayRecommendationResponseDto(BaseModel):
    dayNumber: int
    candidates: int  # Assuming 'candidates' is a count based on the provided JSON
    itinerary: List[RecommendationCandidateResponseDto]


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
        candidates_count = len(day['candidates'])
        itinerary = []
        for candidate in day['candidates']:
            day_response = RecommendationCandidateResponseDto(
                dayNumber=day['dayNumber'],
                places=[
                    PlaceMusicPair(
                        placeId=place['placeId'],
                        placeName=place['placeName'],
                        category=place['category'],
                        duration=place['duration'],
                        order=place['order'],
                        new_order=place.get('new_order'),
                        timeOfDay=place['timeOfDay'],
                        music_bool=place['music_bool'],
                        musicId=place.get('top_musicId'),
                        musicName=place.get('song_title'),
                        musicArtist=place.get('artist_name'),
                        spotify_id=place.get('spotify_id'),
                        duration=place['duration'],
                        price=place['price']
                    ) for place in candidate['itinerary']
                ],
                travelSegments=candidate['travelSegments']
            )
            itinerary.append(day_response)
        
        day_recommendation = DayRecommendationResponseDto(
            dayNumber=day['dayNumber'],
            candidates=candidates_count,
            itinerary=itinerary
        )
        recommendations.append(day_recommendation)

    response = FinalRecommendationResponseDto(
        recommendations=recommendations
    )

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)