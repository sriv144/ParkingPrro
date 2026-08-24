import type { ApiErrorBody, AuthResponse } from "@parkingpro/api-contracts";

const apiUrl = (
  import.meta.env.VITE_API_URL || "http://localhost:5000"
).replace(/\/$/, "");
let accessToken: string | null = null;
let refreshPromise: Promise<boolean> | null = null;

const wait = (milliseconds: number) =>
  new Promise<void>((resolve) => window.setTimeout(resolve, milliseconds));

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code: string,
    readonly fields: Record<string, string[]> = {},
  ) {
    super(message);
  }
}

export function setAccessToken(value: string | null) {
  accessToken = value;
}

export function csrfToken() {
  return sessionStorage.getItem("parkingpro.csrf") ?? "";
}

export function setCsrfToken(value: string | null) {
  if (value) sessionStorage.setItem("parkingpro.csrf", value);
  else sessionStorage.removeItem("parkingpro.csrf");
}

export async function wakeService(onRetry?: (attempt: number) => void) {
  for (let attempt = 0; attempt < 8; attempt += 1) {
    try {
      const response = await fetch(`${apiUrl}/health/live`, {
        headers: { Accept: "application/json" },
        signal: AbortSignal.timeout(10_000),
      });
      if (response.ok) return;
    } catch {
      // A sleeping preview and a temporarily unavailable network share this path.
    }
    if (attempt < 7) {
      onRetry?.(attempt + 1);
      await wait(Math.min(750 * 2 ** attempt, 6_000));
    }
  }
  throw new ApiError(
    "The demo API did not become ready. Check your connection and retry.",
    503,
    "SERVICE_UNAVAILABLE",
  );
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
  allowRefresh = true,
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body) headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  const response = await fetch(`${apiUrl}${path}`, {
    ...init,
    credentials: "include",
    headers,
  });
  if (
    response.status === 401 &&
    allowRefresh &&
    !path.startsWith("/api/v1/auth/")
  ) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return apiRequest<T>(path, init, false);
  }
  if (!response.ok) {
    const body = (await response
      .json()
      .catch(() => null)) as ApiErrorBody | null;
    throw new ApiError(
      body?.error.message ?? `Request failed with status ${response.status}.`,
      response.status,
      body?.error.code ?? "HTTP_ERROR",
      body?.error.fields,
    );
  }
  return (await response.json()) as T;
}

async function refreshAccessToken(): Promise<boolean> {
  refreshPromise ??= (async () => {
    const csrf = csrfToken();
    if (!csrf) return false;
    const response = await fetch(`${apiUrl}/api/v1/auth/refresh`, {
      method: "POST",
      credentials: "include",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf,
      },
      body: JSON.stringify({ client_type: "web" }),
    });
    if (!response.ok) {
      setAccessToken(null);
      setCsrfToken(null);
      return false;
    }
    const session = (await response.json()) as AuthResponse;
    setAccessToken(session.access_token);
    setCsrfToken(session.csrf_token);
    return true;
  })().finally(() => {
    refreshPromise = null;
  });
  return refreshPromise;
}
