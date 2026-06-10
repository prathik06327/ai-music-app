import logging
from main import calculate_overall_score

# Set up logging so we can see the debug logs from calculate_overall_score
logging.basicConfig(level=logging.INFO, format='%(message)s')

def run_test():
    print("========================================")
    print("Testing Overall Score Weighted System")
    print("========================================")
    
    pitch_score = 90
    rhythm_score = 80
    tempo_score = 95
    timbre_score = 70

    print(f"Inputs:")
    print(f" - Pitch Score:  {pitch_score} (Weight: 50%)")
    print(f" - Rhythm Score: {rhythm_score} (Weight: 25%)")
    print(f" - Tempo Score:  {tempo_score} (Weight: 10%)")
    print(f" - Timbre Score: {timbre_score} (Weight: 15%)")
    print("\n--- Weighting Calculation Log ---")

    overall = calculate_overall_score(
        pitch_score=pitch_score,
        rhythm_score=rhythm_score,
        tempo_score=tempo_score,
        timbre_score=timbre_score
    )

    print("----------------------------------------")
    print(f"Final Overall Score Result: {overall}")
    print("========================================")

if __name__ == "__main__":
    run_test()
