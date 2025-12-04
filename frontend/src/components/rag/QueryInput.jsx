import { useState, useRef, useEffect } from 'react';
import { VoiceInput } from './VoiceInput';

export function QueryInput({ onSend, disabled, onExportChat }) {
  const [query, setQuery] = useState('');
  const [showExportMenu, setShowExportMenu] = useState(false);
  const textareaRef = useRef(null);
  const exportMenuRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [query]);

  // Close export menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (exportMenuRef.current && !exportMenuRef.current.contains(event.target)) {
        setShowExportMenu(false);
      }
    };

    if (showExportMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showExportMenu]);

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

  const handleExport = (format) => {
    if (onExportChat) {
      onExportChat(format);
    }
    setShowExportMenu(false);
  };

  const handleSearch = () => {
    // Placeholder for future search functionality
    console.log('Search functionality - coming soon');
  };

  return (
    <div className="relative flex items-end gap-3">
      {/* Query Input Container */}

      <div className="flex-1">
        <form onSubmit={handleSubmit} className="relative">
          {/* Input container with improved design */}
          <div className="relative bg-white border border-gray-300 rounded-2xl shadow-sm hover:shadow-md focus-within:border-orange-500 focus-within:shadow-lg transition-all duration-200">
            <textarea
              ref={textareaRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your documents..."
              disabled={disabled}
              rows={1}
              className="w-full px-5 py-4 pr-16 bg-transparent focus:outline-none resize-none text-gray-900 placeholder-gray-500 overflow-hidden"
              style={{ minHeight: '56px', maxHeight: '120px' }}
            />
            
            {/* Enhanced Send button with right arrow */}
            <button
              type="submit"
              disabled={disabled || !query.trim()}
              className="absolute right-3 bottom-3 p-2.5 bg-orange-500 hover:bg-orange-600 text-white rounded-xl transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:bg-gray-400 shadow-sm hover:shadow-md transform hover:scale-105 disabled:hover:scale-100"
              title="Send message"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
          </div>
        </form>

      </div>

      {/* Options Box - Compact design */}
      <div className="w-24" ref={exportMenuRef}>
        <div className="relative bg-white border border-gray-300 rounded-2xl shadow-sm hover:shadow-md focus-within:border-orange-500 focus-within:shadow-lg transition-all duration-200">
          <div className="flex items-center gap-1 px-2 py-3">
            {/* Export Button */}
            <button
              type="button"
              onClick={() => setShowExportMenu(!showExportMenu)}
              disabled={disabled}
              className="p-2 text-green-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed flex-1"
              title="Export Chat"
            >
              <svg className="w-4 h-4 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </button>

            {/* Search Button */}
            <button
              type="button"
              onClick={handleSearch}
              disabled={disabled}
              className="p-2 text-blue-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed flex-1"
              title="Search (Coming Soon)"
            >
              <svg className="w-4 h-4 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </div>
        </div>

        {/* Export dropdown menu */}
        {showExportMenu && (
          <div className="absolute bottom-full right-0 mb-2 w-56 bg-white border border-gray-200 rounded-xl shadow-xl py-2 z-20">
            <button
              onClick={() => handleExport('markdown')}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3 transition-colors"
            >
              <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Export as Markdown</span>
            </button>
            <button
              onClick={() => handleExport('text')}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3 transition-colors"
            >
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Export as Text</span>
            </button>
            <button
              onClick={() => handleExport('pdf')}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3 transition-colors"
            >
              <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <span>Export as PDF</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
