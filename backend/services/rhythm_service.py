import librosa
import numpy as np
from services.audio_service import load_audio

def extract_onsets(audio_path: str) -> np.ndarray:
    """
    Extracts note onset times from an audio file.

    Onset:
    An onset is the exact moment when a new musical event (like a sung note, 
    a drum hit, or a plucked string) begins. It is characterized by a sudden 
    burst of energy in the audio signal.

    Rhythm Detection:
    By finding these onsets, we can map out the rhythm of a performance. 
    Comparing the onsets of a user's vocal track with those of the reference 
    track allows us to evaluate how well the user matched the intended rhythm.

    Note Timing:
    The output of this function is an array of timestamps (in seconds) indicating 
    when each note was sung. This note timing data is crucial for assessing rhythmic 
    accuracy separately from pitch accuracy.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        np.ndarray: An array of onset times in seconds.
    """
    # Load the audio using our existing audio service
    y, sr = load_audio(audio_path)
    
    # Use librosa to detect onsets
    # onset_detect returns frame indices by default
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    
    # Convert frame indices to time in seconds
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    
    return onset_times

def compare_rhythm(reference_onsets: np.ndarray, user_onsets: np.ndarray) -> dict:
    """
    Compares reference and user onset times to calculate timing differences 
    and produce an MVP rhythm score.

    This uses a basic alignment procedure by zipping the arrays up to the 
    shortest length between them.

    Args:
        reference_onsets (np.ndarray): The reference onset times in seconds.
        user_onsets (np.ndarray): The user onset times in seconds.

    Returns:
        dict: A dictionary containing 'average_timing_difference' and 'rhythm_score'.
    """
    min_length = min(len(reference_onsets), len(user_onsets))
    
    if min_length == 0:
        return {
            "average_timing_difference": 0.0,
            "rhythm_score": 0.0
        }
        
    reference_trimmed = reference_onsets[:min_length]
    user_trimmed = user_onsets[:min_length]
    
    # Calculate average timing difference in seconds
    timing_differences = np.abs(reference_trimmed - user_trimmed)
    average_timing_difference = float(np.mean(timing_differences))
    
    # Simple MVP rhythm scoring approach:
    # 1.0 seconds off = minus 100 points
    # (e.g. 0.1s off = score of 90)
    raw_score = 100 - (average_timing_difference * 100)
    rhythm_score = float(np.clip(raw_score, 0, 100))
    
    return {
        "average_timing_difference": average_timing_difference,
        "rhythm_score": rhythm_score
    }

def extract_tempo(audio_path: str) -> float:
    """
    Extracts the overall tempo of an audio file in Beats Per Minute (BPM).

    BPM (Beats Per Minute):
    BPM is a measure of tempo in music, describing how many beats occur in a single 
    minute. It gives a general sense of the speed or pace of the track. By comparing 
    the BPM of a user's performance against the reference, we can see if they 
    were singing consistently too fast or too slow overall.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        float: The estimated tempo in BPM.
    """
    # Load the audio
    y, sr = load_audio(audio_path)
    
    # Use librosa to estimate the tempo
    # beat_track returns the estimated tempo and the frame indices of the beats
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    
    # Depending on the librosa version, tempo can be a float or a 1D numpy array
    tempo_bpm = float(tempo[0] if isinstance(tempo, np.ndarray) else tempo)
    
    return tempo_bpm

def compare_tempo(reference_bpm: float, user_bpm: float) -> dict:
    """
    Compares reference and user Beats Per Minute (BPM) to calculate the 
    tempo difference and produce an MVP tempo score.

    Args:
        reference_bpm (float): The reference tempo in BPM.
        user_bpm (float): The user tempo in BPM.

    Returns:
        dict: A dictionary containing 'tempo_difference' and 'tempo_score'.
    """
    tempo_difference = abs(reference_bpm - user_bpm)
    
    # Simple MVP scoring formula:
    # Deduct 5 points for every 1 BPM off
    raw_score = 100 - (tempo_difference * 5)
    tempo_score = float(np.clip(raw_score, 0, 100))
    
    return {
        "tempo_difference": tempo_difference,
        "tempo_score": tempo_score
    }
