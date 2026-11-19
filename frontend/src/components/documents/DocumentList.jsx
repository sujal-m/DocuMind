import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Trash2, 
  RotateCw, 
  Search, 
  Layers, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Eye,
  Filter
} from 'lucide-react';
import { documentService } from '../../services/documentService';

export default function DocumentList({ onSelectDocument, refreshTrigger }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [actionLoadingId, setActionLoadingId] = useState(null);

  const fetchDocuments = async () => {
    try {
      const data = await documentService.listDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [refreshTrigger]);

  // Polling when any document is pending or processing
  useEffect(() => {
    const hasActiveProcessing = documents.some(
      (d) => d.status === 'pending' || d.status === 'processing'
    );
    if (!hasActiveProcessing) return;

    const timer = setInterval(() => {
      fetchDocuments();
    }, 3000);

    return () => clearInterval(timer);
  }, [documents]);

  const handleDelete = async (docId, docName) => {
    if (!window.confirm(`Are you sure you want to permanently delete "${docName}"? This will purge all associated vectors from FAISS.`)) {
      return;
    }
    setActionLoadingId(docId);
    try {
      await documentService.deleteDocument(docId);
      await fetchDocuments();
    } catch (err) {
      alert(`Error deleting document: ${err.message}`);
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleReindex = async (docId) => {
    setActionLoadingId(docId);
    try {
      await documentService.reindexDocument(docId);
      await fetchDocuments();
    } catch (err) {
      alert(`Error re-indexing: ${err.message}`);
    } finally {
      setActionLoadingId(null);
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getStatusBadge = (status, errorMsg) => {
    switch (status) {
      case 'indexed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Indexed</span>
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 animate-pulse">
            <Clock className="w-3.5 h-3.5 animate-spin" />
            <span>Processing</span>
          </span>
        );
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Clock className="w-3.5 h-3.5" />
            <span>Queued</span>
          </span>
        );
      case 'error':
        return (
          <span 
            title={errorMsg || 'Failed to extract text'}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20 cursor-help"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Failed</span>
          </span>
        );
      default:
        return null;
    }
  };

  const getDocTypeColor = (type) => {
    switch (type.toLowerCase()) {
      case 'pdf': return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      case 'docx': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'txt': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      default: return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
    }
  };

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch = doc.original_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || doc.status.toUpperCase() === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-base font-semibold text-white">Indexed Knowledge Repository</h3>
          <p className="text-xs text-slate-400">
            {documents.length} document{documents.length === 1 ? '' : 's'} registered in vector catalog
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 w-48"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Status</option>
            <option value="INDEXED">Indexed</option>
            <option value="PROCESSING">Processing</option>
            <option value="PENDING">Queued</option>
            <option value="ERROR">Failed</option>
          </select>

          <button
            onClick={fetchDocuments}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
            title="Refresh List"
          >
            <RotateCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Document Table / List */}
      {loading ? (
        <div className="py-12 text-center text-slate-400 text-sm">
          <RotateCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-400" />
          Loading document collection...
        </div>
      ) : filteredDocs.length === 0 ? (
        <div className="py-12 border border-dashed border-slate-800 rounded-xl text-center">
          <FileText className="w-8 h-8 mx-auto text-slate-600 mb-2" />
          <p className="text-sm font-medium text-slate-300">No documents found</p>
          <p className="text-xs text-slate-500 mt-1">Upload a PDF, DOCX or TXT file above to get started</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-medium">
                <th className="pb-3 pl-2">Document</th>
                <th className="pb-3">Size</th>
                <th className="pb-3">Pages</th>
                <th className="pb-3">Chunks</th>
                <th className="pb-3">Status</th>
                <th className="pb-3 text-right pr-2">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredDocs.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3.5 pl-2">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase border ${getDocTypeColor(doc.file_type)}`}>
                        {doc.file_type}
                      </span>
                      <div className="min-w-0 max-w-xs">
                        <p className="font-medium text-slate-200 truncate" title={doc.original_name}>
                          {doc.original_name}
                        </p>
                        <p className="text-[11px] text-slate-500 truncate font-mono">
                          ID: {doc.id.slice(0, 8)}...
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 text-slate-400">{formatBytes(doc.file_size)}</td>
                  <td className="py-3.5 text-slate-400">{doc.page_count ?? 1}</td>
                  <td className="py-3.5 text-slate-300 font-medium">
                    <span className="flex items-center gap-1">
                      <Layers className="w-3.5 h-3.5 text-indigo-400" />
                      {doc.chunk_count}
                    </span>
                  </td>
                  <td className="py-3.5">
                    {getStatusBadge(doc.status, doc.error_message)}
                  </td>
                  <td className="py-3.5 text-right pr-2">
                    <div className="flex items-center justify-end gap-1.5">
                      <button
                        onClick={() => onSelectDocument && onSelectDocument(doc.id)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
                        title="View Extracted Chunks"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button
                        disabled={actionLoadingId === doc.id}
                        onClick={() => handleReindex(doc.id)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition disabled:opacity-50"
                        title="Re-index Document"
                      >
                        <RotateCw className={`w-3.5 h-3.5 ${actionLoadingId === doc.id ? 'animate-spin' : ''}`} />
                      </button>
                      <button
                        disabled={actionLoadingId === doc.id}
                        onClick={() => handleDelete(doc.id, doc.original_name)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-900/40 text-slate-300 hover:text-rose-400 transition disabled:opacity-50"
                        title="Delete Document"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

