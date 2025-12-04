import { useState, useEffect } from "react";
import { Button } from "../common/Button";
import { useToast } from "../../hooks/useToast";

export function NotesPanel({ sessionId, onClose, isExpanded = true, hideHeader = false }) {
  const [notes, setNotes] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const { showToast } = useToast();

  // Load notes for current session
  useEffect(() => {
    if (sessionId) {
      const savedNotes = localStorage.getItem(`notes_${sessionId}`);
      setNotes(savedNotes || "");
    } else {
      setNotes("");
    }
  }, [sessionId]);

  const handleSave = () => {
    if (!sessionId) {
      showToast({ type: "error", message: "No active session" });
      return;
    }

    setIsSaving(true);
    localStorage.setItem(`notes_${sessionId}`, notes);

    setTimeout(() => {
      setIsSaving(false);
      showToast({ type: "success", message: "Notes saved" });
    }, 300);
  };

  const handleClear = () => {
    if (window.confirm("Clear all notes? This cannot be undone.")) {
      setNotes("");
      if (sessionId) {
        localStorage.removeItem(`notes_${sessionId}`);
      }
      showToast({ type: "success", message: "Notes cleared" });
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header - Only show if not hidden */}
      {!hideHeader && (
        <div className="p-4 border-b border-gray-200" style={{ background: 'linear-gradient(to bottom, rgb(249 250 251), white)' }}>
          <div className="flex items-center justify-between">
            {/* Close button for mobile */}
            {onClose && (
              <button
                onClick={onClose}
                className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Close notes"
              >
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
            
            {/* Header Title */}
            <div className="flex items-center gap-2 flex-1">
              <svg className="w-5 h-5 text-amber-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span className="text-sm font-medium text-gray-700">Notes</span>
            </div>
          </div>
        </div>
      )}

      {/* Expanded Content */}
      {isExpanded && (
        <>


          {/* Notes Content */}
          <div className="flex-1 overflow-y-auto px-2 py-2">
            {!sessionId ? (
              <div className="text-center py-12 px-4">
                <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </div>
                <p className="text-sm font-medium text-gray-900 mb-1">No active session</p>
                <p className="text-xs text-gray-500">Select a chat to start taking notes</p>
              </div>
            ) : (
              <div className="space-y-3 px-2">
                {/* Notes Input Area */}
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Start typing your notes here...

• Key insights from the conversation
• Important points to remember  
• Follow-up questions
• Summary and action items"
                    className="w-full h-64 resize-none p-3 focus:outline-none text-sm text-gray-700 placeholder-gray-400 leading-relaxed"
                    style={{ minHeight: '200px' }}
                  />
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    onClick={handleSave}
                    disabled={!sessionId || isSaving}
                    className="shadow-sm hover:shadow-md transition-shadow"
                    size="sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                    </svg>
                    {isSaving ? "Saving..." : "Save"}
                  </Button>

                  <Button
                    onClick={handleClear}
                    disabled={!notes.trim()}
                    variant="secondary"
                    className="shadow-sm hover:shadow-md transition-shadow text-red-600 hover:text-red-700 hover:bg-red-50"
                    size="sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Clear
                  </Button>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
