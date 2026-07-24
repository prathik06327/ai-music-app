import json
import logging
from pathlib import Path

import numpy as np

from services.pitch_visualization_service import generate_pitch_visualization


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_AUDIO_CANDIDATES = [
    BASE_DIR / "outputs" / "htdemucs" / "song-ef1ba18f" / "vocals.wav",
    BASE_DIR / "outputs" / "htdemucs" / "reference-3c144b3c" / "vocals.wav",
    BASE_DIR / "outputs" / "htdemucs" / "reference-68c62594" / "vocals.wav",
    BASE_DIR / "outputs" / "htdemucs" / "reference-7d8171b6" / "vocals.wav",
    BASE_DIR / "outputs" / "htdemucs" / "reference-88ff1805" / "vocals.wav",
    BASE_DIR / "outputs" / "htdemucs" / "reference-e5ec63d5" / "vocals.wav",
    BASE_DIR / "outputs" / "htdemucs" / "reference-e98cd241" / "vocals.wav",
    BASE_DIR / "outputs" / "htdemucs" / "compare-25b4f83c" / "vocals.wav",
    BASE_DIR / "outputs" / "htdemucs" / "compare-2a2c8b74" / "vocals.wav",
    BASE_DIR / "outputs" / "htdemucs" / "compare-39143503" / "vocals.wav",
    BASE_DIR / "outputs" / "htdemucs" / "compare-6de606b9" / "vocals.wav",
    BASE_DIR / "outputs" / "htdemucs" / "compare-b8cbc8aa" / "vocals.wav",
]


def _find_audio_fixture() -> Path:
    """Returns the first available vocals fixture in the repository outputs tree."""
    for candidate in DEFAULT_AUDIO_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("No vocals.wav fixture was found in backend/outputs/htdemucs.")


def _print_pitch_points(title: str, points: list[dict[str, float]]) -> None:
    """Prints a compact preview of pitch points for manual inspection."""
    print(title)
    for point in points:
        print(f"  time={point['time']:.2f} sec, pitch={point['pitch']:.2f} Hz")


def main() -> None:
    """Runs the pitch visualization pipeline against the repository vocals fixture."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("-" * 37)
    print("Pitch Visualization Test")
    print("-" * 37)

    audio_path = _find_audio_fixture()

    try:
        print(f"Generating pitch visualization for: {audio_path.as_posix()}")
        result = generate_pitch_visualization(audio_path.as_posix())

        payload_json = json.dumps(result)
        pitch_points = result["pitch_points"]
        pitch_values = np.array([point["pitch"] for point in pitch_points], dtype=float)
        pitch_times = np.array([point["time"] for point in pitch_points], dtype=float)

        print(f"Audio Duration: {result['duration']:.2f} seconds")
        print(f"Sample Rate: {result['sample_rate']} Hz")
        print(f"Frame Count: {result['frame_count']}")

        if pitch_values.size > 0:
            print(f"Minimum Pitch: {float(np.min(pitch_values)):.2f} Hz")
            print(f"Maximum Pitch: {float(np.max(pitch_values)):.2f} Hz")
            print(f"Average Pitch: {float(np.mean(pitch_values)):.2f} Hz")
        else:
            print("Minimum Pitch: N/A")
            print("Maximum Pitch: N/A")
            print("Average Pitch: N/A")

        if pitch_times.size > 1 and np.any(np.diff(pitch_times) <= 0):
            raise ValueError("Pitch timestamps are not strictly increasing.")

        if np.any(~np.isfinite(pitch_values)):
            raise ValueError("Visualization output contains non-finite pitch values.")
        if np.any(pitch_values <= 0):
            raise ValueError("Visualization output contains zero or negative pitch values.")

        first_points = pitch_points[:10]
        last_points = pitch_points[-10:] if len(pitch_points) > 10 else pitch_points

        print("First 10 Pitch Points:")
        _print_pitch_points("", first_points)
        print("Last 10 Pitch Points:")
        if last_points is not first_points:
            _print_pitch_points("", last_points)
        else:
            _print_pitch_points("", last_points)

        print("JSON serialization: successful")
        print(f"Output characters: {len(payload_json)}")
        print("Pitch visualization data generated successfully.")
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
    except Exception as exc:
        print(f"Error executing pitch visualization test:\n{exc}")
    finally:
        print("-" * 37)


if __name__ == "__main__":
    main()