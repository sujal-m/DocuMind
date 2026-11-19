import React, { useState } from 'react';
import { Wrench, CheckCircle2, AlertCircle, ChevronDown, ChevronUp, Terminal } from 'lucide-react';

export default function ToolExecutionBadge({ toolActivity }) {
  const [expanded, setExpanded] = useState(false);

  const getToolDisplayName = (name) => {
    switch (name) {
      case 'search_documents': return 'Vector Search';
      case 'summarize_document': return 'Document Summarizer';
      case 'compare_documents': return 'Cross-Document Comparator';
      case 'extract_information': return 'Structured Data Extractor';
      case 'answer_from_documents': return 'Targeted Q&A Retreival';
      default: return name;
    }
  };

  return (
    <div className="border border-slate-800 bg-slate-950/70 rounded-xl overflow-hidden text-xs my-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-3 py-2 flex items-center justify-between text-left hover:bg-slate-900/60 transition"
      >
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0">
            <Wrench className="w-3 h-3" />
          </div>
          <span className="font-semibold text-slate-300">
            {getToolDisplayName(toolActivity.tool_name)}
          </span>
          <span className="text-[10px] font-mono text-slate-500 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
            tool_call
          </span>
        </div>

        <div className="flex items-center gap-2">
          {toolActivity.success ? (
            <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
              <CheckCircle2 className="w-3 h-3" /> Success
            </span>
          ) : (
            <span className="flex items-center gap-1 text-[11px] text-rose-400 font-medium">
              <AlertCircle className="w-3 h-3" /> Failed
            </span>
          )}
          {expanded ? <ChevronUp className="w-3.5 h-3.5 text-slate-400" /> : <ChevronDown className="w-3.5 h-3.5 text-slate-400" />}
        </div>
      </button>

      {expanded && (
        <div className="p-3 border-t border-slate-800/80 bg-slate-900/40 space-y-2 text-[11px] font-mono">
          <div>
            <p className="text-slate-500 uppercase text-[9px] font-bold tracking-wider mb-0.5">Parameters:</p>
            <pre className="bg-slate-950 p-2 rounded-lg text-slate-300 overflow-x-auto border border-slate-800/60">
              {JSON.stringify(toolActivity.arguments, null, 2)}
            </pre>
          </div>
          <div>
            <p className="text-slate-500 uppercase text-[9px] font-bold tracking-wider mb-0.5">Output Execution Trace:</p>
            <p className="bg-slate-950 p-2 rounded-lg text-slate-400 border border-slate-800/60 font-sans">
              {toolActivity.result_summary}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
