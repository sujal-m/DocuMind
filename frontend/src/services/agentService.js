import api from './api';

export const agentService = {
  async chatAgent({ message, conversation_id = null, document_ids = null }) {
    const payload = {
      message,
      conversation_id,
      document_ids: document_ids && document_ids.length > 0 ? document_ids : null,
    };
    const response = await api.post('/agent/chat', payload);
    return response.data;
  },

  async listConversations(skip = 0, limit = 50) {
    const response = await api.get('/conversations', { params: { skip, limit } });
    return response.data;
  },

  async createConversation(title = 'New Research Session') {
    const response = await api.post('/conversations', null, { params: { title } });
    return response.data;
  },

  async getConversation(conversationId) {
    const response = await api.get(`/conversations/${conversationId}`);
    return response.data;
  },

  async renameConversation(conversationId, title) {
    const response = await api.patch(`/conversations/${conversationId}`, { title });
    return response.data;
  },

  async deleteConversation(conversationId) {
    const response = await api.delete(`/conversations/${conversationId}`);
    return response.data;
  },
};
