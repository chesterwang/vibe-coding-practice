#!/usr/bin/env python3
"""
Test script to verify the API connection and basic functionality
"""

import os
import requests

# Configuration
API_KEY = os.getenv("LASTFM_API_KEY", "your_api_key_here")  # Replace with your actual API key
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

def test_api_connection():
    """
    Test the API connection with a simple request
    """
    if API_KEY == "your_api_key_here":
        print("ERROR: Please set your Last.fm API key as an environment variable LASTFM_API_KEY")
        print("You can get an API key from: https://www.last.fm/api/account/create")
        return False
    
    # Test with a simple request to get top artists for post-rock
    params = {
        "method": "tag.gettopartists",
        "tag": "post-rock",
        "api_key": API_KEY,
        "format": "json",
        "limit": 5,  # Just get a few for testing
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if "topartists" in data and "artist" in data["topartists"]:
            print("API connection successful!")
            print(f"Retrieved {len(data['topartists']['artist'])} test artists:")
            for artist in data["topartists"]["artist"]:
                if isinstance(artist, dict) and "name" in artist:
                    print(f"  - {artist['name']}")
            return True
        else:
            print("API returned unexpected data format:")
            print(data)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing API connection...")
    success = test_api_connection()
    if success:
        print("\nYou can now run the full script with: python get_artists.py")
    else:
        print("\nPlease fix the API issues before running the full script.")