"""
Transcription service using OpenAI Whisper API.
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI  
import asyncio

from app.core.config import settings


class TranscriptionService:
    """Service for transcribing audio files using OpenAI Whisper."""

    def __init__(self):
        """Initialize the transcription service."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe_audio(
        self, 
        file_path: str, 
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file using OpenAI Whisper.
        
        Args:
            file_path: Path to the audio file
            language: Optional language code (e.g., 'en', 'fr')
        
        Returns:
            Dictionary containing transcription and metadata
        """
        try:
            loop = asyncio.get_event_loop()
            
            def _transcribe():
                with open(file_path, "rb") as audio_file:
                    return self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        language=language,
                    )
            
            response = await loop.run_in_executor(None, _transcribe)
            # Extract segments with speaker identification (basic)
            segments = []
            if hasattr(response, 'segments') and response.segments:
                for segment in response.segments:
                    segments.append({
                        "text": getattr(segment, "text", ""),
                        "start": getattr(segment, "start", None),
                        "end": getattr(segment, "end", None),
                        "speaker": None
                    })
            
            
            return {
                "transcription": response.text,
                "language": response.language if hasattr(response, 'language') else language,
                "duration": response.duration if hasattr(response, 'duration') else None,
                "segments": segments
            }
        
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

    async def transcribe_with_speaker_diarization(
        self, 
        file_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio with basic speaker separation.
        
        Note: OpenAI Whisper doesn't provide native speaker diarization.
        This is a placeholder for potential future enhancement with services
        like AssemblyAI or Deepgram that offer speaker diarization.
        
        Args:
            file_path: Path to the audio file
            language: Optional language code
        
        Returns:
            Dictionary containing transcription with speaker segments
        """
        result = await self.transcribe_audio(file_path, language)
        
        # Add a note that speaker diarization is not available
        result["speaker_diarization_available"] = False
        
        return result


# Create a singleton instance
transcription_service = TranscriptionService()
