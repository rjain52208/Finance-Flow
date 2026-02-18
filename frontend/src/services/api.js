import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  getCurrentUser: () => api.get('/users/me/'),
  updateProfile: (data) => api.put('/users/update_profile/', data),
};

// Transactions API
export const transactionsAPI = {
  getAll: (params) => api.get('/transactions/', { params }),
  create: (data) => api.post('/transactions/', data),
  update: (id, data) => api.put(`/transactions/${id}/`, data),
  delete: (id) => api.delete(`/transactions/${id}/`),
  bulkUpload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/transactions/bulk_upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  bulkCategorize: () => api.post('/transactions/bulk_categorize/'),
};

// Categories API
export const categoriesAPI = {
  getAll: () => api.get('/categories/'),
  create: (data) => api.post('/categories/', data),
  update: (id, data) => api.put(`/categories/${id}/`, data),
  delete: (id) => api.delete(`/categories/${id}/`),
};

// Budgets API
export const budgetsAPI = {
  getAll: () => api.get('/budgets/'),
  create: (data) => api.post('/budgets/', data),
  update: (id, data) => api.put(`/budgets/${id}/`, data),
  delete: (id) => api.delete(`/budgets/${id}/`),
  getStatus: (id) => api.get(`/budgets/${id}/status/`),
};

// Analytics API
export const analyticsAPI = {
  getSummary: (period = 'month') => api.get('/analytics/summary/', { params: { period } }),
  getSpendingByCategory: (period = 'month') => api.get('/analytics/spending_by_category/', { params: { period } }),
  getMonthlyTrends: () => api.get('/analytics/monthly_trends/'),
  calculateInvestmentReturns: (interval) => api.post('/analytics/calculate_investment_returns/', { interval }),
};
