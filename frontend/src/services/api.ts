import axios from 'axios';
import type { 
  AuditRequest, 
  AuditResult, 
  ReportData, 
  ReportResponse,
  MoonScapeStatus 
} from '@/types/audit';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Show user-friendly error messages
    if (typeof window !== 'undefined' && (window as any).showAlert) {
      const message = error.response?.data?.detail || 
                     error.response?.data?.message || 
                     error.message || 
                     'An unexpected error occurred';
      
      (window as any).showAlert({
        type: 'error',
        title: 'API Error',
        message,
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
