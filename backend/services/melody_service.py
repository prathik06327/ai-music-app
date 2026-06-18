import logging

import numpy as np

from services.alignment_service import align_pitch_contours
from services.pitch_service import extract_pitch

logger = logging.getLogger(__name__)


def _sanitize_pitch_contour(pitch_contour: np.ndarray) -> np.ndarray:
    """
    Removes silent or invalid frames before melody comparison.

    TorchCREPE can produce unvoiced or invalid values in sparse regions. Those
    frames should not influence melodic contour similarity, so we keep only
    finite positive pitch values.
    """
    contour = np.asarray(pitch_contour, dtype=float).reshape(-1)
    contour = contour[np.isfinite(contour)]
    contour = contour[contour > 0]
    return contour


def _correlation_to_score(similarity: float) -> float:
    """
    Converts a Pearson correlation coefficient in [-1, 1] to a 0-100 score.
    """
    score = ((similarity + 1.0) / 2.0) * 100.0
    return float(np.clip(score, 0.0, 100.0))


def _safe_similarity(reference_aligned: np.ndarray, user_aligned: np.ndarray) -> float:
    """
    Computes a stable correlation coefficient for two aligned contours.

    np.corrcoef() returns NaN for constant or empty arrays, so we handle those
    cases explicitly and keep the service deterministic.
    """
    if reference_aligned.size == 0 or user_aligned.size == 0:
        logger.warning("Cannot compute melody similarity from empty aligned contours.")
        return 0.0

    if np.array_equal(reference_aligned, user_aligned):
        logger.info("Aligned contours are identical; returning perfect melody similarity.")
        return 1.0

    reference_std = float(np.std(reference_aligned))
    user_std = float(np.std(user_aligned))
    if reference_std == 0.0 or user_std == 0.0:
        logger.warning("One or both aligned contours are constant; treating correlation as neutral.")
        return 0.0

    correlation_matrix = np.corrcoef(reference_aligned, user_aligned)
    similarity = float(correlation_matrix[0, 1])

    if not np.isfinite(similarity):
        logger.warning("Correlation produced a non-finite value; falling back to neutral similarity.")
        return 0.0

    return float(np.clip(similarity, -1.0, 1.0))


def analyze_melody_similarity(reference_audio_path: str, user_audio_path: str) -> dict:
    """
    Measures how closely the user's melodic contour follows the reference.

    The analysis reuses the existing pitch extraction and DTW alignment services,
    then compares the aligned contours using Pearson correlation.
    """
    logger.info("Starting melody similarity analysis")
    logger.info(f"Reference audio: {reference_audio_path}")
    logger.info(f"User audio: {user_audio_path}")

    reference_pitch = extract_pitch(reference_audio_path)
    user_pitch = extract_pitch(user_audio_path)

    logger.info("Sanitizing pitch contours before DTW alignment")
    reference_pitch = _sanitize_pitch_contour(reference_pitch)
    user_pitch = _sanitize_pitch_contour(user_pitch)

    if reference_pitch.size == 0 or user_pitch.size == 0:
        logger.warning("No voiced pitch frames available for melody analysis.")
        return {
            "melody_score": 0.0,
            "similarity": 0.0,
        }

    logger.info("Aligning pitch contours with DTW")
    aligned_reference, aligned_user = align_pitch_contours(reference_pitch, user_pitch)

    logger.info("Computing melody similarity using numpy.corrcoef")
    similarity = _safe_similarity(aligned_reference, aligned_user)
    melody_score = _correlation_to_score(similarity)

    logger.info(f"Melody similarity result: {similarity:.4f}")
    logger.info(f"Melody score result: {melody_score:.2f}")

    return {
        "melody_score": float(melody_score),
        "similarity": float(similarity),
    }
