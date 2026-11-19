import React from 'react';
import { Bot, User, Sparkles, ShieldCheck, AlertCircle, CheckCircle2 } from 'lucide-react';
import CitationCard from './CitationCard';

export default function MessageItem({ message, onSelectCitation, activeCitation }) {
  const isAssistant = message.sender === 'assistant';

  const renderContentWithCitations = (text) => {
    if (!text) return null;

    // Split text by numbered citations [1], [2], etc.
    const parts = text.split(/(\[\d+(?:,\s*\d+)*\])/g);

    return parts.map((part, index) => {
      const match = part.match(/\[(\d+(?:,\s*\d+)*)\]/);
      if (match) {
        const nums = match[1].split(',').map((n) => n.trim());
        return (
          <span key={index} className="inline-flex gap-1 mx-1 font-semibold align-baseline">
            {nums.map((num) => {
              const matchingCitation = message.citations?.find((c) => String(c.index) === num);
              return (
                <button
                  key={num}
                  onClick={() => matchingCitation && onSelectCitation && onSelectCitation(matchingCitation)}
                  className="px-1.5 py-0.2 rounded bg-indigo-500/20 hover:bg-indigo-500/40 text-indigo-300 border border-indigo-500/40 text-[10px] cursor-pointer transition font-mono"
                  title={matchingCitation ? `${matchingCitation.document_name} (Page ${matchingCitation.page_number})` : `Citation ${num}`}
                >
                  [{num}]
                </button>
              );
            })}
          </span>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  const getConfidenceBadge = (confidence) => {
    switch (confidence) {
      case 'high':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" /> Grounded High Confidence
          </span>
        );
      case 'medium':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
            <ShieldCheck className="w-3 h-3" /> Moderate Confidence
          </span>
        );
      case 'insufficient_data':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/20">
            <AlertCircle className="w-3 h-3" /> Insufficient Corpus Data
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className={`flex gap-4 p-5 ${isAssistant ? 'bg-slate-900/60 border-y border-slate-800/60' : ''}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5 ${
          isAssistant
            ? 'bg-gradient-to-tr from-indigo-600 to-violet-500 text-white shadow-md shadow-indigo-500/20'
            : 'bg-slate-800 text-slate-300 border border-slate-700'
        }`}
      >
        {isAssistant ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
      </div>

      {/* Message Content */}
      <div className="flex-1 space-y-3 min-w-0">
        <div className="flex items-center justify-between">
          <p className="text-xs font-semibold text-slate-300">
            {isAssistant ? 'DocuMind Research Agent' : 'You'}
          </p>
          {isAssistant && message.confidence && getConfidenceBadge(message.confidence)}
        </div>

        <div className="text-xs text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">
          {renderContentWithCitations(message.content)}
        </div>

        {/* Citations Grid */}
        {isAssistant && message.citations && message.citations.length > 0 && (
          <div className="pt-2">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Verified Sources & Provenance ({message.citations.length})
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {message.citations.map((c) => (
                <CitationCard
                  key={c.index}
                  citation={c}
                  isSelected={activeCitation?.chunk_id === c.chunk_id}
                  onSelect={(cit) => onSelectCitation && onSelectCitation(cit)}
                />
              ))}
            </div>
          </div>
        )}

        {isAssistant && message.model_name && (
          <div className="text-[10px] text-slate-500 flex items-center gap-1 pt-1">
            <Sparkles className="w-3 h-3 text-indigo-400" />
            <span>Generated using {message.model_name}</span>
          </div>
        )}
      </div>
    </div>
  );
}
