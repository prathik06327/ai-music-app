import json
import logging
import socket
from urllib import error, request

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"
REQUEST_TIMEOUT_SECONDS = 45


def _clamp_score(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def _build_prompt(
    pitch_score: float,
    rhythm_score: float,
    tempo_score: float,
    timbre_score: float,
    overall_score: float,
) -> str:
    return (
        "You are a professional vocal coach.\n"
        "Write feedback in plain text only, no markdown.\n"
        "Keep the response to about 150 words.\n\n"
        "Performance scores (0-100):\n"
        f"- Overall: {overall_score:.2f}\n"
        f"- Pitch: {pitch_score:.2f}\n"
        f"- Rhythm: {rhythm_score:.2f}\n"
        f"- Tempo: {tempo_score:.2f}\n"
        f"- Timbre: {timbre_score:.2f}\n\n"
        "Required output structure:\n"
        "Overall Summary:\n"
        "Strengths:\n"
        "Areas For Improvement:\n\n"
        "Be specific, constructive, and practical."
    )


def generate_feedback(
    pitch_score: float,
    rhythm_score: float,
    tempo_score: float,
    timbre_score: float,
    overall_score: float,
) -> str:
    pitch_score = _clamp_score(pitch_score)
    rhythm_score = _clamp_score(rhythm_score)
    tempo_score = _clamp_score(tempo_score)
    timbre_score = _clamp_score(timbre_score)
    overall_score = _clamp_score(overall_score)

    prompt = _build_prompt(
        pitch_score=pitch_score,
        rhythm_score=rhythm_score,
        tempo_score=tempo_score,
        timbre_score=timbre_score,
        overall_score=overall_score,
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    req = request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    logger.info("Generating AI feedback with Ollama model %s", OLLAMA_MODEL)

    try:
        with request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            status_code = getattr(resp, "status", 200)
            raw_body = resp.read().decode("utf-8", errors="replace")
    except error.HTTPError as exc:
        logger.exception("Ollama HTTP error: %s", exc)
        detail = exc.read().decode("utf-8", errors="replace") if exc.fp else str(exc)
        raise RuntimeError(f"Ollama HTTP error ({exc.code}): {detail}") from exc
    except error.URLError as exc:
        logger.exception("Failed to reach Ollama: %s", exc)
        raise RuntimeError(f"Could not connect to Ollama at {OLLAMA_URL}") from exc
    except socket.timeout as exc:
        logger.exception("Ollama request timed out")
        raise RuntimeError("Feedback generation timed out") from exc
    except Exception as exc:
        logger.exception("Unexpected Ollama request error")
        raise RuntimeError(f"Unexpected feedback generation error: {exc}") from exc

    if status_code != 200:
        logger.error("Unexpected Ollama status code %s", status_code)
        raise RuntimeError(f"Ollama returned status code {status_code}")

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        logger.exception("Invalid JSON from Ollama: %s", raw_body[:500])
        raise RuntimeError("Invalid response format from Ollama") from exc

    # Ollama's generate endpoint returns a structure that may vary; try common keys
    feedback = None
    if isinstance(parsed, dict):
        feedback = parsed.get("response") or parsed.get("text") or parsed.get("output")
    if feedback is None:
        # If JSON was an array or different shape, fall back to raw body
        feedback = raw_body

    feedback = str(feedback).strip()
    if not feedback:
        logger.error("Ollama returned empty feedback response")
        raise RuntimeError("Ollama returned an empty feedback response")

    logger.info("AI feedback generated successfully")
    return feedback
