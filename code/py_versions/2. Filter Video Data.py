
# coding: utf-8

# # 2. Filter  Video Metadata
# 
# Now that we have all the data from Alex Jones' uploads between January 1, 2015 and May 4, 2018, we can filter out the videos that do not mention the mainstream media and prepare the dataset ready for analysis. The list of words given is saved in data/filter_mm_words.txt, so we will open this file and then search through the video titles using the Pandas .contains() method. 

# In[1]:


import pandas as pd
from datetime import datetime


# In[2]:


video_df = pd.read_csv("../data/video_metadata.csv")

# Open the file with the words we want to filter our dataframe on
filter_words = open("../data/filter_mm_words.txt").readlines()
# Join the list with the OR operator, so that we can search for any of the words
filter_words = '|'.join([word.strip().lower() for word in filter_words])

# Filter based on if any of the words appear in the video title
filtered_mm_df = video_df[video_df['video_title']
                          .str.lower().str.contains(filter_words)]
other_rows = video_df[~video_df['video_title']
                      .str.lower().str.contains(filter_words)]

# Save to CSV files
filtered_mm_df.to_csv("../data/video_metadata_mainstream_media.csv", 
                      sep=',', encoding="utf-8", index = False, header=True)
other_rows.to_csv("../data/video_metadata_not_mainstream_media.csv", 
                  sep=',', encoding="utf-8", index = False, header=True)
print 'Data written to files.'

