import type { Reservation } from "@parkingpro/api-contracts";
import { colors } from "@parkingpro/design-tokens";
import { useQuery } from "@tanstack/react-query";
import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { apiRequest } from "../src/lib/api";
import { EmptyState, PrimaryButton, Screen } from "../src/ui/primitives";

export default function ActiveReservationScreen() {
  const reservations = useQuery({
    queryKey: ["reservations"],
    queryFn: () => apiRequest<Reservation[]>("/api/v1/reservations"),
    refetchInterval: 10_000,
  });
  const active = reservations.data?.find((item) =>
    ["held", "confirmed", "checked_in"].includes(item.status),
  );
  return (
    <Screen>
      <View style={styles.content}>
        <Pressable
          accessibilityLabel="Back to parking map"
          accessibilityRole="button"
          onPress={() => router.back()}
        >
          <Text style={styles.back}>← Map</Text>
        </Pressable>
        <Text style={styles.title}>Active reservation</Text>
        {active ? (
          <View style={styles.card}>
            <Text
              accessibilityLabel={`Reservation status: ${active.status.replace("_", " ")}`}
              style={styles.status}
            >
              {active.status.replace("_", " ")}
            </Text>
            <Text style={styles.name}>{active.lot_name}</Text>
            <Text style={styles.meta}>
              {active.registration_number} · Spot {active.spot_code}
            </Text>
            <Text style={styles.time}>
              {new Date(active.starts_at).toLocaleString()} –{" "}
              {new Date(active.ends_at).toLocaleTimeString()}
            </Text>
            {active.qr_payload ? (
              <PrimaryButton
                label="Open parking pass"
                onPress={() =>
                  router.push({
                    pathname: "/pass/[id]",
                    params: { id: active.id },
                  })
                }
              />
            ) : (
              <PrimaryButton
                label="Complete test payment"
                onPress={() =>
                  router.push({
                    pathname: "/checkout/[id]",
                    params: { id: active.id },
                  })
                }
              />
            )}
          </View>
        ) : (
          <EmptyState
            title="No active reservation"
            body="Create a reservation from the Bengaluru map to see live state here."
          />
        )}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: { flex: 1, padding: 22, gap: 18 },
  back: { color: colors.cyan500, fontWeight: "800" },
  title: { color: colors.paper50, fontSize: 31, fontWeight: "900" },
  card: {
    borderWidth: 1,
    borderColor: colors.ink700,
    borderRadius: 18,
    backgroundColor: colors.ink900,
    padding: 20,
    gap: 12,
  },
  status: {
    color: colors.green500,
    textTransform: "uppercase",
    fontWeight: "900",
    letterSpacing: 1.1,
  },
  name: { color: colors.paper50, fontSize: 25, fontWeight: "900" },
  meta: { color: colors.cyan500, fontWeight: "800" },
  time: { color: colors.paper300, lineHeight: 22, marginBottom: 10 },
});
