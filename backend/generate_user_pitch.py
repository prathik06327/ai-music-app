import sys
from services.pitch_service import extract_pitch, save_pitch_contour

def main():
    # Assuming user vocals are named user_vocals.wav or passed through uploads
    input_audio = "user_vocals.wav"
    output_csv = "outputs/pitch/user_pitch.csv"
    
    try:
        print(f"DEBUG: Attempting to extract pitch from '{input_audio}'...")
        pitch_values = extract_pitch(input_audio)
        
        print(f"DEBUG: Extraction successful.")
        print(f"DEBUG: Number of frames extracted: {len(pitch_values)}")
        print(f"DEBUG: First 5 pitch values (Hz): {pitch_values[:5]}")
        
        print(f"DEBUG: Saving pitch contour to '{output_csv}'...")
        save_pitch_contour(pitch_values, output_csv)
        
        print("DEBUG: Process completed successfully.")
        
    except Exception as e:
        print(f"ERROR: Failed during pitch processing - {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()