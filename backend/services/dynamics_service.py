import logging

import librosa
import numpy as np

from services.alignment_service import align_pitch_contours
from services.audio_service import load_audio

logger = logging.getLogger(__name__)


def _extract_rms_curve(audio_path: str) -> np.ndarray:
    """
    Loads audio and extracts its RMS energy contour.
    """
    audio_array, _ = load_audio(audio_path)
    rms_curve = librosa.feature.rms(y=audio_array)[0]
    return np.asarray(rms_curve, dtype=float).reshape(-1)


def _sanitize_rms_curve(rms_curve: np.ndarray) -> np.ndarray:
    """
    Removes invalid and silent frames from the RMS contour.
    """
    curve = np.asarray(rms_curve, dtype=float).reshape(-1)
    curve = curve[np.isfinite(curve)]
    curve = curve[curve > 0]
    return curve


def _cosine_similarity(reference_curve: np.ndarray, user_curve: np.ndarray) -> float:
    """
    Computes cosine similarity for two aligned RMS contours.
    """
    if reference_curve.size == 0 or user_curve.size == 0:
        logger.warning("Cannot compute dynamics similarity from empty aligned RMS curves.")
        return 0.0

    reference_norm = float(np.linalg.norm(reference_curve))
    user_norm = float(np.linalg.norm(user_curve))
    if reference_norm == 0.0 or user_norm == 0.0:
        logger.warning("One or both aligned RMS curves have zero magnitude.")
        return 0.0

    similarity = float(np.dot(reference_curve, user_curve) / (reference_norm * user_norm))
    if not np.isfinite(similarity):
        logger.warning("Cosine similarity produced a non-finite value; falling back to neutral similarity.")
        return 0.0

    return float(np.clip(similarity, -1.0, 1.0))


def _similarity_to_score(similarity: float) -> float:
    """
    Maps cosine similarity from [-1, 1] to a 0-100 score.
    """
    score = ((similarity + 1.0) / 2.0) * 100.0
    return float(np.clip(score, 0.0, 100.0))


def analyze_dynamics(reference_audio_path: str, user_audio_path: str) -> dict:
    """
    Measures how closely the user matches the reference performance's dynamics.
    """
    logger.info("Starting dynamics analysis")
    logger.info(f"Reference audio: {reference_audio_path}")
    logger.info(f"User audio: {user_audio_path}")

    reference_rms = _sanitize_rms_curve(_extract_rms_curve(reference_audio_path))
    user_rms = _sanitize_rms_curve(_extract_rms_curve(user_audio_path))

    logger.info(f"Reference RMS frames after sanitization: {reference_rms.size}")
    logger.info(f"User RMS frames after sanitization: {user_rms.size}")

    if reference_rms.size == 0 or user_rms.size == 0:
        logger.warning("No valid RMS frames available for dynamics analysis.")
        return {
            "dynamics_score": 0.0,
            "similarity": 0.0,
        }

    logger.info("Aligning RMS curves with DTW")
    aligned_reference, aligned_user = align_pitch_contours(reference_rms, user_rms)

    logger.info("Computing cosine similarity for aligned RMS curves")
    similarity = _cosine_similarity(aligned_reference, aligned_user)
    dynamics_score = _similarity_to_score(similarity)

    logger.info(f"Dynamics similarity result: {similarity:.4f}")
    logger.info(f"Dynamics score result: {dynamics_score:.2f}")

    return {
        "dynamics_score": float(dynamics_score),
        "similarity": float(similarity),
    }
