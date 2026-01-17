"""CLI entry point for Spotify to YouTube Music playlist transfer."""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(Path(__file__).parent.parent / ".env")

from spotify import SpotifyClient
from ytmusic import YTMusicClient
from transfer import PlaylistTransfer, print_progress, print_results


def cmd_test_spotify(args):
    """Test Spotify connection by fetching a playlist."""
    client = SpotifyClient()

    print(f"Fetching playlist: {args.url}")
    playlist = client.get_playlist(args.url)
    print(f"\nPlaylist: {playlist['name']}")
    print(f"Owner: {playlist['owner']['display_name']}")

    tracks = client.get_playlist_tracks(args.url)
    print(f"Total tracks: {len(tracks)}\n")

    print("First 10 tracks:")
    print("-" * 60)
    for i, track in enumerate(tracks[:10], 1):
        print(f"{i:2}. {track['artist']} - {track['name']}")

    if len(tracks) > 10:
        print(f"... and {len(tracks) - 10} more tracks")


def cmd_test_youtube(args):
    """Test YouTube Music connection by searching for a song."""
    client = YTMusicClient()

    print(f"Searching for: {args.artist} - {args.title}")
    result = client.search_song(args.artist, args.title)

    if result:
        print(f"\nFound: {result['title']}")
        print(f"Artist: {result['artist']}")
        print(f"Album: {result['album']}")
        print(f"Video ID: {result['videoId']}")
    else:
        print("\nNo results found")


def cmd_create(args):
    """Transfer a Spotify playlist to YouTube Music."""
    transfer = PlaylistTransfer()

    print(f"Transferring playlist: {args.url}")
    if args.dry_run:
        print("[DRY RUN MODE - No playlist will be created]\n")
    print()

    results = transfer.transfer_playlist(
        spotify_url=args.url,
        dry_run=args.dry_run,
        progress_callback=print_progress,
    )

    print_results(results)

    # Log not found tracks if any
    if results["not_found"] > 0 and not args.no_log:
        transfer.log_not_found(results["not_found_tracks"])
        print(f"\nNot found tracks logged to: noresults_youtube.txt")


def main():
    parser = argparse.ArgumentParser(
        description="Transfer Spotify playlists to YouTube Music"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Test Spotify command
    test_parser = subparsers.add_parser("test", help="Test Spotify connection")
    test_parser.add_argument("url", help="Spotify playlist URL")
    test_parser.set_defaults(func=cmd_test_spotify)

    # Test YouTube Music command
    yt_parser = subparsers.add_parser("test-yt", help="Test YouTube Music connection")
    yt_parser.add_argument("artist", help="Artist name")
    yt_parser.add_argument("title", help="Song title")
    yt_parser.set_defaults(func=cmd_test_youtube)

    # Create/transfer playlist command
    create_parser = subparsers.add_parser(
        "create", help="Transfer a Spotify playlist to YouTube Music"
    )
    create_parser.add_argument("url", help="Spotify playlist URL")
    create_parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Only search for matches, don't create playlist"
    )
    create_parser.add_argument(
        "--no-log",
        action="store_true",
        help="Don't log not-found tracks to file"
    )
    create_parser.set_defaults(func=cmd_create)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
