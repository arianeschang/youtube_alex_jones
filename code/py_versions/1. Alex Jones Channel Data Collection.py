
# coding: utf-8

# # 1. Alex Jones Videos Data Collection 
# 
# On his YouTube channel, Alex Jones often posts videos attacking the credibility of mainstream media. We are interested in doing a small analysis of this phenonemon.
# 
# First, we'll need to collect the metadata for all the videos posted between January 1st, 2015 and May 4th, 2018 (as specified). 
# 
# For this code to work, you'll need to replace the youtube_key with a valid Google Youtube API token. 

# We're going to use the pandas library because it's useful and quick when manipulating large amounts of data. 

# In[ ]:


import requests
import urllib
import pandas as pd

###### CHANGE THIS #######
youtube_key = "mykey"
##########################


# We'll first need to write a function that accesses the YouTube API. We'll be able to use this everytime we need to query some information. This function accepts a list of tuples that contains the information for our query, as well as the type of resource (a playlist, channel, video, etc.) we are concerned with. It encodes the list of tuples into a string that can be used with the URL to request the JSON with the information necessary. 

# In[ ]:


def get_response(query_type, parameters):
    '''
    inputs: query_type - the resource type that we need information for 
                    (e.g. playlists, channels, videos, etc.)
            parameters - list of tuples with the parameter names 
                    and their values in our query 
                    (ex: [('part', 'contentDetails'), ('forUsername', 'username')]
    '''
    
    base_url = 'https://www.googleapis.com/youtube/v3/'
    
    # We always need to pass our key, so we'll add it to the list here
    parameters.append(('key', youtube_key))
    
    # Takes a list of tuples and encodes it into a url-ready string like:
    # 'part=contentDetails&key=mykey&forUsername=theAlexJonesChannel'
    url_suffix = urllib.urlencode(parameters)
    
    # Constructs the url to query and returns the json response
    http_endpoint = base_url + query_type + '?' + url_suffix
    response = requests.get(http_endpoint)
    response_json = response.json()
    
    return response_json


# We're going to need a helper function that searches through the json responses (dictionaries) for the values that we want. There are occasions in which the target value does not exist in the response. We will deal with this possibility by returning nonexistent values as None. Because we often need multiple values from one dictionary, we'll accept a list of keys, and return a list of the appropriate values from the dictionary. 

# In[ ]:


def get_values(json_dict, keys):
    '''
    Occasionally, the API will be missing a value that we need. In those cases, we 
    return None for that value. Because we often need multiple values from one
    JSON dictionary, we'll pass through a list of keys, and return a list of values. 
    
    Inputs: keys - a list of target keys that we need
            dictionary - the json dictionary that we are searching through
    '''

    return [json_dict[key] if key in json_dict else None for key in keys]


# We'll also need a function that retrieves the necessary information about the channel. Because we are only looking for Jones' uploads, we'll search for the 'uploads' playlist specifically. 

# In[ ]:


def get_channel_info(username):
    ''' Gets the ID of the users uploads playlist, and the channel ID'''

    playlist_params = [('part', 'contentDetails,id'), ('forUsername', username)]
    playlist_info = get_response('channels', playlist_params)
    
    playlist_ID = playlist_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    channel_Id = playlist_info['items'][0]['id']
    
    return playlist_ID, channel_Id


# To get a users' uploaded videos, we'll use the playlist ID and then gather all the information we need for each video in the uploads. 
# 
# The YouTube API only returns a maximum of 50 results with every call, so we'll need to move through the pages to get the data using the nextPageToken. We run an initial search with 50 results, and then loop through the rest of the pages. 
# 
# We also only want videos between Jan 1, 2015 and May 4 2018. We'll check each video to make sure it lies between these dates. The videos are listed in chronological order, so if it is more recent than May 4 (May 5 at 00:00), we continue through the loop but ignore this video. If it's older than Jan 1, 2015, then we know we're done and can return our dataframe. 

# In[ ]:


def get_all_videos(playlist_ID, channel_ID):
    '''
    Make a pandas dataframe with all the videos uploaded by this user. 
    
    Inputs: playlist_ID - the id of the uploads playlist
            channel_ID - the id of the users' channel, which will
            be written into our final dataframe
    Returns: video_df - the dataframe with all the videos' data
    '''
    
    video_data = []
    
    # The information we'll be collecting for each video
    headers = ['video_id', 'channel_title', 'channel_id', 'video_publish_date',
               'video_title', 'video_view_count', 'video_like_count', 
               'video_dislike_count', 'video_comment_count']
    
    # Get videos in the playlist
    video_params = [('part','snippet'), ('playlistId', playlist_ID), ('maxResults', 50)]
    video_search = get_response('playlistItems', video_params)
    
    # While there are more search results, we loop through each page of 50 results 
    while len(video_search['items']) > 0:
        
        for video in video_search['items']:
            
            video_snippet = video['snippet']

            # Ignore videos before May 4th, inclusive (so May 5 at 00:00) 
            if video_snippet['publishedAt'] > '2018-05-05T00:00:00Z':
                continue
                
            # Once we hit Jan 1, 2015, we are done and return the dataframe
            elif video_snippet['publishedAt'] < '2015-01-01T00:00:00Z':
                video_df = pd.DataFrame(video_data, columns=headers)
                return video_df
            
            # Get the information we need and then add to our whole list of data. 
            this_video_data = get_video_data(video_snippet, channel_ID)
            video_data.append(this_video_data)
            print ("Gathering video ID: " + str(this_video_data[0]) + \
                                ", \n title: " + this_video_data[4])

        # Get the next video using the nextPageToken
        next_video = video_params + [('pageToken', video_search['nextPageToken'])]
        video_search = get_response('playlistItems', next_video)

    video_df = pd.DataFrame(video_data, columns=headers)
    return video_df


# In each video, we'll need to extract the information we want. To get the like, dislike, view and comment counts, we'll need to run one more query to the YouTube API for each individual video.

# In[ ]:


def get_video_data(video_snippet, channel_Id):
    
    '''
    Takes a snippet of information about a video and turns it into a set of attributes
    that we can add to our dataset. We query the YouTube API using a video ID to get the
    relevant statistics for that video. 
    
    Inputs: video_snippet - json object containing relevant information about the video
            channel_Id - the channel ID of our user
    Returns: video_data - a list with all the information we want for this video
    '''

    video_id = video_snippet['resourceId']['videoId']

    # Gather some information that we can get from the video snippet in the playlist results
    [video_channel, video_date, video_title] = \
           get_values(video_snippet, ['channelTitle', 'publishedAt', 'title'])
        
    # Send another query to find the statistics that we need for the individual videos
    video_params = [('part', 'statistics'), ('id', video_id)]
    video_json = get_response('videos', video_params)

    # Get the viewer statistics about this video
    [video_items] = get_values(video_json, ['items'])
    stats = video_items[0]['statistics']
    
    # Grab all our information from the stats JSON response and return this row
    [video_view_count, video_like_count, video_dislike_count, video_comment_count] = \
            get_values(stats, ['viewCount', 'likeCount', 'dislikeCount', 'commentCount'])

    return [video_id, video_channel, channel_Id, video_date, video_title, video_view_count,
            video_like_count, video_dislike_count, video_comment_count]


# In[ ]:


def main():
    username = "TheAlexJonesChannel"
    
    # Start with getting the info we need from the username, and channel
    playlist_ID, channel_ID = get_channel_info(username)

    # Gather all the video data.
    video_df = get_all_videos(playlist_ID, channel_ID)

    # Write our data to a CSV (changed for now to metadata2 to not overwrite)
    video_df.to_csv("../data/video_metadata2.csv", sep=',', encoding="utf-8", 
                    index = False, header=True)



# In[ ]:


if __name__ == "__main__":
    main()

