
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
});

// Automatically add the API Key to every request
apiClient.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('data_prep_api_key');
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

export default apiClient;