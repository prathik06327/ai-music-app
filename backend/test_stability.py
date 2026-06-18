import logging
import wave
from pathlib import Path

import numpy as np

from services.stability_service import analyze_vocal_stability


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
STABILITY_TEST_DIR = OUTPUTS_DIR / "stability_test"
REFERENCE_AUDIO_PATH = OUTPUTS_DIR / "htdemucs" / "song" / "vocals.wav"


def _write_tone(file_path: Path, frequencies: list[float], sample_rate: int = 16000) -> None:
    """
    Writes a simple mono WAV file containing a sequence of frequency sweeps or steps.
    """
    segments = []
    duration = 0.5
    for freq in frequencies:
        time_axis = np.linspace(0.0, duration, int(sample_rate * duration), endpoint=False)
        tone = 0.2 * np.sin(2.0 * np.pi * freq * time_axis)
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
    Uses backend audio if available, otherwise synthesizes test WAVs inside backend/outputs.
    """
    if REFERENCE_AUDIO_PATH.is_file():
        return REFERENCE_AUDIO_PATH.as_posix(), REFERENCE_AUDIO_PATH.as_posix()

    STABILITY_TEST_DIR.mkdir(parents=True, exist_ok=True)
    reference_path = STABILITY_TEST_DIR / "reference.wav"
    user_path = STABILITY_TEST_DIR / "user.wav"

    # Reference has steady pitch, User has slightly wavering pitch
    _write_tone(reference_path, [220.0, 220.0])
    # To make it deterministic
    _write_tone(user_path, [220.0, 221.0])

    return reference_path.as_posix(), user_path.as_posix()


def main():
    """
    Test script for vocal stability analysis.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("-" * 40)
    print("Vocal Stability Test")
    print("-" * 40)

    reference_audio, user_audio = _build_test_audio_paths()

    try:
        print(f"Analyzing stability between:\nReference: {reference_audio}\nUser:      {user_audio}")
        result = analyze_vocal_stability(reference_audio, user_audio)

        print(f"Reference Variance: {result['reference_variance']:.4f}")
        print(f"User Variance: {result['user_variance']:.4f}")
        print(f"Stability Score: {result['stability_score']:.2f}")
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
    except Exception as exc:
        print(f"Error executing stability analysis:\n{exc}")
    finally:
        print("-" * 40)


if __name__ == "__main__":
    main()
