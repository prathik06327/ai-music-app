"""
Audio Loading Verification Script

This script verifies that the audio loading pipeline is functioning correctly 
before integrating TorchCREPE pitch detection. It tests the `load_audio` 
function by attempting to load 'vocals.wav', and then calculates and prints 
the resulting waveform's shape, sample rate, and total duration.
"""

import librosa
from services.audio_service import load_audio

def main():
    """
    Executes the audio loading test.
    
    Attempts to load 'vocals.wav', analyzes the loaded audio properties, and 
    displays the results. Handles potential loading errors gracefully.
    """
    print("-" * 32)
    print("Audio Loading Test")
    print("-" * 32)
    
    file_to_test = "outputs/htdemucs/song/vocals.wav"
    
    try:
        # 3. Load the audio file
        audio, sample_rate = load_audio(file_to_test)
        
        # 4. Calculate audio duration
        duration = librosa.get_duration(y=audio, sr=sample_rate)
        
        # 5. Print the information
        print(f"Audio Shape: {audio.shape}")
        print(f"Sample Rate: {sample_rate} Hz")
        print(f"Duration: {duration:.2f} seconds")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find the file '{file_to_test}'.")
        print(f"Details: {e}")
    except ValueError as e:
        print(f"Error: Invalid audio file.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"Error: An unexpected issue occurred during loading.")
        print(f"Details: {e}")
    finally:
        print("-" * 32)

if __name__ == "__main__":
    main()
