from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import subprocess
from hashlib import sha256
from pathlib import Path
import logging
from uuid import uuid4
from services.pitch_service import (
    calculate_pitch_score,
    compare_pitch_contours,
    extract_pitch,
    plot_pitch_contours
)
from services.rhythm_service import (
    extract_onsets,
    compare_rhythm,
    extract_tempo,
    compare_tempo
)
from services.timbre_service import (
    extract_audio_embedding,
    compare_embeddings,
    calculate_timbre_score
)
from services.feedback_service import generate_feedback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PitchAnalysisRequest(BaseModel):
    reference_vocals_path: str
    user_vocals_path: str

class TimbreAnalysisRequest(BaseModel):
    reference_vocals_path: str
    user_vocals_path: str

class PerformanceAnalysisRequest(BaseModel):
    reference_vocals_path: str
    user_vocals_path: str


class FeedbackGenerationRequest(BaseModel):
    pitch_score: float
    rhythm_score: float
    tempo_score: float
    timbre_score: float
    overall_score: float

# 1. Use pathlib.Path for setting up directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/")
def root():
    return {"message": "AI Music App Running"}


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as audio_file:
        for chunk in iter(lambda: audio_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_same_audio_file(reference_path: Path, user_path: Path) -> bool:
    """
    Returns True when both analysis inputs point to the same file or identical bytes.

    This prevents duplicate model inference from turning an exact self-comparison into
    a 99.x score due to tiny nondeterministic or floating-point differences.
    """
    try:
        if reference_path.resolve() == user_path.resolve():
            return True
        if reference_path.stat().st_size != user_path.stat().st_size:
            return False
        return _file_sha256(reference_path) == _file_sha256(user_path)
    except OSError:
        return False


@app.post("/analyze-pitch")
def analyze_pitch(request: PitchAnalysisRequest):
    reference_path = Path(request.reference_vocals_path)
    user_path = Path(request.user_vocals_path)

    if not reference_path.is_file():
        logger.error(f"Reference file not found: {reference_path}")
        raise HTTPException(status_code=400, detail="Reference vocals file was not found.")
    if not user_path.is_file():
        logger.error(f"User file not found: {user_path}")
        raise HTTPException(status_code=400, detail="User vocals file was not found.")

    try:
        same_audio_file = _is_same_audio_file(reference_path, user_path)

        logger.info("Extracting reference pitch contour...")
        reference_pitch = extract_pitch(reference_path.as_posix())
        
        if same_audio_file:
            logger.info("Same audio detected; reusing reference pitch contour.")
            user_pitch = reference_pitch.copy()
        else:
            logger.info("Extracting user pitch contour...")
            user_pitch = extract_pitch(user_path.as_posix())
        
        logger.info("Comparing pitch contours...")
        pitch_comparison = compare_pitch_contours(reference_pitch, user_pitch)
        average_pitch_error = pitch_comparison["average_difference"]
        max_diff = pitch_comparison["max_difference"]
        min_diff = pitch_comparison["min_difference"]
        
        logger.info("Calculating pitch score...")
        pitch_score = calculate_pitch_score(average_pitch_error)
        
        logger.info("Generating pitch comparison graph...")
        graph_path = plot_pitch_contours(reference_pitch, user_pitch)
        
    except ValueError as exc:
        logger.error(f"ValueError during analysis: {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error(f"RuntimeError during analysis: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected error during analysis: {exc}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc

    return {
        "pitch_score": pitch_score,
        "average_difference": average_pitch_error,
        "max_difference": max_diff,
        "min_difference": min_diff,
        "graph_path": graph_path
    }


@app.post("/analyze-timbre")
def analyze_timbre(request: TimbreAnalysisRequest):
    reference_path = Path(request.reference_vocals_path)
    user_path = Path(request.user_vocals_path)

    if not reference_path.is_file():
        logger.error(f"Reference file not found: {reference_path}")
        raise HTTPException(status_code=400, detail="Reference vocals file was not found.")
    if not user_path.is_file():
        logger.error(f"User file not found: {user_path}")
        raise HTTPException(status_code=400, detail="User vocals file was not found.")

    try:
        same_audio_file = _is_same_audio_file(reference_path, user_path)

        logger.info("Extracting embeddings for timbre analysis...")
        ref_embedding = extract_audio_embedding(reference_path.as_posix())
        if same_audio_file:
            logger.info("Same audio detected; reusing reference timbre embedding.")
            user_embedding = ref_embedding.copy()
        else:
            user_embedding = extract_audio_embedding(user_path.as_posix())

        logger.info("Comparing embeddings for timbre analysis...")
        comparison = compare_embeddings(ref_embedding, user_embedding)
        similarity = comparison.get("similarity", 0.0)

        logger.info("Calculating timbre score...")
        timbre_score = calculate_timbre_score(similarity)

    except RuntimeError as exc:
        logger.error(f"RuntimeError during timbre analysis: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected error during timbre analysis: {exc}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc

    return {
        "timbre_score": float(timbre_score),
        "similarity": float(similarity)
    }


def calculate_overall_score(
    pitch_score: float,
    rhythm_score: float,
    tempo_score: float,
    timbre_score: float
) -> float:
    """
    Calculates the overall performance score using a weighted system.

    Weighting System:
    - Pitch (50%): The most critical component of singing. Adjusting and hitting the correct notes.
    - Rhythm (25%): Timing and hitting notes at the correct time (onsets).
    - Tempo (10%): Overall speed consistency.
    - Timbre (15%): Tone, style, and texture consistency compared to the reference track.

    Args:
        pitch_score (float): Score between 0 and 100
        rhythm_score (float): Score between 0 and 100
        tempo_score (float): Score between 0 and 100
        timbre_score (float): Score between 0 and 100

    Returns:
        float: The calculated overall score rounded to 2 decimal places.
    """
    # 1. Validate all input scores are between 0 and 100
    for name, s in [('pitch', pitch_score), ('rhythm', rhythm_score), ('tempo', tempo_score), ('timbre', timbre_score)]:
        if not (0 <= s <= 100):
            logger.warning(f"Invalid score for {name}: {s}. Clamping for calculation.")

    # Calculate weighted contributions
    pitch_contribution = max(0.0, min(100.0, pitch_score)) * 0.50
    rhythm_contribution = max(0.0, min(100.0, rhythm_score)) * 0.25
    tempo_contribution = max(0.0, min(100.0, tempo_score)) * 0.10
    timbre_contribution = max(0.0, min(100.0, timbre_score)) * 0.15

    overall_score = pitch_contribution + rhythm_contribution + tempo_contribution + timbre_contribution

    # Log individual contributions
    logger.info(f"Pitch contribution: {pitch_contribution}")
    logger.info(f"Rhythm contribution: {rhythm_contribution}")
    logger.info(f"Tempo contribution: {tempo_contribution}")
    logger.info(f"Timbre contribution: {timbre_contribution}")
    logger.info(f"Final original score (raw): {overall_score}")

    # 2. Clamp final result between 0 and 100
    overall_score = max(0.0, min(100.0, overall_score))

    # 3. Round final score to 2 decimal places
    overall_score = round(overall_score, 2)

    logger.info(f"Final overall score (clamped & rounded): {overall_score}")

    return overall_score

@app.post("/analyze-performance")
def analyze_performance(request: PerformanceAnalysisRequest):
    reference_path = Path(request.reference_vocals_path)
    user_path = Path(request.user_vocals_path)

    if not reference_path.is_file():
        logger.error(f"Reference file not found: {reference_path}")
        raise HTTPException(status_code=400, detail="Reference vocals file was not found.")
    if not user_path.is_file():
        logger.error(f"User file not found: {user_path}")
        raise HTTPException(status_code=400, detail="User vocals file was not found.")

    try:
        same_audio_file = _is_same_audio_file(reference_path, user_path)

        # --- Pitch Analysis ---
        logger.info("Extracting reference pitch contour...")
        reference_pitch = extract_pitch(reference_path.as_posix())
        if same_audio_file:
            logger.info("Same audio detected; reusing reference pitch contour.")
            user_pitch = reference_pitch.copy()
        else:
            logger.info("Extracting user pitch contour...")
            user_pitch = extract_pitch(user_path.as_posix())
        
        logger.info("Comparing pitch contours...")
        pitch_comparison = compare_pitch_contours(reference_pitch, user_pitch)
        pitch_score = calculate_pitch_score(pitch_comparison["average_difference"])
        
        # --- Rhythm Analysis ---
        logger.info("Extracting reference onsets...")
        reference_onsets = extract_onsets(reference_path.as_posix())
        if same_audio_file:
            logger.info("Same audio detected; reusing reference onsets.")
            user_onsets = reference_onsets.copy()
        else:
            logger.info("Extracting user onsets...")
            user_onsets = extract_onsets(user_path.as_posix())
        
        logger.info("Comparing rhythm...")
        rhythm_comparison = compare_rhythm(reference_onsets, user_onsets)
        rhythm_score = rhythm_comparison["rhythm_score"]
        
        # --- Tempo Analysis ---
        logger.info("Extracting reference tempo...")
        reference_tempo = extract_tempo(reference_path.as_posix())
        if same_audio_file:
            logger.info("Same audio detected; reusing reference tempo.")
            user_tempo = reference_tempo
        else:
            logger.info("Extracting user tempo...")
            user_tempo = extract_tempo(user_path.as_posix())
        
        logger.info("Comparing tempo...")
        tempo_comparison = compare_tempo(reference_tempo, user_tempo)
        tempo_score = tempo_comparison["tempo_score"]
        
        # --- Timbre Analysis ---
        logger.info("Extracting reference embedding...")
        reference_embedding = extract_audio_embedding(reference_path.as_posix())
        if same_audio_file:
            logger.info("Same audio detected; reusing reference embedding.")
            user_embedding = reference_embedding.copy()
        else:
            logger.info("Extracting user embedding...")
            user_embedding = extract_audio_embedding(user_path.as_posix())

        logger.info("Comparing embeddings...")
        timbre_comparison = compare_embeddings(reference_embedding, user_embedding)
        timbre_score = calculate_timbre_score(timbre_comparison.get("similarity", 0.0))

        # --- Overall Score ---
        logger.info("Calculating overall score...")
        overall_score = calculate_overall_score(
            pitch_score=pitch_score,
            rhythm_score=rhythm_score,
            tempo_score=tempo_score,
            timbre_score=timbre_score
        )
        
    except ValueError as exc:
        logger.error(f"ValueError during analysis: {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error(f"RuntimeError during analysis: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected error during analysis: {exc}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc

    return {
        "pitch_score": float(pitch_score),
        "rhythm_score": float(rhythm_score),
        "tempo_score": float(tempo_score),
        "timbre_score": float(timbre_score),
        "overall_score": float(overall_score)
    }


@app.post("/generate-feedback")
def generate_feedback_endpoint(request: FeedbackGenerationRequest):
    try:
        feedback = generate_feedback(
            pitch_score=request.pitch_score,
            rhythm_score=request.rhythm_score,
            tempo_score=request.tempo_score,
            timbre_score=request.timbre_score,
            overall_score=request.overall_score,
        )
    except RuntimeError as exc:
        logger.error("Feedback generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error during feedback generation")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc

    return {"feedback": feedback}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info("upload started")
    original_filename = Path(file.filename).name
    original_path = Path(original_filename)

    if not original_filename.lower().endswith((".mp3", ".wav")):
        raise HTTPException(status_code=400, detail="Only mp3 and wav files are allowed.")
    
    # 2. Reject files larger than 50MB
    MAX_FILE_SIZE = 50 * 1024 * 1024 # 50MB
    if getattr(file, "size", 0) and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
    
    # 3. Use pathlib operator (/) to safely construct paths
    filename = f"{original_path.stem}-{uuid4().hex[:8]}{original_path.suffix.lower()}"
    file_path = UPLOAD_DIR / filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {exc}") from exc

    logger.info("running demucs")
    try:
        subprocess.run(
            ["demucs", "-o", str(OUTPUT_DIR), str(file_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail="Demucs is not installed or is not available on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        error_output = exc.stderr or exc.stdout or str(exc)
        raise HTTPException(status_code=500, detail=f"Demucs processing failed: {error_output}") from exc

    # 3. Construct the vocals.wav path as a relative Path object
    vocals_path = OUTPUT_DIR / "htdemucs" / Path(filename).stem / "vocals.wav"

    # 4. Check for existence clearly using the boolean method
    if not vocals_path.exists():
        raise HTTPException(status_code=500, detail="Demucs completed but vocals output was not found.")
        
    logger.info("separation completed")
    # 5. Simplify API response to standard JSON mapping, using .as_posix() 
    return {
        "success": True,
        "vocals_path": vocals_path.as_posix()
    }
