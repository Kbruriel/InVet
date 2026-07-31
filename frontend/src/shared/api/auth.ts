import { apiGet, ApiError } from './http-client';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
}

export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new ApiError(response.status, errorData.detail || 'Error al iniciar sesión', errorData);
  }

  return response.json();
}

export async function register(userData: RegisterData): Promise<AuthResponse> {
  const response = await fetch('/api/v1/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new ApiError(response.status, errorData.detail || 'Error al registrarse', errorData);
  }

  return response.json();
}

export async function getUserProfile(): Promise<UserProfile> {
  try {
    return await apiGet<UserProfile>('/api/v1/auth/me');
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      throw new Error('No autorizado. Por favor, inicie sesión nuevamente.');
    }
    throw error;
  }
}

export async function refreshToken(): Promise<AuthResponse> {
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (!refreshToken) {
    throw new Error('No se encontró refresh token');
  }

  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new ApiError(response.status, errorData.detail || 'Error al refrescar token', errorData);
  }

  return response.json();
}

export async function logout() {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
}