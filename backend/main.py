from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import subprocess
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 1. Use pathlib.Path for setting up directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/")
def root():
    return {"message": "AI Music App Running"}

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
