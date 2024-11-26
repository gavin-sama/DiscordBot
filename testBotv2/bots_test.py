import pytest
from unittest.mock import Mock

# basic test definitions
def add(a, b):
    """Adds two numbers."""
    return a + b

def add_extra(a, b):
    """Adds two numbers and adds an extra 10."""
    return a + b + 10

# basic test functions
def test_add():
    assert add(2, 3) == 5

def test_add_extra():
    assert add_extra(2, 3) == 15






# discord functionality definitions
def send_message(channel, message):
    """Simulates sending a message to a Discord channel."""
    if not channel:
        raise ValueError("Channel is required.")
    return f"Message sent to {channel}: {message}"

def is_in_voice_channel(user):
    """Checks if the user is in a voice channel."""
    return bool(user.get("voice_channel"))

def add_to_queue(song_url, queue):
    """Adds a song URL to the music queue."""
    queue.append(song_url)
    return queue

def play_next_song(queue):
    """Simulates playing the next song in the queue."""
    if not queue:
        raise ValueError("Queue is empty.")
    return queue.pop(0)

def mute_user(user):
    """Simulates muting a user."""
    user["muted"] = True
    return user

def unmute_user(user):
    """Simulates unmuting a user."""
    user["muted"] = False
    return user


# basic discord test functions
def test_send_message():
    assert send_message("general", "Hello!") == "Message sent to general: Hello!"
    with pytest.raises(ValueError):
        send_message(None, "Hello!")

def test_is_in_voice_channel():
    user_in_voice = {"voice_channel": "General"}
    user_not_in_voice = {}
    
    assert is_in_voice_channel(user_in_voice) == True
    assert is_in_voice_channel(user_not_in_voice) == False

def test_add_to_queue():
    queue = []
    result = add_to_queue("song_url_1", queue)
    assert result == ["song_url_1"]
    result = add_to_queue("song_url_2", queue)
    assert result == ["song_url_1", "song_url_2"]

def test_play_next_song():
    queue = ["song_url_1", "song_url_2"]
    assert play_next_song(queue) == "song_url_1"
    assert queue == ["song_url_2"]
    with pytest.raises(ValueError):
        play_next_song([])

def test_mute_user():
    user = {"name": "TestUser", "muted": False}
    result = mute_user(user)
    assert result["muted"] == True

def test_unmute_user():
    user = {"name": "TestUser", "muted": True}
    result = unmute_user(user)
    assert result["muted"] == False



## ERROR TESTING  -- if the specified error is raised, the test will pass.
def test_add_invalid_input():
    with pytest.raises(TypeError):
        add("string", 3)
    with pytest.raises(TypeError):
        add(2, None)


def test_send_message_invalid_channel():
    with pytest.raises(ValueError): 
        send_message(None, "Hello!")



