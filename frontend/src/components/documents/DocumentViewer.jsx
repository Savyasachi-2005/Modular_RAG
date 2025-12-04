import { useState, useEffect } from 'react';

export function DocumentViewer({ document, onClose }) {
  const [loading, setLoading] = useState(true);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger animation after mount
    setTimeout(() => setIsVisible(true), 10);
  }, []);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300); // Wait for animation to complete
  };

  const handleLoad = () => {
    setLoading(false);
  };

  const getFileType = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    return ext;
  };

  const renderContent = () => {
    const fileType = getFileType(document.filename);
    
    if (fileType === 'pdf') {
      // Get the API URL from environment or use default
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      return (
        <iframe
          src={`${apiUrl}/documents/view/${document.filename}`}
          className="w-full h-full border-0"
          onLoad={handleLoad}
          title={document.title}
        />
      );
    }
    
    if (['txt', 'md'].includes(fileType)) {
      return (
        <div className="p-6 h-full overflow-y-auto bg-gray-50">
          <pre className="whitespace-pre-wrap font-mono text-sm text-gray-800 leading-relaxed">
            {document.content || 'Content not available for preview'}
          </pre>
        </div>
      );
    }
    
    return (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <div className="text-center p-8">
          <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{document.title}</h3>
          <p className="text-gray-600 mb-4">Preview not available for {fileType.toUpperCase()} files</p>
          <div className="inline-block bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <p className="text-sm text-gray-700 text-left space-y-1">
              <span className="block"><span className="font-medium">File:</span> {document.filename}</span>
              <span className="block"><span className="font-medium">Chunks:</span> {document.chunks}</span>
              <span className="block"><span className="font-medium">Uploaded:</span> {new Date(document.uploaded_at).toLocaleDateString()}</span>
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Backdrop */}
      <div 
        className={`fixed inset-0 bg-black transition-opacity duration-300 z-40 ${
          isVisible ? 'bg-opacity-40' : 'bg-opacity-0'
        }`}
        onClick={handleClose}
      />
      
      {/* Slide-in Panel */}
      <div 
        className={`fixed top-0 right-0 h-full w-full md:w-3/4 lg:w-2/3 xl:w-1/2 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-out ${
          isVisible ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-white">
          <div className="flex-1 min-w-0 mr-4">
            <h2 className="text-lg font-semibold text-gray-900 truncate">{document.title}</h2>
            <p className="text-sm text-gray-500 truncate">{document.filename}</p>
          </div>
          <button
            onClick={handleClose}
            className="flex-shrink-0 p-2 hover:bg-gray-100 rounded-full transition-colors"
            aria-label="Close preview"
          >
            <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="h-[calc(100%-73px)] relative bg-gray-50">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 z-10">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
                <p className="text-sm text-gray-600">Loading document...</p>
              </div>
            </div>
          )}
          {renderContent()}
        </div>
      </div>
    </>
  );
}
