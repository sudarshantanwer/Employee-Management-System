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
  phone?: string | null;
  address?: string | null;
  emergency_contact?: string | null;
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
  phone?: string;
  address?: string;
  emergency_contact?: string;
}

export interface Department {
  id: string;
  name: string;
  description: string | null;
  head_employee_id: string | null;
  employee_count: number;
  created_at: string;
  updated_at: string;
}

export interface DepartmentFormData {
  name: string;
  description?: string;
  head_employee_id?: string;
}

export interface UserRecord {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  auth_provider: AuthProvider;
  employee_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedUsers {
  items: UserRecord[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ProfileData {
  user_id: string;
  email: string;
  full_name: string;
  role: Role;
  employee_id: string | null;
  employee: Employee | null;
}

export interface ProfileUpdateData {
  phone?: string;
  address?: string;
  emergency_contact?: string;
}

export interface DepartmentCount {
  department: string;
  count: number;
}

export interface RecentActivity {
  action: string;
  user_id: string;
  resource: string;
  resource_id: string | null;
  timestamp: string;
}

export interface DashboardAnalytics {
  total_employees: number;
  total_departments: number;
  average_salary: number;
  new_hires_this_month: number;
  employees_by_department: DepartmentCount[];
  recent_activity: RecentActivity[];
}

export interface AuditLog {
  id: string;
  user_id: string;
  action: string;
  resource: string;
  resource_id: string | null;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface PaginatedAuditLogs {
  items: AuditLog[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface OrgChartNode {
  id: string;
  name: string;
  designation: string;
  department: string;
  manager_id: string | null;
  children: OrgChartNode[];
}

export interface BulkImportResult {
  created: number;
  skipped: number;
  errors: string[];
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
