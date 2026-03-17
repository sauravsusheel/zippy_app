import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const processQuery = async (query, tableName = null) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/query`, {
      query: query,
      table_name: tableName
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      return {
        success: false,
        error: error.response.data.detail || 'Server error occurred'
      };
    } else if (error.request) {
      return {
        success: false,
        error: 'Cannot connect to backend server. Make sure it is running on port 8000.'
      };
    } else {
      return {
        success: false,
        error: error.message
      };
    }
  }
};

export const getQueryHistory = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/history`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch history:', error);
    return { history: [] };
  }
};

export const uploadDataset = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_BASE_URL}/api/upload-dataset`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to upload dataset:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Upload failed'
    };
  }
};
