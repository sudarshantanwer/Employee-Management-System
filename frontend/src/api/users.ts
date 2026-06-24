import { apiClient } from './client';
import { ApiResponse, PaginatedUsers, Role, UserRecord } from '../types';

export async function fetchUsers(params: {
  page?: number;
  limit?: number;
  search?: string;
  role?: Role;
}): Promise<PaginatedUsers> {
  const { data } = await apiClient.get<ApiResponse<PaginatedUsers>>('/api/v1/users', {
    params,
  });
  return data.data;
}

export async function updateUser(
  id: string,
  payload: {
    role?: Role;
    employee_id?: string | null;
    is_active?: boolean;
    full_name?: string;
  }
): Promise<UserRecord> {
  const { data } = await apiClient.put<ApiResponse<UserRecord>>(`/api/v1/users/${id}`, payload);
  return data.data;
}
