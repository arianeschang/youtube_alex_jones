import requests
import urllib
import pandas as pd
pd.set_option('display.max_columns', None)  

def get_all_videos(username):

	# Get playlist with all uploads 
	playlist_params = [('part', 'contentDetails,id'), ('forUsername', username)]
	playlist_info = get_response('channels?', playlist_params)
	playlist_ID = playlist_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']
	channel_Id = playlist_info['items'][0]['id']

	# Get videos in the playlist
	video_params = [('part','snippet'), ('playlistId',playlist_ID), ('maxResults', 50)]
	video_search = get_response('playlistItems?', video_params)

	video_data = []
	headers = ['video_id', 'channel_title', 'channel_id', 'video_publish_date', 
			'video_title', 'video_view_count', 'video_like_count', 'video_dislike_count',
			 'video_comment_count', 'video_description']

	while True:
		for video in video_search['items']:
			video_snippet = video['snippet']

			if video_snippet['publishedAt'] > '2018-05-05T00:00:00Z':
				print video_snippet['publishedAt']
				continue
			elif video_snippet['publishedAt'] < '2015-01-01T00:00:00Z':
				return video_data

			this_video_data = get_video_data(video_snippet, channel_Id)
			video_data.append(this_video_data)
			print this_video_data[3]

		# Get the next video. 
		next_video = video_params + [('pageToken', video_search['nextPageToken'])]
		video_search = get_response('playlistItems?', next_video)

		# Save our data so far in case something goes wrong later. 
		video_df = pd.DataFrame(video_data, columns=headers)
		video_df.to_pickle("data/video_data2.pkl")


		# If there's no more results, we break
		if len(video_search['items']) == 0:
			break

	return video_df

	

def get_response(query_type, parameters):
	'''
	inputs: query_type - the resource type that we need information for (e.g. playlists, channels, videos, etc.)
	        parameters - list of tuples correpsonding to the parameter names and their values in our query 
	'''
	base_url = 'https://www.googleapis.com/youtube/v3/'
	key = "mykey"

	parameters.append(('key', key))

	# Takes a list of tuples and encodes it into a url like:
	# 'part=contentDetails&key=mykey'
	url_suffix = urllib.urlencode(parameters)

	# Constructs the url to query and returns the json response
	http_endpoint = base_url + query_type + url_suffix
	response = requests.get(http_endpoint)
	response_json = response.json()
	return response_json

def get_video_data(video_snippet, channel_Id):

	video_id = video_snippet['resourceId']['videoId']

	video_channel = video_snippet['channelTitle']
	video_date = video_snippet['publishedAt']
	video_title = video_snippet['title']

	# Get the description, but only save the first line. The rest of the description tends
	# to be irrelevant and is just a list of links, etc. 
	video_description = video_snippet['description'].split('\n')[0].strip()
	video_description = video_description.replace(',', ' ')

	video_params = [('part', 'statistics,snippet'), ('id', video_id)]
	video_json = get_response('videos?', video_params)

	stats = video_json['items'][0]['statistics']

	video_view_count = get_value(stats, 'viewCount')
	video_like_count = get_value(stats, 'likeCount')
	video_dislike_count = get_value(stats, 'dislikeCount')
	video_comment_count = get_value(stats, 'commentCount')
	
	this_video = [video_id, video_channel, channel_Id, video_date, video_title, video_view_count,
			video_like_count, video_dislike_count, video_comment_count, video_description]
	return this_video

def get_value(dictionary, key):
	# Sometimes, keys don't exist so we want to write None in these cases. 
	if key in dictionary:
		return dictionary[key]
	else:
		return None

def main():
	username = "TheAlexJonesChannel"

	# If we haven't yet extracted the data
	video_data = get_all_videos(username)

	# If we have the dataset pickled
	#video_data = pd.read_pickle("data/video_data.pkl")

	# Write our data to a CSV
	#video_data.to_csv("data/video_data.csv", sep=',', encoding="utf-8", index = False, header=True)


	




if __name__ == "__main__":
    main()
