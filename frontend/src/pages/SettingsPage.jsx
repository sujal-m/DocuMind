import React from 'react';
import { Settings as SettingsIcon, ShieldCheck, Database, Cpu, HardDrive } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System Configuration</h1>
        <p className="text-sm text-slate-400 mt-1">
          Review application parameters, model selections, and vector indexing thresholds.
        </p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl divide-y divide-slate-800 text-xs">
        <div className="p-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <div>
              <p className="font-semibold text-slate-200">LLM Reasoning Engine</p>
              <p className="text-slate-500">Google Gemini API via official Python SDK</p>
            </div>
          </div>
          <span className="font-mono bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-slate-300">
            gemini-2.5-flash
          </span>
        </div>

        <div className="p-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="w-5 h-5 text-emerald-400" />
            <div>
              <p className="font-semibold text-slate-200">Embedding Model</p>
              <p className="text-slate-500">Local Sentence Transformers</p>
            </div>
          </div>
          <span className="font-mono bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-slate-300">
            all-MiniLM-L6-v2 (384d)
          </span>
        </div>

        <div className="p-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <HardDrive className="w-5 h-5 text-violet-400" />
            <div>
              <p className="font-semibold text-slate-200">Vector Index Engine</p>
              <p className="text-slate-500">Facebook AI Similarity Search</p>
            </div>
          </div>
          <span className="font-mono bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-slate-300">
            faiss.IndexIDMap2(IndexFlatIP)
          </span>
        </div>

        <div className="p-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-5 h-5 text-amber-400" />
            <div>
              <p className="font-semibold text-slate-200">Chunking Strategy</p>
              <p className="text-slate-500">Recursive character splitting with overlap</p>
            </div>
          </div>
          <span className="font-mono bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-slate-300">
            Size: 500 tokens / Overlap: 100
          </span>
        </div>
      </div>
    </div>
  );
}

