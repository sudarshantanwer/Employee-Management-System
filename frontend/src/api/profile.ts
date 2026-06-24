import { apiClient } from './client';
import { ApiResponse, ProfileData, ProfileUpdateData } from '../types';

export async function fetchProfile(): Promise<ProfileData> {
  const { data } = await apiClient.get<ApiResponse<ProfileData>>('/api/v1/profile/me');
  return data.data;
}

export async function updateProfile(payload: ProfileUpdateData): Promise<ProfileData> {
  const { data } = await apiClient.put<ApiResponse<ProfileData>>('/api/v1/profile/me', payload);
  return data.data;
}
