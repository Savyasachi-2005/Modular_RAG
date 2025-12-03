import { useState, useRef, useEffect } from 'react';
import { VoiceInput } from './VoiceInput';

export function QueryInput({ onSend, disabled }) {
  const [query, setQuery] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [query]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !disabled) {
      onSend(query.trim());
      setQuery('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Handle voice transcription - just set the text
  const handleTranscribe = (text) => {
    setQuery(text);
  };

  // Handle auto-submit from voice input
  const handleVoiceAutoSubmit = (text) => {
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setQuery('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <textarea
        ref={textareaRef}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question..."
        disabled={disabled}
        rows={1}
        className="w-full px-4 py-3 pr-24 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 resize-none text-sm transition-all overflow-hidden"
        style={{ minHeight: '44px', maxHeight: '200px' }}
      />
      <div className="absolute right-2 bottom-2 flex items-center gap-1">
        <VoiceInput 
          onTranscribe={handleTranscribe}
          onAutoSubmit={handleVoiceAutoSubmit}
          disabled={disabled}
        />
        <button
          type="submit"
          disabled={disabled || !query.trim()}
          className="p-2 bg-orange-500 text-white rounded-md hover:bg-orange-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </form>
  );
}
