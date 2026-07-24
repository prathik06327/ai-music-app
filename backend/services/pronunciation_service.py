import logging
from pathlib import Path
from threading import Lock

import whisper
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)

_MODEL_NAME = "base"
_whisper_model = None
_model_lock = Lock()


def _get_whisper_model():
    """
    Lazily loads the Whisper model once per Python process.
    """
    global _whisper_model

    if _whisper_model is None:
        with _model_lock:
            if _whisper_model is None:
                logger.info("Loading Whisper model: %s", _MODEL_NAME)
                _whisper_model = whisper.load_model(_MODEL_NAME)
                logger.info("Whisper model loaded")

    return _whisper_model


def _normalize_transcript(text: str) -> str:
    """
    Normalizes Whisper output for stable text similarity scoring.
    """
    return " ".join((text or "").strip().split())


def _transcribe_audio(audio_path: str) -> str:
    """
    Transcribes an audio file with Whisper and returns normalized text.
    """
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    logger.info("Transcribing audio for pronunciation analysis: %s", audio_path)
    model = _get_whisper_model()
    logger.info("Running deterministic Whisper transcription")
    result = model.transcribe(
        path.as_posix(),
        fp16=False,
        temperature=0.0,
        condition_on_previous_text=False,
    )
    transcript = _normalize_transcript(result.get("text", ""))

    if transcript:
        logger.info("Transcript generated with %d characters", len(transcript))
    else:
        logger.warning("Whisper returned an empty transcript for %s", audio_path)

    return transcript


def _score_transcripts(reference_text: str, user_text: str) -> float:
    """
    Converts transcript similarity into a 0-100 pronunciation score.
    """
    if not reference_text and not user_text:
        logger.warning("Both transcripts are empty; pronunciation score is 0.")
        return 0.0

    if not reference_text:
        logger.warning("Reference transcript is empty; pronunciation score is 0.")
        return 0.0

    if not user_text:
        logger.warning("User transcript is empty; pronunciation score is 0.")
        return 0.0

    score = float(fuzz.ratio(reference_text.lower(), user_text.lower()))
    return max(0.0, min(100.0, score))


def _final_score(score: float) -> int:
    return max(0, min(100, int(round(score))))


def analyze_pronunciation_accuracy(reference_audio_path: str, user_audio_path: str) -> dict:
    """
    Measures lyrical pronunciation similarity between reference and user vocals.
    """
    logger.info("Starting pronunciation accuracy analysis")
    logger.info("Reference vocals: %s", reference_audio_path)
    logger.info("User vocals: %s", user_audio_path)

    reference_text = _transcribe_audio(reference_audio_path)
    user_text = _transcribe_audio(user_audio_path)

    if len(reference_text.split()) < 2 or len(user_text.split()) < 2:
        logger.warning(
            "Short transcript detected during pronunciation analysis "
            "(reference_words=%d, user_words=%d).",
            len(reference_text.split()),
            len(user_text.split()),
        )

    pronunciation_score = _final_score(_score_transcripts(reference_text, user_text))

    logger.info("Pronunciation score: %.2f", pronunciation_score)

    return {
        "pronunciation_score": pronunciation_score,
        "reference_text": reference_text,
        "user_text": user_text,
    }
