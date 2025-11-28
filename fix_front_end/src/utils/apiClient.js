// src/utils/apiClient.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000'; // Change to your Python server

export const apiClient = {
  get: async (endpoint) => {
    try {
      const response = await axios.get(`${API_BASE_URL}${endpoint}`);
      return response.data;
    } catch (error) {
      console.error('GET request error:', error);
      throw error;
    }
  },

  post: async (endpoint, data) => {
    try {
      const response = await axios.post(`${API_BASE_URL}${endpoint}`, data);
      return response.data;
    } catch (error) {
      console.error('POST request error:', error);
      throw error;
    }
  },
};
