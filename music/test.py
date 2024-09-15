import pandas as pd

# 데이터프레임을 축약 없이 출력하도록 설정
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# CSV 파일 로드
df = pd.read_csv('/root/standardized_results.csv')

# 숫자 데이터만 선택
numeric_df = df.select_dtypes(include=[float, int])

# 각 행에서 가장 큰 값을 가지는 열 이름을 새로운 열로 추가
df['max_column'] = numeric_df.idxmax(axis=1)

print(df[['Unnamed: 0', 'max_column']])
