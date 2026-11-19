import api from './api';

export const evaluationService = {
  async runEvaluation(params = { k: 5, min_score: 0.0, use_llm_judge: true }) {
    const response = await api.post('/evaluation/run', params);
    return response.data;
  },

  async getLatestResults() {
    const response = await api.get('/evaluation/results');
    return response.data;
  },

  async getBenchmarkDataset() {
    const response = await api.get('/evaluation/benchmark');
    return response.data;
  }
};

