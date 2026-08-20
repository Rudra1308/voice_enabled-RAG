from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.stt import stt_engine

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribes an uploaded audio file using Whisper."""
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be audio.")
        
    audio_data = await file.read()
    
    try:
        text = await stt_engine.transcribe(audio_data)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
