import asyncio
import io
import logging
from concurrent.futures import ThreadPoolExecutor

import torch
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

class SpeechToTextEngine:
    _instance = None
    
    def __init__(self, model_size: str = "base"):
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
        # faster-whisper accepts file path or binary file-like object
        audio_stream = io.BytesIO(audio_data)
        segments, _info = self.model.transcribe(audio_stream, beam_size=5)
        
        text = "".join([segment.text for segment in segments])
        return text.strip()

    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribes audio bytes into text."""
        # Run in threadpool to prevent blocking the async event loop
        loop = asyncio.get_running_loop()
        text = await loop.run_in_executor(self.executor, self._transcribe_sync, audio_data)
        return text

stt_engine = SpeechToTextEngine()
