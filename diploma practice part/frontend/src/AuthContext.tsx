import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { apiGet, apiPost, type User } from './api';

type Ctx = {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  ready: boolean;
};

const AuthContext = createContext<Ctx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const t = localStorage.getItem('token');
    const u = localStorage.getItem('user');
    if (t) setToken(t);
    if (u) {
      try {
        setUser(JSON.parse(u) as User);
      } catch {
        /* ignore */
      }
    }
    setReady(true);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await apiPost<{
      access_token: string;
      token_type: string;
    }>('/api/auth/login', { email, password });
    localStorage.setItem('token', res.access_token);
    setToken(res.access_token);
    const me = await apiGet<User>('/api/auth/me');
    localStorage.setItem('user', JSON.stringify(me));
    setUser(me);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  }, []);

  const v = useMemo(
    () => ({ user, token, login, logout, ready }),
    [user, token, login, logout, ready]
  );

  return <AuthContext.Provider value={v}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const c = useContext(AuthContext);
  if (!c) throw new Error('useAuth outside provider');
  return c;
}
