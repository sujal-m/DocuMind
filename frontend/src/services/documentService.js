import api from './api';

export const documentService = {
  async uploadDocument(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        }
      },
    });
    return response.data;
  },

  async listDocuments(skip = 0, limit = 100) {
    const response = await api.get('/documents', {
      params: { skip, limit },
    });
    return response.data;
  },

  async getDocument(documentId) {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  },

  async getDocumentStatus(documentId) {
    const response = await api.get(`/documents/${documentId}/status`);
    return response.data;
  },

  async deleteDocument(documentId) {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
  },

  async reindexDocument(documentId) {
    const response = await api.post(`/documents/${documentId}/reindex`);
    return response.data;
  },
};

