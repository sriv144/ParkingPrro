import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../state/AuthContext";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { ready, user } = useAuth();
  if (!ready)
    return (
      <main className="service-state">
        <p className="eyebrow">Starting demo service</p>
        <h1>Restoring the secure workspace…</h1>
      </main>
    );
  if (!user || (user.role !== "operator" && user.role !== "admin"))
    return <Navigate to="/" replace />;
  return children;
}
