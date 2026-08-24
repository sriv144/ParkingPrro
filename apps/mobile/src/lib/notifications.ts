import Constants from "expo-constants";
import * as Notifications from "expo-notifications";
import { Platform } from "react-native";

import { apiRequest } from "./api";

const PUSH_TOKEN_KEY = "parkingpro.push-token.v1";

export async function registerForReservationReminders(): Promise<void> {
  if (Platform.OS !== "android" && Platform.OS !== "ios") return;

  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("reservations", {
      name: "Reservation reminders",
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#12D7E8",
    });
  }

  const existing = await Notifications.getPermissionsAsync();
  const permission =
    existing.status === "granted"
      ? existing
      : await Notifications.requestPermissionsAsync();
  if (permission.status !== "granted") return;

  const configuredProjectId = Constants.expoConfig?.extra?.eas?.projectId as
    string | undefined;
  const projectId = configuredProjectId || Constants.easConfig?.projectId;
  if (!projectId) return;

  const token = (await Notifications.getExpoPushTokenAsync({ projectId })).data;
  await apiRequest("/api/v1/auth/push-token", {
    method: "POST",
    body: JSON.stringify({ token, platform: Platform.OS }),
  });
  const SecureStore = await import("expo-secure-store");
  await SecureStore.setItemAsync(PUSH_TOKEN_KEY, token);
}

export async function removeReservationReminderToken(): Promise<void> {
  const SecureStore = await import("expo-secure-store");
  const token = await SecureStore.getItemAsync(PUSH_TOKEN_KEY);
  if (!token || (Platform.OS !== "android" && Platform.OS !== "ios")) return;
  await apiRequest("/api/v1/auth/push-token", {
    method: "DELETE",
    body: JSON.stringify({ token, platform: Platform.OS }),
  });
  await SecureStore.deleteItemAsync(PUSH_TOKEN_KEY);
}
