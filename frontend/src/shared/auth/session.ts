/** Utilidades para manejo de sesion */

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('refresh_token');
}

export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}

export function clearSession(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

export function requireAuth(): string | never {
  const token = getAccessToken();
  if (!token) {
    throw new Error('No autorizado');
  }
  return token;
}
