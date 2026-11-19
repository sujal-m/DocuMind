import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, X, Loader2 } from 'lucide-react';
import { documentService } from '../../services/documentService';

export default function UploadDropzone({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentFileName, setCurrentFileName] = useState('');
  const [feedback, setFeedback] = useState(null); // { type: 'success' | 'error' | 'info', message: '' }
  const fileInputRef = useRef(null);

  const handleFiles = async (files) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    const allowed = ['.pdf', '.docx', '.txt'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowed.includes(ext)) {
      setFeedback({
        type: 'error',
        message: `Invalid file type "${ext}". Supported formats: PDF, DOCX, TXT.`,
      });
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setFeedback({
        type: 'error',
        message: 'File size exceeds 50MB limit.',
      });
      return;
    }

    setUploading(true);
    setProgress(0);
    setCurrentFileName(file.name);
    setFeedback(null);

    try {
      const response = await documentService.uploadDocument(file, (p) => setProgress(p));
      const isDup = response.is_duplicate;
      setFeedback({
        type: isDup ? 'info' : 'success',
        message: isDup
          ? `"${file.name}" is already indexed in the knowledge base.`
          : `"${file.name}" uploaded successfully! Chunking and FAISS indexing started in background.`,
      });
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.message || 'Failed to upload document.',
      });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">Ingest Documents</h3>
          <p className="text-xs text-slate-400">PDF, Word (DOCX), or plain text (TXT) up to 50MB</p>
        </div>
      </div>

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !uploading && fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition flex flex-col items-center justify-center ${
          isDragging
            ? 'border-indigo-500 bg-indigo-950/20'
            : 'border-slate-700/80 hover:border-slate-600 bg-slate-950/40 hover:bg-slate-950/70'
        } ${uploading ? 'opacity-75 cursor-not-allowed' : ''}`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => handleFiles(e.target.files)}
          accept=".pdf,.docx,.txt"
          className="hidden"
          disabled={uploading}
        />

        <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-3 shadow-inner">
          {uploading ? <Loader2 className="w-6 h-6 animate-spin" /> : <UploadCloud className="w-6 h-6" />}
        </div>

        {uploading ? (
          <div className="w-full max-w-xs space-y-2">
            <p className="text-sm font-medium text-slate-200 truncate">Uploading {currentFileName}...</p>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-xs text-slate-400">{progress}% completed</p>
          </div>
        ) : (
          <>
            <p className="text-sm font-medium text-slate-200">
              Drag & drop document here, or <span className="text-indigo-400 underline">browse files</span>
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Supports automatic page extraction, recursive chunking & vector indexing
            </p>
          </>
        )}
      </div>

      {/* Feedback banner */}
      {feedback && (
        <div
          className={`mt-4 p-3 rounded-xl flex items-start justify-between text-xs border ${
            feedback.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-300'
              : feedback.type === 'info'
              ? 'bg-sky-950/40 border-sky-800/60 text-sky-300'
              : 'bg-rose-950/40 border-rose-800/60 text-rose-300'
          }`}
        >
          <div className="flex items-center gap-2">
            {feedback.type === 'error' ? (
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            ) : (
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
            )}
            <span>{feedback.message}</span>
          </div>
          <button
            onClick={() => setFeedback(null)}
            className="text-slate-400 hover:text-slate-200 ml-2"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
}

