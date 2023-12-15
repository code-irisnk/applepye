"""This module contains functions that get data from Windows' Media Controls API."""
import time
import psutil as ps
import winsdk.windows.media.control as mc


def is_apple_music_running():
    """Checks if Apple Music is running on Windows.

    Returns:
        bool: True if Apple Music is running, False otherwise.
    """
    all_processes = ps.process_iter(['pid', 'name'])
    return any(proc.name() == 'AppleMusic.exe' for proc in all_processes)


async def get_song_info():
    """Gets the currently playing song's title and artist from Windows' Media Controls.

    Returns:
        dict: A dictionary containing the song title and artist.
    """
    sys_controls = mc.GlobalSystemMediaTransportControlsSessionManager
    session_manager = await sys_controls.request_async()
    current_session = session_manager.get_current_session()
    song_info = {}

    if current_session:
        media_properties = await current_session.try_get_media_properties_async()

        if media_properties:
            song_info['title'] = media_properties.title
            if media_properties.album_artist:
                song_info['artist'] = media_properties.album_artist.split(' — ')[
                    0]
            else:
                song_info['artist'] = "Unknown Artist"
        else:
            print("No media properties available.")
    else:
        print("No current session available.")

    return song_info


async def get_song_position():
    """Gets the song's current position in seconds from Windows' Media Controls.
    returns:
        int: The song's current position in seconds.
    """
    sys_controls = mc.GlobalSystemMediaTransportControlsSessionManager
    session_manager = await sys_controls.request_async()
    current_session = session_manager.get_current_session()
    if current_session:
        timeline_properties = current_session.get_timeline_properties()
        if timeline_properties:
            return timeline_properties.position.total_seconds()
        return 0


async def song_playing():
    """Checks if a song is currently playing in Apple Music.

    Returns:
        bool: True if a song is playing, False otherwise or if the session is paused.
    """
    sys_controls = mc.GlobalSystemMediaTransportControlsSessionManager
    session_manager = await sys_controls.request_async()
    current_session = session_manager.get_current_session()

    if current_session:

        media_properties = await current_session.try_get_media_properties_async()
        initial_position = await get_song_position()
        time.sleep(2)
        current_position = await get_song_position()
        if "AppleMusic" in current_session.source_app_user_model_id:
            if media_properties and initial_position != current_position:
                return True
            print("Song is paused on Apple Music.")
            return False
        print("Song is not playing on Apple Music.")
        return False
    print("No app is playing music.")
    return False
