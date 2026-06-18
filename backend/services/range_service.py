import logging

import numpy as np

from services.pitch_service import extract_pitch

logger = logging.getLogger(__name__)


def _sanitize_pitch(pitch_contour: np.ndarray) -> np.ndarray:
    """
    Removes silent or invalid frames before calculating vocal range.
    """
    contour = np.asarray(pitch_contour, dtype=float).reshape(-1)
    contour = contour[np.isfinite(contour)]
    contour = contour[contour > 0.0]
    return contour


def _calculate_range_width(pitch_contour: np.ndarray) -> float:
    """
    Calculates max pitch minus min pitch for valid pitched frames.
    """
    if pitch_contour.size == 0:
        logger.warning("Cannot calculate vocal range from an empty pitch contour.")
        return 0.0

    min_pitch = float(np.min(pitch_contour))
    max_pitch = float(np.max(pitch_contour))
    range_width = max_pitch - min_pitch

    logger.info("Minimum pitch: %.2f Hz", min_pitch)
    logger.info("Maximum pitch: %.2f Hz", max_pitch)
    logger.info("Range width: %.2f Hz", range_width)

    return float(max(0.0, range_width))


def _calculate_range_score(reference_range: float, user_range: float) -> float:
    """
    Scores how closely the user's range width matches the reference range width.
    """
    if reference_range == 0.0 and user_range == 0.0:
        logger.info("Both vocal ranges are zero; returning perfect range score.")
        return 100.0

    if reference_range == 0.0 or user_range == 0.0:
        logger.warning("One vocal range is zero; ranges cannot be proportionally compared.")
        return 0.0

    # Score as the proportional closeness of the two range widths. Using min/max
    # keeps the score smoothly bounded within (0, 100]; the previous linear penalty
    # (difference / reference * 100) saturated hard to 0 once the user's range
    # differed from the reference by >=100%, which is common for any two real takes.
    score = (min(reference_range, user_range) / max(reference_range, user_range)) * 100.0

    return float(np.clip(score, 0.0, 100.0))


def analyze_vocal_range(reference_audio_path: str, user_audio_path: str) -> dict:
    """
    Measures how closely the user's vocal range matches the reference performance.
    """
    logger.info("Starting vocal range analysis")
    logger.info("Reference audio: %s", reference_audio_path)
    logger.info("User audio: %s", user_audio_path)

    reference_pitch = extract_pitch(reference_audio_path)
    user_pitch = extract_pitch(user_audio_path)

    reference_clean = _sanitize_pitch(reference_pitch)
    user_clean = _sanitize_pitch(user_pitch)

    if reference_clean.size == 0 or user_clean.size == 0:
        logger.warning(
            "No valid pitched frames available for range analysis "
            "(reference_frames=%d, user_frames=%d).",
            reference_clean.size,
            user_clean.size,
        )

    logger.info("Calculating reference vocal range")
    reference_range = _calculate_range_width(reference_clean)

    logger.info("Calculating user vocal range")
    user_range = _calculate_range_width(user_clean)

    range_score = _calculate_range_score(reference_range, user_range)

    logger.info("Reference range: %.2f Hz", reference_range)
    logger.info("User range: %.2f Hz", user_range)
    logger.info("Range score: %.2f", range_score)

    return {
        "range_score": float(range_score),
        "reference_range": float(reference_range),
        "user_range": float(user_range),
    }
