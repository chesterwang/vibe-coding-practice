import json
import requests
from typing import List, Dict, Optional
import logging
import numpy as np
import os
import pickle
import glob
from openai import OpenAI
import faiss
from sklearn.metrics.pairwise import cosine_similarity


def ensure_output_directory():
    """
    Ensure the output directory exists in the same directory as the script
    """
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

# Set up logging
output_dir = ensure_output_directory()
log_filepath = os.path.join(output_dir, 'artist_similarity_results.log')
logging.basicConfig(
    filename=log_filepath,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def read_json_file(filename: str) -> List[Dict]:
    """
    Read the JSON file and extract artist objects
    First look in the output directory, then in the script directory if not found
    """
    # Check if file exists in output directory first
    output_dir = ensure_output_directory()
    filepath = os.path.join(output_dir, filename)

    if not os.path.exists(filepath):
        # If not in output directory, look in the script's directory
        filepath = os.path.join(os.path.dirname(__file__), filename)

    with open(filepath, 'r', encoding='utf-8') as file:
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

def calculate_embeddings_siliconflow(artist_summaries: List[Dict], api_key: str, output_file: str = 'artist_embeddings.pkl') -> str:
    """
    Use SiliconFlow API to calculate embeddings for summary strings and save to file
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

        # Change default file extension to .pkl if using default name
        if output_file == 'artist_embeddings.pkl':
            output_file = 'artist_embeddings.pkl'

        # If custom filename provided, ensure it has .pkl extension
        if not output_file.endswith('.pkl'):
            output_file = output_file.rsplit('.', 1)[0] + '.pkl'

        output_dir = ensure_output_directory()
        filepath = os.path.join(output_dir, output_file)

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

        # Save the artist summaries with embeddings to a pickle file
        with open(filepath, 'wb') as f:
            pickle.dump(artist_summaries, f)

        print(f"Embeddings saved to {filepath}")
        return filepath

    except Exception as e:
        print(f"Error calculating embeddings: {str(e)}")
        # For demonstration purposes, we'll return random embeddings if API is not available
        print("Using random embeddings for demonstration...")
        for artist in artist_summaries:
            # Generate a random embedding vector of 512 dimensions
            artist['embedding'] = np.random.random(512).tolist()

        # Change default file extension to .pkl if using default name
        if output_file == 'artist_embeddings.pkl':
            output_file = 'artist_embeddings.pkl'
        # If custom filename provided, ensure it has .pkl extension
        if not output_file.endswith('.pkl'):
            output_file = output_file.rsplit('.', 1)[0] + '.pkl'

        output_dir = ensure_output_directory()
        filepath = os.path.join(output_dir, output_file)

        # Save the artist summaries with random embeddings to a pickle file
        with open(filepath, 'wb') as f:
            pickle.dump(artist_summaries, f)

        print(f"Random embeddings saved to {filepath}")
        return filepath

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

def find_similar_artists(input_file: str = 'artist_embeddings.pkl', threshold: float = 0.3, top_k: int = 10):
    """
    Find similar artists based on cosine similarity of embeddings loaded from a file
    """
    # Load embeddings from the pickle file in the output directory
    output_dir = ensure_output_directory()
    filepath = os.path.join(output_dir, input_file)
    print(f"Loading embeddings from {filepath}")
    with open(filepath, 'rb') as f:
        artist_with_embeddings = pickle.load(f)

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
            'mbid': artist['mbid'],
            'similar_artists': similar_list
        }
        similar_artists_results.append(result_entry)

        logging.info(f"Artist '{artist['name']}' has {len(similar_list)} similar artists: {[s['name'] for s in similar_list]}")

    return similar_artists_results

def save_artist_similarity_results(results: List[Dict], filename: str = 'artist_similarity_results.json'):
    """
    Save similarity results to a JSON file
    """
    output_dir = ensure_output_directory()
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def get_artist_detail_files():
    """
    Find all artist details files matching the pattern
    """

    output_dir =  ensure_output_directory()
    search_pattern = os.path.join(output_dir, 'artist_details_page_*.json')
    artist_details_files = glob.glob(search_pattern)
    artist_details_files.sort()  # Sort to process in order (page_1, page_2, etc.)
    return artist_details_files

def process_single_artist_file(file_path: str, siliconflow_api_key: str):
    """
    Process a single artist file to compute embeddings
    """
    print(f"\nProcessing {os.path.basename(file_path)}...")

    # Extract page number from filename to create corresponding output filename
    filename_pattern = r'artist_details_page_(\d+)\.json'
    import re
    match = re.search(filename_pattern, os.path.basename(file_path))
    if match:
        page_num = match.group(1)
        output_pickle_file = f"artist_embeddings_page_{page_num}.pkl"
    else:
        # Fallback if filename format doesn't match expected pattern
        output_pickle_file = f"artist_embeddings_{os.path.basename(file_path).replace('.json', '.pkl')}"

    # Read and process the JSON file
    artists = read_json_file(os.path.basename(file_path))  # Use just the filename
    print(f"Found {len(artists)} artists in {os.path.basename(file_path)}")

    # Extract summaries
    artist_summaries = extract_summary_field(artists)
    print(f"Found {len(artist_summaries)} artists with summary information")

    # Calculate embeddings using SiliconFlow API (using first 30 for testing)
    embeddings_file = calculate_embeddings_siliconflow(artist_summaries[0:30], siliconflow_api_key, output_file=output_pickle_file)

    print(f"Embeddings saved to {os.path.basename(embeddings_file)}")
    return embeddings_file


def combine_all_embeddings(generated_pickle_files: List[str]):
    """
    Load data from all pickle files and combine them
    """
    print(f"\nCombining data from {len(generated_pickle_files)} pickle files...")
    all_artist_data = []

    for pickle_file in generated_pickle_files:
        print(f"Loading data from {os.path.basename(pickle_file)}...")
        # Load from the output directory
        output_dir = ensure_output_directory()
        pickle_file_path = os.path.join(output_dir, os.path.basename(pickle_file))
        with open(pickle_file_path, 'rb') as f:
            artist_data = pickle.load(f)
            all_artist_data.extend(artist_data)  # Combine all artist data

    print(f"Total artists in combined dataset: {len(all_artist_data)}")

    # Save combined dataset to a single pickle file for similarity calculation
    output_dir = ensure_output_directory()
    combined_pickle_file = os.path.join(output_dir, 'artist_embeddings_combined.pkl')
    with open(combined_pickle_file, 'wb') as f:
        pickle.dump(all_artist_data, f)

    print(f"Combined embeddings saved to {os.path.basename(combined_pickle_file)}")
    return combined_pickle_file



if __name__ == "__main__":
    # Get all artist detail files
    artist_details_files = get_artist_detail_files()
    print(f"Found {len(artist_details_files)} artist details files: {[os.path.basename(f) for f in artist_details_files]}")

    # Process each artist details file
    siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY", "YOUR_API_KEY_HERE")
    generated_pickle_files = []

    for file_path in artist_details_files:
        embeddings_file = process_single_artist_file(file_path, siliconflow_api_key)
        generated_pickle_files.append(embeddings_file)

    # Combine all embeddings and calculate similarities
    combined_pickle_file = combine_all_embeddings(generated_pickle_files)

    # Calculate similarity using the combined embeddings file
    print("Calculating similarities on combined dataset...")
    artist_similarity_results = find_similar_artists(os.path.basename(combined_pickle_file), threshold=0.3, top_k=10)

    # Save results to JSON
    save_artist_similarity_results(artist_similarity_results)

    # Print a few examples
    for i, artist in enumerate(artist_similarity_results[:5]):  # Show more examples
        print(f"\nArtist {i+1}: {artist['artist']}")
        print(f"Similar artists: {[s['name'] for s in artist['similar_artists']]}")