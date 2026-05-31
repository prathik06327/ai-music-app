import sys
import numpy as np
from services.rhythm_service import extract_onsets

def main():
    """
    Test script to verify the rhythm extraction pipeline.
    It loads an audio file, extracts the onset times, and prints timing statistics.
    """
    audio_file = "outputs/htdemucs/song/vocals.wav"
    
    try:
        print(f"Extracting onsets from: {audio_file}")
        
        # 1. & 2. Load audio and extract onset times
        onset_times = extract_onsets(audio_file)
        
        # 3. Print metrics
        print("\n--- Rhythm Metrics ---")
        print(f"Number of onsets detected: {len(onset_times)}")
        
        print("\n--- First 20 Onset Timestamps (seconds) ---")
        print(np.round(onset_times[:20], 3))
        
    except FileNotFoundError:
        print(f"Error: Could not find the file '{audio_file}'.")
    except Exception as e:
        print(f"Error during rhythm extraction test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()