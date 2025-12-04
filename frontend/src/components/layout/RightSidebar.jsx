import { useState } from "react";
import { NotesPanel } from "../notes/NotesPanel";

export function RightSidebar({ sessionId, onClose }) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div
      className={`bg-white border-l border-gray-200 flex flex-col h-full shadow-sm transition-all duration-300 ${
        isExpanded ? "w-80" : "w-16"
      }`}
    >
      {/* Header - Notes Toggle */}
      <div
        className="p-4 border-b border-gray-200"
        style={{ background: "linear-gradient(to bottom, rgb(249 250 251), white)" }}
      >
        <div className="flex items-center justify-between">
          {/* Close button for mobile */}
          {onClose && (
            <button
              onClick={onClose}
              className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Close sidebar"
            >
              <svg
                className="w-5 h-5 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}

          {/* Notes Toggle Button */}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className={`flex items-center gap-2 hover:bg-white hover:shadow-sm rounded-lg px-3 py-2.5 transition-all w-full border border-transparent hover:border-gray-200 ${
              !isExpanded ? "justify-center" : ""
            }`}
            title={isExpanded ? "Collapse notes" : "Expand notes"}
          >
            {isExpanded ? (
              <>
                <svg
                  className="w-4 h-4 text-amber-500 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
                <span className="text-sm font-medium text-gray-700">Notes</span>
                <svg
                  className="w-4 h-4 text-gray-400 ml-auto transition-transform"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </>
            ) : (
              <div className="flex items-center justify-center w-full py-1">
                {/* Larger SVG for collapsed state */}
                <svg
                  className="w-6 h-6 text-amber-500 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Notes Content */}
      <div className="flex-1 overflow-hidden">
        <NotesPanel sessionId={sessionId} isExpanded={isExpanded} hideHeader={true} />
      </div>
    </div>
  );
}
