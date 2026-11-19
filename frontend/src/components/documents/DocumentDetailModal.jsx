import React, { useState, useEffect } from 'react';
import { X, Layers, Hash, FileText, Calendar, Copy, Check, Search, ShieldCheck } from 'lucide-react';
import { documentService } from '../../services/documentService';

export default function DocumentDetailModal({ documentId, onClose }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copiedHash, setCopiedHash] = useState(false);
  const [chunkQuery, setChunkQuery] = useState('');

  useEffect(() => {
    if (!documentId) return;
    const fetchDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await documentService.getDocument(documentId);
        setDetail(data);
      } catch (err) {
        setError(err.message || 'Failed to fetch document details.');
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [documentId]);

  const copyHash = (hash) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  if (!documentId) return null;

  const filteredChunks = detail?.chunks?.filter((c) =>
    c.content.toLowerCase().includes(chunkQuery.toLowerCase())
  ) || [];

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white truncate max-w-lg">
                {detail?.original_name || 'Document Inspector'}
              </h2>
              <p className="text-xs text-slate-400">
                UUID: <span className="font-mono text-slate-300">{documentId}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">Loading chunk provenance...</div>
        ) : error ? (
          <div className="p-12 text-center text-rose-400 text-sm">{error}</div>
        ) : detail ? (
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Metadata Pills */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <p className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Pages</p>
                <p className="text-sm font-semibold text-slate-200 mt-0.5">{detail.page_count ?? 1}</p>
              </div>
              <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <p className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Total Chunks</p>
                <p className="text-sm font-semibold text-indigo-400 mt-0.5">{detail.chunk_count}</p>
              </div>
              <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <p className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Format</p>
                <p className="text-sm font-semibold text-slate-200 uppercase mt-0.5">{detail.file_type}</p>
              </div>
              <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <p className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Status</p>
                <p className="text-sm font-semibold text-emerald-400 capitalize mt-0.5">{detail.status}</p>
              </div>
            </div>

            {/* SHA-256 Hash Card */}
            <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 overflow-hidden">
                <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                <span className="text-slate-400 shrink-0 font-medium">SHA-256 Hash:</span>
                <span className="font-mono text-slate-300 truncate">{detail.file_hash}</span>
              </div>
              <button
                onClick={() => copyHash(detail.file_hash)}
                className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] transition shrink-0 ml-2"
              >
                {copiedHash ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedHash ? 'Copied' : 'Copy'}</span>
              </button>
            </div>

            {/* Chunks Explorer */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Layers className="w-4 h-4 text-indigo-400" />
                  <span>Extracted Chunks ({detail.chunks.length})</span>
                </h3>
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2" />
                  <input
                    type="text"
                    placeholder="Search chunk text..."
                    value={chunkQuery}
                    onChange={(e) => setChunkQuery(e.target.value)}
                    className="pl-8 pr-3 py-1 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 w-44"
                  />
                </div>
              </div>

              <div className="space-y-3">
                {filteredChunks.length === 0 ? (
                  <p className="text-xs text-slate-500 py-4 text-center">No matching chunks found.</p>
                ) : (
                  filteredChunks.map((chunk) => (
                    <div
                      key={chunk.id}
                      className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 text-xs space-y-2 hover:border-slate-700 transition"
                    >
                      <div className="flex items-center justify-between text-[11px] text-slate-400 border-b border-slate-800/60 pb-2">
                        <div className="flex items-center gap-2 font-medium">
                          <span className="px-2 py-0.5 rounded bg-indigo-950/60 text-indigo-400 border border-indigo-800/40">
                            Chunk #{chunk.chunk_index}
                          </span>
                          <span className="text-slate-300">Page {chunk.page_number}</span>
                        </div>
                        <div className="flex items-center gap-3 text-slate-500">
                          <span>~{chunk.token_count} tokens</span>
                          {chunk.faiss_id && (
                            <span className="font-mono text-emerald-400/80">FAISS ID: {chunk.faiss_id}</span>
                          )}
                        </div>
                      </div>
                      <p className="text-slate-300 whitespace-pre-wrap leading-relaxed font-sans">
                        {chunk.content}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

