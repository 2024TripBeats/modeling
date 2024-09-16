import pandas as pd
import ast
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

df1 = pd.read_csv('/root/melon_hashtags_concat.csv')
df2 = pd.read_csv('/root/travel_hashtags_total.csv')

df1 = df1[:5]
df2 = df2.iloc[:5,2:]

# 해시태그 문자열을 리스트로 변환하고 각 해시태그에서 #을 제거하는 함수
def process_hashtags(hashtag_str):
    hashtag_str = hashtag_str.strip()
    hashtag_list = hashtag_str.split() 
    return [tag.replace('#', '') for tag in hashtag_list]

# OpenAI API 키 설정
openai.api_key = ''

# 텍스트를 임베딩하는 함수 정의
def embed_text(text):

    response = openai.embeddings.create(
    input=text,
    model="text-embedding-3-large"
    )
    return np.array(response.data[0].embedding)

# 리스트 형태의 텍스트 임베딩
def embed_text_list(text_list):
    embeddings = [embed_text(text) for text in text_list]
    return np.array(embeddings)

# 벡터화된 방식으로 코사인 유사도 계산
def calculate_cosine_similarities(embeddings1, embeddings2):
    similarities = cosine_similarity(embeddings1, embeddings2)
    return similarities

# 두 리스트의 텍스트 임베딩 간 거리 계산 및 평균 계산
def calculate_mean_distance(text_list1, text_list2):
    embeddings1 = embed_text_list(text_list1)
    embeddings2 = embed_text_list(text_list2)

    similarities = calculate_cosine_similarities(embeddings1, embeddings2)
    mean_distance = np.mean(similarities)

    return mean_distance, similarities

# 해시태그 열을 처리하여 #을 제거
df1['generated'] = df1['generated'].apply(process_hashtags)
df2['HASHTAGS'] = df2['HASHTAGS'].apply(process_hashtags)

# 교차 연산 결과 저장용 데이터 프레임 생성
results_df = pd.DataFrame(index=[f"Music Tag {i+1}" for i in df1.index], columns=[f"Travel Tag {j+1}" for j in df2.index])

# 각 행별로 교차 연산하여 결과 저장
for i in df1.index:
    for j in df2.index:
        mean_distance, _ = calculate_mean_distance(df1['generated'][i], df2['HASHTAGS'][j])
        results_df.at[f"Music Tag {i+1}", f"Travel Tag {j+1}"] = mean_distance

# 행과 열을 전치
transposed_results_df = results_df.transpose()

# 결과 출력
print(transposed_results_df)


