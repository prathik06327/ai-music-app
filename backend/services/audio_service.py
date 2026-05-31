import numpy as np
import librosa
from pathlib import Path

def load_audio(audio_path: str) -> tuple[np.ndarray, int]:
    """
    Loads an audio file, resamples it to 16 kHz mono, and normalizes the waveform.

    This utility prepares an audio track for downstream processing, such as pitch
    extraction and ML model inference.

    Args:
        audio_path (str): The path to the audio file to load.

    Returns:
        tuple[np.ndarray, int]: A tuple containing:
            - audio_array (np.ndarray): The normalized 1-D audio waveform.
            - sample_rate (int): The sample rate of the audio (strictly 16000).

    Raises:
        FileNotFoundError: If the specified file does not exist or is not a file.
        RuntimeError: If librosa encounters an error while loading the file.
        ValueError: If the loaded audio file is completely empty.

    Example:
        >>> audio, sr = load_audio('outputs/vocals.wav')
        >>> print(audio.shape, sr)
        (123456,) 16000
    """
    path = Path(audio_path)

    # 1. Validate Input
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not path.is_file():
        raise FileNotFoundError(f"Path is not a file: {audio_path}")

    # 2. Load Audio
    try:
        # Load forcing 16000 Hz and mono
        audio_array, sample_rate = librosa.load(
            path.as_posix(),
            sr=16000,
            mono=True
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load audio file {audio_path}. Error: {e}") from e

    # 3. Validate Loaded Audio
    if audio_array.size == 0:
        raise ValueError(f"The audio file {audio_path} is empty or corrupted.")

    # 4. Normalize Audio
    normalized_audio = librosa.util.normalize(audio_array)

    return normalized_audio, sample_rate

if __name__ == "__main__":
    # 8. Usage Example
    example_file = "outputs/htdemucs/song/vocals.wav"
    
    try:
        # If running locally without a real file, it will catch the FileNotFoundError gracefully
        audio, sr = load_audio(example_file)
        
        duration = len(audio) / sr
        print(f"Sample Rate: {sr}")
        print(f"Waveform Shape: {audio.shape}")
        print(f"Duration: {duration:.2f} seconds")
    except FileNotFoundError:
        print(f"Please provide a valid '{example_file}' to test this script successfully.")
