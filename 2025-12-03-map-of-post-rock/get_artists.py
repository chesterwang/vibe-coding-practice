#!/usr/bin/env python3
"""
Script to get artist information data following the spec:
1. Get top artists by tag (post-rock)
2. Get detailed info for each artist
"""

import os
import requests
import json
import time
from typing import List, Dict, Any

# Configuration
API_KEY = os.getenv("LASTFM_API_KEY", "your_api_key_here")  # Replace with your actual API key
if API_KEY == "your_api_key_here":
    print("WARNING: Please set your Last.fm API key as an environment variable LASTFM_API_KEY")
    print("You can get an API key from: https://www.last.fm/api/account/create")

BASE_URL = "http://ws.audioscrobbler.com/2.0/"
TAG = "post-rock"
LIMIT = 1000

def get_top_artists_by_tag(tag: str, page: int = 1) -> Dict[str, Any]:
    """
    Get top artists for a given tag
    """
    params = {
        "method": "tag.gettopartists",
        "tag": tag,
        "api_key": API_KEY,
        "format": "json",
        "limit": LIMIT,
        "page": page
    }
    
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    
    return response.json()

def get_artist_info(artist_name: str) -> Dict[str, Any]:
    """
    Get detailed info for a specific artist
    """
    params = {
        "method": "artist.getinfo",
        "artist": artist_name,
        "api_key": API_KEY,
        "format": "json"
    }
    
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    
    return response.json()

def save_json(data: Any, filename: str):
    """
    Save data to a JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_artists_by_tag():
    """
    Step 1: Get all artists by tag through multiple requests
    """
    print("Step 1: Getting top artists by tag...")
    
    page = 1
    all_artists_data = []
    
    while True:
        print(f"Fetching page {page}...")
        
        try:
            data = get_top_artists_by_tag(TAG, page)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break
        
        # Save the raw response to a file
        filename = f"top_artists_page_{page}.json"
        save_json(data, filename)
        print(f"Saved {filename}")
        
        # Check if we have more artists to fetch
        if "topartists" not in data or "artist" not in data["topartists"]:
            print("No more artists found.")
            break
            
        artists = data["topartists"]["artist"]
        
        # If the number of artists is less than the limit, we've reached the end
        if len(artists) < LIMIT:
            print(f"Got {len(artists)} artists on page {page}, which is less than limit {LIMIT}. Stopping.")
            break
        
        page += 1
        # Be respectful to the API
        time.sleep(0.5)
    
    print(f"Completed Step 1. Got {page} pages of artists.")
    return page

def get_artist_details_for_pages(num_pages: int):
    """
    Step 2: Get detailed info for each artist from all pages
    """
    print("Step 2: Getting detailed artist info...")
    
    for page_num in range(1, num_pages + 1):
        print(f"Processing artists from page {page_num}...")
        
        # Load the artist data for this page
        filename = f"top_artists_page_{page_num}.json"
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
        except FileNotFoundError:
            print(f"File {filename} not found, skipping...")
            continue
        
        if "topartists" not in page_data or "artist" not in page_data["topartists"]:
            print(f"No artists found in {filename}, skipping...")
            continue
        
        artists = page_data["topartists"]["artist"]
        artist_details_list = []
        
        for idx, artist in enumerate(artists):
            if isinstance(artist, dict) and "name" in artist:
                artist_name = artist["name"]
                print(f"  Getting info for '{artist_name}' ({idx + 1}/{len(artists)})...")
                
                try:
                    artist_info = get_artist_info(artist_name)
                    artist_details_list.append(artist_info)
                    
                    # Be respectful to the API
                    time.sleep(0.5)
                except requests.exceptions.RequestException as e:
                    print(f"    Error getting info for '{artist_name}': {e}")
                    # Append error info instead of failing completely
                    artist_details_list.append({
                        "error": f"Failed to get info for {artist_name}",
                        "artist_name": artist_name,
                        "exception": str(e)
                    })
            else:
                print(f"  Invalid artist data: {artist}")
        
        # Save artist details for this page
        details_filename = f"artist_details_page_{page_num}.json"
        save_json(artist_details_list, details_filename)
        print(f"  Saved {details_filename}")
    
    print("Completed Step 2.")

def main():
    """
    Main function that executes both steps
    """
    print("Starting the artist data retrieval process...")
    
    # Step 1: Get all artists by tag
    num_pages = get_all_artists_by_tag()
    
    if num_pages > 0:
        # Step 2: Get detailed info for each artist
        get_artist_details_for_pages(num_pages)
    
    print("Process completed!")

if __name__ == "__main__":
    main()