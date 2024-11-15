import discord
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


print("DISCORD_TOKEN loaded:", DISCORD_TOKEN) 

if DISCORD_TOKEN is None:
    print("Error: DISCORD_TOKEN not found in .env file.")
else:
    print("DISCORD_TOKEN loaded successfully.")

# Initialize the bot
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # If the message starts with the command !track
    if message.content.startswith("!track"):
        # Parse the track name from the message
        track_name = message.content[len("!track "):]

        # Set up RapidAPI endpoint, headers, and parameters
        url = "https://shazam8.p.rapidapi.com/track/search"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "shazam8.p.rapidapi.com"
        }
        querystring = {"query": track_name}

        # Send a request to the API
        response = requests.get(url, headers=headers, params=querystring)
        
        # Check the API response status
        if response.status_code == 200:
            data = response.json()
            # Ensure that results exist in the response
            if 'tracks' in data and len(data['tracks']['hits']) > 0:
                # Access the title and artist information
                track = data['tracks']['hits'][0]['track']
                title = track.get("title", "Unknown")
                artist = track.get("subtitle", "Unknown")  # Some APIs use 'subtitle' for artist

                # Send the information back to the Discord channel
                await message.channel.send(f"Track: {title}\nArtist: {artist}")
            else:
                await message.channel.send("No track information found.")
        else:
            await message.channel.send("Couldn't fetch track information.")

# Run the bot with the token
client.run(DISCORD_TOKEN)

