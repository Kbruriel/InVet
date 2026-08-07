/** Cliente API para autenticacion */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function authRegister(payload: {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}): Promise<{ access_token: string; refresh_token: string; token_type: string }> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    const err = error as { detail?: string };
    throw { status: response.status, detail: err.detail || 'Error en registro' };
  }

  return response.json();
}

export async function authLogin(payload: {
  email: string;
  password: string;
}): Promise<{ access_token: string; refresh_token: string; token_type: string }> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    const err = error as { detail?: string };
    throw { status: response.status, detail: err.detail || 'Error en login' };
  }

  return response.json();
}

export async function authRefresh(refreshToken: string): Promise<{
  access_token: string;
  refresh_token: string;
  token_type: string;
}> {
  const response = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    const err = error as { detail?: string };
    throw { status: response.status, detail: err.detail || 'Error en refresh' };
  }

  return response.json();
}

export async function authGetProfile(token: string): Promise<{
  id: number;
  email: string;
  firstName: string | null;
  lastName: string | null;
  role: string;
}> {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    const err = error as { detail?: string };
    throw { status: response.status, detail: err.detail || 'Error al obtener perfil' };
  }

  return response.json();
}

export async function authLogout(token: string, refreshToken?: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/auth/logout`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token: refreshToken || null }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    const err = error as { detail?: string };
    throw { status: response.status, detail: err.detail || 'Error en logout' };
  }

  return response.json();
}

export async function authRequestPasswordReset(email: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/auth/password-reset/request`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    const err = error as { detail?: string };
    throw { status: response.status, detail: err.detail || 'Error en solicitud de reset' };
  }

  return response.json();
}

export async function authConfirmPasswordReset(
  resetToken: string,
  newPassword: string
): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/auth/password-reset/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reset_token: resetToken, new_password: newPassword }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    const err = error as { detail?: string };
    throw { status: response.status, detail: err.detail || 'Error en confirmacion de reset' };
  }

  return response.json();
}
