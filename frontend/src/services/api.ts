import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface QueryRequest {
  user_query: string;
}

export interface QueryResponse {
  user_query: string;
  sql_query?: string;
  results?: any[];
  explanation?: string;
  chart_config?: {
    type: string;
    x_field: string;
    y_field: string;
  };
  citations?: string[];
  error?: string;
  execution_time?: number;
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds
});

export const sendQuery = async (userQuery: string): Promise<QueryResponse> => {
  try {
    const response = await apiClient.post<QueryResponse>('/api/v1/sales/query', {
      user_query: userQuery,
    });
    return response.data;
  } catch (error: any) {
    if (error.response) {
      // Server responded with error
      throw new Error(error.response.data.detail || 'Server error');
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Please check if the backend is running.');
    } else {
      // Something else happened
      throw new Error(error.message || 'Unknown error occurred');
    }
  }
};

export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get('/health');
    return response.status === 200;
  } catch {
    return false;
  }
};
