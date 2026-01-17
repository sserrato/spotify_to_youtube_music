"""YouTube Music API client for searching and creating playlists."""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Optional

from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials


def get_oauth_path() -> Optional[str]:
    """Get path to oauth.json file, or None if not found."""
    # Check env var first
    env_path = os.environ.get("YTMUSIC_OAUTH_JSON")
    if env_path and Path(env_path).exists():
        return env_path

    # Check project root
    project_root = Path(__file__).parent.parent
    oauth_path = project_root / "oauth.json"
    if oauth_path.exists():
        return str(oauth_path)

    # Check current directory
    if Path("oauth.json").exists():
        return "oauth.json"

    return None


class YTMusicClient:
    """Client for interacting with YouTube Music API."""

    def __init__(self, oauth_path: Optional[str] = None, require_auth: bool = False):
        """Initialize YouTube Music client.

        Args:
            oauth_path: Path to oauth.json file. If not provided, searches
                        in standard locations.
            require_auth: If True, raise error if no auth found. If False,
                          use unauthenticated mode (search only).
        """
        if oauth_path is None:
            oauth_path = get_oauth_path()

        # Always use unauthenticated client for search (more reliable)
        self.yt = YTMusic()

        # Store auth info for playlist operations
        self._oauth_path = oauth_path
        self._auth_client = None
        self.authenticated = oauth_path is not None

        if require_auth and not oauth_path:
            raise FileNotFoundError(
                "YouTube Music oauth.json not found. Run 'ytmusicapi oauth' to authenticate."
            )

    def _get_auth_client(self) -> YTMusic:
        """Get authenticated client for playlist operations (lazy loading)."""
        if self._auth_client is None and self._oauth_path:
            with open(self._oauth_path) as f:
                oauth_data = json.load(f)

            client_id = oauth_data.pop("client_id", None)
            client_secret = oauth_data.pop("client_secret", None)

            if client_id and client_secret:
                oauth_creds = OAuthCredentials(client_id=client_id, client_secret=client_secret)
                self._auth_client = YTMusic(oauth_data, oauth_credentials=oauth_creds)
            else:
                self._auth_client = YTMusic(self._oauth_path)

        return self._auth_client

    def search_song(self, artist: str, title: str) -> Optional[Dict]:
        """Search for a song on YouTube Music.

        Args:
            artist: Artist name
            title: Song title

        Returns:
            Best matching result or None if not found
        """
        # Clean the title (remove feat., ft., etc.)
        clean_title = self._clean_song_title(title)
        query = f"{artist} {clean_title}"

        results = self.yt.search(query, filter="songs", limit=5)

        if not results:
            return None

        # Return the first (best) match
        return self._extract_song_info(results[0])

    def _clean_song_title(self, title: str) -> str:
        """Remove featuring artists and other noise from song title."""
        # Remove (feat. ...), [feat. ...], (ft. ...), etc.
        patterns = [
            r"\s*[\(\[]feat\..*?[\)\]]",
            r"\s*[\(\[]ft\..*?[\)\]]",
            r"\s*[\(\[]featuring.*?[\)\]]",
            r"\s*[\(\[]with.*?[\)\]]",
            r"\s*-\s*remaster.*$",
            r"\s*[\(\[]remaster.*?[\)\]]",
            r"\s*[\(\[].*?version[\)\]]",
            r"\s*[\(\[].*?edit[\)\]]",
        ]
        result = title
        for pattern in patterns:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE)
        return result.strip()

    def _extract_song_info(self, result: Dict) -> Dict:
        """Extract relevant info from a search result."""
        artists = result.get("artists", [])
        artist_names = [a.get("name", "") for a in artists if a]

        return {
            "videoId": result.get("videoId"),
            "title": result.get("title", ""),
            "artist": artist_names[0] if artist_names else "",
            "artists": artist_names,
            "album": result.get("album", {}).get("name", "") if result.get("album") else "",
            "duration": result.get("duration", ""),
        }

    def create_playlist(self, title: str, description: str = "") -> str:
        """Create a new playlist.

        Args:
            title: Playlist title
            description: Playlist description

        Returns:
            Playlist ID

        Raises:
            RuntimeError: If not authenticated
        """
        if not self.authenticated:
            raise RuntimeError(
                "Authentication required to create playlists. "
                "Run 'ytmusicapi oauth' to authenticate."
            )
        auth_client = self._get_auth_client()
        playlist_id = auth_client.create_playlist(
            title=title,
            description=description,
            privacy_status="PRIVATE",
        )
        return playlist_id

    def add_songs_to_playlist(self, playlist_id: str, video_ids: List[str]) -> bool:
        """Add songs to a playlist.

        Args:
            playlist_id: ID of the playlist
            video_ids: List of video IDs to add

        Returns:
            True if successful
        """
        if not video_ids:
            return True

        # Remove duplicates while preserving order
        unique_ids = list(dict.fromkeys(video_ids))

        auth_client = self._get_auth_client()
        result = auth_client.add_playlist_items(playlist_id, unique_ids)
        return result.get("status") == "STATUS_SUCCEEDED" if isinstance(result, dict) else bool(result)

    def get_playlist(self, playlist_id: str) -> Dict:
        """Get playlist details."""
        return self.yt.get_playlist(playlist_id)

    def search_songs_batch(
        self, tracks: List[Dict], progress_callback=None
    ) -> tuple[List[str], List[Dict]]:
        """Search for multiple songs.

        Args:
            tracks: List of track dicts with 'artist' and 'name' keys
            progress_callback: Optional callback(current, total) for progress

        Returns:
            Tuple of (found_video_ids, not_found_tracks)
        """
        found_ids = []
        not_found = []

        for i, track in enumerate(tracks):
            if progress_callback:
                progress_callback(i + 1, len(tracks))

            result = self.search_song(track["artist"], track["name"])

            if result and result.get("videoId"):
                found_ids.append(result["videoId"])
            else:
                not_found.append(track)

        return found_ids, not_found
