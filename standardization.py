import pandas as pd

#embedding.py에서 생성한 최종 dataframe을 여기 넣으면 됩니다!
data = {
    "Music Tag 1": [0.297656, 0.319222, 0.309455, 0.302183, 0.300958],
    "Music Tag 2": [0.328332, 0.327784, 0.326439, 0.331421, 0.318885],
    "Music Tag 3": [0.308139, 0.319177, 0.319489, 0.314603, 0.313903],
    "Music Tag 4": [0.299758, 0.319255, 0.302547, 0.304073, 0.305749],
    "Music Tag 5": [0.320915, 0.327511, 0.305312, 0.312745, 0.311345]
}

# Creating the DataFrame
df = pd.DataFrame(data, index=["Travel Tag 1", "Travel Tag 2", "Travel Tag 3", "Travel Tag 4", "Travel Tag 5"])

# Standardizing by subtracting the mean and dividing by the standard deviation for each music tag
standardized_df = df.apply(lambda x: (x - x.mean()) / x.std())

print(standardized_df)
