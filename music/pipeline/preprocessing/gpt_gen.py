import pandas as pd
import requests

# 데이터프레임 생성
df1 = pd.read_csv('/root/TripBeats_modeling-repo/music/data/visitjeju_tourist_v2.csv')
df2 = df1.copy()

# API 요청 헤더 설정
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer ____"
}

# 해시태그 생성 함수
def generate_hashtags(row):
    visit_area1 = row['tourist_address']
    visit_area2 = row['tourist']
    prompt = f"""요구사항 2가지를 답변 형식에 맞게 풀이해줘.
        요구사항1. 장소 관련 해시태그를 제외하고 '{visit_area1}'에 있는'{visit_area2}'를 방문했을 때 여행자가 느낄 감정에 대한 해시태그를 한국어로 15개씩 생성해줘. 
        다만, 신남, 즐거움과 같은 너무 흔한 단어는 피해줘. 예를 들어, 서울시 종로구에 있는 경복궁은 다음과 같은 결과가 나올 거야. 
        요구사항2. 해당 여행지가 다음의 5가지 카테고리 중 어디에 해당되는지 골라줘. 1. 자연관광지: 폭포,바다 등 자연환경, 산책로, 둘레길 2. 역사,유적,종교 3. 전시회, 박물관 등 문화시설 4. 레저 스포츠 관련 엑티비티: 스키, 카트, 수상레저 5. 테마시설: 놀이공원, 워터파크
        답변은 다음의 형식을 무조건 지켜줘. 
        '해시태그': #역사와함께 #평화로운 #고즈넉한 #시간여행 #문화체험 #아름다운기억 #감동적인순간 #마음의쉼터 #고전의멋 #감성충전 #전통의향기 #추억속으로 #힐링타임 #매혹적인경험 #잔잔한감동
        '카테고리': 2. 역사,유적,종교 """
    message = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    payload = {
        "model": "gpt-4o-2024-05-13",
        "messages": message,
        "max_tokens": 200,
        "temperature": 0.7
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        try:
            content = response.json()
            hashtags = content['choices'][0]['message']['content']
            return hashtags
        except (KeyError, IndexError, json.JSONDecodeError):
            return "해시태그 생성 실패"
    else:
        return "API 요청 실패"

# 데이터프레임의 각 행에 대해 해시태그 생성
df2['HASHTAGS'] = df1.apply(generate_hashtags, axis=1)

# df2를 CSV 파일로 저장
df2.to_csv('/root/TripBeats_modeling-repo/music/data/visitjeju_tourist_v2_hashtags.csv', index=False)

# 결과 출력
print(df2['HASHTAGS'])