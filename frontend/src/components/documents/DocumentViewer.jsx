import { useState } from 'react';

export function DocumentViewer({ document, onClose }) {
  const [loading, setLoading] = useState(true);

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
      return (
        <iframe
          src={`/api/documents/view/${document.filename}`}
          className="w-full h-full border-0"
          onLoad={handleLoad}
          title={document.title}
        />
      );
    }
    
    if (['txt', 'md'].includes(fileType)) {
      return (
        <div className="p-6 h-full overflow-y-auto">
          <pre className="whitespace-pre-wrap font-mono text-sm text-gray-800 leading-relaxed">
            {document.content || 'Content not available for preview'}
          </pre>
        </div>
      );
    }
    
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{document.title}</h3>
          <p className="text-gray-600 mb-4">Preview not available for {fileType.toUpperCase()} files</p>
          <p className="text-sm text-gray-500">
            File: {document.filename}<br/>
            Chunks: {document.chunks}<br/>
            Uploaded: {new Date(document.uploaded_at).toLocaleDateString()}
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-4xl h-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{document.title}</h2>
            <p className="text-sm text-gray-500">{document.filename}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 relative">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
            </div>
          )}
          {renderContent()}
        </div>
      </div>
    </div>
  );
}
