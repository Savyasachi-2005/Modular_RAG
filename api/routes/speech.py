"""
Speech Routes
API endpoints for speech-to-text and text-to-speech functionality.
"""

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Dict, Any
from pydantic import BaseModel, Field
from controller.speech_controller import speech_controller
from service.auth_service import get_current_user
import io

router = APIRouter(
    prefix="/speech",
    tags=["Speech Services"],
    responses={404: {"description": "Not found"}},
)


class TextToSpeechRequest(BaseModel):
    """Request schema for text-to-speech conversion."""
    text: str = Field(..., description="The text to convert to speech (any length - chunking handled internally)", min_length=1)
    target_language_code: str = Field("en-IN", description="Target language code")
    speaker: str = Field("anushka", description="Voice speaker name")
    pitch: float = Field(0, ge=-10, le=10, description="Voice pitch adjustment")
    pace: float = Field(1, ge=0.5, le=2, description="Speech pace/speed")
    loudness: float = Field(1, ge=0.5, le=2, description="Audio loudness")


class TranscriptionResponse(BaseModel):
    """Response schema for transcription."""
    text: str = Field(..., description="The transcribed text")


@router.post(
    "/to-text",
    response_model=TranscriptionResponse,
    summary="Convert speech to text"
)
async def speech_to_text(
    file: UploadFile = File(..., description="Audio file to transcribe (wav, mp3, webm, ogg)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Transcribe an audio file to text using SarvamAI ASR.
    
    Accepts audio files in common formats (wav, mp3, webm, ogg).
    Returns the recognized text from the audio.
    
    This is a protected endpoint and requires authentication.
    """
    return await speech_controller.transcribe_audio(file, current_user)


@router.post(
    "/to-audio",
    summary="Convert text to speech",
    responses={
        200: {
            "content": {"audio/wav": {}},
            "description": "Audio file stream"
        }
    }
)
async def text_to_speech(
    request: TextToSpeechRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Convert text to speech using SarvamAI TTS.
    
    Accepts text and optional voice parameters.
    Returns audio as a streaming response.
    
    This is a protected endpoint and requires authentication.
    """
    audio_bytes = await speech_controller.text_to_speech(
        text=request.text,
        user=current_user,
        target_language_code=request.target_language_code,
        speaker=request.speaker,
        pitch=request.pitch,
        pace=request.pace,
        loudness=request.loudness
    )
    
    # Return as streaming response
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/wav",
        headers={
            "Content-Disposition": "attachment; filename=speech.wav",
            "Content-Length": str(len(audio_bytes))
        }
    )


@router.get(
    "/health",
    summary="Speech service health check"
)
async def speech_health_check():
    """
    Check if the speech service is available and configured.
    """
    return await speech_controller.check_service_status()
