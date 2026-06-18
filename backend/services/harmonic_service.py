import logging

import librosa
import numpy as np

from services.audio_service import load_audio

logger = logging.getLogger(__name__)


def _feature_stats(feature: np.ndarray) -> list[float]:
    """
    Returns mean and standard deviation for a librosa feature matrix.
    """
    feature = np.asarray(feature, dtype=float)
    if feature.size == 0:
        logger.warning("Encountered empty harmonic feature; using zero stats.")
        return [0.0, 0.0]

    return [float(np.mean(feature)), float(np.std(feature))]


def extract_harmonic_features(audio_path: str) -> np.ndarray:
    """
    Extracts chroma and spectral summary features for harmonic similarity.
    """
    logger.info("Loading audio for harmonic analysis: %s", audio_path)
    audio, sample_rate = load_audio(audio_path)

    if audio.size == 0:
        logger.warning("Loaded audio is empty for harmonic analysis: %s", audio_path)
        return np.zeros(6, dtype=float)

    logger.info("Extracting chroma_stft, spectral_centroid, and spectral_bandwidth")
    chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)

    feature_vector = np.array(
        [
            *_feature_stats(chroma),
            *_feature_stats(spectral_centroid),
            *_feature_stats(spectral_bandwidth),
        ],
        dtype=float,
    )

    feature_vector = np.nan_to_num(feature_vector, nan=0.0, posinf=0.0, neginf=0.0)
    logger.info("Harmonic feature vector extracted with shape: %s", feature_vector.shape)

    return feature_vector


def _cosine_similarity(reference_features: np.ndarray, user_features: np.ndarray) -> float:
    """
    Compares two feature vectors using cosine similarity mapped to 0.0-1.0.
    """
    reference = np.asarray(reference_features, dtype=float).reshape(-1)
    user = np.asarray(user_features, dtype=float).reshape(-1)

    if reference.shape != user.shape:
        logger.error("Feature shape mismatch: reference=%s user=%s", reference.shape, user.shape)
        return 0.0

    if reference.size == 0 or user.size == 0:
        logger.warning("Cannot compare empty harmonic feature vectors.")
        return 0.0

    if np.allclose(reference, user, rtol=1e-6, atol=1e-6):
        logger.info("Harmonic feature vectors are identical.")
        return 1.0

    reference_norm = float(np.linalg.norm(reference))
    user_norm = float(np.linalg.norm(user))

    if reference_norm == 0.0 or user_norm == 0.0:
        logger.warning("Cannot compare zero-norm harmonic feature vectors.")
        return 0.0

    cosine = float(np.dot(reference, user) / (reference_norm * user_norm))
    cosine = float(np.clip(cosine, -1.0, 1.0))

    return (cosine + 1.0) / 2.0


def analyze_harmonic_similarity(reference_audio_path: str, user_audio_path: str) -> dict:
    """
    Compares harmonic and spectral characteristics of reference and user vocals.
    """
    logger.info("Starting harmonic similarity analysis")
    logger.info("Reference audio: %s", reference_audio_path)
    logger.info("User audio: %s", user_audio_path)

    reference_features = extract_harmonic_features(reference_audio_path)
    user_features = extract_harmonic_features(user_audio_path)

    similarity = _cosine_similarity(reference_features, user_features)
    harmonic_score = float(np.clip(similarity * 100.0, 0.0, 100.0))

    logger.info("Feature similarity: %.4f", similarity)
    logger.info("Harmonic score: %.2f", harmonic_score)

    return {
        "harmonic_score": harmonic_score,
        "similarity": float(similarity),
    }
