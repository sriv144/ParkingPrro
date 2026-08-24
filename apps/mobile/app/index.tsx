import { colors } from "@parkingpro/design-tokens";
import { router } from "expo-router";
import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { apiRequest } from "../src/lib/api";
import { useAuthStore } from "../src/state/auth-store";
import { Brand, Screen } from "../src/ui/primitives";

type ServiceState = "checking" | "starting" | "unavailable";

export default function ServiceStartingScreen() {
  const hydrate = useAuthStore((state) => state.hydrate);
  const [serviceState, setServiceState] = useState<ServiceState>("checking");

  const connect = useCallback(async () => {
    setServiceState("checking");
    const slowTimer = setTimeout(() => setServiceState("starting"), 2_500);
    try {
      await apiRequest("/health/live", {}, { retries: 8 });
      await hydrate();
      router.replace(useAuthStore.getState().user ? "/map" : "/sign-in");
    } catch {
      setServiceState("unavailable");
    } finally {
      clearTimeout(slowTimer);
    }
  }, [hydrate]);

  useEffect(() => {
    const task = setTimeout(() => void connect(), 0);
    return () => clearTimeout(task);
  }, [connect]);

  const title =
    serviceState === "unavailable"
      ? "The demo service is unavailable"
      : "Starting the demo service";
  const body =
    serviceState === "unavailable"
      ? "Check your connection and try again. Booking actions are never queued offline."
      : "The free preview can take up to a minute to wake. ParkingPro will retry safely.";

  return (
    <Screen>
      <View style={styles.content}>
        <Brand />
        {serviceState !== "unavailable" ? (
          <ActivityIndicator size="large" color={colors.cyan500} />
        ) : (
          <Text style={styles.offline}>!</Text>
        )}
        <View style={styles.copy}>
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.body}>{body}</Text>
        </View>
        <Pressable
          accessibilityRole="button"
          onPress={() => void connect()}
          style={styles.button}
        >
          <Text style={styles.buttonText}>
            {serviceState === "unavailable" ? "Try again" : "Retry now"}
          </Text>
        </Pressable>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: {
    flex: 1,
    padding: 28,
    justifyContent: "space-between",
    alignItems: "center",
  },
  copy: { alignItems: "center", gap: 10, maxWidth: 320 },
  title: {
    color: colors.paper50,
    fontSize: 22,
    fontWeight: "700",
    textAlign: "center",
  },
  body: {
    color: colors.paper300,
    fontSize: 16,
    lineHeight: 24,
    textAlign: "center",
  },
  offline: {
    color: colors.red500,
    borderColor: colors.red500,
    borderWidth: 2,
    borderRadius: 32,
    fontSize: 34,
    width: 64,
    height: 64,
    textAlign: "center",
  },
  button: {
    width: "100%",
    minHeight: 52,
    borderWidth: 1,
    borderColor: colors.cyan500,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: { color: colors.cyan500, fontSize: 16, fontWeight: "700" },
});
