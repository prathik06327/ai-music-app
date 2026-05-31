import os

os.environ.setdefault("MPLCONFIGDIR", "outputs/matplotlib")

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import torchcrepe
from pathlib import Path
from services.audio_service import load_audio
from services.alignment_service import align_pitch_contours


def extract_pitch(audio_path: str) -> np.ndarray:
    """
    Extracts the fundamental frequency (F0) contour from an audio file using TorchCREPE.

    This function utilizes the TorchCREPE deep learning model to estimate the 
    dominant pitch of the audio at small time intervals (frames). It is highly 
    effective for tracking melodies from isolated vocal tracks.

    Args:
        audio_path (str): The path to the audio file capable of being processed.

    Returns:
        np.ndarray: A 1D NumPy array containing the estimated pitch values in Hertz (Hz) 
                    for each time frame.

    Raises:
        FileNotFoundError: If the provided audio file does not exist.
        ValueError: If the audio format is invalid or empty.
        RuntimeError: If TorchCREPE fails to execute its prediction.

    Example:
        >>> pitches = extract_pitch("vocals.wav")
        >>> print(pitches)
        [220.1 221.3 220.7 ...]
    """
    # Step 1: Load and format the audio
    # Our audio_service ensures the file exists, is not empty, is mono, and is 16 kHz.
    try:
        audio_array, sample_rate = load_audio(audio_path)
    except Exception as e:
        raise ValueError(f"Failed to load audio for pitch extraction: {e}") from e

    # Step 2: Convert the NumPy array into a PyTorch tensor
    # Models running in PyTorch require tensors. We cast it to a standard 32-bit float.
    audio_tensor = torch.tensor(audio_array, dtype=torch.float32)

    # Step 3: Add a batch dimension
    # TorchCREPE expects multiple tracks at once (a "batch"). Even though we only 
    # have one track, we must reshape it from [samples] to [1, samples].
    audio_tensor = audio_tensor.unsqueeze(0)

    # Step 4: Configure TorchCREPE settings
    # Hop length: How many audio samples to skip before making the next pitch estimation.
    # At 16000 Hz, a hop length of 160 means we get 100 pitch estimations per second (10ms steps).
    hop_length = 160
    
    # Minimum and Maximum frequencies: We constrain the model to look for pitches 
    # strictly between 50 Hz (deep bass) and 1000 Hz (high soprano vocal range).
    fmin = 50.0
    fmax = 1000.0
    
    # Prediction model: 'full' is highly accurate but slightly slower than 'tiny'.
    model_capacity = "tiny"

    # Step 5: Run Pitch Prediction
    try:
        # We instruct TorchCREPE to analyze our tensor frame-by-frame and return the dominant pitches.
        pitch_tensor = torchcrepe.predict(
            audio=audio_tensor,
            sample_rate=sample_rate,
            hop_length=hop_length,
            fmin=fmin,
            fmax=fmax,
            model=model_capacity,
            device='cpu' # Run on standard CPU to ensure maximum compatibility
        )
    except Exception as e:
        raise RuntimeError(f"TorchCREPE failed to predict pitch: {e}") from e

    # Step 6: Format the output
    # Remove PyTorch's computational graph mapping, pull it out of the [1, frames] batch, 
    # and convert it back into a standard dense 1D NumPy array for easy handling in Python.
    pitch_values = pitch_tensor.squeeze(0).detach().numpy()

    return pitch_values


def compare_pitch_contours(reference_pitch: np.ndarray, user_pitch: np.ndarray) -> dict:
    """
    Compares two pitch contours by first aligning them and then calculating 
    frame-by-frame absolute differences.
    
    Why alignment improves scoring:
    Comparing raw contours directly requires the user to have mathematically perfect 
    timing, which is impossible. By using DTW (Dynamic Time Warping) to align the 
    contours first, we ensure that matching musical notes are compared against each 
    other, ignoring minor timing imperfections. This results in a much fairer and 
    more accurate pitch score.

    Args:
        reference_pitch (np.ndarray): The reference pitch contour in Hz.
        user_pitch (np.ndarray): The user's pitch contour in Hz.

    Returns:
        dict: Difference statistics containing average_difference, max_difference,
              and min_difference.

    Raises:
        ValueError: If either pitch contour is empty.
    """
    if len(reference_pitch) == 0 or len(user_pitch) == 0:
        raise ValueError("Cannot compare empty pitch contours.")

    # 1. Align the contours using DTW
    aligned_reference, aligned_user = align_pitch_contours(reference_pitch, user_pitch)

    # 2. Compare aligned contours calculating the absolute difference matrix
    differences = np.abs(aligned_reference - aligned_user)

    # 3. Return the calculated metrics
    return {
        "average_difference": float(np.mean(differences)),
        "max_difference": float(np.max(differences)),
        "min_difference": float(np.min(differences)),
    }


def calculate_pitch_score(average_pitch_error: float) -> float:
    """
    Calculates a pitch score from the average pitch error.

    Args:
        average_pitch_error (float): The average pitch difference in Hz.

    Returns:
        float: A score between 0 and 100.
    """
    # Temporary MVP scoring algorithm:
    # subtract 1 point for every 5 Hz of average pitch error.
    # This should be replaced later with a musically informed scoring model.
    score = 100 - (average_pitch_error / 5)

    # Clamp the score to the expected 0-100 range.
    return float(np.clip(score, 0, 100))


def plot_pitch_contours(reference_contour: np.ndarray, user_contour: np.ndarray) -> str:
    """
    Plots reference and user pitch contours on the same graph and saves the image.

    Args:
        reference_contour (np.ndarray): The reference pitch contour in Hz.
        user_contour (np.ndarray): The user's pitch contour in Hz.

    Returns:
        str: The saved plot file path.
    """
    output_path = Path("outputs/pitch/pitch_comparison.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 6))
    plt.plot(reference_contour, label="Reference Pitch")
    plt.plot(user_contour, label="User Pitch")
    plt.xlabel("Frame")
    plt.ylabel("Pitch (Hz)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return output_path.as_posix()


def save_pitch_contour(pitch_values: np.ndarray, output_path: str) -> None:
    """
    Saves extracted pitch values to a CSV file for later visualization or analysis.

    Args:
        pitch_values (np.ndarray): The continuous series of estimated pitches in Hz.
        output_path (str): The destination path where the CSV file should be written.

    Raises:
        ValueError: If the provided pitch array is empty.
        OSError: If there are permission or filesystem errors writing the file.
    """
    if pitch_values.size == 0:
        raise ValueError("Cannot save an empty array of pitch values.")

    path = Path(output_path)
    
    # Ensure outputs/pitch exists
    pitch_out_dir = Path("outputs/pitch")
    pitch_out_dir.mkdir(parents=True, exist_ok=True)
    
    # Also ensure the parent of the specified path exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Step 2: Structure Data
    # Wrap the raw numbers into an easy-to-read tabular format using pandas.
    df = pd.DataFrame({
        "frame_index": range(len(pitch_values)),
        "pitch_hz": pitch_values
    })

    # Step 3: Write Output
    try:
        # Write to disk. We set index=False so pandas doesn't write out the row numbers.
        df.to_csv(path, index=False)
    except OSError as e:
        raise OSError(f"Failed to write pitch contour to {output_path}: {e}") from e

    print(f"Successfully saved pitch contour to: {path.as_posix()}")


if __name__ == "__main__":
    # USAGE EXAMPLE
    test_audio = "outputs/htdemucs/song/vocals.wav"
    out_csv = "outputs/pitch_contour.csv"

    try:
        print(f"Extracting pitches from {test_audio} using TorchCREPE...")
        extracted_pitches = extract_pitch(test_audio)
        
        print(f"Extracted {len(extracted_pitches)} pitch values.")
        
        save_pitch_contour(extracted_pitches, out_csv)
        
    except FileNotFoundError:
        print(f"Please ensure '{test_audio}' exists in the current directory before running this test.")
    except Exception as general_error:
        print(f"An error occurred: {general_error}")
