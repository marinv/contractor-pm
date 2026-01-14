import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const login = (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  return api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
};

export const register = (data) => api.post('/auth/register', data);
export const getMe = () => api.get('/auth/me');

export const uploadLogo = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/auth/upload-logo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const deleteLogo = () => api.delete('/auth/logo');

export const updateProfile = (data) => api.put('/auth/profile', data);

// Projects
export const getProjects = (status) => {
  const params = status ? { status_filter: status } : {};
  return api.get('/projects', { params });
};
export const getProject = (id) => api.get(`/projects/${id}`);
export const createProject = (data) => api.post('/projects', data);
export const updateProject = (id, data) => api.put(`/projects/${id}`, data);
export const deleteProject = (id) => api.delete(`/projects/${id}`);

// Worker Types
export const getWorkerTypes = () => api.get('/worker-types');
export const createWorkerType = (data) => api.post('/worker-types', data);
export const updateWorkerType = (id, data) => api.put(`/worker-types/${id}`, data);
export const deleteWorkerType = (id) => api.delete(`/worker-types/${id}`);

// Time Entries
export const getTimeEntries = (projectId) => api.get(`/projects/${projectId}/time-entries`);
export const createTimeEntry = (projectId, data) => {
  console.log('Sending time entry data:', JSON.stringify(data));
  return api.post(`/projects/${projectId}/time-entries`, data);
};
export const updateTimeEntry = (id, data) => api.put(`/time-entries/${id}`, data);
export const deleteTimeEntry = (id) => api.delete(`/time-entries/${id}`);

// Materials
export const getMaterials = (projectId) => api.get(`/projects/${projectId}/materials`);
export const createMaterial = (projectId, data) => api.post(`/projects/${projectId}/materials`, data);
export const updateMaterial = (id, data) => api.put(`/materials/${id}`, data);
export const deleteMaterial = (id) => api.delete(`/materials/${id}`);

// Reports
export const getReportUrl = (projectId, format) =>
  `${API_URL}/projects/${projectId}/report?format=${format}`;

export const sendOfferEmail = (projectId, data) =>
  api.post(`/projects/${projectId}/send-email`, data);

export default api;
