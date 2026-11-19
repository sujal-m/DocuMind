import React, { useState, useEffect, useRef } from 'react';
import { useOutletContext } from 'react-router-dom';
import { 
  Send, 
  Bot, 
  Layers, 
  Sparkles, 
  Filter, 
  RefreshCw, 
  SlidersHorizontal,
  CheckCircle2,
  AlertCircle,
  FileText,
  Wrench,
  Cpu
} from 'lucide-react';
import { agentService } from '../services/agentService';
import { documentService } from '../services/documentService';
import MessageItem from '../components/chat/MessageItem';
import PassageInspector from '../components/chat/PassageInspector';

const INITIAL_WELCOME_MSG = {
  id: 'welcome',
  sender: 'assistant',
  content: 'Welcome to DocuMind Research Workspace. I am your autonomous AI research agent powered by Gemini Function Calling. I can search across your library, generate multi-section document summaries, perform cross-document comparisons, and extract structured JSON schemas with exact page provenance.\n\nWhat research question or analysis would you like to start with?',
  citations: [],
  tool_activities: [],
  confidence: 'high',
  model_name: 'gemini-3.1-flash-lite',
};

export default function WorkspacePage() {
  const { activeConversationId, setActiveConversationId, newChatKey } = useOutletContext() || {};

  const [messages, setMessages] = useState([INITIAL_WELCOME_MSG]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [availableDocs, setAvailableDocs] = useState([]);
  const [selectedDocIds, setSelectedDocIds] = useState([]);
  const [activePassages, setActivePassages] = useState([]);
  const [activeCitation, setActiveCitation] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  const messagesEndRef = useRef(null);

  // Load available documents for filter
  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const docs = await documentService.listDocuments();
        setAvailableDocs(docs.filter((d) => d.status === 'indexed'));
      } catch (err) {
        console.error('Failed to load documents:', err);
      }
    };
    fetchDocs();
  }, []);

  // When activeConversationId changes, load messages from backend
  useEffect(() => {
    if (activeConversationId) {
      const loadHistory = async () => {
        try {
          setLoading(true);
          const conv = await agentService.getConversation(activeConversationId);
          if (conv && conv.messages) {
            setMessages(conv.messages);
          }
        } catch (err) {
          console.error('Failed to load conversation history:', err);
        } finally {
          setLoading(false);
        }
      };
      loadHistory();
    } else {
      setMessages([INITIAL_WELCOME_MSG]);
      setActivePassages([]);
      setActiveCitation(null);
    }
  }, [activeConversationId, newChatKey]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    const query = inputQuery.trim();
    if (!query || loading) return;

    // Append user message immediately
    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      content: query,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const response = await agentService.chatAgent({
        message: query,
        conversation_id: activeConversationId || null,
        document_ids: selectedDocIds.length > 0 ? selectedDocIds : null,
      });

      // Update active conversation ID if newly created
      if (!activeConversationId && response.conversation_id) {
        if (setActiveConversationId) {
          setActiveConversationId(response.conversation_id);
        }
      }

      const assistantMsg = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        content: response.message,
        citations: response.citations || [],
        tool_activities: response.tool_activities || [],
        confidence: response.confidence || 'high',
        model_name: response.model_name,
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // If tool activities included search passages, surface them in inspector
      const searchTool = response.tool_activities?.find((t) => t.tool_name === 'search_documents');
      if (searchTool && searchTool.arguments) {
        // Build mock passages or map citations
      }
      if (response.citations && response.citations.length > 0) {
        setActiveCitation(response.citations[0]);
      }
    } catch (err) {
      const errorMsg = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        content: `Agent execution encountered an error: ${err.message || 'Service failure'}. Please verify document index status and API key.`,
        citations: [],
        tool_activities: [],
        confidence: 'insufficient_data',
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCitation = (citation) => {
    setActiveCitation(citation);
  };

  const toggleDocSelection = (docId) => {
    setSelectedDocIds((prev) =>
      prev.includes(docId) ? prev.filter((id) => id !== docId) : [...prev, docId]
    );
  };

  const samplePrompts = [
    'Search the documents and explain the core retrieval pipeline architecture.',
    'Summarize the primary document in the knowledge base.',
    'Compare the uploaded documents and identify any conflicting information.',
    'Extract the key technical specifications and parameters into a structured schema.',
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Central Chat Workspace */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-950">
        {/* Workspace Toolbar */}
        <div className="h-12 border-b border-slate-800 bg-slate-900/50 px-6 flex items-center justify-between text-xs text-slate-300 shrink-0">
          <div className="flex items-center gap-3">
            <span className="font-semibold text-slate-200">Agent Mode:</span>
            <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium flex items-center gap-1">
              <Cpu className="w-3 h-3" /> Autonomous Function Calling
            </span>
            <span className="text-slate-600">|</span>
            {selectedDocIds.length === 0 ? (
              <span className="text-slate-400">All {availableDocs.length} Documents</span>
            ) : (
              <span className="text-indigo-400 font-medium">Filtered to {selectedDocIds.length} doc(s)</span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border transition ${
                showFilters || selectedDocIds.length > 0
                  ? 'bg-indigo-600 text-white border-indigo-500'
                  : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
              }`}
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>Scope Filter</span>
            </button>
          </div>
        </div>

        {/* Filter Drawer */}
        {showFilters && (
          <div className="bg-slate-900 border-b border-slate-800 p-4 animate-in slide-in-from-top-2 duration-150 text-xs shrink-0">
            <div className="max-w-4xl mx-auto space-y-3">
              <div className="flex items-center justify-between">
                <p className="font-semibold text-white">Restrict Research Agent to Specific Documents:</p>
                {selectedDocIds.length > 0 && (
                  <button
                    onClick={() => setSelectedDocIds([])}
                    className="text-indigo-400 hover:underline text-[11px]"
                  >
                    Clear Filter (Search Entire Corpus)
                  </button>
                )}
              </div>
              <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                {availableDocs.length === 0 ? (
                  <p className="text-slate-500 italic">No indexed documents available.</p>
                ) : (
                  availableDocs.map((doc) => {
                    const isSelected = selectedDocIds.includes(doc.id);
                    return (
                      <button
                        key={doc.id}
                        onClick={() => toggleDocSelection(doc.id)}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs transition ${
                          isSelected
                            ? 'bg-indigo-600 text-white border-indigo-500 shadow-sm'
                            : 'bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700'
                        }`}
                      >
                        <FileText className="w-3.5 h-3.5 shrink-0" />
                        <span className="truncate max-w-[200px]">{doc.original_name}</span>
                      </button>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        )}

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto divide-y divide-slate-800/40">
          {messages.map((msg) => (
            <MessageItem
              key={msg.id}
              message={msg}
              onSelectCitation={handleSelectCitation}
              activeCitation={activeCitation}
            />
          ))}

          {loading && (
            <div className="flex gap-4 p-5 bg-slate-900/40 border-y border-slate-800/40 animate-pulse">
              <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 animate-spin" />
              </div>
              <div className="space-y-2 flex-1">
                <p className="text-xs font-semibold text-indigo-400 flex items-center gap-2">
                  <Wrench className="w-3.5 h-3.5 animate-spin" />
                  <span>Agent orchestrating tools & reasoning with Gemini...</span>
                </p>
                <div className="h-3 bg-slate-800 rounded w-3/4"></div>
                <div className="h-3 bg-slate-800 rounded w-1/2"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Prompts if initial state */}
        {messages.length === 1 && (
          <div className="px-6 py-3 bg-slate-950 border-t border-slate-900 flex flex-wrap gap-2 shrink-0">
            {samplePrompts.map((prompt, i) => (
              <button
                key={i}
                onClick={() => setInputQuery(prompt)}
                className="text-xs px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 transition text-left"
              >
                &ldquo;{prompt}&rdquo;
              </button>
            ))}
          </div>
        )}

        {/* Input Form */}
        <div className="p-4 bg-slate-900 border-t border-slate-800 shrink-0">
          <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto flex items-center gap-2">
            <input
              type="text"
              placeholder="Ask research questions, compare documents, summarize, or extract data..."
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              disabled={loading}
              className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 shadow-inner"
            />
            <button
              type="submit"
              disabled={loading || !inputQuery.trim()}
              className="px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center gap-2 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-indigo-600/20"
            >
              <span>Ask Agent</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>
      </div>

      {/* Right-Hand Context Passage Inspector */}
      <PassageInspector
        passages={activePassages}
        activeCitation={activeCitation}
      />
    </div>
  );
}
