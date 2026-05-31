import numpy as np
from services.pitch_service import extract_pitch

def main():
    """
    Test script to verify the pitch extraction pipeline using TorchCREPE.
    It loads an audio file, extracts the pitch contour, and prints basic statistics.
    """
    print("-" * 40)
    print("Pitch Extraction Test")
    print("-" * 40)
    
    audio_file = "outputs/htdemucs/song/vocals.wav"
    
    try:
        print(f"Extracting pitch from '{audio_file}'... (This may take a moment based on your CPU)")
        
        # Extract the pitch contour
        pitch_contour = extract_pitch(audio_file)
        
        # Calculate statistics
        contour_length = len(pitch_contour)
        first_20_values = np.round(pitch_contour[:20], 2)
        
        # Ignore 0s and NaNs which might represent unvoiced frames
        valid_pitches = pitch_contour[~np.isnan(pitch_contour)]
        valid_pitches = valid_pitches[valid_pitches > 0]
        
        # Print output
        print(f"Contour Length: {contour_length} frames")
        print("\nFirst 20 pitch values (Hz):")
        print(first_20_values)
        
        if len(valid_pitches) > 0:
            print(f"\nMinimum Pitch: {np.min(valid_pitches):.2f} Hz")
            print(f"Maximum Pitch: {np.max(valid_pitches):.2f} Hz")
        else:
            print("\nNo voiced frames detected (array is empty or filled with 0s/NaNs).")
            
    except FileNotFoundError:
        print(f"Error: Could not find '{audio_file}'. Remember to place it in the same directory.")
    except Exception as e:
        print(f"Error executing pitch extraction:\n{e}")
    finally:
        print("-" * 40)

if __name__ == "__main__":
    main()
