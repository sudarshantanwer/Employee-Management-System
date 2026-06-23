import { apiClient, clearStoredAuth, getStoredTokens, setStoredTokens, setStoredUser } from './client';
import { ApiResponse, AuthData, TokenPair } from '../types';

export async function login(email: string, password: string): Promise<AuthData> {
  const { data } = await apiClient.post<ApiResponse<AuthData>>('/api/v1/auth/login', {
    email,
    password,
  });
  setStoredTokens(data.data.tokens);
  setStoredUser({
    user_id: data.data.user_id,
    email: data.data.email,
    full_name: data.data.full_name,
    role: data.data.role,
  });
  return data.data;
}

export async function register(
  email: string,
  password: string,
  fullName: string
): Promise<AuthData> {
  const { data } = await apiClient.post<ApiResponse<AuthData>>('/api/v1/auth/register', {
    email,
    password,
    full_name: fullName,
    role: 'EMPLOYEE',
  });
  setStoredTokens(data.data.tokens);
  setStoredUser({
    user_id: data.data.user_id,
    email: data.data.email,
    full_name: data.data.full_name,
    role: data.data.role,
  });
  return data.data;
}

export async function logout(): Promise<void> {
  const tokens = getStoredTokens();
  if (tokens) {
    try {
      await apiClient.post('/api/v1/auth/logout', {
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
      });
    } catch {
      // Clear local auth even if server logout fails
    }
  }
  clearStoredAuth();
}

export async function refreshTokens(): Promise<TokenPair> {
  const tokens = getStoredTokens();
  if (!tokens?.refresh_token) throw new Error('No refresh token');
  const { data } = await apiClient.post<ApiResponse<TokenPair>>('/api/v1/auth/refresh', {
    refresh_token: tokens.refresh_token,
  });
  setStoredTokens(data.data);
  return data.data;
}
