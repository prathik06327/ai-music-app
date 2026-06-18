import argparse
import logging
from pathlib import Path

from services.pronunciation_service import analyze_pronunciation_accuracy


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_REFERENCE_AUDIO_PATH = BASE_DIR / "outputs" / "htdemucs" / "song" / "vocals.wav"


def _parse_args():
    parser = argparse.ArgumentParser(description="Test pronunciation accuracy analysis.")
    parser.add_argument(
        "--reference",
        default=DEFAULT_REFERENCE_AUDIO_PATH.as_posix(),
        help="Path to reference vocals audio.",
    )
    parser.add_argument(
        "--user",
        default=None,
        help="Path to user vocals audio. Defaults to the reference path for a smoke test.",
    )
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = _parse_args()

    reference_audio_path = args.reference
    user_audio_path = args.user or reference_audio_path

    print("-" * 40)
    print("Pronunciation Accuracy Test")
    print("-" * 40)

    try:
        result = analyze_pronunciation_accuracy(reference_audio_path, user_audio_path)

        print("Reference Transcript")
        print(result["reference_text"])
        print("User Transcript")
        print(result["user_text"])
        print("Pronunciation Score")
        print(f"{result['pronunciation_score']:.2f}")
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
    except Exception as exc:
        print(f"Error executing pronunciation accuracy analysis:\n{exc}")
    finally:
        print("-" * 40)


if __name__ == "__main__":
    main()
