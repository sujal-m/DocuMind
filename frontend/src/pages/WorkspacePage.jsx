import React from 'react';
import { BrainCircuit, Sparkles, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function WorkspacePage() {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="border border-indigo-500/30 bg-indigo-950/20 rounded-2xl p-8 text-center space-y-4">
        <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto shadow-inner">
          <BrainCircuit className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-white">Research Workspace Ready for Phase 2</h2>
        <p className="text-sm text-slate-300 max-w-lg mx-auto">
          Phase 1 (Foundation & Document Ingestion) is currently active. The interactive conversational RAG chat, citation inspector, and Gemini tool loop will be integrated in Phase 2.
        </p>
        <div className="pt-2">
          <Link
            to="/documents"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition"
          >
            <span>Upload Documents in Document Library</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}

