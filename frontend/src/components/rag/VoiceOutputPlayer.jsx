import { useState, useRef, useEffect } from 'react';
import { speechService } from '../../services/speechService';
import { useToast } from '../../hooks/useToast';

/**
 * VoiceOutputPlayer Component
 * Converts text to speech and plays the audio.
 * Handles long stitched audio files with play/stop controls.
 * Can auto-play on mount or be triggered manually.
 */
export function VoiceOutputPlayer({ 
  text, 
  autoPlay = false, 
  onPlayStart, 
  onPlayEnd,
  className = '' 
}) {
  const [isLoading, setIsLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [hasAudio, setHasAudio] = useState(false);
  const audioRef = useRef(null);
  const { showToast } = useToast();

  // Cleanup audio URL on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, []);

  // Cleanup old audio URL when creating new one
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  // Auto-play on mount if enabled
  useEffect(() => {
    if (autoPlay && text && !hasAudio && !isLoading) {
      handlePlay();
    }
  }, [autoPlay, text]);

  const handlePlay = async () => {
    if (!text || isLoading) return;

    // If we already have audio loaded, just play it
    if (hasAudio && audioRef.current) {
      try {
        audioRef.current.currentTime = 0;
        await audioRef.current.play();
        setIsPlaying(true);
        onPlayStart?.();
      } catch (error) {
        console.error('Error playing cached audio:', error);
      }
      return;
    }

    setIsLoading(true);
    try {
      const audioBlob = await speechService.textToSpeech(text);
      const url = URL.createObjectURL(audioBlob);
      
      // Cleanup previous URL if exists
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
      setAudioUrl(url);

      // Create audio element with proper event handlers
      const audio = new Audio();
      audioRef.current = audio;
      
      // Set up event handlers before setting src
      audio.onplay = () => {
        setIsPlaying(true);
        onPlayStart?.();
      };

      audio.onpause = () => {
        setIsPlaying(false);
      };

      audio.onended = () => {
        setIsPlaying(false);
        onPlayEnd?.();
      };

      audio.onerror = (e) => {
        console.error('Audio playback error:', e);
        setIsPlaying(false);
        setHasAudio(false);
        showToast({ type: 'error', message: 'Failed to play audio.' });
      };

      audio.oncanplaythrough = () => {
        setHasAudio(true);
      };

      // Set source and load
      audio.src = url;
      audio.load();

      // Wait for audio to be ready then play
      await new Promise((resolve, reject) => {
        audio.oncanplaythrough = () => {
          setHasAudio(true);
          resolve();
        };
        audio.onerror = reject;
      });

      await audio.play();
      
    } catch (error) {
      console.error('Error converting text to speech:', error);
      showToast({ 
        type: 'error', 
        message: error.response?.data?.detail || 'Failed to convert text to speech.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const handleToggle = () => {
    if (isPlaying) {
      handleStop();
    } else {
      handlePlay();
    }
  };

  return (
    <div className={`inline-flex items-center gap-1 ${className}`}>
      {/* Play/Loading button */}
      <button
        type="button"
        onClick={handleToggle}
        disabled={isLoading || !text}
        className={`
          p-1.5 rounded-md transition-all duration-200 inline-flex items-center justify-center
          ${isPlaying 
            ? 'bg-orange-100 text-orange-600 hover:bg-orange-200' 
            : 'bg-gray-100 text-gray-500 hover:bg-gray-200 hover:text-gray-700'
          }
          ${isLoading ? 'opacity-50 cursor-wait' : ''}
          ${!text ? 'opacity-40 cursor-not-allowed' : ''}
        `}
        title={isPlaying ? 'Pause' : isLoading ? 'Loading audio...' : 'Play audio'}
      >
        {isLoading ? (
          // Loading spinner
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        ) : isPlaying ? (
          // Pause icon (two vertical bars)
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <rect x="6" y="5" width="4" height="14" rx="1" />
            <rect x="14" y="5" width="4" height="14" rx="1" />
          </svg>
        ) : (
          // Speaker/Play icon
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          </svg>
        )}
      </button>

      {/* Stop button - only visible when playing or has audio loaded */}
      {(isPlaying || hasAudio) && (
        <button
          type="button"
          onClick={handleStop}
          disabled={!isPlaying && !hasAudio}
          className={`
            p-1.5 rounded-md transition-all duration-200 inline-flex items-center justify-center
            ${isPlaying 
              ? 'bg-red-100 text-red-600 hover:bg-red-200' 
              : 'bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-gray-600'
            }
          `}
          title="Stop and reset"
        >
          {/* Stop icon (square) */}
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <rect x="6" y="6" width="12" height="12" rx="1" />
          </svg>
        </button>
      )}
    </div>
  );
}
