import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react';
import { login as apiLogin, googleLoginWithCode as apiGoogleLoginWithCode, logout as apiLogout, register as apiRegister } from '../api/auth';
import { clearStoredAuth, getStoredUser, setStoredUser } from '../api/client';
import { Role, User } from '../types';

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  googleLogin: (code: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (...roles: Role[]) => boolean;
  canViewEmployees: boolean;
  canCreateEmployee: boolean;
  canUpdateEmployee: boolean;
  canDeleteEmployee: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => getStoredUser());
  const [isLoading, setIsLoading] = useState(false);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const auth = await apiLogin(email, password);
      const u: User = {
        user_id: auth.user_id,
        email: auth.email,
        full_name: auth.full_name,
        role: auth.role,
      };
      setUser(u);
      setStoredUser(u);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const googleLogin = useCallback(async (code: string) => {
    setIsLoading(true);
    try {
      const auth = await apiGoogleLoginWithCode(code);
      const u: User = {
        user_id: auth.user_id,
        email: auth.email,
        full_name: auth.full_name,
        role: auth.role,
      };
      setUser(u);
      setStoredUser(u);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (email: string, password: string, fullName: string) => {
    setIsLoading(true);
    try {
      const auth = await apiRegister(email, password, fullName);
      const u: User = {
        user_id: auth.user_id,
        email: auth.email,
        full_name: auth.full_name,
        role: auth.role,
      };
      setUser(u);
      setStoredUser(u);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
    clearStoredAuth();
  }, []);

  const hasRole = useCallback(
    (...roles: Role[]) => (user ? roles.includes(user.role) : false),
    [user]
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      googleLogin,
      register,
      logout,
      hasRole,
      canViewEmployees: user?.role === 'ADMIN' || user?.role === 'MANAGER',
      canCreateEmployee: user?.role === 'ADMIN' || user?.role === 'MANAGER',
      canUpdateEmployee: user?.role === 'ADMIN' || user?.role === 'MANAGER',
      canDeleteEmployee: user?.role === 'ADMIN',
    }),
    [user, isLoading, login, googleLogin, register, logout, hasRole]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
