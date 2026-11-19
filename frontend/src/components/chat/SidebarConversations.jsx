import React, { useState, useEffect } from 'react';
import { MessageSquare, Trash2, Edit2, Check, X, Plus } from 'lucide-react';
import { agentService } from '../../services/agentService';

export default function SidebarConversations({ activeId, onSelect, onNewChat }) {
  const [conversations, setConversations] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const loadConversations = async () => {
    try {
      const data = await agentService.listConversations(0, 30);
      setConversations(data);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [activeId]);

  const handleDelete = async (e, convId) => {
    e.stopPropagation();
    if (!window.confirm('Delete this conversation history?')) return;
    try {
      await agentService.deleteConversation(convId);
      if (activeId === convId) {
        onNewChat && onNewChat();
      }
      loadConversations();
    } catch (err) {
      alert(`Failed to delete: ${err.message}`);
    }
  };

  const startRename = (e, conv) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditTitle(conv.title);
  };

  const saveRename = async (e, convId) => {
    e.stopPropagation();
    if (!editTitle.trim()) return;
    try {
      await agentService.renameConversation(convId, editTitle.trim());
      setEditingId(null);
      loadConversations();
    } catch (err) {
      alert(`Failed to rename: ${err.message}`);
    }
  };

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between px-3 py-1.5 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
        <span>Research Sessions</span>
        <button
          onClick={onNewChat}
          className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition"
          title="New Research Session"
        >
          <Plus className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="space-y-0.5 max-h-56 overflow-y-auto px-1">
        {conversations.length === 0 ? (
          <p className="text-[11px] text-slate-500 italic px-3 py-2">No past sessions</p>
        ) : (
          conversations.map((conv) => {
            const isActive = activeId === conv.id;
            const isEditing = editingId === conv.id;

            return (
              <div
                key={conv.id}
                onClick={() => !isEditing && onSelect && onSelect(conv.id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-lg text-xs cursor-pointer transition ${
                  isActive
                    ? 'bg-indigo-950/50 text-indigo-300 font-medium border border-indigo-800/40'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
                  {isEditing ? (
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      className="bg-slate-950 text-white border border-slate-700 rounded px-1.5 py-0.5 text-xs w-full focus:outline-none focus:border-indigo-500"
                      autoFocus
                    />
                  ) : (
                    <span className="truncate text-left" title={conv.title}>
                      {conv.title}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition shrink-0 ml-1">
                  {isEditing ? (
                    <>
                      <button
                        onClick={(e) => saveRename(e, conv.id)}
                        className="p-1 hover:text-emerald-400"
                        title="Save"
                      >
                        <Check className="w-3 h-3" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingId(null);
                        }}
                        className="p-1 hover:text-rose-400"
                        title="Cancel"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={(e) => startRename(e, conv)}
                        className="p-1 hover:text-indigo-400"
                        title="Rename"
                      >
                        <Edit2 className="w-3 h-3" />
                      </button>
                      <button
                        onClick={(e) => handleDelete(e, conv.id)}
                        className="p-1 hover:text-rose-400"
                        title="Delete"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
