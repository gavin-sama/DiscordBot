import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv
import requests
import random

load_dotenv()
TOKEN = os.getenv('discord_token')
APIKEY = os.getenv('YOUTUBE_APIKEY')

if not TOKEN:
    raise ValueError("Discord token not found in .env file.")
if not APIKEY:
    raise ValueError("YouTube API key not found in .env file.")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

yt_dl_options = {
    "format": "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -ar 48000 -ac 2 -b:a 192k -filter:a "volume=0.5"',
}

voice_clients = {}
queues = {}

# Coding-themed jokes and responses
coding_responses = [
    "I'm like a void function, I just work—no return required!",
    "Music with me? Nothing's ever null!",
    "I'm NULL if I'm not jamming with you.",
    "When you're with me, the tunes are always in sync.",
    "Don't throw an exception—play some jams instead!",
    "Binary for you: ",
    "I'm like a linked list of songs—always pointing to the next track!",
    "I'm the head node of this music queue. 🎵",
    "No garbage collection here—just pure jams.",
    "Catch me throwing tunes, not errors!",
    "You jam with me, and I'll never segfault.",
    "Give me.head() and I'll fetch the best vibes.",
]

# Convert text to binary (helper function for jokes)
def text_to_binary(text):
    return " ".join(format(ord(char), "08b") for char in text)

# Function to search for a YouTube video by name
def get_video_url(search_query):
    try:
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
        response.raise_for_status()
        data = response.json()
        video_id = data['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    except (KeyError, IndexError):
        return None
    except requests.RequestException as e:
        print(f"Error fetching video URL: {e}")
        return None

@client.event
async def on_ready():
    print(f'{client.user} is now jamming!')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # Respond to mentions
    if client.user in message.mentions:
        response = random.choice(coding_responses)
        
        # Handle binary-specific jokes
        if "Binary for you:" in response:
            binary_message = text_to_binary("Jamming")
            await message.channel.send(f"{response} {binary_message}")
        else:
            await message.channel.send(response)
        return  # Avoid processing commands after responding to a mention

    # Music commands below
    if message.content.startswith("?play"):
        try:
            if message.guild.id not in voice_clients:
                voice_client = await message.author.voice.channel.connect()
                voice_clients[message.guild.id] = voice_client
            else:
                voice_client = voice_clients[message.guild.id]

            command_parts = message.content.split(maxsplit=1)
            if len(command_parts) < 2:
                await message.channel.send("Please provide a song name or YouTube URL.")
                return

            search_input = command_parts[1]
            if search_input.startswith("http"):
                url = search_input
            else:
                url = get_video_url(search_input)
                if not url:
                    await message.channel.send("Could not find a video for the given name.")
                    return

            if message.guild.id not in queues:
                queues[message.guild.id] = []

            queues[message.guild.id].append(url)

            if not voice_client.is_playing():
                await play_next_in_queue(message.guild.id, message)
            else:
                await message.channel.send("Song added to queue!")

        except Exception as e:
            print(f"Error in ?play command: {e}")
            await message.channel.send("An error occurred while trying to play the song.")

    elif message.content.startswith("?pause"):
        try:
            guild_id = message.guild.id
            if guild_id in voice_clients and voice_clients[guild_id].is_playing():
                voice_clients[guild_id].pause()
                await message.channel.send("Playback paused.")
            else:
                await message.channel.send("No song is currently playing.")
        except Exception as e:
            print(f"Error in ?pause command: {e}")
            await message.channel.send("Could not pause playback.")

    elif message.content.startswith("?resume"):
        try:
            guild_id = message.guild.id
            if guild_id in voice_clients and voice_clients[guild_id].is_paused():
                voice_clients[guild_id].resume()
                await message.channel.send("Playback resumed.")
            else:
                await message.channel.send("No song is paused.")
        except Exception as e:
            print(f"Error in ?resume command: {e}")
            await message.channel.send("Could not resume playback.")

    elif message.content.startswith("?queue"):
        guild_id = message.guild.id
        if guild_id in queues and queues[guild_id]:
            queue_list = "\n".join([f"{i + 1}. {url}" for i, url in enumerate(queues[guild_id])])
            await message.channel.send(f"Current queue:\n{queue_list}")
        else:
            await message.channel.send("The queue is empty.")

    elif message.content.startswith("?skip"):
        guild_id = message.guild.id
        try:
            if guild_id in voice_clients and voice_clients[guild_id].is_playing():
                voice_clients[guild_id].stop()
                await message.channel.send("Skipped to the next song.")
            else:
                await message.channel.send("No song is currently playing.")
        except Exception as e:
            print(f"Error in ?skip command: {e}")
            await message.channel.send("Could not skip playback.")

    elif message.content.startswith("?stop"):
        guild_id = message.guild.id
        try:
            if guild_id in voice_clients:
                await voice_clients[guild_id].disconnect()
                del voice_clients[guild_id]
                queues[guild_id] = []
                await message.channel.send("Playback stopped and queue cleared.")
        except Exception as e:
            print(f"Error in ?stop command: {e}")
            await message.channel.send("Could not stop playback.")

async def play_next_in_queue(guild_id, message):
    if guild_id not in queues or not queues[guild_id]:
        return

    url = queues[guild_id].pop(0)
    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        song = data["url"]

        current_folder = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(current_folder, "ffmpeg", "ffmpeg.exe")
        player = discord.FFmpegOpusAudio(song, executable=ffmpeg_path, **ffmpeg_options)

        voice_clients[guild_id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(
            play_next_in_queue(guild_id, message), client.loop
        ))
        await message.channel.send(f"Now playing: {data.get('title', 'Unknown Title')}")
    except Exception as e:
        print(f"Error in play_next_in_queue: {e}")
        await message.channel.send("An error occurred while trying to play the next song.")

# Run the bot
client.run(TOKEN)
