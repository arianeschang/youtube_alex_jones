import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy
from datetime import datetime
import seaborn as sns
sns.set()


def analyze(mm_rows, other_rows):   

	print mm_rows.head()
	print other_rows.head()
	mm_rows.set_index('video_publish_date', inplace=True)
	other_rows.set_index('video_publish_date', inplace=True)


	mm_rows['like/dislike'] = mm_rows['video_like_count']/(mm_rows['video_dislike_count'] + mm_rows['video_like_count'])
	other_rows['like/dislike'] = other_rows['video_like_count']/(other_rows['video_dislike_count'] + other_rows['video_like_count'])

	mm_rows['like/view'] = mm_rows['video_like_count']/mm_rows['video_view_count']
	other_rows['like/view'] = other_rows['video_like_count']/other_rows['video_view_count']
	print mm_rows.describe(include=[np.number])
	print other_rows.describe(include=[np.number])

	print scipy.stats.ttest_ind(mm_rows.dropna()['like/view'],other_rows.dropna()['like/view'])

	print other_rows.groupby(['count_filter_words'])['video_like_count'].mean()

	other_rows = other_rows.dropna()
	treatment1 = other_rows[other_rows["count_filter_words"] == 0.0]["video_like_count"]  
	treatment2 = other_rows[other_rows["count_filter_words"] == 1.0]["video_like_count"]  
	treatment3 = other_rows[other_rows["count_filter_words"] == 2.0]["video_like_count"]  
	treatment4 = other_rows[other_rows["count_filter_words"] == 3.0]["video_like_count"]  
	treatment5 = other_rows[other_rows["count_filter_words"] == 4.0]["video_like_count"] 
	treatment6 = other_rows[other_rows["count_filter_words"] == 5.0]["video_like_count"] 
	treatment7 = other_rows[other_rows["count_filter_words"] == 6.0]["video_like_count"] 

	f_val, p_val = scipy.stats.f_oneway(treatment1, treatment2, treatment3, treatment4, treatment5, treatment6, treatment7)
	print p_val  
 



	
	'''
	sns.lmplot(x='video_publish_date', y='video_view_count', data=mm_rows, x_estimator=np.mean);
	plt.show()

	sns.lmplot(x='video_publish_date', y='video_view_count',  data=other_rows, x_estimator=np.mean);
	plt.show()

	
	other_rows[['video_view_count']].plot(figsize=(20,10), linewidth=5, fontsize=20)
	plt.xlabel('Publish Date', fontsize=20)
	plt.show()


	mm_rows[['video_view_count']].plot(figsize=(20,10), linewidth=5, fontsize=20)
	plt.xlabel('Publish Date', fontsize=20)
	plt.show()
	'''
	










def filter_rows(df, words):

	contains_words = '|'.join(words)

	df['video_title'] = df['video_title'].str.lower()
	df['video_description'] = df['video_description'].str.lower()

	df['count_filter_words'] = 0
	
	for word in words:
		count_descr = df['video_description'].str.count(word)
		count_title = df['video_title'].str.count(word)
		df['count_filter_words'] += (count_descr + count_title)

	filtered_df = df[df['count_filter_words'] > 0]
	other_rows = df[df['count_filter_words'] == 0]
	filtered_df.to_csv("data/video_metadata_mainstream_media.csv", sep=',', encoding="utf-8", index = False, header=True)

	return filtered_df, other_rows



def main():

	video_data = pd.DataFrame.from_csv("data/video_metadata.csv")
	video_data['video_publish_date'] = pd.to_datetime(video_data['video_publish_date'])
	video_data['video_publish_date'] = video_data['video_publish_date'].dt.strftime('%Y/%M/%D')


	filter_phrases = open("data/filter_mm_words.txt").readlines()
	filter_phrases = [phrase.strip().lower() for phrase in filter_phrases]

	filtered_df, other_rows = filter_rows(video_data, filter_phrases)

	analyze(filtered_df, video_data)

if __name__ == "__main__":
    main()
