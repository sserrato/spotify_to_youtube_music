# Spotify to YouTube Music Playlist Transfer

Transfer your Spotify playlists to YouTube Music with a simple CLI tool.

## Features

- Transfer any public Spotify playlist to YouTube Music
- 100% match rate for most playlists
- Dry-run mode to preview matches before creating playlists
- Logs unmatched tracks for manual review
- No YouTube API quota limits (uses unofficial ytmusicapi)

## Requirements

- Python 3.9+
- Spotify Developer Account
- YouTube Music Account

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/spotify_to_youtube_playlist.git
cd spotify_to_youtube_playlist

# Install dependencies
pip install -r requirements.txt
```

## Setup

### 1. Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click "Create App"
3. Fill in the app details (name, description)
4. Set Redirect URI to `http://127.0.0.1`
5. Copy your **Client ID** and **Client Secret**

Create a `.env` file in the project root:

```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

### 2. YouTube Music Authentication

YouTube Music requires browser authentication to create playlists. This method extracts your session cookies from the browser.

#### Step 1: Open YouTube Music in your browser

Go to https://music.youtube.com and make sure you're logged in.

#### Step 2: Open Developer Tools

- **Chrome/Edge**: Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
- **Firefox**: Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
- **Safari**: First enable Developer Tools in Safari → Settings → Advanced → "Show features for web developers", then press `Cmd+Option+I`

#### Step 3: Capture a network request

1. Go to the **Network** tab in Developer Tools
2. Click on any song or playlist in YouTube Music to trigger some requests
3. In the filter box, type `browse` to find the relevant request
4. Look for a **POST** request to `/browse`

#### Step 4: Copy the request as cURL

- **Chrome/Firefox**: Right-click the request → **Copy** → **Copy as cURL**
- **Safari**: Click the request, then in the Headers panel, manually copy the **Cookie** and **Authorization** headers

#### Step 5: Create the authentication file

Run the ytmusicapi browser setup:

```bash
ytmusicapi browser --file oauth.json
```

When prompted, paste the cURL command (or headers) and press Enter twice.

Alternatively, if you have the raw headers, create `oauth.json` manually:

```json
{
  "Accept": "*/*",
  "Content-Type": "application/json",
  "X-Goog-AuthUser": "0",
  "x-origin": "https://music.youtube.com",
  "Authorization": "SAPISIDHASH your_auth_hash_here",
  "Cookie": "your_full_cookie_string_here"
}
```

The authentication remains valid for approximately 2 years (until your YouTube Music browser session expires).

## Usage

### Test Spotify Connection

```bash
python src/main.py test "https://open.spotify.com/playlist/YOUR_PLAYLIST_ID"
```

### Test YouTube Music Search

```bash
python src/main.py test-yt "Artist Name" "Song Title"
```

### Transfer a Playlist (Dry Run)

Preview matches without creating the playlist:

```bash
python src/main.py create --dry-run "https://open.spotify.com/playlist/YOUR_PLAYLIST_ID"
```

### Transfer a Playlist

```bash
python src/main.py create "https://open.spotify.com/playlist/YOUR_PLAYLIST_ID"
```

### Transfer Without Logging Unmatched Tracks

```bash
python src/main.py create --no-log "https://open.spotify.com/playlist/YOUR_PLAYLIST_ID"
```

## Example Output

```
Transferring playlist: https://open.spotify.com/playlist/2TqFrDJ06YuRxZjtAuA3Zy

[28/28] (100%) Arcade Fire - Neon Bible

============================================================
Playlist: He Would Have Laughed
============================================================
Total tracks:    28
Matched:         28
Not found:       0
Match rate:      100.0%

Playlist created: https://music.youtube.com/playlist?list=PLDJavhpBQR_Wp3i4mnZTY4UkJ8B7VR9BV
```

## Troubleshooting

### OAuth HTTP 400 Error

If you get an HTTP 400 error when using Google OAuth authentication, use the browser authentication method instead. This is a known issue with ytmusicapi OAuth.

### "SAPISID not found" Error

Make sure you copy the **complete** cURL command from your browser. The Cookie header must include the `SAPISID` cookie.

### Tracks Not Found

Some tracks may not be available on YouTube Music or may have different metadata. Unmatched tracks are logged to `noresults_youtube.txt` for manual review.

## Project Structure

```
spotify_to_youtube_playlist/
├── src/
│   ├── main.py        # CLI entry point
│   ├── spotify.py     # Spotify API client
│   ├── ytmusic.py     # YouTube Music API client
│   └── transfer.py    # Transfer orchestration
├── requirements.txt   # Python dependencies
├── .env              # Spotify credentials (gitignored)
├── oauth.json        # YouTube Music auth (gitignored)
└── README.md
```

## Credits

- Based on [sigma67/spotify_to_ytmusic](https://github.com/sigma67/spotify_to_ytmusic)
- Uses [spotipy](https://github.com/spotipy-dev/spotipy) for Spotify API
- Uses [ytmusicapi](https://github.com/sigma67/ytmusicapi) for YouTube Music API

## License

MIT
