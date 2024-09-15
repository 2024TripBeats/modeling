import pandas as pd
import requests

master_visit_all = pd.read_csv(r"C:\Users\user\Documents\카카오톡 받은 파일\master_visit_all.csv")
extracted_sim_final = pd.read_csv(r"C:\Users\user\Desktop\컨퍼\extracted_sim_final.csv")
api_key="Your key"
def gpt_api_zero(api_key,stopwords, requirewords,extracted_sim_final,master_visit_all):
    # CSV 파일을 데이터프레임으로 읽기
    df = pd.read_csv(csv_path)
    
    # DataFrame을 JSON 형식으로 변환
    df_text = df.to_string(index=False)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    message = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "category_mapping = {'자연': '1', '숲': '1', '산책로': '7', '쇼핑': '4', '역사': '2', '유적': '2', '종교시설': '2', '문화': '3', '공연장': '3', '영화관': '3', '전시관': '3', '상업지구': '4', '시장': '4', '레저': '5', '스포츠': '5', '테마시설': '6', '놀이공원': '6', '워터파크': '6', '축제': '8', '행사': '8'}"
                }
            ]
        },
        {
            "role": "user",
            "content": [{
                "type": "text",
                "text":'stopwords:'+ stopwords
            }]
        },
        {
            "role": "user",
            "content": [{
                "type": "text",
                "text":"위 stopwords에 대하여 category_mapping을 참고하여 몇번 카테고리를 제외해야 할까? \n답변에는 카테고리 숫자 한가지만 포함해줘. 절대 카테고리 숫자외에 어떠한 말도 답변에 포함시키지마.\n 만약 stop words의 내용이 어떠한 카테고리와도 관련이 없거나 아예 내용이 없다면 아무 내용도 답하지 말아줘"
            }]
            },
        {
            "role": "user",
            "content": [{
                "type": "text",
                "text":'requirewords:'+ requirewords
            }]
        },
        {
            "role": "user",
            "content": [{
                "type": "text",
                "text":"위 requirewords에 대하여 category_mapping을 참고하여 몇번 카테고리를 우선적으로 넣어야 할까? \n답변에 카테고리 숫자 한가지만 포함해줘. \n절대 카테고리 숫자외에 어떠한 말도 답변에 포함시키지마. 만약 require words의 내용이 어떠한 카테고리와도 관련이 없거나 아예 내용이 없다면 아무 내용도 답하지 말아줘."
            }]
        },
        {
            "role": "user",
            "content": [{
                "type": "text",
                "text":"너는 requirewords를 통해 넣어야 할 카테고리 숫자와 stopwords를 통해 제외해야 할 카테고리 숫자 2개를 답변해야 해. \n각각의 숫자는 ,를 통해 구분해줘"
            }]
        }
    ]

    payload = {
        "model": "gpt-4o",
        "messages": message,
        "max_tokens": 1000,
        "temperature": 0
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        response_json = response.json()
        content = response_json['choices'][0]['message']['content']
        split_content = content.split(',')
        stop = split_content[1]
        require = split_content[0]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        stop, require =  None, None
    # Stop, require 값을 리스트로 변환
    categories_to_remove = stop.split(',')
    categories_to_increase = require.split(',')

    # Stopwords 처리
    original_places = master_visit_all['VISIT_AREA_NM'].tolist()
    master_visit_all = master_visit_all[~master_visit_all['VISIT_AREA_TYPE_CD'].isin(categories_to_remove)]

    # extracted_sim_final에서 행 제거
    removed_places = master_visit_all['VISIT_AREA_NM'].tolist()
    to_remove = [item for item in original_places if item not in removed_places]
    extracted_sim_final = extracted_sim_final[~extracted_sim_final['Unnamed: 0'].isin(to_remove)]

    # requirewords 처리
    master_visit_all.loc[master_visit_all['VISIT_AREA_TYPE_CD'].isin(categories_to_increase), 'total_score'] += 5
                                              
    #전처리
                                              
    master_visit_all = master_visit_all.drop(columns='Unnamed: 0')
    extracted_sim_final.set_index('Unnamed: 0', inplace=True)
                                              
                                              
    return master_visit_all,extracted_sim_final
    
