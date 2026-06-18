import logging
import numpy as np

from services.pitch_service import extract_pitch

logger = logging.getLogger(__name__)


def _sanitize_pitch(pitch_contour: np.ndarray) -> np.ndarray:
    """
    Removes zero and NaN values to only analyze valid pitched frames.
    """
    contour = np.asarray(pitch_contour, dtype=float).reshape(-1)
    contour = contour[np.isfinite(contour)]
    contour = contour[contour > 0.0]
    return contour


def _calculate_stats(pitch_contour: np.ndarray) -> dict:
    """
    Calculates pitch mean, standard deviation, and variance.
    """
    if pitch_contour.size == 0:
        return {"mean": 0.0, "std": 0.0, "variance": 0.0}

    return {
        "mean": float(np.mean(pitch_contour)),
        "std": float(np.std(pitch_contour)),
        "variance": float(np.var(pitch_contour)),
    }


def analyze_vocal_stability(reference_audio_path: str, user_audio_path: str) -> dict:
    """
    Measures how steady the user's pitch remains by comparing pitch fluctuation (variance).
    Smaller fluctuations (lower variance) relative to the reference yield a higher score.
    """
    logger.info("Starting vocal stability analysis")

    ref_pitch = extract_pitch(reference_audio_path)
    user_pitch = extract_pitch(user_audio_path)

    ref_clean = _sanitize_pitch(ref_pitch)
    user_clean = _sanitize_pitch(user_pitch)

    ref_stats = _calculate_stats(ref_clean)
    user_stats = _calculate_stats(user_clean)

    ref_var = ref_stats["variance"]
    user_var = user_stats["variance"]

    # Calculate stability score as the proportional closeness of the two pitch
    # variances. Using min/max keeps the score smoothly bounded within (0, 100]:
    # the previous linear penalty (diff / ref * 100) saturated hard to 0 whenever
    # the user's variance differed from the reference by >=100%, which happens for
    # almost any two genuinely different recordings.
    if ref_var == 0.0 and user_var == 0.0:
        score = 100.0
    elif ref_var == 0.0 or user_var == 0.0:
        score = 0.0
    else:
        score = (min(ref_var, user_var) / max(ref_var, user_var)) * 100.0

    score = float(np.clip(score, 0.0, 100.0))

    logger.info(f"Reference variance: {ref_var:.4f}")
    logger.info(f"User variance: {user_var:.4f}")
    logger.info(f"Stability score: {score:.2f}")

    return {
        "stability_score": score,
        "reference_variance": ref_var,
        "user_variance": user_var,
    }
