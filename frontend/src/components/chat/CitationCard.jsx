import React from 'react';
import { FileText, ExternalLink } from 'lucide-react';

export default function CitationCard({ citation, onSelect, isSelected }) {
  return (
    <div
      onClick={() => onSelect && onSelect(citation)}
      className={`p-3 rounded-xl border text-xs cursor-pointer transition flex items-start gap-3 ${
        isSelected
          ? 'bg-indigo-950/60 border-indigo-500 shadow-sm shadow-indigo-500/20'
          : 'bg-slate-900 border-slate-800 hover:border-slate-700 hover:bg-slate-800/60'
      }`}
    >
      <div className="w-6 h-6 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold text-[11px] shrink-0 mt-0.5">
        [{citation.index}]
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <p className="font-semibold text-slate-200 truncate">{citation.document_name}</p>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-medium shrink-0">
            Page {citation.page_number}
          </span>
        </div>
        <p className="text-slate-400 text-[11px] mt-1 line-clamp-2 leading-relaxed">
          "{citation.snippet}"
        </p>
      </div>
    </div>
  );
}
