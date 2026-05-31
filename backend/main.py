from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
import subprocess
from pathlib import Path
import logging
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class PitchAnalysisRequest(BaseModel):
    reference_vocals_path: str
    user_vocals_path: str

class PerformanceAnalysisRequest(BaseModel):
    reference_vocals_path: str
    user_vocals_path: str

# 1. Use pathlib.Path for setting up directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/")
def root():
    return {"message": "AI Music App Running"}


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
        logger.info("Extracting reference pitch contour...")
        reference_pitch = extract_pitch(reference_path.as_posix())
        
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
        # --- Pitch Analysis ---
        logger.info("Extracting reference pitch contour...")
        reference_pitch = extract_pitch(reference_path.as_posix())
        logger.info("Extracting user pitch contour...")
        user_pitch = extract_pitch(user_path.as_posix())
        
        logger.info("Comparing pitch contours...")
        pitch_comparison = compare_pitch_contours(reference_pitch, user_pitch)
        pitch_score = calculate_pitch_score(pitch_comparison["average_difference"])
        
        # --- Rhythm Analysis ---
        logger.info("Extracting reference onsets...")
        reference_onsets = extract_onsets(reference_path.as_posix())
        logger.info("Extracting user onsets...")
        user_onsets = extract_onsets(user_path.as_posix())
        
        logger.info("Comparing rhythm...")
        rhythm_comparison = compare_rhythm(reference_onsets, user_onsets)
        rhythm_score = rhythm_comparison["rhythm_score"]
        
        # --- Tempo Analysis ---
        logger.info("Extracting reference tempo...")
        reference_tempo = extract_tempo(reference_path.as_posix())
        logger.info("Extracting user tempo...")
        user_tempo = extract_tempo(user_path.as_posix())
        
        logger.info("Comparing tempo...")
        tempo_comparison = compare_tempo(reference_tempo, user_tempo)
        tempo_score = tempo_comparison["tempo_score"]
        
        # --- Overall Score ---
        overall_score = (pitch_score + rhythm_score + tempo_score) / 3.0
        
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
        "rhythm_score": rhythm_score,
        "tempo_score": tempo_score,
        "overall_score": overall_score
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info("upload started")
    filename = Path(file.filename).name

    if not filename.lower().endswith((".mp3", ".wav")):
        raise HTTPException(status_code=400, detail="Only mp3 and wav files are allowed.")
    
    # 2. Reject files larger than 50MB
    MAX_FILE_SIZE = 50 * 1024 * 1024 # 50MB
    if getattr(file, "size", 0) and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
    
    # 3. Use pathlib operator (/) to safely construct paths
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
