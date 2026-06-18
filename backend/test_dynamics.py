import logging
import wave
from pathlib import Path

import numpy as np

from services.dynamics_service import analyze_dynamics


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
DYNAMICS_TEST_DIR = OUTPUTS_DIR / "dynamics_test"
REFERENCE_AUDIO_PATH = OUTPUTS_DIR / "htdemucs" / "song" / "vocals.wav"


def _write_test_audio(file_path: Path, envelopes: list[float], sample_rate: int = 16000) -> None:
    """
    Writes a simple mono WAV file whose loudness changes over time.
    """
    segment_duration_seconds = 0.3
    silence_duration_seconds = 0.05
    frequency = 220.0

    segments = []
    for amplitude in envelopes:
        time_axis = np.linspace(0.0, segment_duration_seconds, int(sample_rate * segment_duration_seconds), endpoint=False)
        tone = amplitude * np.sin(2.0 * np.pi * frequency * time_axis)
        segments.append(tone.astype(np.float32))

        silence = np.zeros(int(sample_rate * silence_duration_seconds), dtype=np.float32)
        segments.append(silence)

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

    DYNAMICS_TEST_DIR.mkdir(parents=True, exist_ok=True)
    reference_path = DYNAMICS_TEST_DIR / "reference.wav"
    user_path = DYNAMICS_TEST_DIR / "user.wav"

    # Same envelope so the test is deterministic and exercises the full pipeline.
    reference_envelopes = [0.12, 0.28, 0.18, 0.42, 0.22, 0.35]
    user_envelopes = [0.12, 0.28, 0.18, 0.42, 0.22, 0.35]

    _write_test_audio(reference_path, reference_envelopes)
    _write_test_audio(user_path, user_envelopes)

    return reference_path.as_posix(), user_path.as_posix()


def main():
    """
    Test script for dynamics similarity analysis.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("-" * 40)
    print("Dynamics Similarity Test")
    print("-" * 40)

    reference_audio, user_audio = _build_test_audio_paths()

    try:
        print(f"Analyzing dynamics similarity between:\nReference: {reference_audio}\nUser:      {user_audio}")
        result = analyze_dynamics(reference_audio, user_audio)

        print(f"Dynamics Similarity: {result['similarity']:.4f}")
        print(f"Dynamics Score: {result['dynamics_score']:.2f}")
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
    except Exception as exc:
        print(f"Error executing dynamics similarity analysis:\n{exc}")
    finally:
        print("-" * 40)


if __name__ == "__main__":
    main()