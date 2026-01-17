# Spotify to YouTube Playlist Exporter

## Project Overview

A tool to export playlists from Spotify to YouTube Music, inspired by TuneMyMusic.

## Reference Project

This project is based on [sigma67/spotify_to_ytmusic](https://github.com/sigma67/spotify_to_ytmusic) (MIT License).

### Key Libraries Used
- **[spotipy](https://github.com/spotipy-dev/spotipy)** (>=2.25.0) - Spotify Web API wrapper
- **[ytmusicapi](https://github.com/sigma67/ytmusicapi)** (>=1.10.0,<1.11.0) - Unofficial YouTube Music API (avoids quota limits!) - Pinned for Python 3.9 compatibility

### Reference Architecture (sigma67)
```
spotify_to_ytmusic/
├── main.py          # CLI entry point with argparse
├── controllers.py   # Orchestrates transfers (create, update, all, liked commands)
├── spotify.py       # Spotify client (OAuth + Client Credentials flows)
├── ytmusic.py       # YTMusic client (search, create playlist, add items)
├── settings.py      # Configuration management
└── settings.ini     # Credentials storage
```

### How sigma67 Works
1. **Spotify Auth**: Uses `spotipy` with either OAuth (for liked songs) or Client Credentials
2. **Fetch Tracks**: Paginates through playlist (100 tracks/request), extracts artist + title + album
3. **Search YTMusic**: For each track, searches `"{artist} {song}"`, uses `get_best_fit_song_id()`
4. **Create Playlist**: Uses `ytmusicapi` to create playlist and add matched video IDs
5. **Handle Failures**: Unmatched tracks logged to `noresults_youtube.txt`

### Key Insight: ytmusicapi vs YouTube Data API
The official YouTube Data API has strict quota limits (10,000 units/day, 100 units/search).
`ytmusicapi` is an unofficial API that **bypasses these limits** by mimicking browser requests.

## Core Functionality

1. **Connect to Spotify** - Authenticate and fetch user playlists
2. **Select Playlist** - Choose which playlist(s) to export
3. **Search YouTube Music** - Find matching tracks on YouTube Music
4. **Create YouTube Playlist** - Build the playlist on the destination platform

## Technical Approach

### Spotify Integration
- Use `spotipy` library (Spotify Web API wrapper)
- Two auth modes:
  - **Client Credentials** - For public playlists (no user login)
  - **OAuth** - For private playlists and liked songs
- Key methods:
  - `playlist_tracks(playlist_id)` - Get tracks with pagination
  - `current_user_playlists()` - List user's playlists
  - `current_user_saved_tracks()` - Get liked songs

### YouTube Music Integration
- Use `ytmusicapi` library (unofficial, no quota limits)
- OAuth via browser headers or oauth.json
- Key methods:
  - `search(query, filter="songs")` - Search for tracks
  - `create_playlist(title, description)` - Create new playlist
  - `add_playlist_items(playlist_id, video_ids)` - Add tracks

### Track Matching Strategy
- Search query: `"{artist} {song title}"`
- Clean song names (remove "feat.", "ft.", etc.)
- Use `get_best_fit_song_id()` to pick best match
- Cache results to avoid redundant searches
- Log unmatched tracks for manual review

## Project Structure

```
spotify_to_youtube_playlist/
├── CLAUDE.md           # This file
├── src/
│   ├── spotify.py      # Spotify API client (using spotipy)
│   ├── ytmusic.py      # YouTube Music client (using ytmusicapi)
│   ├── transfer.py     # Transfer orchestration logic
│   └── main.py         # CLI entry point
├── requirements.txt    # Python dependencies
├── settings.ini        # Credentials (gitignored)
└── settings.ini.example # Credentials template
```

## Dependencies

```
spotipy>=2.25.0
ytmusicapi>=1.10.0,<1.11.0
python-dotenv>=1.0.0
```

## Required API Credentials

1. **Spotify**
   - Create app at https://developer.spotify.com/dashboard
   - Get Client ID and Client Secret
   - Set redirect URI to `http://127.0.0.1`

2. **YouTube Music** (optional - only needed to create playlists)
   - Run `ytmusicapi oauth` to authenticate via browser
   - This creates `oauth.json` with your credentials
   - Note: Search works without authentication

## Configuration

Create a `.env` file in the project root:

```bash
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
```

For YouTube Music playlist creation, place `oauth.json` in the project root.

## Development Phases

### Phase 1: Spotify Integration ✅
- [x] Set up spotipy with Client Credentials
- [x] Fetch playlist by URL
- [x] Extract track metadata (artist, name, album, duration)
- [x] Handle pagination for large playlists

### Phase 2: YouTube Music Integration ✅
- [x] Implement search functionality (unauthenticated mode)
- [ ] Set up ytmusicapi OAuth (deferred - needed only for playlist creation)
- [ ] Create playlists and add items

### Phase 3: Transfer Logic ✅
- [x] Implement track matching (search + best fit)
- [x] Handle unmatched tracks (log to file)
- [x] Build end-to-end transfer flow
- [x] Add dry-run mode

### Phase 4: CLI & Polish ✅
- [x] Add progress indicators
- [x] Support create command with dry-run mode
- [x] Generate transfer report

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Test Spotify connection
python src/main.py test <spotify_playlist_url>

# Test YouTube Music search
python src/main.py test-yt "Artist Name" "Song Title"

# Transfer a playlist (dry-run - shows matches without creating playlist)
python src/main.py create --dry-run <spotify_playlist_url>

# Transfer a playlist (requires YouTube Music OAuth)
python src/main.py create <spotify_playlist_url>

# Transfer without logging not-found tracks
python src/main.py create --no-log <spotify_playlist_url>
```

## Notes

- Using `ytmusicapi` avoids YouTube Data API quota limits
- Spotify Client Credentials work for public playlists only
- YouTube Music search works without authentication
- To create playlists on YouTube Music, you need OAuth (`oauth.json`)
- Unmatched tracks are logged to `noresults_youtube.txt`
- Pinned to ytmusicapi <1.11.0 for Python 3.9 compatibility
