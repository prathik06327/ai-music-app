import logging
import tempfile
import wave
from pathlib import Path

import numpy as np

from services.melody_service import analyze_melody_similarity


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
MELODY_TEST_DIR = OUTPUTS_DIR / "melody_test"
REFERENCE_AUDIO_PATH = OUTPUTS_DIR / "htdemucs" / "song" / "vocals.wav"


def _write_tone_melody(file_path: Path, notes_hz: list[float], sample_rate: int = 16000) -> None:
    """
    Writes a simple mono WAV file containing a sequence of sine-wave notes.
    """
    note_duration_seconds = 0.35
    silence_duration_seconds = 0.05

    audio_segments = []
    for frequency in notes_hz:
        time_axis = np.linspace(0.0, note_duration_seconds, int(sample_rate * note_duration_seconds), endpoint=False)
        tone = 0.2 * np.sin(2.0 * np.pi * frequency * time_axis)
        audio_segments.append(tone)

        silence = np.zeros(int(sample_rate * silence_duration_seconds), dtype=np.float32)
        audio_segments.append(silence)

    audio = np.concatenate(audio_segments).astype(np.float32)
    audio_int16 = np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)

    with wave.open(file_path.as_posix(), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())


def _build_test_audio_paths() -> tuple[str, str]:
    """
    Uses backend audio if available, otherwise synthesizes test WAVs inside backend/outputs.
    """
    if REFERENCE_AUDIO_PATH.is_file():
        return REFERENCE_AUDIO_PATH.as_posix(), REFERENCE_AUDIO_PATH.as_posix()

    MELODY_TEST_DIR.mkdir(parents=True, exist_ok=True)
    reference_path = MELODY_TEST_DIR / "reference.wav"
    user_path = MELODY_TEST_DIR / "user.wav"

    # Use the same melodic contour so the test is deterministic and exercises the full pipeline.
    reference_notes = [220.0, 246.94, 261.63, 293.66, 329.63, 349.23]
    user_notes = [220.0, 246.94, 261.63, 293.66, 329.63, 349.23]

    _write_tone_melody(reference_path, reference_notes)
    _write_tone_melody(user_path, user_notes)

    return reference_path.as_posix(), user_path.as_posix()


def main():
    """
    Test script for melody similarity analysis.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("-" * 40)
    print("Melody Similarity Test")
    print("-" * 40)

    reference_audio, user_audio = _build_test_audio_paths()

    try:
        print(f"Analyzing melody similarity between:\nReference: {reference_audio}\nUser:      {user_audio}")
        result = analyze_melody_similarity(reference_audio, user_audio)

        print(f"Melody Similarity: {result['similarity']:.4f}")
        print(f"Melody Score: {result['melody_score']:.2f}")
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
    except Exception as exc:
        print(f"Error executing melody similarity analysis:\n{exc}")
    finally:
        print("-" * 40)


if __name__ == "__main__":
    main()