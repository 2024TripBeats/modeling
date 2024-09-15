import pandas as pd

# Load the datasets
melon_hashtags = pd.read_csv('C:\\Users\\minjeong\\OneDrive\\24-2\\tripbeats\\music\\melon_hashtags_concat_final2.csv')
song_data = pd.read_csv('C:\\Users\\minjeong\\OneDrive\\24-2\\tripbeats\\music\\song_data_final.csv')

# Merge the datasets on the specified keys
merged_data = pd.merge(melon_hashtags, song_data, on=['song_title', 'artist_name', 'album_name', 'like_cnt'])

# Save the merged dataset to a new CSV file
merged_data.to_csv('C:\\Users\\minjeong\\OneDrive\\24-2\\tripbeats\\music\\merged_data.csv', index=False)
