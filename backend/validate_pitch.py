import sys
from services.pitch_service import (
    extract_pitch, 
    compare_pitch_contours, 
    calculate_pitch_score, 
    plot_pitch_contours
)

def main():
    audio_path = "outputs/htdemucs/song/vocals.wav"
    
    try:
        print(f"Loading reference and user audio from: {audio_path}")
        
        # 1. & 2. Load and extract pitch twice (simulating reference and user)
        print("Extracting reference pitch...")
        reference_contour = extract_pitch(audio_path)
        
        print("Extracting user pitch...")
        user_contour = extract_pitch(audio_path)
        
        # Print contour lengths
        print("\n--- Contour Lengths ---")
        print(f"Reference Contour Length: {len(reference_contour)}")
        print(f"User Contour Length: {len(user_contour)}")
        
        # 3. Compare pitch contours
        print("\nComparing pitch contours...")
        comparison_stats = compare_pitch_contours(reference_contour, user_contour)
        
        avg_diff = comparison_stats["average_difference"]
        max_diff = comparison_stats["max_difference"]
        min_diff = comparison_stats["min_difference"]
        
        # 4. Calculate pitch score
        final_score = calculate_pitch_score(avg_diff)
        
        # 5. Print metrics
        print("\n--- Pitch Comparison Metrics ---")
        print(f"Average Pitch Difference: {avg_diff:.2f} Hz")
        print(f"Max Pitch Difference: {max_diff:.2f} Hz")
        print(f"Min Pitch Difference: {min_diff:.2f} Hz")
        print(f"Final Pitch Score: {final_score:.2f} / 100")
        
        # Generate plot
        print("\n--- Generating Plot ---")
        plot_path = plot_pitch_contours(reference_contour, user_contour)
        print(f"Plot saved to: {plot_path}")
        
    except Exception as e:
        print(f"Error during validation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()