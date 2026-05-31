import sys
import numpy as np
from services.pitch_service import extract_pitch
from services.alignment_service import align_pitch_contours

def main():
    """
    Debugging utility to test Dynamic Time Warping (DTW) alignment.
    Loads a reference pitch contour and a user pitch contour (simulated here by 
    loading the same file or distinct ones), applies alignment, and prints metrics.
    """
    # For testing purposes, we use the separated vocal track. 
    # In a real scenario, user_audio would point to the user's recorded vocals.
    reference_audio = "outputs/htdemucs/song/vocals.wav"
    user_audio = "outputs/htdemucs/song/vocals.wav"
    
    try:
        print(f"Loading reference from: {reference_audio}")
        reference_contour = extract_pitch(reference_audio)
        
        print(f"Loading user from: {user_audio}")
        user_contour = extract_pitch(user_audio)
        
        # 1. Print Original Lengths
        print("\n--- Original Pitch Contours ---")
        print(f"Reference Length: {len(reference_contour)}")
        print(f"User Length: {len(user_contour)}")
        
        # 2. Run DTW Alignment
        print("\nRunning Dynamic Time Warping (DTW) alignment...")
        aligned_reference, aligned_user = align_pitch_contours(reference_contour, user_contour)
        
        # 3. Print Aligned Metrics
        print("\n--- Aligned Pitch Contours ---")
        print(f"Aligned Reference Length: {len(aligned_reference)}")
        print(f"Aligned User Length: {len(aligned_user)}")
        
        print("\n--- First 20 Aligned Values ---")
        # Ensure we only attempt to print up to 20 to prevent index errors on very short files
        print("Aligned Reference [0:20]:")
        print(np.round(aligned_reference[:20], 1))
        
        print("\nAligned User [0:20]:")
        print(np.round(aligned_user[:20], 1))
        
    except Exception as e:
        print(f"Error during DTW test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()