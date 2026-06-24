import { apiClient } from './client';
import { ApiResponse, PaginatedAuditLogs } from '../types';

export async function fetchAuditLogs(params: {
  page?: number;
  limit?: number;
  action?: string;
  user_id?: string;
}): Promise<PaginatedAuditLogs> {
  const { data } = await apiClient.get<ApiResponse<PaginatedAuditLogs>>(
    '/api/v1/audit-logs',
    { params }
  );
  return data.data;
}
