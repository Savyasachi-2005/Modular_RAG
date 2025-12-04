import { useState } from 'react';
import { DocumentUpload } from '../documents/DocumentUpload';
import { DocumentSelector } from './DocumentSelector';
import { Button } from '../common/Button';

export function ChatSidebar({ 
  sessions, 
  currentSessionId, 
  onSessionSelect, 
  onNewSession,
  onDeleteSession,
  onUploadSuccess,
  selectedDocuments = [],
  onDocumentSelectionChange
}) {
  const [showUpload, setShowUpload] = useState(false);

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-full shadow-sm">
      {/* Header */}
      <div className="p-4 border-b border-gray-200" style={{ background: 'linear-gradient(to bottom, rgb(249 250 251), white)' }}>
        <Button 
          onClick={onNewSession} 
          className="w-full justify-center shadow-sm hover:shadow-md transition-shadow" 
          size="sm"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Chat
        </Button>
      </div>

      {/* Document Selector */}
      <DocumentSelector 
        selectedDocs={selectedDocuments}
        onSelectionChange={onDocumentSelectionChange}
      />

      {/* Upload Section */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50/30">
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="w-full flex items-center justify-between px-3 py-2.5 text-sm font-medium text-gray-700 hover:bg-white hover:shadow-sm rounded-lg transition-all border border-transparent hover:border-gray-200"
        >
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            Upload Document
          </span>
          <svg 
            className={`w-4 h-4 text-gray-400 transition-transform ${showUpload ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        {showUpload && (
          <div className="mt-3">
            <DocumentUpload 
              onUploadSuccess={() => {
                onUploadSuccess?.();
                setShowUpload(false);
              }}
              compact
            />
          </div>
        )}
      </div>

      {/* Sessions List - Google AI Studio Style */}
      <div className="flex-1 overflow-y-auto px-2 py-2">
        {sessions.length === 0 ? (
          <div className="text-center py-12 px-4">
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <p className="text-sm font-medium text-gray-900 mb-1">No chats yet</p>
            <p className="text-xs text-gray-500">Start a new conversation</p>
          </div>
        ) : (
          <div className="space-y-1">
            {sessions.map((session) => (
              <div
                key={session.session_id}
                className={`group relative rounded-lg cursor-pointer transition-all ${
                  currentSessionId === session.session_id
                    ? 'bg-orange-50 border-l-4 border-orange-500'
                    : 'hover:bg-gray-50 border-l-4 border-transparent'
                }`}
                onClick={() => onSessionSelect(session.session_id)}
              >
                <div className="px-3 py-2.5 flex items-center justify-between">
                  <div className="flex-1 min-w-0 pr-2">
                    {/* Chat Title */}
                    <p className={`text-sm truncate font-medium leading-tight ${
                      currentSessionId === session.session_id
                        ? 'text-gray-900'
                        : 'text-gray-700'
                    }`}>
                      {session.title}
                    </p>
                  </div>
                  
                  {/* Delete Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(session.session_id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 text-red-500 rounded transition-all shrink-0"
                    title="Delete chat"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
