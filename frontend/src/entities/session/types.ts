/** Tipos para autenticacion */

export interface AuthRegisterPayload {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

export interface AuthLoginPayload {
  email: string;
  password: string;
}

export interface AuthRefreshPayload {
  refresh_token: string;
}

export interface AuthTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthProfileResponse {
  id: number;
  email: string;
  firstName: string | null;
  lastName: string | null;
  role: string;
}

export interface AuthGenericMessageResponse {
  message: string;
}

export type AuthError = {
  status: number;
  detail: string;
};
