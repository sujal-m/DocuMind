import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Files, 
  Layers, 
  BrainCircuit, 
  LineChart, 
  ArrowRight, 
  ShieldCheck, 
  Sparkles,
  Database,
  Search,
  CheckCircle2
} from 'lucide-react';
import { documentService } from '../services/documentService';

export default function DashboardPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const data = await documentService.listDocuments(0, 5);
        setDocuments(data);
      } catch (err) {
        console.error('Failed to load dashboard docs:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDocs();
  }, []);

  const totalChunks = documents.reduce((acc, d) => acc + (d.chunk_count || 0), 0);
  const indexedCount = documents.filter((d) => d.status === 'indexed').length;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Hero Welcome */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-950/60 via-slate-900 to-slate-900 border border-slate-800 p-8 shadow-sm">
        <div className="max-w-2xl space-y-3 z-10 relative">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Document Intelligence & Research Platform</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Grounded Research & Multi-Document Analysis
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            DocuMind extracts page-aware structures from PDF, DOCX, and TXT files, generates 384-dimensional semantic embeddings, indexes vectors in FAISS, and equips Google Gemini with autonomous research tools.
          </p>
          <div className="flex items-center gap-3 pt-2">
            <Link
              to="/workspace"
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm flex items-center gap-2 transition shadow-md shadow-indigo-600/20"
            >
              <span>Launch Research Agent</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/documents"
              className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm transition border border-slate-700"
            >
              Manage Documents
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Catalog Documents</p>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
              <Files className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{documents.length}</p>
          <p className="text-xs text-slate-500 mt-1">{indexedCount} indexed & searchable</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Indexed Chunks</p>
            <div className="p-2 rounded-xl bg-violet-500/10 text-violet-400">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{totalChunks}</p>
          <p className="text-xs text-slate-500 mt-1">Average 500 tokens / chunk</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Vector Store</p>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">FAISS CPU</p>
          <p className="text-xs text-emerald-400/90 mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> IndexFlatIP (Cosine)
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Embedding Model</p>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400">
              <BrainCircuit className="w-4 h-4" />
            </div>
          </div>
          <p className="text-base font-bold text-white mt-2 truncate">all-MiniLM-L6-v2</p>
          <p className="text-xs text-slate-500 mt-1">384 Dimensions, L2-Norm</p>
        </div>
      </div>

      {/* Quick Launch Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/documents"
          className="bg-slate-900 border border-slate-800 hover:border-indigo-500/60 rounded-2xl p-6 transition group"
        >
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mb-4 group-hover:scale-105 transition">
            <Files className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white group-hover:text-indigo-400 transition">
            1. Ingest Knowledge
          </h3>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            Upload PDF, DOCX or TXT files. DocuMind extracts page-indexed text, chunks content, and builds persistent FAISS vectors.
          </p>
        </Link>

        <Link
          to="/workspace"
          className="bg-slate-900 border border-slate-800 hover:border-violet-500/60 rounded-2xl p-6 transition group"
        >
          <div className="w-10 h-10 rounded-xl bg-violet-500/10 text-violet-400 flex items-center justify-center mb-4 group-hover:scale-105 transition">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white group-hover:text-violet-400 transition">
            2. Research & Reasoning
          </h3>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            Ask complex multi-hop research questions across documents. Verify claims through exact page and chunk citations.
          </p>
        </Link>

        <Link
          to="/evaluation"
          className="bg-slate-900 border border-slate-800 hover:border-emerald-500/60 rounded-2xl p-6 transition group"
        >
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-4 group-hover:scale-105 transition">
            <LineChart className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white group-hover:text-emerald-400 transition">
            3. Measure Performance
          </h3>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            Execute reproducible retrieval benchmarks (Precision@K, Recall@K, MRR, NDCG) and judge answer faithfulness.
          </p>
        </Link>
      </div>

      {/* Recent Documents Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-white">Recent Documents</h3>
          <Link to="/documents" className="text-xs text-indigo-400 hover:underline">
            View All Documents &rarr;
          </Link>
        </div>

        {loading ? (
          <p className="text-xs text-slate-400 py-4 text-center">Loading recent files...</p>
        ) : documents.length === 0 ? (
          <p className="text-xs text-slate-500 py-4 text-center">No documents uploaded yet.</p>
        ) : (
          <div className="divide-y divide-slate-800/60 text-xs">
            {documents.slice(0, 5).map((d) => (
              <div key={d.id} className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-300 border border-slate-700">
                    {d.file_type}
                  </span>
                  <div>
                    <p className="font-medium text-slate-200">{d.original_name}</p>
                    <p className="text-[11px] text-slate-500">{d.chunk_count} chunks indexed</p>
                  </div>
                </div>
                <span className="capitalize text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full text-[11px] border border-emerald-500/20">
                  {d.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

