import { apiClient } from './client';
import { ApiResponse, Department, DepartmentFormData } from '../types';

export async function fetchDepartments(): Promise<Department[]> {
  const { data } = await apiClient.get<ApiResponse<Department[]>>('/api/v1/departments');
  return data.data;
}

export async function createDepartment(payload: DepartmentFormData): Promise<Department> {
  const { data } = await apiClient.post<ApiResponse<Department>>('/api/v1/departments', payload);
  return data.data;
}

export async function updateDepartment(
  id: string,
  payload: Partial<DepartmentFormData>
): Promise<Department> {
  const { data } = await apiClient.put<ApiResponse<Department>>(
    `/api/v1/departments/${id}`,
    payload
  );
  return data.data;
}

export async function deleteDepartment(id: string): Promise<Department> {
  const { data } = await apiClient.delete<ApiResponse<Department>>(
    `/api/v1/departments/${id}`
  );
  return data.data;
}
