import axios from 'axios';
import { SearchResponse } from '../types/search';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

export const searchAPI = {
  searchByImage: async (
    image: File,
    bbox: number[][],
    threshold: number,
    topK: number,
    tileSize: number,
  ): Promise<SearchResponse> => {
    const formData = new FormData();
    formData.append('query_image', image);
    formData.append('bbox', JSON.stringify(bbox));
    formData.append('threshold', threshold.toString());
    formData.append('top_k', topK.toString());
    formData.append('tile_size', tileSize.toString());

    const response = await api.post('/api/v1/search', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  searchByText: async (
    text: string,
    bbox: number[][],
    threshold: number,
    topK: number,
    tileSize: number,
  ): Promise<SearchResponse> => {
    const formData = new FormData();
    formData.append('query_text', text);
    formData.append('bbox', JSON.stringify(bbox));
    formData.append('threshold', threshold.toString());
    formData.append('top_k', topK.toString());
    formData.append('tile_size', tileSize.toString());

    const response = await api.post('/api/v1/search', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getHealth: async () => {
    const response = await api.get('/api/v1/health');
    return response.data;
  },

  getMLHealth: async () => {
    const response = await api.get('/api/v1/ml/health');
    return response.data;
  },
};

export default api;
