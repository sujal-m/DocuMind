import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/common/Sidebar';
import Navbar from '../components/common/Navbar';

export default function AppLayout() {
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [newChatKey, setNewChatKey] = useState(0);

  const handleNewChat = () => {
    setActiveConversationId(null);
    setNewChatKey((k) => k + 1);
  };

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden font-sans">
      {/* Left Sidebar with integrated history */}
      <Sidebar
        activeConversationId={activeConversationId}
        onSelectConversation={(id) => setActiveConversationId(id)}
        onNewChat={handleNewChat}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto">
          <Outlet context={{ activeConversationId, setActiveConversationId, newChatKey, handleNewChat }} />
        </main>
      </div>
    </div>
  );
}
