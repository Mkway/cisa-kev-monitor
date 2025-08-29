import axios from 'axios';
import type {
  VulnerabilityListResponse,
  Vulnerability,
  VulnerabilitySearchRequest,
  VulnerabilityStats,
  DataSyncStatus
} from '@/types/vulnerability';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const vulnerabilityApi = {
  // 취약점 목록 조회
  getVulnerabilities: (params: {
    page?: number;
    per_page?: number;
    vendor?: string;
    product?: string;
    ransomware_only?: boolean;
    date_from?: string;
    date_to?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<VulnerabilityListResponse> =>
    apiClient.get('/vulnerabilities', { params }).then(res => res.data),

  // 특정 CVE 상세 정보 조회
  getVulnerabilityByCve: (cveId: string): Promise<Vulnerability> =>
    apiClient.get(`/vulnerabilities/${cveId}`).then(res => res.data),

  // 고급 검색
  searchVulnerabilities: (searchRequest: VulnerabilitySearchRequest): Promise<VulnerabilityListResponse> =>
    apiClient.post('/vulnerabilities/search', searchRequest).then(res => res.data),

  // 통계 정보
  getStats: (): Promise<VulnerabilityStats> =>
    apiClient.get('/vulnerabilities/stats/overview').then(res => res.data),

  // 벤더 목록
  getVendors: (params: { search?: string; limit?: number }): Promise<Array<{ name: string; vulnerability_count: number }>> =>
    apiClient.get('/vulnerabilities/vendors/', { params }).then(res => res.data),

  // 제품 목록
  getProducts: (params: { vendor?: string; search?: string; limit?: number }): Promise<Array<{ name: string; vendor_name: string; vulnerability_count: number }>> =>
    apiClient.get('/vulnerabilities/products/', { params }).then(res => res.data),
};

export const syncApi = {
  // 동기화 상태 조회
  getSyncStatus: (): Promise<DataSyncStatus> =>
    apiClient.get('/sync/status').then(res => res.data),

  // 동기화 트리거
  triggerSync: (force: boolean = false): Promise<{ message: string; status: string }> =>
    apiClient.post('/sync/trigger', {}, { params: { force } }).then(res => res.data),

  // 즉시 동기화
  syncNow: (): Promise<{ message: string; stats: any; catalog_version: string; date_released: string }> =>
    apiClient.post('/sync/sync-now').then(res => res.data),

  // 동기화 진행 상황
  getSyncProgress: (): Promise<{
    status: string;
    progress: number;
    total_records: number | null;
    processed_records: number | null;
    last_sync_at: string | null;
    error_message: string | null;
    in_progress_flag: boolean;
  }> =>
    apiClient.get('/sync/progress').then(res => res.data),
};

export const generalApi = {
  // API 상태 확인
  getApiStatus: (): Promise<{ status: string; version: string }> =>
    apiClient.get('/status').then(res => res.data),
};

export default apiClient;