"""ApplePye"""

import sys
import time
import json
import asyncio
import platform
import pylast as fm
import windows_functions as win


async def get_song_info():
    """Gets the currently playing song's title and artist
    returns:
        dict: A dictionary containing the song title and artist."""
    if platform.system() == 'Windows':
        return await win.get_song_info()
    sys.exit()


async def song_playing():
    """Checks if a song is currently playing in Apple Music.
    Returns:
        bool: True if a song is playing, False otherwise or if the session is paused."""
    if platform.system() == 'Windows':
        return await win.song_playing()
    sys.exit()


async def get_song_position():
    """Gets the song's current position in seconds from Windows' Media Controls.
    returns:
        int: The song's current position in seconds."""
    if platform.system() == 'Windows':
        return await win.get_song_position()
    sys.exit()


def is_apple_music_running():
    """Checks if Apple Music is running.
    Returns:
        bool: True if Apple Music is running, False otherwise."""
    if platform.system() == 'Windows':
        return win.is_apple_music_running()
    sys.exit()


if platform.system() != 'Windows':
    print("Not running on Windows")
    sys.exit()
previous_song_info = [None, None]


def authenticate_last_fm():
    """Authenticates with Last.fm using the credentials stored in auth.json.

    Returns:
        pylast.LastFMNetwork: A Last.fm network object.
    """
    try:
        with open('auth.json', 'r', encoding='utf-8') as f:
            auth_data = json.load(f)
            return fm.LastFMNetwork(
                api_key=auth_data['api_key'],
                api_secret=auth_data['api_secret'],
                username=auth_data['username'],
                password_hash=auth_data['password_hash']
            )
    except FileNotFoundError:
        print("Error: auth.json file not found")
    except json.JSONDecodeError:
        print("Error: auth.json file is not in valid JSON format")
    except KeyError as err:
        print(f"Error: Missing key {err} in auth.json file")
    return None


async def update_now_playing(last_fm, song_info):
    """Updates the 'now playing' information on Last.fm without scrobbling.

    Args:
        last_fm (pylast.LastFMNetwork): A Last.fm network object.
        song_info (dict): A dictionary containing the current song title and artist.
    """
    none_dict = dict(zip(previous_song_info, [None, None]))
    empty_dict = dict(zip(previous_song_info, ["", ""]))
    if (
            await song_playing()
            and song_info
            and song_info not in (none_dict, empty_dict)
    ):
        try:
            if song_info != previous_song_info:
                last_fm.update_now_playing(
                    artist=song_info['artist'],
                    title=song_info['title']
                )
                print("Updated 'now playing' on Last.fm:",
                      song_info['artist'],
                      "-", song_info['title']
                      )
                previous_song_info[0] = song_info['artist']
                previous_song_info[1] = song_info['title']
        except fm.NetworkError as err:
            print(f"Error updating 'now playing' on Last.fm: {err}")


async def update_now_playing_thread(last_fm):
    """Thread function to update 'now playing' every 10 seconds."""
    while True:
        song_info = await get_song_info()
        await update_now_playing(last_fm, song_info)
        time.sleep(10)


async def scrobble(last_fm, song_info):
    """Scrobbles a song to Last.fm.

    Args:
        last_fm (pylast.LastFMNetwork): A Last.fm network object.
        song_info (dict): A dictionary containing the song title and artist.
    """
    if await song_playing():
        timestamp = int(time.time())
        last_fm.scrobble(
            artist=song_info['artist'],
            title=song_info['title'],
            timestamp=timestamp
        )
        print(
            "Scrobbled", song_info['artist'],
            "-", song_info['title'],
            "at", timestamp,
            "to Last.fm."
        )


def get_song_duration(last_fm, song_info):
    """Gets the duration of the currently playing song from Last.fm.

    Args:
        last_fm (pylast.LastFMNetwork): A Last.fm network object.
        song_info (dict): A dictionary containing the song title and artist.

    Returns:
        int: The duration of the currently playing song in seconds.
    """
    try:
        track = last_fm.get_track(song_info['artist'], song_info['title'])
        song_duration = max(int(track.get_duration() / 1000), 60)
    except fm.WSError:
        song_duration = 60
    return song_duration


# noinspection PyAsyncCall
async def scrobble_loop():
    """The main scrobbling loop."""
    last_fm = authenticate_last_fm()

    if last_fm is not None:
        print("Successfully authenticated with Last.fm as " +
              last_fm.username + ".")

        # Start the 'now playing' update thread
        asyncio.create_task(update_now_playing_thread(last_fm))

        while True:
            if is_apple_music_running():
                current_song_info = await get_song_info()
                # Check if the player is currently playing
                if await song_playing():
                    start_time = int(time.time())
                    playback_time = 0
                    try:
                        song_duration = get_song_duration(
                            last_fm, current_song_info)
                        print("Song duration:", song_duration)
                    except fm.WSError:
                        print(
                            "Error getting duration for:",
                            current_song_info['artist'],
                            "-", current_song_info['title']
                        )
                        print("Defaulting to 60 seconds.")
                        song_duration = 60
                    threshold = int(song_duration / 2) + 1
                    while playback_time <= threshold and current_song_info:
                        await asyncio.sleep(1)
                        playback_time = int(time.time()) - start_time
                        print("Playback time:", playback_time)
                        print("Scrobble threshold:", threshold)
                        current_song_info = await get_song_info()
                        if await song_playing() and playback_time >= threshold:
                            await scrobble(last_fm, current_song_info)
                            start_time = int(time.time())
                            playback_time = 0
                        else:
                            print("Song playback didn't meet scrobbling criteria.")
                else:
                    print(int(time.time()), "Player is paused.")
            else:
                print(int(time.time()), "Apple Music is not running.")

            await asyncio.sleep(5)
    else:
        print(
            "Last.fm authentication failed!",
            "Please check your credentials."
        )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrobble_loop())
