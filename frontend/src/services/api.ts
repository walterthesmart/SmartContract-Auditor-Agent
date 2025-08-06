import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import type {
  AuditRequest,
  AuditResult,
  ReportData,
  ReportResponse,
  MoonScapeStatus
} from '@/types/audit';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Enhanced API client with retry logic
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Increased timeout for audit operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

// Retry logic for failed requests
const retryRequest = async (config: AxiosRequestConfig, retryCount = 0): Promise<any> => {
  try {
    return await api(config);
  } catch (error) {
    if (retryCount < MAX_RETRIES && shouldRetry(error as AxiosError)) {
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (retryCount + 1)));
      return retryRequest(config, retryCount + 1);
    }
    throw error;
  }
};

// Determine if request should be retried
const shouldRetry = (error: AxiosError): boolean => {
  if (!error.response) return true; // Network error
  const status = error.response.status;
  return status >= 500 || status === 429; // Server errors or rate limiting
};

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Enhanced response interceptor with detailed error handling
api.interceptors.response.use(
  (response) => {
    // Log successful requests in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ API Success: ${response.config.method?.toUpperCase()} ${response.config.url}`);
    }
    return response;
  },
  (error: AxiosError) => {
    console.error('API Error:', error.response?.data || error.message);

    // Enhanced error handling with specific error types
    if (typeof window !== 'undefined' && (window as any).showAlert) {
      let title = 'API Error';
      let message = 'An unexpected error occurred';
      let type: 'error' | 'warning' = 'error';

      if (!error.response) {
        // Network error
        title = 'Connection Error';
        message = 'Unable to connect to the server. Please check your internet connection.';
      } else {
        const status = error.response.status;
        const data = error.response.data as any;

        switch (status) {
          case 400:
            title = 'Invalid Request';
            message = data?.detail || 'The request contains invalid data.';
            break;
          case 401:
            title = 'Authentication Required';
            message = 'Please authenticate to access this resource.';
            break;
          case 403:
            title = 'Access Denied';
            message = 'You do not have permission to perform this action.';
            break;
          case 404:
            title = 'Not Found';
            message = 'The requested resource was not found.';
            break;
          case 429:
            title = 'Rate Limited';
            message = 'Too many requests. Please wait a moment and try again.';
            type = 'warning';
            break;
          case 500:
            title = 'Server Error';
            message = 'Internal server error. Please try again later.';
            break;
          case 503:
            title = 'Service Unavailable';
            message = 'The service is temporarily unavailable. Please try again later.';
            break;
          default:
            message = data?.detail || data?.message || `Request failed with status ${status}`;
        }
      }

      (window as any).showAlert({
        type,
        title,
        message,
        duration: type === 'warning' ? 6000 : 5000,
      });
    }

    return Promise.reject(error);
  }
);

export const auditService = {
  // Analyze smart contract
  async analyzeContract(request: AuditRequest): Promise<AuditResult> {
    const response = await api.post<AuditResult>('/analyze', request);
    return response.data;
  },

  // Generate audit report
  async generateReport(data: ReportData): Promise<ReportResponse> {
    const response = await api.post<ReportResponse>('/generate-report', data);
    return response.data;
  },

  // Upload contract file
  async uploadContract(file: File, contractName: string, language: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('contract_name', contractName);
    formData.append('language', language);

    const response = await api.post('/upload-contract', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await api.get<{ status: string }>('/health');
    return response.data;
  },
};

export const moonscapeService = {
  // Get MoonScape status
  async getStatus(): Promise<MoonScapeStatus> {
    const response = await api.get<MoonScapeStatus>('/moonscape/status');
    return response.data;
  },

  // Get agent registry info
  async getRegistryInfo() {
    const response = await api.get('/moonscape/registry');
    return response.data;
  },

  // Get active connections
  async getConnections() {
    const response = await api.get('/moonscape/connections');
    return response.data;
  },
};

export default api;
