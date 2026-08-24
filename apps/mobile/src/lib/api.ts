import type { ApiErrorBody, AuthResponse } from "@parkingpro/api-contracts";
import Constants from "expo-constants";
import * as SecureStore from "expo-secure-store";

const apiUrl =
  (Constants.expoConfig?.extra?.apiUrl as string | undefined)?.replace(
    /\/$/,
    "",
  ) ?? "http://10.0.2.2:5000";

let accessToken: string | null = null;
let refreshPromise: Promise<boolean> | null = null;
const refreshKey = "parkingpro.refresh.v1";

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

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
  options: { retries?: number; refresh?: boolean } = {},
): Promise<T> {
  const retries = options.retries ?? 0;
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body) headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  try {
    const response = await fetch(`${apiUrl}${path}`, { ...init, headers });
    if (
      response.status === 401 &&
      options.refresh !== false &&
      !path.startsWith("/api/v1/auth/")
    ) {
      const refreshed = await refreshAccessToken();
      if (refreshed)
        return apiRequest<T>(path, init, { ...options, refresh: false });
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
  } catch (error) {
    if (
      retries > 0 &&
      (!(error instanceof ApiError) ||
        error.status === 502 ||
        error.status === 503)
    ) {
      await new Promise((resolve) => setTimeout(resolve, 2_000));
      return apiRequest<T>(path, init, { retries: retries - 1 });
    }
    throw error;
  }
}

async function refreshAccessToken(): Promise<boolean> {
  refreshPromise ??= (async () => {
    const refreshToken = await SecureStore.getItemAsync(refreshKey);
    if (!refreshToken) return false;
    const response = await fetch(`${apiUrl}/api/v1/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        client_type: "mobile",
        refresh_token: refreshToken,
      }),
    });
    if (!response.ok) {
      await SecureStore.deleteItemAsync(refreshKey);
      accessToken = null;
      return false;
    }
    const session = (await response.json()) as AuthResponse;
    accessToken = session.access_token;
    if (session.refresh_token)
      await SecureStore.setItemAsync(refreshKey, session.refresh_token);
    return true;
  })().finally(() => {
    refreshPromise = null;
  });
  return refreshPromise;
}

export function idempotencyKey() {
  const random = Math.random().toString(36).slice(2);
  return `${Date.now()}-${random}-parkingpro`;
}
