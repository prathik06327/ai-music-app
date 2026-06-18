import logging
import wave
from pathlib import Path

import numpy as np

from services.harmonic_service import analyze_harmonic_similarity


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
HARMONIC_TEST_DIR = OUTPUTS_DIR / "harmonic_test"
REFERENCE_AUDIO_PATH = OUTPUTS_DIR / "htdemucs" / "song" / "vocals.wav"


def _write_tone_sequence(file_path: Path, frequencies: list[float], sample_rate: int = 16000) -> None:
    """
    Writes a simple mono WAV file containing a sequence of sine-wave notes.
    """
    segments = []
    note_duration_seconds = 0.35

    for frequency in frequencies:
        time_axis = np.linspace(
            0.0,
            note_duration_seconds,
            int(sample_rate * note_duration_seconds),
            endpoint=False,
        )
        tone = 0.2 * np.sin(2.0 * np.pi * frequency * time_axis)
        segments.append(tone)

    audio = np.concatenate(segments).astype(np.float32)
    audio_int16 = np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)

    with wave.open(file_path.as_posix(), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())


def _build_test_audio_paths() -> tuple[str, str]:
    """
    Uses backend audio if available, otherwise synthesizes deterministic test WAVs.
    """
    if REFERENCE_AUDIO_PATH.is_file():
        return REFERENCE_AUDIO_PATH.as_posix(), REFERENCE_AUDIO_PATH.as_posix()

    HARMONIC_TEST_DIR.mkdir(parents=True, exist_ok=True)
    reference_path = HARMONIC_TEST_DIR / "reference.wav"
    user_path = HARMONIC_TEST_DIR / "user.wav"

    reference_notes = [220.0, 261.63, 329.63, 440.0]
    user_notes = [220.0, 261.63, 329.63, 440.0]

    _write_tone_sequence(reference_path, reference_notes)
    _write_tone_sequence(user_path, user_notes)

    return reference_path.as_posix(), user_path.as_posix()


def main():
    """
    Test script for harmonic similarity analysis.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("-" * 40)
    print("Harmonic Similarity Test")
    print("-" * 40)

    reference_audio, user_audio = _build_test_audio_paths()

    try:
        result = analyze_harmonic_similarity(reference_audio, user_audio)

        print(f"Feature Similarity: {result['similarity']:.4f}")
        print(f"Harmonic Score: {result['harmonic_score']:.2f}")
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
    except Exception as exc:
        print(f"Error executing harmonic similarity analysis:\n{exc}")
    finally:
        print("-" * 40)


if __name__ == "__main__":
    main()
