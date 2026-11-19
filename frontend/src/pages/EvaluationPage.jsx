import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  Database,
  Search,
  BookOpen,
  HelpCircle,
  FileText,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Target,
  Zap,
  Layers
} from 'lucide-react';
import { evaluationService } from '../services/evaluationService';

export default function EvaluationPage() {
  const [results, setResults] = useState(null);
  const [benchmark, setBenchmark] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetchingInitial, setFetchingInitial] = useState(true);
  const [activeTab, setActiveTab] = useState('retrieval'); // 'retrieval' | 'answers' | 'benchmark'
  const [expandedQuery, setExpandedQuery] = useState(null);
  const [k, setK] = useState(5);
  const [useLlmJudge, setUseLlmJudge] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setFetchingInitial(true);
    try {
      const [resData, benchData] = await Promise.allSettled([
        evaluationService.getLatestResults(),
        evaluationService.getBenchmarkDataset()
      ]);
      if (resData.status === 'fulfilled' && resData.value) {
        setResults(resData.value);
      }
      if (benchData.status === 'fulfilled' && benchData.value) {
        setBenchmark(benchData.value);
      }
    } catch (err) {
      console.error('Failed to load initial evaluation data:', err);
    } finally {
      setFetchingInitial(false);
    }
  };

  const handleRunEvaluation = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await evaluationService.runEvaluation({
        k: parseInt(k, 10),
        min_score: 0.0,
        use_llm_judge: useLlmJudge
      });
      setResults(data);
    } catch (err) {
      console.error('Evaluation run failed:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to complete evaluation run');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (queryId) => {
    setExpandedQuery(expandedQuery === queryId ? null : queryId);
  };

  return (
    <div className="flex-1 overflow-y-auto bg-slate-950 p-6 md:p-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Module 4 Benchmark Engine
            </span>
            {results && (
              <span className="text-xs text-slate-500 flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                Last evaluated: {new Date(results.timestamp).toLocaleTimeString()}
              </span>
            )}
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <LineChart className="w-6 h-6 text-emerald-400" />
            Evaluation & RAG Benchmarking
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Quantify semantic retrieval accuracy (Precision, Recall, MRR, NDCG) and generated answer quality with LLM-as-a-judge.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl text-xs text-slate-300">
            <span>Top-K:</span>
            <select
              value={k}
              onChange={(e) => setK(Number(e.target.value))}
              disabled={loading}
              className="bg-slate-800 border border-slate-700 text-white rounded px-2 py-0.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            >
              <option value={3}>3</option>
              <option value={5}>5</option>
              <option value={10}>10</option>
            </select>
          </div>

          <label className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl text-xs text-slate-300 cursor-pointer hover:bg-slate-850">
            <input
              type="checkbox"
              checked={useLlmJudge}
              onChange={(e) => setUseLlmJudge(e.target.checked)}
              disabled={loading}
              className="rounded bg-slate-800 border-slate-700 text-emerald-500 focus:ring-emerald-500"
            />
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>LLM Judge</span>
          </label>

          <button
            onClick={handleRunEvaluation}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-medium text-sm shadow-lg shadow-emerald-950/50 transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <RotateCcw className="w-4 h-4 animate-spin text-white" />
                <span>Running Benchmark Suite...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Run Evaluation</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/30 flex items-start gap-3 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Evaluation Error</p>
            <p className="text-xs text-rose-200 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* Metrics Summary Grid */}
      {results ? (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Precision@K */}
            <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm hover:border-slate-700 transition">
              <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
                <span>Precision@{results.k}</span>
                <Target className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-white tracking-tight">
                {(results.mean_precision_at_k * 100).toFixed(1)}%
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Ratio of retrieved chunks that are relevant</p>
            </div>

            {/* Recall@K */}
            <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm hover:border-slate-700 transition">
              <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
                <span>Recall@{results.k}</span>
                <Layers className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-2xl font-bold text-white tracking-tight">
                {(results.mean_recall_at_k * 100).toFixed(1)}%
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Coverage of corpus relevant passages</p>
            </div>

            {/* MRR */}
            <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm hover:border-slate-700 transition">
              <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
                <span>MRR</span>
                <Zap className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-2xl font-bold text-white tracking-tight">
                {results.mean_mrr.toFixed(3)}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Mean Reciprocal Rank of first relevant item</p>
            </div>

            {/* NDCG */}
            <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm hover:border-slate-700 transition">
              <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
                <span>NDCG@{results.k}</span>
                <LineChart className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-2xl font-bold text-white tracking-tight">
                {results.mean_ndcg.toFixed(3)}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Normalized Discounted Cumulative Gain</p>
            </div>
          </div>

          {/* Secondary Row: Latency and Answer Quality */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Avg Retrieval Latency */}
            <div className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                <span>Avg Retrieval Latency</span>
                <Clock className="w-4 h-4 text-blue-400" />
              </div>
              <div className="text-xl font-bold text-slate-200">
                {results.avg_latency_ms.toFixed(1)} <span className="text-xs font-normal text-slate-400">ms</span>
              </div>
            </div>

            {/* Faithfulness */}
            <div className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                <span>Faithfulness (Judge)</span>
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-xl font-bold text-emerald-400">
                {(results.mean_faithfulness * 100).toFixed(1)}%
              </div>
            </div>

            {/* Answer Relevance */}
            <div className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                <span>Answer Relevance</span>
                <Sparkles className="w-4 h-4 text-purple-400" />
              </div>
              <div className="text-xl font-bold text-purple-300">
                {(results.mean_answer_relevance * 100).toFixed(1)}%
              </div>
            </div>

            {/* Citation Accuracy */}
            <div className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                <span>Citation Integrity</span>
                <CheckCircle2 className="w-4 h-4 text-teal-400" />
              </div>
              <div className="text-xl font-bold text-teal-400">
                {results.citation_accuracy_pct.toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 border-b border-slate-800 pt-2">
            <button
              onClick={() => setActiveTab('retrieval')}
              className={`pb-3 px-3 text-sm font-medium border-b-2 transition ${
                activeTab === 'retrieval'
                  ? 'border-emerald-500 text-white'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Retrieval Breakdown ({results.retrieval_results.length})
            </button>
            <button
              onClick={() => setActiveTab('answers')}
              className={`pb-3 px-3 text-sm font-medium border-b-2 transition ${
                activeTab === 'answers'
                  ? 'border-emerald-500 text-white'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Answer & Judge Quality ({results.answer_results.length})
            </button>
            <button
              onClick={() => setActiveTab('benchmark')}
              className={`pb-3 px-3 text-sm font-medium border-b-2 transition ${
                activeTab === 'benchmark'
                  ? 'border-emerald-500 text-white'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Golden Dataset ({benchmark.length})
            </button>
          </div>

          {/* Tab 1: Retrieval Breakdown */}
          {activeTab === 'retrieval' && (
            <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/60">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-850/80 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
                  <tr>
                    <th className="py-3 px-4">Query ID</th>
                    <th className="py-3 px-4">Benchmark Query</th>
                    <th className="py-3 px-4">Target Doc</th>
                    <th className="py-3 px-4 text-center">Retrieved</th>
                    <th className="py-3 px-4 text-center">Relevant</th>
                    <th className="py-3 px-4 text-right">Precision@{results.k}</th>
                    <th className="py-3 px-4 text-right">Recall@{results.k}</th>
                    <th className="py-3 px-4 text-right">MRR</th>
                    <th className="py-3 px-4 text-right">NDCG@{results.k}</th>
                    <th className="py-3 px-4 text-right">Latency</th>
                    <th className="py-3 px-4 text-center">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {results.retrieval_results.map((row) => (
                    <React.Fragment key={row.query_id}>
                      <tr className="hover:bg-slate-850/50 transition">
                        <td className="py-3 px-4 font-semibold text-emerald-400">{row.query_id}</td>
                        <td className="py-3 px-4 font-sans text-slate-200 max-w-xs truncate" title={row.query}>
                          {row.query}
                        </td>
                        <td className="py-3 px-4 font-sans text-slate-400">
                          {row.target_document ? (
                            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[11px]">
                              {row.target_document}
                            </span>
                          ) : (
                            <span className="text-slate-500 italic">None (Unanswerable)</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center">{row.retrieved_count}</td>
                        <td className="py-3 px-4 text-center text-emerald-400 font-bold">{row.relevant_count}</td>
                        <td className="py-3 px-4 text-right">{(row.precision_at_k * 100).toFixed(1)}%</td>
                        <td className="py-3 px-4 text-right">{(row.recall_at_k * 100).toFixed(1)}%</td>
                        <td className="py-3 px-4 text-right">{row.mrr.toFixed(3)}</td>
                        <td className="py-3 px-4 text-right">{row.ndcg_at_k.toFixed(3)}</td>
                        <td className="py-3 px-4 text-right text-slate-400">{row.latency_ms.toFixed(1)}ms</td>
                        <td className="py-3 px-4 text-center font-sans">
                          <button
                            onClick={() => toggleExpand(row.query_id)}
                            className="p-1 rounded hover:bg-slate-750 text-slate-400 hover:text-white"
                          >
                            {expandedQuery === row.query_id ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                          </button>
                        </td>
                      </tr>
                      {expandedQuery === row.query_id && (
                        <tr>
                          <td colSpan={11} className="p-4 bg-slate-950 font-sans border-b border-slate-800">
                            <div className="space-y-3">
                              <p className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                                <Search className="w-3.5 h-3.5 text-emerald-400" />
                                Retrieved Passages for "{row.query}"
                              </p>
                              <div className="space-y-2">
                                {row.retrieved_passages.map((p, idx) => (
                                  <div
                                    key={idx}
                                    className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-1"
                                  >
                                    <div className="flex items-center justify-between text-slate-400 text-[11px]">
                                      <span className="font-semibold text-slate-300">
                                        Passage {idx + 1}: {p.document_name} (Page {p.page_number})
                                      </span>
                                      <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                                        Score: {(p.similarity_score * 100).toFixed(1)}%
                                      </span>
                                    </div>
                                    <p className="text-slate-300 font-sans leading-relaxed">{p.content}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Tab 2: Answer & Judge Quality */}
          {activeTab === 'answers' && (
            <div className="space-y-4">
              {results.answer_results.map((ans) => (
                <div
                  key={ans.query_id}
                  className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3 hover:border-slate-700 transition"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-800 text-emerald-400 border border-slate-700">
                        {ans.query_id}
                      </span>
                      <h4 className="text-sm font-semibold text-white">{ans.query}</h4>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        Faithfulness: {(ans.faithfulness * 100).toFixed(0)}%
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20">
                        Relevance: {(ans.answer_relevance * 100).toFixed(0)}%
                      </span>
                      <span
                        className={`px-2.5 py-0.5 rounded-full border ${
                          ans.citation_valid
                            ? 'bg-teal-500/10 text-teal-300 border-teal-500/20'
                            : 'bg-rose-500/10 text-rose-300 border-rose-500/20'
                        }`}
                      >
                        {ans.citation_valid ? 'Citations Valid' : 'Citations Unverified'}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div className="space-y-1">
                      <span className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
                        Generated Answer
                      </span>
                      <p className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 leading-relaxed">
                        {ans.generated_answer}
                      </p>
                    </div>

                    <div className="space-y-1">
                      <span className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
                        Reference Ground Truth
                      </span>
                      <p className="p-3 rounded-xl bg-slate-950/50 border border-slate-850 text-slate-400 leading-relaxed">
                        {ans.reference_answer}
                      </p>
                    </div>
                  </div>

                  {ans.judge_rationale && (
                    <div className="text-xs bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/80 text-slate-400 flex items-start gap-2">
                      <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                      <span>
                        <strong className="text-slate-300">Judge Rationale:</strong> {ans.judge_rationale}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Tab 3: Benchmark Golden Dataset */}
          {activeTab === 'benchmark' && (
            <div className="space-y-3">
              {benchmark.map((b, i) => (
                <div
                  key={b.query_id || i}
                  className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-emerald-400 font-semibold">{b.query_id}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        b.is_answerable
                          ? 'bg-blue-500/10 text-blue-300 border border-blue-500/20'
                          : 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                      }`}
                    >
                      {b.is_answerable ? 'Answerable Case' : 'Negative Rejection Case'}
                    </span>
                  </div>
                  <p className="text-white font-medium text-sm">{b.query}</p>
                  <div className="flex flex-wrap gap-2 text-slate-400 text-[11px]">
                    <span>
                      Target Doc:{' '}
                      <strong className="text-slate-300">{b.target_document || 'None (Corpus Null)'}</strong>
                    </span>
                    <span>•</span>
                    <span>
                      Keywords:{' '}
                      <strong className="text-slate-300">
                        {b.ground_truth_keywords?.length > 0
                          ? b.ground_truth_keywords.join(', ')
                          : 'None'}
                      </strong>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* Empty State */
        <div className="p-12 rounded-3xl border border-slate-800 bg-slate-900/40 text-center space-y-6 max-w-2xl mx-auto my-8 shadow-xl">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto shadow-inner">
            <LineChart className="w-8 h-8" />
          </div>
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-white tracking-tight">Run Real RAG & Retrieval Benchmark</h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Execute reproducible quantitative tests across seeded SLA, AI Ethics, and Expense policy documents.
              Measures live FAISS retrieval with Precision@K, Recall@K, MRR, NDCG, and rates answer faithfulness via Gemini.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-left pt-2">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-850">
              <span className="text-[11px] text-slate-500 block">Metric</span>
              <span className="text-xs font-semibold text-emerald-400">Precision@K</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-850">
              <span className="text-[11px] text-slate-500 block">Metric</span>
              <span className="text-xs font-semibold text-cyan-400">Recall@K</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-850">
              <span className="text-[11px] text-slate-500 block">Metric</span>
              <span className="text-xs font-semibold text-amber-400">MRR / NDCG</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-850">
              <span className="text-[11px] text-slate-500 block">Judge</span>
              <span className="text-xs font-semibold text-purple-400">Faithfulness</span>
            </div>
          </div>

          <button
            onClick={handleRunEvaluation}
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm shadow-lg shadow-emerald-950/60 inline-flex items-center gap-2 transition"
          >
            {loading ? (
              <>
                <RotateCcw className="w-4 h-4 animate-spin" />
                <span>Running Benchmark Suite...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Run Benchmark Now</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
