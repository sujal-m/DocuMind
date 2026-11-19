import React, { useState } from 'react';
import UploadDropzone from '../components/documents/UploadDropzone';
import DocumentList from '../components/documents/DocumentList';
import DocumentDetailModal from '../components/documents/DocumentDetailModal';

export default function DocumentsPage() {
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Document Knowledge Base</h1>
        <p className="text-sm text-slate-400 mt-1">
          Ingest, manage, and inspect your heterogeneous document catalog for grounded RAG research.
        </p>
      </div>

      {/* Upload Zone */}
      <UploadDropzone onUploadSuccess={handleUploadSuccess} />

      {/* Document Library Table */}
      <DocumentList
        onSelectDocument={(id) => setSelectedDocId(id)}
        refreshTrigger={refreshTrigger}
      />

      {/* Modal Inspector */}
      {selectedDocId && (
        <DocumentDetailModal
          documentId={selectedDocId}
          onClose={() => setSelectedDocId(null)}
        />
      )}
    </div>
  );
}

