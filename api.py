import os
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

# Import the core logic from our existing main pipeline
from main import process_whatsapp_audio_to_intent

app = FastAPI(
    title="JEM HR Audio Intent API",
    description="API for ingesting native-language WhatsApp voice notes and processing them into HR intents.",
    version="1.0.0"
)

# A temporary directory to store the uploaded audio files before processing
TEMP_DIR = Path("temp_audio")
TEMP_DIR.mkdir(exist_ok=True)

@app.post("/process-audio/")
async def upload_and_process_audio(audio_file: UploadFile = File(...)):
    """
    Receives an audio file (e.g., from WhatsApp), saves it temporarily, and runs it 
    through the Whisper intent pipeline.
    """
    if not audio_file.filename:
        raise HTTPException(status_code=400, detail="No filename provided in upload.")
        
    temp_file_path = TEMP_DIR / audio_file.filename
    
    try:
        # Save the uploaded file to disk
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
            
        print(f"[API] Received and saved audio file: {temp_file_path}")
        
        # We assume OPENAI_API_KEY is already loaded in the environment where Uvicorn is running
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            # For local testing without a key, we'll fall back to our dummy key behavior from main.py
            print("[API] WARNING: OPENAI_API_KEY not found in environment. Using dummy key for testing.")
            api_key = "dummy-key-for-testing"
            
        # Run the audio through our business logic wrapper
        result = process_whatsapp_audio_to_intent(str(temp_file_path), openai_api_key=api_key)
        
        if result is None:
            # If the pipeline returned None, an internal safety check failed (invalid audio or API error)
            raise HTTPException(
                status_code=500, 
                detail="The audio processing pipeline failed. Check server logs for details (validation error, OpenAI API error, etc.)."
            )
            
        return JSONResponse(content=result)
        
    finally:
        # Always clean up the temporary file after processing to prevent disk-fill issues
        if temp_file_path.exists():
            temp_file_path.unlink()
            print(f"[API] Cleaned up temporary file: {temp_file_path}")

@app.get("/health")
def health_check():
    """Simple health check endpoint for monitoring."""
    return {"status": "healthy", "service": "whisper-pipeline"}
