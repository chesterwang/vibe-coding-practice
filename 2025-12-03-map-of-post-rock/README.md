# Post-Rock Artist Data Retrieval

This project retrieves post-rock artist information from Last.fm's API according to the specification.

## Process

The script performs two main steps:

### Step 1: Get Top Artists by Tag
- Fetches top post-rock artists using the Last.fm API
- Makes multiple requests with pagination until all artists are retrieved
- Saves each API response as a separate JSON file (e.g., `top_artists_page_1.json`)
- Continues until the number of artists returned is less than the limit (1000)

### Step 2: Get Detailed Artist Info
- For each artist retrieved in Step 1, gets detailed information
- Creates corresponding artist detail files (e.g., `artist_details_page_1.json`)
- Each artist detail file contains information for all artists from the corresponding page

## Setup

1. Get a Last.fm API key from: https://www.last.fm/api/account/create
2. Set your API key as an environment variable:
   ```bash
   export LASTFM_API_KEY="your_api_key_here"
   ```
   Or update the `API_KEY` variable directly in `get_artists.py`

## Usage

Run the script:
```bash
python get_artists.py
```

## Files Created

- `top_artists_page_X.json`: Raw API responses containing lists of artists
- `artist_details_page_X.json`: Detailed information for each artist

## Dependencies

- Python 3.x
- requests library (`pip install requests`)

## API Limits

The script includes rate limiting (0.5 second delay between requests) to be respectful to the API.