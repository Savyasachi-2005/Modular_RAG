"""
Speech Schemas
Pydantic models for speech-related request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional


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


class SpeechServiceStatus(BaseModel):
    """Response schema for service status check."""
    available: bool = Field(..., description="Whether the service is available")
    message: str = Field(..., description="Status message")
