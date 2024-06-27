# 
#장소 유사도 함수 실행 방법
# 사용자로부터 선호도 입력받기 
user_preference = ['백운계곡관광지','소래역사관','명동난타극장','KT&G상상마당 홍대','안흥지 애련정']

# 추천 장소를 계산
recommended_places = recommend_places(extracted_sim, user_preference)


print("추천 장소 순서 및 유사도 값:")
print(recommended_places)
