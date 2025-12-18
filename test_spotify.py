import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def initialize_spotify():
    """Initialize Spotify API"""
    global spotify_client
    SPOTIFY_SCOPE = "user-read-playback-state,user-modify-playback-state"
    
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=SPOTIFY_SCOPE,
            cache_path=".spotify_cache"
    ))

        
    print("Spotify API initialized successfully!")
    return True

def spotify_current():
    """Get current playing track"""
    try:
        if not spotify_client:
            print("Spotify is not configured.")
            return True
        
        current = spotify_client.current_playback()
        if current and current['is_playing']:
            track = current['item']['name']
            artist = current['item']['artists'][0]['name']
            print(f"Currently playing {track} by {artist}")
        else:
            print("Nothing is currently playing")
        return True
        
    except Exception as e:
        print(f"Error getting current track: {str(e)}")
        return True

def spotify_play():
    """Resume Spotify playback"""
    try:
        if not spotify_client:
            print("Spotify is not configured.")
            return True
        
        devices = spotify_client.devices()
        if not devices['devices']:
            print("No active Spotify devices found. Please open Spotify on a device.")
            return True
        
        spotify_client.start_playback()
        print("Playing music")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "NO_ACTIVE_DEVICE" in error_msg:
            print("No active Spotify device found. Please open Spotify.")
        elif "PREMIUM_REQUIRED" in error_msg:
            print("Spotify Premium is required for playback control.")
        else:
            print(f"Error playing music: {error_msg}")
        return True

def spotify_pause():
    """Pause Spotify playback"""
    try:
        if not spotify_client:
            print("Spotify is not configured.")
            return True
        
        spotify_client.pause_playback()
        print("Music paused")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "NO_ACTIVE_DEVICE" in error_msg:
            print("No active Spotify device found.")
        else:
            print(f"Error pausing music: {error_msg}")
        return True

def spotify_next():
    """Skip to next track"""
    try:
        if not spotify_client:
            print("Spotify is not configured.")
            return True
        
        spotify_client.next_track()
        print("Playing next track")
        return True
        
    except Exception as e:
        print(f"Error skipping track: {str(e)}")
        return True

def spotify_previous():
    """Go to previous track"""
    try:
        if not spotify_client:
            print("Spotify is not configured.")
            return True
        
        spotify_client.previous_track()
        print("Playing previous track")
        return True
        
    except Exception as e:
        print(f"Error going to previous track: {str(e)}")
        return True


load_dotenv()
initialize_spotify()



