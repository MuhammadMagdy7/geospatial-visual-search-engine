import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

export const searchAPI = {
  search: async (image: File, bbox: number[][], threshold: number, topK: number) => {
    const formData = new FormData();
    formData.append('query_image', image);
    formData.append('bbox', JSON.stringify(bbox));
    formData.append('threshold', threshold.toString());
    formData.append('top_k', topK.toString());

    const response = await api.post('/api/v1/search', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  getHealth: async () => {
    const response = await api.get('/api/v1/health');
    return response.data;
  }
};

export default api;
