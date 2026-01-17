#!/usr/bin/env python3
"""Helper script to set up YouTube Music OAuth."""

import json
import sys
import time

from ytmusicapi.auth.oauth import OAuthCredentials


def main():
    print("YouTube Music OAuth Setup")
    print("=" * 40)

    client_id = input("Enter your Google Client ID: ").strip()
    if not client_id:
        print("Error: Client ID is required")
        sys.exit(1)

    client_secret = input("Enter your Google Client Secret: ").strip()
    if not client_secret:
        print("Error: Client Secret is required")
        sys.exit(1)

    print("\nInitializing OAuth flow...")
    creds = OAuthCredentials(client_id=client_id, client_secret=client_secret)
    code = creds.get_code()

    print(f"\n1. Go to: {code['verification_url']}")
    print(f"2. Enter code: {code['user_code']}")
    input("\nPress Enter after authorizing in browser...")

    print("Fetching token...")
    token = creds.token_from_code(code['device_code'])

    # token is already a dict
    oauth_data = token if isinstance(token, dict) else vars(token)

    # Calculate expires_at if not present (ytmusicapi expects this)
    if 'expires_at' not in oauth_data and 'expires_in' in oauth_data:
        oauth_data['expires_at'] = int(time.time()) + oauth_data['expires_in']

    oauth_data['client_id'] = client_id
    oauth_data['client_secret'] = client_secret

    with open('oauth.json', 'w') as f:
        json.dump(oauth_data, f, indent=2)

    print("\nSuccess! oauth.json has been created.")
    print("You can now run: python src/main.py create <spotify_url>")


if __name__ == "__main__":
    main()
