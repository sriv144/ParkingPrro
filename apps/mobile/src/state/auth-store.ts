import type { AuthResponse, UserProfile } from "@parkingpro/api-contracts";
import * as SecureStore from "expo-secure-store";
import { create } from "zustand";

import { apiRequest, setAccessToken } from "../lib/api";
import {
  registerForReservationReminders,
  removeReservationReminderToken,
} from "../lib/notifications";

const REFRESH_KEY = "parkingpro.refresh.v1";

type AuthState = {
  user: UserProfile | null;
  ready: boolean;
  signIn(email: string, password: string): Promise<void>;
  useDemo(): Promise<void>;
  hydrate(): Promise<void>;
  signOut(): Promise<void>;
};

async function acceptSession(
  session: AuthResponse,
  set: (state: Partial<AuthState>) => void,
) {
  setAccessToken(session.access_token);
  if (session.refresh_token) {
    await SecureStore.setItemAsync(REFRESH_KEY, session.refresh_token);
  }
  set({ user: session.user, ready: true });
  void registerForReservationReminders().catch(() => undefined);
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  ready: false,
  async signIn(email, password) {
    const session = await apiRequest<AuthResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
        client_type: "mobile",
        device_name: "ParkingPro Android",
      }),
    });
    await acceptSession(session, set);
  },
  async useDemo() {
    const email =
      process.env.EXPO_PUBLIC_DEMO_DRIVER_EMAIL ?? "driver@parkingpro.demo";
    const password =
      process.env.EXPO_PUBLIC_DEMO_DRIVER_PASSWORD ?? "ParkingPro-Demo-2026";
    await useAuthStore.getState().signIn(email, password);
  },
  async hydrate() {
    const refreshToken = await SecureStore.getItemAsync(REFRESH_KEY);
    if (!refreshToken) {
      set({ ready: true });
      return;
    }
    try {
      const session = await apiRequest<AuthResponse>("/api/v1/auth/refresh", {
        method: "POST",
        body: JSON.stringify({
          client_type: "mobile",
          refresh_token: refreshToken,
        }),
      });
      await acceptSession(session, set);
    } catch {
      await SecureStore.deleteItemAsync(REFRESH_KEY);
      setAccessToken(null);
      set({ user: null, ready: true });
    }
  },
  async signOut() {
    await removeReservationReminderToken().catch(() => undefined);
    const refreshToken = await SecureStore.getItemAsync(REFRESH_KEY);
    if (refreshToken) {
      await apiRequest("/api/v1/auth/logout", {
        method: "POST",
        body: JSON.stringify({
          client_type: "mobile",
          refresh_token: refreshToken,
        }),
      }).catch(() => undefined);
    }
    await SecureStore.deleteItemAsync(REFRESH_KEY);
    setAccessToken(null);
    set({ user: null, ready: true });
  },
}));
