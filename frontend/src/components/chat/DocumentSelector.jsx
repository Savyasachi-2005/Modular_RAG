import { useState, useEffect } from 'react';
import { documentService } from '../../services/documentService';

export function DocumentSelector({ selectedDocs, onSelectionChange }) {
  const [documents, setDocuments] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const docs = await documentService.getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleDocument = (docId) => {
    const newSelection = selectedDocs.includes(docId)
      ? selectedDocs.filter(id => id !== docId)
      : [...selectedDocs, docId];
    onSelectionChange(newSelection);
  };

  const selectAll = () => {
    onSelectionChange(documents.map(doc => doc.filename));
  };

  const clearAll = () => {
    onSelectionChange([]);
  };

  return (
    <div className="px-4 py-3 border-b border-gray-200 bg-gray-50/30">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-3 py-2.5 text-sm font-medium text-gray-700 hover:bg-white hover:shadow-sm rounded-lg transition-all border border-transparent hover:border-gray-200"
      >
        <span className="flex items-center gap-2">
          <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>Filter Documents</span>
          {selectedDocs.length > 0 && (
            <span className="bg-blue-100 text-blue-700 text-xs font-semibold px-2 py-0.5 rounded-full">
              {selectedDocs.length}
            </span>
          )}
        </span>
        <svg 
          className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="mt-3 space-y-2 bg-white rounded-lg p-3 border border-gray-200">
          {loading ? (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
              <span className="ml-2 text-xs text-gray-500">Loading documents...</span>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-4">
              <svg className="w-8 h-8 text-gray-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-xs text-gray-500">No documents uploaded</p>
            </div>
          ) : (
            <>
              <div className="flex gap-2 pb-2 border-b border-gray-100">
                <button
                  onClick={selectAll}
                  className="flex-1 text-xs px-3 py-1.5 font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors border border-blue-200"
                >
                  Select All
                </button>
                <button
                  onClick={clearAll}
                  className="flex-1 text-xs px-3 py-1.5 font-medium text-gray-600 hover:bg-gray-100 rounded-md transition-colors border border-gray-200"
                >
                  Clear
                </button>
              </div>
              <div className="max-h-48 overflow-y-auto space-y-1 pt-1">
                {documents.map((doc) => (
                  <label
                    key={doc.filename}
                    className={`flex items-center gap-2.5 px-2.5 py-2 rounded-md cursor-pointer transition-all ${
                      selectedDocs.includes(doc.filename)
                        ? 'bg-blue-50 border border-blue-200'
                        : 'hover:bg-gray-50 border border-transparent'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedDocs.includes(doc.filename)}
                      onChange={() => toggleDocument(doc.filename)}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-900 truncate">{doc.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        <span className="inline-flex items-center gap-1">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                          </svg>
                          {doc.chunks} chunks
                        </span>
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
