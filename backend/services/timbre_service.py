import laion_clap
import logging
import numpy as np
import random
import torch

logger = logging.getLogger(__name__)

# Global variable to hold the cached model instance
_clap_model = None

def load_clap_model():
    """
    Loads the pretrained CLAP (Contrastive Language-Audio Pretraining) model.
    
    Timbre & CLAP Explanation:
    Timbre refers to the unique tone, color, or texture of a voice (e.g., breathy, 
    raspy, bright). While librosa handles rhythm and CREPE handles pitch, CLAP 
    understands the broader acoustic footprint. It allows us to compare the 
    stylistic and tonal characteristics of a user's vocal performance against the 
    original reference track.

    Singleton Pattern:
    Loading a large deep learning model into memory is computationally expensive 
    and slow. This function employs a singleton pattern—it checks if the model 
    is already loaded in the global `_clap_model` variable. If it is, it returns 
    that instance immediately, completely avoiding the overhead of reloading the 
    model on every single API request.

    Returns:
        laion_clap.CLAP_Module: The instantiated and loaded CLAP model.
        
    Raises:
        RuntimeError: If the model fails to instantiate or load its weights.
    """
    global _clap_model
    
    # If the model is already loaded in memory, return it directly
    if _clap_model is not None:
        return _clap_model
        
    logger.info("Initializing CLAP model (HTSAT-tiny). This may take a moment...")
    try:
        # Initialize the CLAP module. 
        # enable_fusion=False and amodel='HTSAT-tiny' match our verification 
        # step and ensure a balance of speed and memory efficiency.
        _clap_model = laion_clap.CLAP_Module(enable_fusion=False, amodel='HTSAT-tiny')
        
        # Automatically downloads and loads the default pretrained checkpoint
        _clap_model.load_ckpt()

        # Evaluation mode disables training-time layers such as dropout so repeated
        # inference on the same audio is more consistent.
        _clap_model.eval()
        logger.info("Model loaded in evaluation mode")
        logger.info("CLAP model successfully loaded into memory.")
        
    except Exception as e:
        logger.error(f"Failed to load CLAP model: {e}")
        raise RuntimeError(f"Failed to load CLAP model: {e}")
        
    return _clap_model

def extract_audio_embedding(audio_path: str) -> np.ndarray:
    """
    Extracts a semantic audio embedding from a vocal track using CLAP.

    Embeddings Explanation:
    An "embedding" is a high-dimensional mathematical vector (a list of numbers) 
    that represents the core characteristics of an audio file. Deep learning models 
    like CLAP compress the complex raw audio into this condensed vector space. 
    Because CLAP maps both text and audio into the same space, similar-sounding 
    audio (or audio matching the same text description) will have embeddings that 
    are mathematically "close" to each other. By comparing the reference and user 
    embeddings, we can quantify the similarity of their voice timbre and style.

    Normalization:
    We L2-normalize the output array securely. This ensures that the magnitude is 1,
    making it so that distance and similarity comparisons focus strictly on the 
    quality and direction of the sound, instead of sheer volume or intensity differences.

    Args:
        audio_path (str): The path to the vocals.wav file (or any audio track).

    Returns:
        np.ndarray: A normalized 1D NumPy array representing the audio embedding.
    """
    # 1. Fetch the loaded model instance (automatically instantiates if it isn't loaded)
    model = load_clap_model()
    
    # 2. Extract embedding using the filelist method
    # It returns a 2D array of embeddings, shape: (1, embedding_dim)
    try:
        logger.info("Generating deterministic CLAP embedding")
        random.seed(0)
        np.random.seed(0)
        torch.manual_seed(0)

        logger.info("Running inference with torch.no_grad()")
        # no_grad avoids building an autograd graph during inference, which reduces
        # memory use, improves performance, and removes another source of variability.
        with torch.no_grad():
            embeddings = model.get_audio_embedding_from_filelist(x=[audio_path], use_tensor=False)
    except Exception as e:
        logger.error(f"Failed to extract embedding from {audio_path}: {e}")
        raise RuntimeError(f"Failed to extract embedding: {e}")
        
    # Isolate the 1D embedding for our single track
    embedding = embeddings[0]
    
    # 3. L2-Normalize the array
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
        
    return embedding


def calculate_timbre_score(similarity: float) -> int:
    """
    Convert similarity into a 0-100 score.
    Clamps values to ensure 0 <= score <= 100.
    
    Example: 0.92 -> 92
    """
    score = int(round(similarity * 100))
    return max(0, min(100, score))


def compare_embeddings(reference_embedding: np.ndarray, user_embedding: np.ndarray) -> dict:
    """
    Compares two CLAP audio embeddings using Cosine Similarity.
    
    Since the embeddings from extract_audio_embedding() are already L2-normalized 
    (meaning their magnitude is 1), the dot product directly yields the cosine similarity.
    Cosine similarity values range from -1 (completely opposite) to 1 (identical).
    We map the output algebraically to a [0, 1] range.

    Args:
        reference_embedding (np.ndarray): The 1D normalized vector of the original track.
        user_embedding (np.ndarray): The 1D normalized vector of the user's vocals.

    Returns:
        dict: A dictionary containing the float 'similarity' score from 0.0 to 1.0.
    """
    try:
        # Check arrays are flat 1D vectors for typical dot product processing
        ref_flat = reference_embedding.flatten()
        user_flat = user_embedding.flatten()

        if ref_flat.shape != user_flat.shape:
            logger.error(
                "Embedding shape mismatch: reference=%s user=%s",
                ref_flat.shape,
                user_flat.shape,
            )
            return {'similarity': 0.0}

        if np.allclose(ref_flat, user_flat, rtol=1e-6, atol=1e-6):
            return {'similarity': 1.0}

        ref_norm = np.linalg.norm(ref_flat)
        user_norm = np.linalg.norm(user_flat)
        if ref_norm == 0 or user_norm == 0:
            logger.error("Cannot compare zero-norm audio embeddings.")
            return {'similarity': 0.0}

        ref_flat = ref_flat / ref_norm
        user_flat = user_flat / user_norm
        
        # Calculate raw cosine similarity [-1.0, 1.0]
        cos_sim = float(np.clip(np.dot(ref_flat, user_flat), -1.0, 1.0))
        
        # Map from [-1.0, 1.0] to [0.0, 1.0]
        mapped_similarity = (cos_sim + 1.0) / 2.0
        
        return {
            'similarity': mapped_similarity
        }
    except Exception as e:
        logger.error(f"Failed to compare embeddings: {e}")
        # Default fallback score in case of dimensional mismatches
        return {'similarity': 0.0}


