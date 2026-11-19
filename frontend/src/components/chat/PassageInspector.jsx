import React from 'react';
import { Layers, FileText, CheckCircle2, X, ChevronRight, Hash } from 'lucide-react';

export default function PassageInspector({ passages, activeCitation, onClose }) {
  if (!passages || passages.length === 0) {
    return (
      <aside className="w-80 lg:w-96 bg-slate-900 border-l border-slate-800 p-6 flex flex-col items-center justify-center text-center text-slate-500">
        <Layers className="w-10 h-10 text-slate-700 mb-2" />
        <p className="text-sm font-medium text-slate-400">Context Passage Inspector</p>
        <p className="text-xs text-slate-600 mt-1">
          Ask a question to inspect retrieved source chunks and similarity scores.
        </p>
      </aside>
    );
  }

  return (
    <aside className="w-80 lg:w-96 bg-slate-900 border-l border-slate-800 flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" />
          <h3 className="text-sm font-semibold text-white">Retrieved Context ({passages.length})</h3>
        </div>
        {onClose && (
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Passages List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {passages.map((p, idx) => {
          const isHighlighted = activeCitation && activeCitation.chunk_id === p.chunk_id;
          const scorePercent = Math.round((p.similarity_score || 0) * 100);

          return (
            <div
              key={p.chunk_id || idx}
              id={`passage-${p.chunk_id}`}
              className={`p-4 rounded-xl border text-xs space-y-2 transition ${
                isHighlighted
                  ? 'bg-indigo-950/70 border-indigo-500 shadow-md shadow-indigo-500/20 ring-1 ring-indigo-500'
                  : 'bg-slate-950/70 border-slate-800 hover:border-slate-700'
              }`}
            >
              {/* Header info */}
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                <div className="flex items-center gap-1.5 font-medium text-slate-200 truncate">
                  <FileText className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  <span className="truncate" title={p.document_name}>{p.document_name}</span>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px] font-semibold shrink-0">
                  {scorePercent}% match
                </span>
              </div>

              {/* Sub-meta */}
              <div className="flex items-center justify-between text-[11px] text-slate-500">
                <span>Page {p.page_number} &bull; Chunk #{p.chunk_index}</span>
                <span>~{p.token_count} tokens</span>
              </div>

              {/* Content text */}
              <p className="text-slate-300 leading-relaxed whitespace-pre-wrap font-sans text-[11.5px] bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                {p.content}
              </p>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
