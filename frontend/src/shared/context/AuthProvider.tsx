'use client';

import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { getUserProfile, logout } from '@/shared/api/auth';

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (token: string) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      refreshUser();
    } else {
      setLoading(false);
    }
  }, []);

  const login = (token: string) => {
    localStorage.setItem('accessToken', token);
    refreshUser();
  };

  const refreshUser = async () => {
    try {
      const profile = await getUserProfile();
      setUser(profile);
      setIsAuthenticated(true);
    } catch (error) {
      // If we can't get user profile, the token might be invalid
      logout();
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    setUser(null);
    setIsAuthenticated(false);
    setLoading(false);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      isAuthenticated, 
      loading,
      login,
      logout: handleLogout,
      refreshUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};