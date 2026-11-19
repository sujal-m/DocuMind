import React from 'react';
import { LineChart, Sparkles } from 'lucide-react';

export default function EvaluationPage() {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="border border-emerald-500/30 bg-emerald-950/20 rounded-2xl p-8 text-center space-y-4">
        <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto shadow-inner">
          <LineChart className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-white">Evaluation Suite Ready for Phase 4</h2>
        <p className="text-sm text-slate-300 max-w-lg mx-auto">
          The automated benchmark framework for Precision@K, Recall@K, MRR, NDCG, and LLM-as-a-judge answer evaluation will activate in Phase 4.
        </p>
      </div>
    </div>
  );
}

