
import axios from 'axios';

const apiBase =
  (typeof import.meta !== 'undefined' && import.meta.env && (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL)) ||
  'http://localhost:8000';

const apiClient = axios.create({
  baseURL: apiBase,
});

// Automatically add the API Key to every request
apiClient.interceptors.request.use((config) => {
  config.withCredentials = true;
  const apiKey = localStorage.getItem('data_prep_api_key');
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

export default apiClient;
