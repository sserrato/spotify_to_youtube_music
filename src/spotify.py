"""Spotify API client for fetching playlists and tracks."""

import os
import re
from configparser import ConfigParser
from typing import List, Dict, Optional

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


def get_config_value(config: ConfigParser, section: str, key: str, env_var: str) -> Optional[str]:
    """Get config value from env var (priority) or config file."""
    value = os.environ.get(env_var)
    if value:
        return value
    try:
        return config.get(section, key)
    except Exception:
        return None


class SpotifyClient:
    """Client for interacting with Spotify API."""

    def __init__(self, config_path: str = "settings.ini"):
        """Initialize Spotify client with credentials from env vars or config file.

        Environment variables take priority over settings.ini:
        - SPOTIFY_CLIENT_ID
        - SPOTIFY_CLIENT_SECRET
        - SPOTIFY_USE_OAUTH (true/false)
        """
        config = ConfigParser()
        config.read(config_path)

        client_id = get_config_value(config, "spotify", "client_id", "SPOTIFY_CLIENT_ID")
        client_secret = get_config_value(config, "spotify", "client_secret", "SPOTIFY_CLIENT_SECRET")

        use_oauth_str = get_config_value(config, "spotify", "use_oauth", "SPOTIFY_USE_OAUTH")
        use_oauth = use_oauth_str and use_oauth_str.lower() in ("true", "1", "yes")

        if not client_id or not client_secret:
            raise ValueError(
                "Spotify credentials not found. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET "
                "environment variables, or configure them in settings.ini"
            )

        if use_oauth:
            # OAuth flow for accessing private playlists and liked songs
            auth_manager = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri="http://127.0.0.1:8888/callback",
                scope="user-library-read playlist-read-private",
            )
        else:
            # Client Credentials for public playlists only
            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret,
            )

        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def extract_playlist_id(self, url: str) -> str:
        """Extract playlist ID from Spotify URL or URI."""
        # Handle full URLs like https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
        match = re.search(r"playlist[/:]([a-zA-Z0-9]+)", url)
        if match:
            return match.group(1)
        # Assume it's already a playlist ID
        return url

    def get_playlist(self, playlist_url: str) -> dict:
        """Fetch playlist metadata."""
        playlist_id = self.extract_playlist_id(playlist_url)
        return self.sp.playlist(playlist_id, fields="id,name,description,owner")

    def get_playlist_tracks(self, playlist_url: str) -> List[Dict]:
        """Fetch all tracks from a playlist with pagination."""
        playlist_id = self.extract_playlist_id(playlist_url)
        tracks = []
        offset = 0
        limit = 100  # Spotify max per request

        while True:
            response = self.sp.playlist_tracks(
                playlist_id,
                offset=offset,
                limit=limit,
                fields="items(track(name,artists,album,duration_ms)),total",
            )

            for item in response["items"]:
                track = item.get("track")
                if track is None:
                    continue  # Skip unavailable tracks

                tracks.append(self._build_track_info(track))

            # Check if we have more tracks to fetch
            if offset + limit >= response["total"]:
                break
            offset += limit

        return tracks

    def _build_track_info(self, track: dict) -> dict:
        """Extract relevant track information."""
        artists = [artist["name"] for artist in track.get("artists", [])]
        return {
            "name": track.get("name", ""),
            "artist": artists[0] if artists else "",
            "artists": artists,
            "album": track.get("album", {}).get("name", ""),
            "duration_s": track.get("duration_ms", 0) // 1000,
        }

    def get_liked_songs(self, limit: Optional[int] = None) -> List[Dict]:
        """Fetch user's liked songs (requires OAuth)."""
        tracks = []
        offset = 0
        batch_size = 50  # Spotify max for saved tracks

        while True:
            response = self.sp.current_user_saved_tracks(offset=offset, limit=batch_size)

            for item in response["items"]:
                track = item.get("track")
                if track:
                    tracks.append(self._build_track_info(track))

            if offset + batch_size >= response["total"]:
                break
            if limit and len(tracks) >= limit:
                break
            offset += batch_size

        return tracks[:limit] if limit else tracks

    def get_user_playlists(self, user_id: Optional[str] = None) -> List[Dict]:
        """Fetch all playlists for a user."""
        playlists = []
        offset = 0
        limit = 50

        while True:
            if user_id:
                response = self.sp.user_playlists(user_id, offset=offset, limit=limit)
            else:
                response = self.sp.current_user_playlists(offset=offset, limit=limit)

            for playlist in response["items"]:
                playlists.append({
                    "id": playlist["id"],
                    "name": playlist["name"],
                    "owner": playlist["owner"]["display_name"],
                    "tracks_total": playlist["tracks"]["total"],
                    "url": playlist["external_urls"]["spotify"],
                })

            if offset + limit >= response["total"]:
                break
            offset += limit

        return playlists
