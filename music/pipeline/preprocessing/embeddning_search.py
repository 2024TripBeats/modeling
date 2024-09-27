import numpy as np
import faiss
import matplotlib.pyplot as plt
from transformers import AutoTokenizer, AutoModel
import torch
import pandas as pd
from sklearn.manifold import TSNE
import time  # 추가된 부분
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams['font.family'] ='NanumGothic'
plt.rcParams['axes.unicode_minus'] =False

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("BM-K/KoSimCSE-roberta", trust_remote_code=True)
model = AutoModel.from_pretrained("BM-K/KoSimCSE-roberta", trust_remote_code=True)

# Load the CSV file containing hashtags and their corresponding IDs
data = pd.read_csv('/root/TripBeats_modeling-repo/music/pipeline/data/merged_data_updated2.csv')

words_with_ids = [(row['minjung_id'], hashtag) for _, row in data.iterrows() for hashtag in row['generated'].replace('#', '').split()]

# Extract only the hashtags for embedding
words = [hashtag for _, hashtag in words_with_ids]
unique_words_count = len(set(words))
print(unique_words_count)

# Check if embeddings already exist
embedding_file = 'music_embeddings.npy'
try:
    embeddings = np.load(embedding_file)  # 임베딩 불러오기
    print("Embeddings loaded from file.")
except FileNotFoundError:
    # Initialize an empty list to store the embeddings
    embeddings = []

    # Compute the embeddings for each word
    start_time = time.time()  # 타이밍 시작
    for word in words:
        inputs = tokenizer(word, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy().astype('float32')
            faiss.normalize_L2(embedding)
            embeddings.append(embedding)
    end_time = time.time()  # 타이밍 종료
    print(f"Embeddings computation time: {end_time - start_time:.2f} seconds")  # 결과 출력

    # Convert the list of embeddings to a numpy array and save to file
    embeddings = np.vstack(embeddings)
    np.save(embedding_file, embeddings)  # 임베딩 저장

# Create a FAISS index and add the embeddings
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Define the categories and their corresponding keywords
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

# Iterate through each category to compute average embeddings and perform searches
for category, keywords in categories.items():
    print(f"Processing category: {category}")
    
    # Compute the average embedding for the specific keywords
    average_embedding = np.zeros((1, model.config.hidden_size), dtype='float32')  # Initialize average embedding

    for keyword in keywords:
        inputs = tokenizer(keyword, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy().astype('float32')
            average_embedding += embedding  # Sum the embeddings

    average_embedding /= len(keywords)  # Average the embeddings

    # Use the average embedding as the query vector
    query_vector = average_embedding

    # Normalize the query vector for cosine similarity
    faiss.normalize_L2(query_vector)

    # Ensure the query vector and index dimensions match
    query_dim = query_vector.shape[1]
    index_dim = index.d

    if query_dim < index_dim:
        # Pad the query vector
        padding = np.zeros((query_vector.shape[0], index_dim - query_dim))
        query_vector = np.hstack((query_vector, padding))
    elif query_dim > index_dim:
        # Trim the query vector
        query_vector = query_vector[:, :index_dim]

    # Define the number of unique words we want
    k = int(unique_words_count * 0.005)
    initial_multiplier = 1  # Start with initial multiplier of 1
    max_multiplier = 100  # Set a reasonable maximum multiplier to prevent infinite loops

    final_selected_indices = []
    unique_words = set()
    current_multiplier = initial_multiplier

    while len(unique_words) < k and current_multiplier <= max_multiplier:
        current_k_search = k * current_multiplier
        print(f"Searching with k_search = {current_k_search} for category: {category}")
        distances, indices = index.search(query_vector, current_k_search)
        
        # Initialize a list to store indices up to k unique words
        selected_indices = []
        for idx in indices[0]:
            word = words[idx]
            selected_indices.append(idx)
            unique_words.add(word)
            if len(unique_words) == k:
                # Once we have k unique words, include all duplicates up to this point
                break
        else:
            # If we didn't break from the loop, continue with a higher multiplier
            current_multiplier += 1
            continue
        # If we broke from the loop, exit the while loop
        break

    # After the loop, check if we have at least k unique words
    if len(unique_words) < k:
        raise ValueError(f"배수 {current_multiplier}까지 검색한 후에 {len(unique_words)}개의 고유 단어만 찾았습니다.")

    # Print the indices, distances, and corresponding words
    selected_distances = distances[0][:len(selected_indices)]
    #print("가장 가운 벡터의 인덱스:", selected_indices)
    #print("각 벡터까지의 거리:", selected_distances)
    #print("가장 가까운 벡터에 해당하는 단어:", [words[idx] for idx in selected_indices])
    selected_indices_words = [words[idx] for idx in selected_indices]
    print(f"가장 가까운 벡터에 해당하는 단어 개수: {len(selected_indices_words)}")
    unique_word_count2 = len(set(selected_indices_words))
    print(f"가장 가까운 벡터에 해당하는 고유 단어 개수: {unique_word_count2}")

    # Get unique minjung_id for the closest words
    minjung_ids = [words_with_ids[idx][0] for idx in selected_indices]  # 리스트로 변경
    print("가장 가까운 벡터에 해당하는 minjung_id:", minjung_ids)

    # Load the CSV file again to filter the rows
    filtered_data = data[data['minjung_id'].isin(minjung_ids)]  # minjung_id가 일치하는 행 필터링
    # filtered_data의 행 개수 출력
    print(f"filtered_data의 행 개수: {len(filtered_data)}")
    #print(filtered_data)  # 결과 출력

# # Prepare for t-SNE visualization
# num_categories = len(categories)  # Get the number of categories
# fig, axes = plt.subplots(5, 5, figsize=(20, 20))  # Create a grid of subplots (3 rows, 5 columns)
# axes = axes.flatten()  # Flatten the 2D array of axes for easy iteration

# # Iterate through each category to compute t-SNE and plot
# for i, (category, keywords) in enumerate(categories.items()):
#     if i >= len(axes):  # Ensure we don't exceed the number of axes
#         break
    
#     print(f"Processing t-SNE for category: {category}")
    
#     # Compute the average embedding for the specific keywords
#     average_embedding = np.zeros((1, model.config.hidden_size), dtype='float32')  # Initialize average embedding

#     for keyword in keywords:
#         inputs = tokenizer(keyword, return_tensors="pt")
#         with torch.no_grad():
#             outputs = model(**inputs)
#             embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy().astype('float32')
#             average_embedding += embedding  # Sum the embeddings

#     average_embedding /= len(keywords)  # Average the embeddings

#     # Use the average embedding as the query vector
#     query_vector = average_embedding

#     # Normalize the query vector for cosine similarity
#     faiss.normalize_L2(query_vector)

#     # Perform the search
#     distances, indices = index.search(query_vector, 10)  # Get top 10 results for visualization

#     # Get the selected words for t-SNE
#     selected_words = [words[idx] for idx in indices[0]]

#     # Compute t-SNE for the embeddings
#     tsne = TSNE(n_components=2, perplexity=30, n_iter=300)
#     embedding_2d = tsne.fit_transform(embeddings)

#     # Plot the embeddings
#     axes[i].scatter(embedding_2d[:, 0], embedding_2d[:, 1], s=5, c='blue', label='All words')
#     selected_indices = [words.index(word) for word in selected_words]
#     axes[i].scatter(embedding_2d[selected_indices, 0], embedding_2d[selected_indices, 1], s=50, c='red', label='Selected words')
    
#     # Add title and legend for each subplot
#     axes[i].set_title(category)
#     axes[i].set_xlim(-40, 40)  # Set x-axis limits
#     axes[i].set_ylim(-40, 40)  # Set y-axis limits
#     axes[i].legend()

# # Adjust layout
# plt.tight_layout()

# # Save the plot
# plt.savefig('/root/TripBeats_modeling-repo/music/pipeline/preprocessing/tsne_projection.png')

# # Display the plot
# plt.show()