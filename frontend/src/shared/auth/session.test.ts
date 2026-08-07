/** Tests para utilidades de sesion */

import { getAccessToken, getRefreshToken, isAuthenticated, clearSession, requireAuth } from './session';

describe('session utils', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('getAccessToken', () => {
    it('returns null when no token exists', () => {
      expect(getAccessToken()).toBeNull();
    });

    it('returns the access token when it exists', () => {
      localStorage.setItem('access_token', 'test-token');
      expect(getAccessToken()).toBe('test-token');
    });
  });

  describe('getRefreshToken', () => {
    it('returns null when no refresh token exists', () => {
      expect(getRefreshToken()).toBeNull();
    });

    it('returns the refresh token when it exists', () => {
      localStorage.setItem('refresh_token', 'test-refresh');
      expect(getRefreshToken()).toBe('test-refresh');
    });
  });

  describe('isAuthenticated', () => {
    it('returns false when no access token', () => {
      expect(isAuthenticated()).toBe(false);
    });

    it('returns true when access token exists', () => {
      localStorage.setItem('access_token', 'test-token');
      expect(isAuthenticated()).toBe(true);
    });
  });

  describe('clearSession', () => {
    it('removes both tokens from localStorage', () => {
      localStorage.setItem('access_token', 'test-token');
      localStorage.setItem('refresh_token', 'test-refresh');
      clearSession();
      expect(getAccessToken()).toBeNull();
      expect(getRefreshToken()).toBeNull();
    });
  });

  describe('requireAuth', () => {
    it('throws when no token exists', () => {
      expect(() => requireAuth()).toThrow('No autorizado');
    });

    it('returns the token when authenticated', () => {
      localStorage.setItem('access_token', 'test-token');
      expect(requireAuth()).toBe('test-token');
    });
  });
});
