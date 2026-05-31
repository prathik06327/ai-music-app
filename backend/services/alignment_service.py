import numpy as np
import librosa

def align_pitch_contours(reference_pitch: np.ndarray, user_pitch: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Aligns two pitch contours using Dynamic Time Warping (DTW).
    
    Dynamic Time Warping (DTW) Explanation:
    DTW is an algorithm designed to measure similarity between two temporal sequences 
    that may vary in speed or timing. For example, if a user sings the same melody as 
    a reference track but slightly slower, faster, or with different phrasing, DTW 
    finds the optimal non-linear alignment between the two sequences.
    
    Warping Path Explanation:
    To perform the alignment, the DTW algorithm computes a "warping path" (wp). 
    This path maps indices of the reference sequence to indices of the user sequence 
    such that the overall distance (the accumulated difference in pitch) is minimized. 
    It ensures that matching musical notes are aligned together despite timing shifts.
    
    Contour Alignment Explanation:
    By following the computed warping path, we 'stretch' or 'squash' the original 
    pitch arrays so that they perfectly align in time. The resulting aligned arrays 
    will have the exact same length, making frame-by-frame comparison (like calculating 
    average differences or scores) highly accurate.
    
    Args:
        reference_pitch (np.ndarray): The reference pitch contour (1D NumPy array).
        user_pitch (np.ndarray): The user's pitch contour (1D NumPy array).
        
    Returns:
        tuple[np.ndarray, np.ndarray]: A tuple containing the aligned reference 
        pitch contour and the aligned user pitch contour (both having the same size).
        
    Raises:
        ValueError: If either of the input pitch contours is empty.
    """
    if reference_pitch.size == 0 or user_pitch.size == 0:
        raise ValueError("Cannot perform DTW alignment on empty pitch contours.")

    # 1. Perform Dynamic Time Warping
    # D is the accumulated cost matrix, wp is the optimal warping path finding the lowest cost.
    D, wp = librosa.sequence.dtw(X=reference_pitch, Y=user_pitch)
    
    # 2. Process the Warping Path
    # librosa.sequence.dtw returns the warping path in reverse chronological order 
    # (from the end of the arrays to the beginning). We use [::-1] to reverse it.
    wp_chronological = wp[::-1]
    
    # Extract the matching indices for both X (reference) and Y (user)
    ref_indices = wp_chronological[:, 0]
    user_indices = wp_chronological[:, 1]
    
    # 3. Create the Aligned Contours
    # We construct the fully aligned 1D sequences by fetching array values at the mapped indices.
    aligned_reference = reference_pitch[ref_indices]
    aligned_user = user_pitch[user_indices]
    
    return aligned_reference, aligned_user
