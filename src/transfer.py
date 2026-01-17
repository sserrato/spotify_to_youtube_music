"""Transfer orchestration between Spotify and YouTube Music."""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from spotify import SpotifyClient
from ytmusic import YTMusicClient


class PlaylistTransfer:
    """Orchestrates playlist transfer from Spotify to YouTube Music."""

    def __init__(self):
        """Initialize transfer with both clients."""
        self.spotify = SpotifyClient()
        self.ytmusic = YTMusicClient()

    def transfer_playlist(
        self,
        spotify_url: str,
        dry_run: bool = False,
        progress_callback=None,
    ) -> Dict:
        """Transfer a Spotify playlist to YouTube Music.

        Args:
            spotify_url: Spotify playlist URL
            dry_run: If True, only search for matches without creating playlist
            progress_callback: Optional callback(current, total, track_name)

        Returns:
            Dict with transfer results
        """
        # Fetch Spotify playlist
        playlist_info = self.spotify.get_playlist(spotify_url)
        tracks = self.spotify.get_playlist_tracks(spotify_url)

        playlist_name = playlist_info["name"]
        total_tracks = len(tracks)

        # Search for tracks on YouTube Music
        found_ids = []
        not_found = []

        for i, track in enumerate(tracks):
            if progress_callback:
                progress_callback(i + 1, total_tracks, f"{track['artist']} - {track['name']}")

            result = self.ytmusic.search_song(track["artist"], track["name"])

            if result and result.get("videoId"):
                found_ids.append(result["videoId"])
            else:
                not_found.append(track)

        results = {
            "playlist_name": playlist_name,
            "total_tracks": total_tracks,
            "matched": len(found_ids),
            "not_found": len(not_found),
            "not_found_tracks": not_found,
            "video_ids": found_ids,
            "dry_run": dry_run,
            "playlist_id": None,
        }

        if dry_run:
            return results

        # Create playlist on YouTube Music
        if not self.ytmusic.authenticated:
            results["error"] = "YouTube Music authentication required to create playlist"
            return results

        try:
            playlist_id = self.ytmusic.create_playlist(
                title=playlist_name,
                description=f"Imported from Spotify",
            )
            results["playlist_id"] = playlist_id

            # Add songs to playlist
            if found_ids:
                self.ytmusic.add_songs_to_playlist(playlist_id, found_ids)

        except Exception as e:
            results["error"] = str(e)

        return results

    def log_not_found(self, not_found_tracks: List[Dict], filepath: str = "noresults_youtube.txt"):
        """Log tracks that weren't found to a file."""
        with open(filepath, "w") as f:
            f.write("# Tracks not found on YouTube Music\n\n")
            for track in not_found_tracks:
                f.write(f"{track['artist']} - {track['name']}\n")


def print_progress(current: int, total: int, track_name: str):
    """Print progress to console."""
    percent = (current / total) * 100
    # Clear line and print progress
    sys.stdout.write(f"\r[{current}/{total}] ({percent:.0f}%) {track_name[:50]:<50}")
    sys.stdout.flush()
    if current == total:
        print()  # New line at end


def print_results(results: Dict):
    """Print transfer results summary."""
    print(f"\n{'=' * 60}")
    print(f"Playlist: {results['playlist_name']}")
    print(f"{'=' * 60}")
    print(f"Total tracks:    {results['total_tracks']}")
    print(f"Matched:         {results['matched']}")
    print(f"Not found:       {results['not_found']}")
    match_rate = (results['matched'] / results['total_tracks'] * 100) if results['total_tracks'] > 0 else 0
    print(f"Match rate:      {match_rate:.1f}%")

    if results.get("dry_run"):
        print(f"\n[DRY RUN] No playlist created")
    elif results.get("playlist_id"):
        print(f"\nPlaylist created: https://music.youtube.com/playlist?list={results['playlist_id']}")
    elif results.get("error"):
        print(f"\nError: {results['error']}")

    if results["not_found"] > 0:
        print(f"\nTracks not found:")
        for track in results["not_found_tracks"][:10]:
            print(f"  - {track['artist']} - {track['name']}")
        if results["not_found"] > 10:
            print(f"  ... and {results['not_found'] - 10} more")
