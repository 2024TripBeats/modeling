import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import faiss

# 파일에서 단어 읽기
def load_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        words = content.replace('\n', ',').split(',')
    return [word.strip() for word in words if word.strip()]

# 임베딩 벡터 생성
def generate_embeddings(words, model, tokenizer, d=128):
    embeddings = []
    for word in words:
        inputs = tokenizer(word, return_tensors='pt')
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        embeddings.append(embedding)
    embeddings = np.vstack(embeddings).astype('float32')
    return embeddings

# 단어 리스트 로드 (모든 단어 사용)
file_path = '/root/TripBeats_modeling-repo/music/data/music_hashtags.txt'
words = load_words(file_path)

# 모델과 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained("Alibaba-NLP/gte-large-en-v1.5", trust_remote_code=True)
model = AutoModel.from_pretrained("Alibaba-NLP/gte-large-en-v1.5", trust_remote_code=True)

# 임베딩 벡터 생성
d = 1024  # gte-large-en-v1.5 모델의 임베딩 차원
word_embeddings = generate_embeddings(words, model, tokenizer, d)

# 벡터 정규화 (코사인 유사도 사용을 위해)
faiss.normalize_L2(word_embeddings)

# Faiss 인덱스 생성 (내적 유사도 사용)
index = faiss.IndexFlatIP(d)

# 벡터를 인덱스에 추가
index.add(word_embeddings)

# 인덱스 저장
faiss.write_index(index, '/root/TripBeats_modeling-repo/music/data/music_hashtags2.index')

# 단어 리스트 저장
np.save('/root/TripBeats_modeling-repo/music/data/music_hashtags2.npy', words)