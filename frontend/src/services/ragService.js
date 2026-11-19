import api from './api';

export const ragService = {
  async queryRAG({ question, document_ids = null, top_k = 5, min_score = null, conversation_id = null }) {
    const payload = {
      question,
      document_ids: document_ids && document_ids.length > 0 ? document_ids : null,
      top_k,
      min_score,
      conversation_id,
    };
    const response = await api.post('/rag/query', payload);
    return response.data;
  },

  async semanticSearch({ query, document_ids = null, top_k = 5, min_score = null }) {
    const payload = {
      query,
      document_ids: document_ids && document_ids.length > 0 ? document_ids : null,
      top_k,
      min_score,
    };
    const response = await api.post('/search/semantic', payload);
    return response.data;
  },
};
