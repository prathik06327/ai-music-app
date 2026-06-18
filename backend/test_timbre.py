import sys
import numpy as np
from services.timbre_service import extract_audio_embedding

def main():
    """
    Validation script to verify the CLAP audio embedding pipeline.
    It loads an audio file, extracts the semantic embedding, and prints basic statistics.
    """
    audio_file = "outputs/htdemucs/compare-4bdc1d8f/vocals.wav"
    
    try:
        print(f"Extracting CLAP embedding from '{audio_file}'... (This may take a moment based on your CPU)")
        
        # 1. & 2. Load audio and extract the embedding
        embedding = extract_audio_embedding(audio_file)
        
        # Calculate statistics
        embedding_shape = embedding.shape
        first_20_values = np.round(embedding[:20], 4)
        min_val = np.min(embedding)
        max_val = np.max(embedding)
        
        # 3. Print output
        print("\n--- CLAP Embedding Metrics ---")
        print(f"Embedding Shape: {embedding_shape}")
        
        print(f"\nMin Value: {min_val:.4f}")
        print(f"Max Value: {max_val:.4f}")
        
        print(f"\nFirst 20 Values:")
        print(first_20_values)
        
    except FileNotFoundError:
        print(f"Error: Could not find the file '{audio_file}'. Please ensure separation has run.")
    except Exception as e:
        print(f"Error during timbre extraction test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()