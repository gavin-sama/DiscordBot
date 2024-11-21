"""
import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv
import requests
import requests_cache
from retry_requests import retry
from dotenv import load_dotenv, find_dotenv

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('discord_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    queues = {}
    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

    @client.event
    async def on_ready():
        print(f'{client.user} is now jamming')

    @client.event
    async def on_message(message):
        if message.content.startswith("?play"):
            try:
                voice_client = await message.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
            except Exception as e:
                print(e)

            try:
                url = message.content.split()[1]

                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

                song = data['url']
                ""'player = discord.FFmpegOpusAudio(song, **ffmpeg_options)""'
                ""'player = discord.FFmpegOpusAudio(song, executable="Users\\cooke\\OneDrive\\cookei@etsu.edu\\VS Code\\testBot\\ffmpeg\\ffmpeg.exe", **ffmpeg_options)""'
                current_folder = os.path.dirname(os.path.abspath(__file__))
                ffmpeg_path = os.path.join(current_folder, "ffmpeg", "ffmpeg.exe")
                player = discord.FFmpegOpusAudio(song, executable=ffmpeg_path, **ffmpeg_options)

                voice_clients[message.guild.id].play(player)
            except Exception as e:
                print(e)

        if message.content.startswith("?pause"):
            try:
                voice_clients[message.guild.id].pause()
            except Exception as e:
                print(e)

        if message.content.startswith("?resume"):
            try:
                voice_clients[message.guild.id].resume()
            except Exception as e:
                print(e)

        if message.content.startswith("?stop"):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
            except Exception as e:
                print(e)
    
 
    
    
    load_dotenv()

    APIKEY = os.getenv('YOUTUBE_APIKEY')

    print(f"Loaded API Key: {APIKEY}")

    if APIKEY is None:
        raise ValueError("YOUTUBE_APIKEY not found. Check .env file.")
    


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
    
    client.run(TOKEN)
    client.run(APIKEY)
    """

import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
TOKEN = os.getenv('discord_token')
APIKEY = os.getenv('YOUTUBE_APIKEY')

# Validate tokens
if not TOKEN:
    raise ValueError("Discord token not found in .env file.")
if not APIKEY:
    raise ValueError("YouTube API key not found in .env file.")

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# YouTube downloader setup
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.25"'
}

# Store voice clients
voice_clients = {}


# Function to search for a YouTube video by name
def get_video_url(search_query):
    try:
        # Make YouTube API call
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/search',
            params={
                'key': APIKEY,
                'q': search_query,
                'type': 'video',
                'part': 'snippet',
                'maxResults': 1
            }
        )
        response.raise_for_status()  # Ensure request was successful
        data = response.json()
        video_id = data['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    except (KeyError, IndexError):
        return None  # Return None if no results found
    except requests.RequestException as e:
        print(f"Error fetching video URL: {e}")
        return None


@client.event
async def on_ready():
    print(f'{client.user} is now jamming!')


@client.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from bots

    if message.content.startswith("?play"):
        try:
            # Connect to the voice channel
            if message.guild.id not in voice_clients:
                voice_client = await message.author.voice.channel.connect()
                voice_clients[message.guild.id] = voice_client
            else:
                voice_client = voice_clients[message.guild.id]

            # Get the search term or URL
            command_parts = message.content.split(maxsplit=1)
            if len(command_parts) < 2:
                await message.channel.send("Please provide a song name or YouTube URL.")
                return

            search_input = command_parts[1]
            if search_input.startswith("http"):  # Input is a URL
                url = search_input
            else:  # Input is a song name/artist
                url = get_video_url(search_input)
                if not url:
                    await message.channel.send("Could not find a video for the given name.")
                    return

            # Fetch audio stream
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            song = data['url']

            # Play the song
            current_folder = os.path.dirname(os.path.abspath(__file__))
            ffmpeg_path = os.path.join(current_folder, "ffmpeg", "ffmpeg.exe")
            player = discord.FFmpegOpusAudio(song, executable=ffmpeg_path, **ffmpeg_options)
            voice_client.play(player)
            await message.channel.send(f"Now playing: {data.get('title', 'Unknown Title')}")

        except Exception as e:
            print(f"Error in ?play command: {e}")
            await message.channel.send("An error occurred while trying to play the song.")

    elif message.content.startswith("?pause"):
        try:
            voice_clients[message.guild.id].pause()
            await message.channel.send("Playback paused.")
        except Exception as e:
            print(f"Error in ?pause command: {e}")
            await message.channel.send("Could not pause playback.")

    elif message.content.startswith("?resume"):
        try:
            voice_clients[message.guild.id].resume()
            await message.channel.send("Playback resumed.")
        except Exception as e:
            print(f"Error in ?resume command: {e}")
            await message.channel.send("Could not resume playback.")

    elif message.content.startswith("?stop"):
        try:
            voice_clients[message.guild.id].stop()
            await voice_clients[message.guild.id].disconnect()
            del voice_clients[message.guild.id]
            await message.channel.send("Playback stopped and disconnected.")
        except Exception as e:
            print(f"Error in ?stop command: {e}")
            await message.channel.send("Could not stop playback.")


# Run the bot
client.run(TOKEN)
