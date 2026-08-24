import type { AuthResponse, UserProfile } from "@parkingpro/api-contracts";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";

import {
  apiRequest,
  csrfToken,
  setAccessToken,
  setCsrfToken,
} from "../lib/api";

type AuthContextValue = {
  user: UserProfile | null;
  ready: boolean;
  login(email: string, password: string): Promise<void>;
  logout(): Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [ready, setReady] = useState(() => !csrfToken());

  const accept = useCallback(async (session: AuthResponse) => {
    setAccessToken(session.access_token);
    setCsrfToken(session.csrf_token);
    setUser(session.user);
  }, []);

  useEffect(() => {
    const csrf = csrfToken();
    if (!csrf) return;
    void apiRequest<AuthResponse>("/api/v1/auth/refresh", {
      method: "POST",
      headers: { "X-CSRF-Token": csrf },
      body: JSON.stringify({ client_type: "web" }),
    })
      .then(accept)
      .catch(() => {
        setAccessToken(null);
        setCsrfToken(null);
        setUser(null);
      })
      .finally(() => setReady(true));
  }, [accept]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      ready,
      async login(email, password) {
        const session = await apiRequest<AuthResponse>("/api/v1/auth/login", {
          method: "POST",
          body: JSON.stringify({
            email,
            password,
            client_type: "web",
            device_name: "Operator web",
          }),
        });
        await accept(session);
      },
      async logout() {
        const csrf = csrfToken();
        await apiRequest("/api/v1/auth/logout", {
          method: "POST",
          headers: { "X-CSRF-Token": csrf },
          body: JSON.stringify({ client_type: "web" }),
        }).catch(() => undefined);
        setAccessToken(null);
        setCsrfToken(null);
        setUser(null);
      },
    }),
    [accept, ready, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be rendered inside AuthProvider");
  return value;
}
