export type Role = 'ADMIN' | 'MANAGER' | 'EMPLOYEE';
export type AuthProvider = 'local' | 'google';

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface User {
  user_id: string;
  email: string;
  full_name: string;
  role: Role;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthData extends User {
  auth_provider?: AuthProvider;
  tokens: TokenPair;
}

export interface Employee {
  id: string;
  name: string;
  email: string;
  department: string;
  designation: string;
  salary: number;
  manager_id: string | null;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
}

export interface PaginatedEmployees {
  items: Employee[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface EmployeeFormData {
  name: string;
  email: string;
  department: string;
  designation: string;
  salary: number;
  manager_id?: string;
}

export interface EmployeeFilters {
  page: number;
  limit: number;
  search: string;
  department: string;
  sort: string;
}

export interface HealthData {
  application: { status: string; healthy: boolean };
  mongodb: { status: string; healthy: boolean };
  redis: { status: string; healthy: boolean };
}
