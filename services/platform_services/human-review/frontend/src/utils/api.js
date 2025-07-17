/**
 * API Utility Functions
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import axios from 'axios';

const CONSTITUTIONAL_HASH = 'cdd01ef066bc6cf2';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api/v1/review',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add constitutional hash
api.interceptors.request.use(
  (config) => {
    // Add constitutional hash to all requests
    if (config.data) {
      config.data.constitutional_hash = CONSTITUTIONAL_HASH;
    } else if (config.method === 'get') {
      config.params = {
        ...config.params,
        constitutional_hash: CONSTITUTIONAL_HASH,
      };
    }
    
    // Add authentication token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    // Validate constitutional hash in response
    if (response.data && response.data.constitutional_hash !== CONSTITUTIONAL_HASH) {
      console.warn('Constitutional hash mismatch in response');
    }
    
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      // Forbidden
      console.error('Access forbidden');
    } else if (error.response?.status >= 500) {
      // Server error
      console.error('Server error:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

// Review API functions
export const reviewAPI = {
  // Get reviewer workload
  getWorkload: async (reviewerId) => {
    try {
      const response = await api.get(`/workload/${reviewerId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch workload');
    }
  },

  // Get review task by ID
  getTask: async (taskId) => {
    try {
      const response = await api.get(`/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch task');
    }
  },

  // Create new review task
  createTask: async (taskData) => {
    try {
      const response = await api.post('/tasks', taskData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create task');
    }
  },

  // Assign task to reviewer
  assignTask: async (taskId, reviewerId) => {
    try {
      const response = await api.post(`/tasks/${taskId}/assign`, {
        reviewer_id: reviewerId,
        auto_assign: !reviewerId,
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to assign task');
    }
  },

  // Submit review
  submitReview: async (submissionData) => {
    try {
      const response = await api.post('/submissions', submissionData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to submit review');
    }
  },

  // Get analytics
  getAnalytics: async () => {
    try {
      const response = await api.get('/analytics');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch analytics');
    }
  },

  // Escalate review
  escalateReview: async (escalationData) => {
    try {
      const response = await api.post('/escalate', escalationData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to escalate review');
    }
  },

  // Send notification
  sendNotification: async (notificationData) => {
    try {
      const response = await api.post('/notifications', notificationData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to send notification');
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Health check failed');
    }
  },
};

// Authentication API functions
export const authAPI = {
  // Login
  login: async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials);
      const { token, user } = response.data;
      
      // Store token
      localStorage.setItem('auth_token', token);
      localStorage.setItem('user_info', JSON.stringify(user));
      
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Login failed');
    }
  },

  // Logout
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clean up local storage
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_info');
    }
  },

  // Get current user
  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/user');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get user info');
    }
  },
};

// Utility functions
export const apiUtils = {
  // Upload file
  uploadFile: async (file, type = 'content') => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);
      formData.append('constitutional_hash', CONSTITUTIONAL_HASH);
      
      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'File upload failed');
    }
  },

  // Download file
  downloadFile: async (fileId, filename) => {
    try {
      const response = await api.get(`/download/${fileId}`, {
        responseType: 'blob',
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      window.URL.revokeObjectURL(url);
    } catch (error) {
      throw new Error(error.response?.data?.error || 'File download failed');
    }
  },

  // Format API errors
  formatError: (error) => {
    if (error.response?.data?.error) {
      return error.response.data.error;
    } else if (error.message) {
      return error.message;
    } else {
      return 'An unexpected error occurred';
    }
  },

  // Check constitutional hash
  validateConstitutionalHash: (hash) => {
    return hash === CONSTITUTIONAL_HASH;
  },
};

// WebSocket connection for real-time updates
export class ReviewWebSocket {
  constructor(url) {
    this.url = url || `ws://localhost:8023/ws`;
    this.socket = null;
    this.listeners = new Map();
  }

  connect() {
    try {
      this.socket = new WebSocket(this.url);
      
      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.emit('connected');
      };
      
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Validate constitutional hash
          if (data.constitutional_hash !== CONSTITUTIONAL_HASH) {
            console.warn('Constitutional hash mismatch in WebSocket message');
            return;
          }
          
          this.emit(data.type, data);
        } catch (error) {
          console.error('WebSocket message parsing error:', error);
        }
      };
      
      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
        this.emit('disconnected');
        
        // Attempt to reconnect after 5 seconds
        setTimeout(() => this.connect(), 5000);
      };
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  send(type, data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type,
        data,
        constitutional_hash: CONSTITUTIONAL_HASH,
      }));
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('WebSocket event callback error:', error);
        }
      });
    }
  }
}

export default api;