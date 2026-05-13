import axios from 'axios';
import { SearchResponse } from '../types/search';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

export const searchAPI = {
  /**
   * Unified search endpoint supporting all three modes.
   */
  search: async (
    bbox: number[][],
    searchMode: string,
    options: {
      // AI Detection params
      targetClass?: string;
      confidenceThreshold?: number;
      // RemoteCLIP params
      queryImage?: File;
      queryText?: string;
      threshold?: number;
      tileSize?: number;
      // Shared
      topK?: number;
    } = {},
  ): Promise<SearchResponse> => {
    const formData = new FormData();
    formData.append('bbox', JSON.stringify(bbox));
    formData.append('search_mode', searchMode);

    // AI Detection params
    if (options.targetClass) {
      formData.append('target_class', options.targetClass);
    }
    if (options.confidenceThreshold !== undefined) {
      formData.append('confidence_threshold', options.confidenceThreshold.toString());
    }

    // RemoteCLIP params
    if (options.queryImage) {
      formData.append('query_image', options.queryImage);
    }
    if (options.queryText) {
      formData.append('query_text', options.queryText);
    }
    if (options.threshold !== undefined) {
      formData.append('threshold', options.threshold.toString());
    }
    if (options.tileSize !== undefined) {
      formData.append('tile_size', options.tileSize.toString());
    }

    // Shared
    if (options.topK !== undefined) {
      formData.append('top_k', options.topK.toString());
    }

    const response = await api.post('/api/v1/search', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  /**
   * Get available YOLO object detection classes (DOTA dataset).
   */
  getClasses: async (): Promise<{ classes: string[]; default: string }> => {
    const response = await api.get('/api/v1/search/classes');
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
