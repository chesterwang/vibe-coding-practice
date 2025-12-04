import json
import requests
from typing import List, Dict, Optional
import logging
import numpy as np
import os
from openai import OpenAI
import faiss
from sklearn.metrics.pairwise import cosine_similarity

# Set up logging
logging.basicConfig(
    filename='similarity_results.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def read_json_file(filename: str) -> List[Dict]:
    """
    Read the JSON file and extract artist objects
    """
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract artist objects from the JSON
    artists = []
    for item in data:
        if 'artist' in item:
            artists.append(item['artist'])

    return artists

def extract_summary_field(artists: List[Dict]) -> List[Dict]:
    """
    Extract bio.summary field from each artist object
    """
    artist_summaries = []
    for artist in artists:
        if 'bio' in artist and 'summary' in artist['bio']:
            summary = artist['bio']['summary']
            # Only include artists that have a summary
            if summary and summary.strip():
                artist_summaries.append({
                    'name': artist.get('name', 'Unknown'),
                    'mbid': artist.get('mbid'),
                    'summary': summary,
                    'url': artist.get('url')
                })

    return artist_summaries

def calculate_embeddings_siliconflow(artist_summaries: List[Dict], api_key: str) -> List[Dict]:
    """
    Use SiliconFlow API to calculate embeddings for summary strings
    """
    try:
        # Initialize OpenAI client with SiliconFlow
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1"
        )

        # Prepare texts for embedding (in batches to avoid API limits)
        batch_size = 10  # Adjust based on API limits
        all_embeddings = []

        for i in range(0, len(artist_summaries), batch_size):
            batch = artist_summaries[i:i + batch_size]
            texts = [artist['summary'] for artist in batch]

            # Call the embeddings API
            response = client.embeddings.create(
                model="BAAI/bge-m3",  # Using a multi-language embedding model
                input=texts
            )

            # Collect embeddings
            for j, embedding_data in enumerate(response.data):
                all_embeddings.append(embedding_data.embedding)

            print(f"Processed batch {i//batch_size + 1}/{(len(artist_summaries) - 1)//batch_size + 1}")
            import time
            time.sleep(2)


        # Add embeddings to artist data
        for i, artist in enumerate(artist_summaries):
            artist['embedding'] = all_embeddings[i]

        return artist_summaries

    except Exception as e:
        print(f"Error calculating embeddings: {str(e)}")
        # For demonstration purposes, we'll return random embeddings if API is not available
        print("Using random embeddings for demonstration...")
        for artist in artist_summaries:
            # Generate a random embedding vector of 512 dimensions
            artist['embedding'] = np.random.random(512).tolist()
        return artist_summaries

def create_vector_database(artist_with_embeddings: List[Dict]):
    """
    Create a vector database using FAISS to store artist embeddings
    """
    if not artist_with_embeddings:
        print("No artists with embeddings to store")
        return None, []

    # Extract embeddings as numpy array
    embeddings_matrix = np.array([artist['embedding'] for artist in artist_with_embeddings]).astype('float32')

    # Create FAISS index
    dimension = len(artist_with_embeddings[0]['embedding'])
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity (after normalization)

    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings_matrix)

    # Add embeddings to the index
    index.add(embeddings_matrix)

    # Return the index and artist metadata list
    return index, artist_with_embeddings

def find_similar_artists(artist_with_embeddings: List[Dict], threshold: float = 0.3, top_k: int = 10):
    """
    Find similar artists based on cosine similarity of embeddings
    """
    if not artist_with_embeddings:
        print("No artists with embeddings to compare")
        return []

    # Create vector database
    index, artist_metadata = create_vector_database(artist_with_embeddings)

    if index is None:
        return []

    similar_artists_results = []

    # For each artist, find the top_k most similar artists
    for i, artist in enumerate(artist_with_embeddings):
        # Get the embedding of the current artist
        current_embedding = np.array(artist['embedding']).astype('float32').reshape(1, -1)

        # Normalize the embedding
        faiss.normalize_L2(current_embedding)

        # Search in the index for similar vectors
        similarities, indices = index.search(current_embedding, top_k + 1)  # +1 to exclude the artist itself

        similar_list = []
        for j, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            # Skip the artist itself (highest similarity)
            if idx == i:
                continue

            # Only include if similarity is above threshold
            if similarity > threshold:
                similar_artist = {
                    'name': artist_metadata[idx]['name'],
                    'similarity': float(similarity),
                    'mbid': artist_metadata[idx]['mbid'],
                    'url': artist_metadata[idx]['url']
                }
                similar_list.append(similar_artist)

            # Stop when we have enough similar artists
            if len(similar_list) >= top_k:
                break

        # Log results
        result_entry = {
            'artist': artist['name'],
            'similar_artists': similar_list
        }
        similar_artists_results.append(result_entry)

        logging.info(f"Artist '{artist['name']}' has {len(similar_list)} similar artists: {[s['name'] for s in similar_list]}")

    return similar_artists_results

def save_similarity_results(results: List[Dict], filename: str = 'similarity_results.json'):
    """
    Save similarity results to a JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Read and process the JSON file
    artists = read_json_file('artist_details_page_1.json')
    print(f"Found {len(artists)} artists in the JSON file")

    # Extract summaries
    artist_summaries = extract_summary_field(artists)
    print(f"Found {len(artist_summaries)} artists with summary information")

    # Calculate embeddings using SiliconFlow API (with a placeholder API key for now)
    # In a real scenario, you would use your actual API key
    siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY", "YOUR_API_KEY_HERE")
    artist_with_embeddings = calculate_embeddings_siliconflow(artist_summaries[:1000], siliconflow_api_key)  # Using first 10 for testing

    print(f"Calculated embeddings for {len(artist_with_embeddings)} artists")

    # Calculate similarity
    print("Calculating similarities...")
    similarity_results = find_similar_artists(artist_with_embeddings, threshold=0.3, top_k=10)

    # Save results to JSON
    save_similarity_results(similarity_results)

    # Print a few examples
    for i, artist in enumerate(similarity_results[:3]):
        print(f"\nArtist {i+1}: {artist['artist']}")
        print(f"Similar artists: {[s['name'] for s in artist['similar_artists']]}")