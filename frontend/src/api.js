import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 12000,
});

const directApi = axios.create({
  baseURL: import.meta.env.VITE_DIRECT_API_URL || 'http://127.0.0.1:5000',
  timeout: 12000,
});

export const postWithFallback = async (url, payload) => {
  try {
    return await api.post(url, payload);
  } catch (error) {
    if (!error.response) {
      return directApi.post(url, payload);
    }
    throw error;
  }
};

export const getApiErrorMessage = (error) => {
  if (error.response?.data?.error) {
    return error.response.data.error;
  }

  if (error.response?.data?.message) {
    return error.response.data.message;
  }

  if (error.response?.data?.reply) {
    return error.response.data.reply;
  }

  if (error.response) {
    const status = error.response.status;
    return `Backend request failed (${status}). Check Flask logs for details.`;
  }

  if (error.code === 'ECONNABORTED' || error.message === 'Network Error') {
    return 'Cannot reach backend at http://127.0.0.1:5000. Start Flask server and retry.';
  }

  return 'Request failed. Please try again.';
};

export default api;
