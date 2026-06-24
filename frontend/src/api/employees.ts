import { apiClient } from './client';
import {
  ApiResponse,
  BulkImportResult,
  Employee,
  EmployeeFormData,
  HealthData,
  OrgChartNode,
  PaginatedEmployees,
} from '../types';

export async function fetchEmployees(params: {
  page?: number;
  limit?: number;
  search?: string;
  department?: string;
  sort?: string;
}): Promise<PaginatedEmployees> {
  const { data } = await apiClient.get<ApiResponse<PaginatedEmployees>>('/api/v1/employees', {
    params,
  });
  return data.data;
}

export async function fetchEmployee(id: string): Promise<Employee> {
  const { data } = await apiClient.get<ApiResponse<Employee>>(`/api/v1/employees/${id}`);
  return data.data;
}

export async function createEmployee(payload: EmployeeFormData): Promise<Employee> {
  const { data } = await apiClient.post<ApiResponse<Employee>>('/api/v1/employees', payload);
  return data.data;
}

export async function updateEmployee(
  id: string,
  payload: Partial<EmployeeFormData>
): Promise<Employee> {
  const { data } = await apiClient.put<ApiResponse<Employee>>(
    `/api/v1/employees/${id}`,
    payload
  );
  return data.data;
}

export async function deleteEmployee(id: string): Promise<Employee> {
  const { data } = await apiClient.delete<ApiResponse<Employee>>(`/api/v1/employees/${id}`);
  return data.data;
}

export async function fetchHealth(): Promise<HealthData> {
  const { data } = await apiClient.get<ApiResponse<HealthData>>('/health');
  return data.data;
}

export async function fetchOrgChart(): Promise<OrgChartNode[]> {
  const { data } = await apiClient.get<ApiResponse<OrgChartNode[]>>(
    '/api/v1/employees/org-chart'
  );
  return data.data;
}

export async function exportEmployeesCsv(): Promise<Blob> {
  const response = await apiClient.get('/api/v1/employees/export', {
    responseType: 'blob',
  });
  return response.data;
}

export async function importEmployeesCsv(file: File): Promise<BulkImportResult> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post<ApiResponse<BulkImportResult>>(
    '/api/v1/employees/import',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return data.data;
}
