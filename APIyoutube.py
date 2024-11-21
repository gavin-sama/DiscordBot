import os
import requests
import requests_cache
from retry_requests import retry
from dotenv import load_dotenv, find_dotenv

"""
load_dotenv()

APIKEY = os.getenv('YOUTUBE_APIKEY')

print(f"Loaded API Key: {APIKEY}")

if APIKEY is None:
    raise ValueError("YOUTUBE_APIKEY not found. Check .env file.")
"""


# Get youtube video URL
def get_video_url(name):
    response = requests.get(f'https://www.googleapis.com/youtube/v3/search?key={APIKEY}&q={name}&type=video&part=snippet&maxResults=1').json()
    video_id = response['items'][0]['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return video_url

# Get youtube video details
def get_video_details(name):
    response = requests.get(f'https://www.googleapis.com/youtube/v3/search?key={APIKEY}&q={name}&type=video&part=snippet&maxResults=1').json()
    video_id = response['items'][0]['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Second API call to get video details
    video_response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?key={APIKEY}&id={video_id}&part=snippet,statistics').json()

    # Extract desired information
    video_info = video_response['items'][0]
    title = video_info['snippet']['title']
    channel_name = video_info['snippet']['channelTitle']
    view_count = video_info['statistics']['viewCount']

    return {
        "video_url": video_url,
        "title": title,
        "channel_name": channel_name,
        "view_count": view_count
    }



if __name__ == "__main__":
    videoName = 'We Are One (Ole Ola)'
    #print(get_video_url(videoName))

    details = get_video_details(videoName)
    print("Video URL:", details['video_url'])
    print("Title:", details['title'])
    print("Channel Name:", details['channel_name'])
    print("Views Count:", details['view_count'])
