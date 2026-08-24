import type { Reservation } from "@parkingpro/api-contracts";
import { colors } from "@parkingpro/design-tokens";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { router } from "expo-router";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";

import { apiRequest, idempotencyKey } from "../src/lib/api";
import { EmptyState, Screen } from "../src/ui/primitives";

export default function HistoryScreen() {
  const queryClient = useQueryClient();
  const reservations = useQuery({
    queryKey: ["reservations"],
    queryFn: () => apiRequest<Reservation[]>("/api/v1/reservations"),
  });
  const cancel = useMutation({
    mutationFn: (id: string) =>
      apiRequest<Reservation>(`/api/v1/reservations/${id}/cancel`, {
        method: "POST",
        headers: { "Idempotency-Key": idempotencyKey() },
      }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["reservations"] }),
  });
  return (
    <Screen>
      <View style={styles.header}>
        <Pressable
          accessibilityLabel="Back to parking map"
          accessibilityRole="button"
          onPress={() => router.back()}
        >
          <Text style={styles.back}>← Map</Text>
        </Pressable>
        <Text style={styles.title}>Your reservations</Text>
      </View>
      <FlatList
        contentContainerStyle={styles.list}
        data={reservations.data ?? []}
        keyExtractor={(item) => item.id}
        ListEmptyComponent={
          <EmptyState
            title="No reservations yet"
            body="Your active passes and completed parking sessions will appear here."
          />
        }
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View style={styles.row}>
              <Text style={styles.name}>{item.lot_name}</Text>
              <Text style={styles.status}>{item.status.replace("_", " ")}</Text>
            </View>
            <Text style={styles.meta}>
              {new Date(item.starts_at).toLocaleString()} ·{" "}
              {item.registration_number}
            </Text>
            <Text style={styles.spot}>
              Spot {item.spot_code} · ₹
              {(item.quoted_amount_paise / 100).toFixed(0)}
            </Text>
            {(item.status === "held" || item.status === "confirmed") &&
            new Date(item.starts_at) > new Date() ? (
              <Pressable
                accessibilityLabel={`Cancel reservation at ${item.lot_name} and refund its test payment`}
                accessibilityRole="button"
                onPress={() => cancel.mutate(item.id)}
              >
                <Text style={styles.cancel}>
                  Cancel and refund test payment
                </Text>
              </Pressable>
            ) : null}
            {item.qr_payload ? (
              <Pressable
                accessibilityLabel={`View QR pass for ${item.lot_name}`}
                accessibilityRole="link"
                onPress={() =>
                  router.push({
                    pathname: "/pass/[id]",
                    params: { id: item.id },
                  })
                }
              >
                <Text style={styles.passLink}>View QR pass →</Text>
              </Pressable>
            ) : null}
          </View>
        )}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { padding: 22, gap: 12 },
  back: { color: colors.cyan500, fontWeight: "800" },
  title: { color: colors.paper50, fontSize: 31, fontWeight: "900" },
  list: { padding: 18, gap: 12, flexGrow: 1 },
  card: {
    borderWidth: 1,
    borderColor: colors.ink700,
    backgroundColor: colors.ink900,
    borderRadius: 15,
    padding: 16,
    gap: 8,
  },
  row: { flexDirection: "row", justifyContent: "space-between", gap: 12 },
  name: { color: colors.paper50, fontSize: 18, fontWeight: "800", flex: 1 },
  status: {
    color: colors.green500,
    fontWeight: "900",
    textTransform: "uppercase",
    fontSize: 11,
  },
  meta: { color: colors.paper300 },
  spot: { color: colors.cyan500, fontWeight: "800" },
  cancel: { color: colors.red500, fontWeight: "800", marginTop: 6 },
  passLink: { color: colors.cyan500, fontWeight: "800", marginTop: 6 },
});
