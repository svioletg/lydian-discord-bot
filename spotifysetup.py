import json

CLIENT_ID = input('Client ID: ').strip()
CLIENT_SECRET = input('Client secret: ').strip()

with open('spotify_config.json', 'w', encoding='utf-8') as f:
    json.dump({
        "spotify":
        {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    }, f)

input('Saved to spotify_config.json; press ENTER to exit...')
