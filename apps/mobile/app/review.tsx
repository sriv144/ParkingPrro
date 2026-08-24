import type { Quote } from "@parkingpro/api-contracts";
import { colors } from "@parkingpro/design-tokens";
import { useMutation, useQuery } from "@tanstack/react-query";
import { router, useLocalSearchParams } from "expo-router";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";

import { ApiError, apiRequest, idempotencyKey } from "../src/lib/api";
import { PrimaryButton, Screen } from "../src/ui/primitives";

type Params = {
  lotId: string;
  vehicleId: string;
  startsAt: string;
  endsAt: string;
  spotType: string;
};

export default function ReviewScreen() {
  const params = useLocalSearchParams<Params>();
  const quote = useQuery({
    queryKey: ["quote", params],
    queryFn: () =>
      apiRequest<Quote>(`/api/v1/lots/${params.lotId}/quote`, {
        method: "POST",
        body: JSON.stringify({
          starts_at: params.startsAt,
          ends_at: params.endsAt,
          spot_type: params.spotType,
        }),
      }),
  });
  const reserve = useMutation({
    mutationFn: () =>
      apiRequest<{ id: string }>("/api/v1/reservations", {
        method: "POST",
        headers: { "Idempotency-Key": idempotencyKey() },
        body: JSON.stringify({
          lot_id: params.lotId,
          vehicle_id: params.vehicleId,
          starts_at: params.startsAt,
          ends_at: params.endsAt,
          spot_type: params.spotType,
        }),
      }),
    onSuccess: (reservation) =>
      router.replace({
        pathname: "/checkout/[id]",
        params: { id: reservation.id },
      }),
  });

  return (
    <Screen>
      <View style={styles.content}>
        <Text style={styles.eyebrow}>Reservation review</Text>
        <Text style={styles.title}>Confirm the details</Text>
        {quote.isLoading ? (
          <ActivityIndicator color={colors.cyan500} />
        ) : quote.data ? (
          <View style={styles.card}>
            <Row
              label="Start"
              value={new Date(params.startsAt).toLocaleString()}
            />
            <Row label="End" value={new Date(params.endsAt).toLocaleString()} />
            <Row label="Spot" value={params.spotType.toUpperCase()} />
            <Row
              label="Duration"
              value={`${quote.data.duration_minutes} minutes`}
            />
            <View style={styles.divider} />
            <Row
              label="Total"
              value={`₹${(quote.data.amount_paise / 100).toFixed(0)}`}
              strong
            />
          </View>
        ) : (
          <Text style={styles.error}>The quote is no longer available.</Text>
        )}
        <Text style={styles.notice}>
          A 10-minute hold starts only after you continue. Payment uses Razorpay
          test mode.
        </Text>
        {reserve.error ? (
          <Text accessibilityRole="alert" style={styles.error}>
            {reserve.error instanceof ApiError
              ? reserve.error.message
              : "Could not reserve this spot."}
          </Text>
        ) : null}
        <PrimaryButton
          accessibilityHint="Creates a temporary reservation and opens test payment"
          disabled={!quote.data || reserve.isPending}
          label={
            reserve.isPending
              ? "Creating secure hold…"
              : "Hold spot for 10 minutes"
          }
          onPress={() => reserve.mutate()}
          testID="hold-reservation-button"
        />
      </View>
    </Screen>
  );
}

function Row({
  label,
  value,
  strong = false,
}: {
  label: string;
  value: string;
  strong?: boolean;
}) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={strong ? styles.strong : styles.value}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  content: { flex: 1, padding: 24, justifyContent: "center", gap: 20 },
  eyebrow: {
    color: colors.cyan500,
    textTransform: "uppercase",
    letterSpacing: 1.4,
    fontWeight: "800",
  },
  title: { color: colors.paper50, fontSize: 32, fontWeight: "900" },
  card: {
    backgroundColor: colors.ink900,
    borderColor: colors.ink700,
    borderWidth: 1,
    borderRadius: 18,
    padding: 18,
    gap: 15,
  },
  row: { flexDirection: "row", justifyContent: "space-between", gap: 20 },
  label: { color: colors.paper300 },
  value: {
    color: colors.paper50,
    fontWeight: "700",
    textAlign: "right",
    flex: 1,
  },
  strong: { color: colors.green500, fontSize: 23, fontWeight: "900" },
  divider: { height: 1, backgroundColor: colors.ink700 },
  notice: { color: colors.paper300, lineHeight: 21 },
  error: { color: colors.red500 },
});
