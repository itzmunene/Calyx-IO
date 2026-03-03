import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '10000');

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Logging interceptor
apiClient.interceptors.request.use((config) => {
  console.log(`🔵 API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    console.log(`🟢 API Response: ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error(`🔴 API Error: ${error.config?.url}`, error.message);
    return Promise.reject(error);
  }
);

export const calyxAPI = {
  // Health check
  health: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Search flowers
  search: async (query: string, limit = 20) => {
    const response = await apiClient.get('/api/v1/search', {
      params: { q: query, limit },
    });
    return response.data;
  },

  // Get catalogue with filters
  getCatalogue: async (filters: {
    name?: string;
    color?: string;
    country?: string;
    sort_by?: string;
    page?: number;
    limit?: number;
  }) => {
    const response = await apiClient.get('/api/v1/catalogue', {
      params: filters,
    });
    return response.data;
  },

  // Get available filters
  getFilters: async () => {
    const response = await apiClient.get('/api/v1/catalogue/filters');
    return response.data;
  },

  // Get popular flowers
  getPopular: async (limit = 10) => {
    const response = await apiClient.get('/api/v1/catalogue/popular', {
      params: { limit },
    });
    return response.data;
  },

  // Get species by ID
  getSpecies: async (speciesId: string) => {
    const response = await apiClient.get(`/api/v1/species/${speciesId}`);
    return response.data;
  },

  // Identify flower from image
  identify: async (imageFile: File) => {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await apiClient.post('/api/v1/identify', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default calyxAPI;