api_key = "AIzaSyBbghAhh2hBgqgJRb10k9HENFLWjCJeTzw"

from apiclient.discovery import build
import datetime
import pandas as pd
import numpy as np

youtube = build('youtube', 'v3', developerKey=api_key)

#Return Youtube channel ID
q=input("Type your favor Youtube channel here: ")
request = youtube.search().list(part='snippet',
                            q=q,
                            type='channel',
                            maxResults=1)
respond = request.execute()
channel_id = respond["items"][0]["id"]["channelId"]


#Get channel video IDs by channel ID
def get_channel_videos(channel_id):
    # all video are in "Upload" section. Get Uploads playlist id
    res = youtube.channels().list(id=channel_id, 
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    videos = []
    next_page_token = None
    
    while 1:
        res = youtube.playlistItems().list(playlistId=playlist_id, 
                                           part='snippet', 
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        videos += res['items']
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
    
    return videos
videos = get_channel_videos(channel_id)

def get_videos_stats(video_ids):
    stats = []
    for i in range(0, len(video_ids), 50):
        res = youtube.videos().list(id=','.join(video_ids[i:i+50]),
                                   part='statistics').execute()
        stats += res['items']
        
    return stats
video_ids = list(map(lambda x:x['snippet']['resourceId']['videoId'], videos))
stats = get_videos_stats(video_ids)

videoTitle = []
videoId = []
videoView = []
videoLike = []
videoDislike = []
videoComment = []
publishedAt=[]
publishedAt_string=[]
channelTitle = []
Year=[]
Month=[]
Day=[]
videoTitle =[videos[video]["snippet"]["title"] for video in range(len(videos))]
channelTitle = [videos[video]["snippet"]['channelTitle'] for video in range(len(videos))]

publishedAt=[videos[video]["snippet"]['publishedAt'].split('T')[0][2:] for video in range(len(videos))]
for i in publishedAt:
    publishedAt_string.append(datetime.datetime.strptime(i, '%y-%m-%d').date())
    Year.append(datetime.datetime.strptime(i, '%y-%m-%d').year)
    Month.append(datetime.datetime.strptime(i, '%y-%m-%d').month)
    Day.append(datetime.datetime.strptime(i, '%y-%m-%d').weekday())
    
for data in range(len(stats)):
    videoView.append(stats[data]['statistics']['viewCount'])
#check if the value is in the key, avoid raising KeyError
    if 'likeCount' in stats[data]['statistics'].keys():
        videoLike.append(stats[data]['statistics']['likeCount']) 
    else:
        videoLike.append(np.nan)
    if 'dislikeCount' in stats[data]['statistics'].keys():
        videoDislike.append(stats[data]['statistics']['dislikeCount']) 
    else:
        videoDislike.append(np.nan)
    if 'commentCount' in stats[data]['statistics'].keys():
        videoComment.append(stats[data]['statistics']['commentCount']) 
    else:
        videoComment.append(np.nan)

dmap = {0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'}
month= {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
data_={'channelTitle':channelTitle,'videoTitle':videoTitle,'videoView':videoView,
      'videoLike':videoLike,'videoDislike':videoDislike,'videoComment':videoComment,
      'publishedAt':publishedAt,'publishedAt_string':publishedAt_string,'Year':Year,
      'Month':Month,'DayofWeek':Day}
df=pd.DataFrame(data_)
df['publishedAt_month']=df['publishedAt_string'].apply(lambda x:str(x)[:7])
# df.drop('publishedAt',axis=1,inplace=True)
df['Month_str']=df['Month'].map(month)
df['DayofWeek']=df['DayofWeek'].map(dmap)
df.to_csv('Schannel1.csv')