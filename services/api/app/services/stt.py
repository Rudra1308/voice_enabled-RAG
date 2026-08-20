import asyncio
import io
import logging
from concurrent.futures import ThreadPoolExecutor

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

class SpeechToTextEngine:
    _instance = None
    
    def __init__(self, model_size: str = "base"):
        self.groq_api_key = settings.GROQ_API_KEY
        if not self.groq_api_key:
            import torch
            from faster_whisper import WhisperModel
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.compute_type = "float16" if self.device == "cuda" else "int8"
            logger.info(f"Loading Whisper model {model_size} on {self.device} with compute_type={self.compute_type}")
            self.model = WhisperModel(model_size, device=self.device, compute_type=self.compute_type)
            self.executor = ThreadPoolExecutor(max_workers=2)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _transcribe_sync(self, audio_data: bytes) -> str:
        audio_stream = io.BytesIO(audio_data)
        segments, _info = self.model.transcribe(audio_stream, beam_size=5)
        text = "".join([segment.text for segment in segments])
        return text.strip()

    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribes audio bytes into text."""
        if self.groq_api_key:
            # Use Groq API
            url = "https://api.groq.com/openai/v1/audio/transcriptions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}"
            }
            # We need to send the audio data as a file
            files = {
                "file": ("audio.webm", audio_data, "audio/webm")
            }
            data = {
                "model": "whisper-large-v3-turbo"
            }
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, headers=headers, files=files, data=data)
                    response.raise_for_status()
                    result = response.json()
                    return result.get("text", "").strip()
            except Exception as e:
                logger.error(f"Error communicating with Groq Whisper: {e!s}")
                return ""
        else:
            # Local fallback
            loop = asyncio.get_running_loop()
            text = await loop.run_in_executor(self.executor, self._transcribe_sync, audio_data)
            return text

stt_engine = SpeechToTextEngine()
