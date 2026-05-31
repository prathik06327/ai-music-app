import sys
from services.pitch_service import extract_pitch, save_pitch_contour

def main():
    input_audio = "outputs/htdemucs/song/vocals.wav"
    output_csv = "outputs/pitch/reference_pitch.csv"
    
    try:
        # Extract pitch
        pitch_values = extract_pitch(input_audio)
        print("Extraction success")
        print(f"Contour length: {len(pitch_values)}")
        
        # Save contour
        save_pitch_contour(pitch_values, output_csv)
        print(f"Save location: {output_csv}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()