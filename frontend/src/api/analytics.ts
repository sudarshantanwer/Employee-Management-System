import { apiClient } from './client';
import { ApiResponse, DashboardAnalytics } from '../types';

export async function fetchDashboardAnalytics(): Promise<DashboardAnalytics> {
  const { data } = await apiClient.get<ApiResponse<DashboardAnalytics>>(
    '/api/v1/analytics/dashboard'
  );
  return data.data;
}
