import type { Reservation } from "@parkingpro/api-contracts";
import { colors } from "@parkingpro/design-tokens";
import { useMutation, useQuery } from "@tanstack/react-query";
import Constants from "expo-constants";
import { router, useLocalSearchParams } from "expo-router";
import { StyleSheet, Text, View } from "react-native";
import RazorpayCheckout from "react-native-razorpay";

import { ApiError, apiRequest, idempotencyKey } from "../../src/lib/api";
import { PrimaryButton, Screen } from "../../src/ui/primitives";

type Order = {
  order_id: string;
  key_id: string;
  amount_paise: number;
  currency: string;
  reservation_id: string;
};
type CheckoutResult = {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
};

export default function CheckoutScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const reservation = useQuery({
    queryKey: ["reservation", id],
    queryFn: () => apiRequest<Reservation>(`/api/v1/reservations/${id}`),
  });
  const checkout = useMutation({
    mutationFn: async () => {
      const order = await apiRequest<Order>(`/api/v1/payments/${id}/order`, {
        method: "POST",
        headers: { "Idempotency-Key": idempotencyKey() },
      });
      const result = (await RazorpayCheckout.open({
        key:
          order.key_id ||
          (Constants.expoConfig?.extra?.razorpayKeyId as string),
        amount: order.amount_paise,
        currency: order.currency,
        order_id: order.order_id,
        name: "ParkingPro",
        description: `Parking at ${reservation.data?.lot_name ?? "Bengaluru facility"}`,
        theme: { color: colors.cyan500 },
      })) as CheckoutResult;
      return apiRequest<Reservation>(`/api/v1/payments/${id}/verify`, {
        method: "POST",
        headers: { "Idempotency-Key": idempotencyKey() },
        body: JSON.stringify(result),
      });
    },
    onSuccess: (confirmed) =>
      router.replace({ pathname: "/pass/[id]", params: { id: confirmed.id } }),
  });

  return (
    <Screen>
      <View style={styles.content}>
        <Text style={styles.eyebrow}>Test checkout</Text>
        <Text style={styles.title}>
          {reservation.data?.lot_name ?? "Your secure hold"}
        </Text>
        <View style={styles.amountCard}>
          <Text style={styles.label}>Amount due</Text>
          <Text style={styles.amount}>
            ₹{((reservation.data?.quoted_amount_paise ?? 0) / 100).toFixed(0)}
          </Text>
          <Text style={styles.test}>RAZORPAY TEST MODE · NO REAL CHARGE</Text>
        </View>
        <Text style={styles.body}>
          Closing the payment sheet leaves the hold active until its expiry
          time. Retrying cannot create a duplicate order.
        </Text>
        {checkout.error ? (
          <Text accessibilityRole="alert" style={styles.error}>
            {checkout.error instanceof ApiError
              ? checkout.error.message
              : "Payment was not completed."}
          </Text>
        ) : null}
        <PrimaryButton
          accessibilityHint="Opens Razorpay in test mode; no real charge is made"
          disabled={!reservation.data || checkout.isPending}
          label={
            checkout.isPending
              ? "Verifying payment…"
              : "Open Razorpay test checkout"
          }
          onPress={() => checkout.mutate()}
          testID="razorpay-checkout-button"
        />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: { flex: 1, justifyContent: "center", padding: 24, gap: 22 },
  eyebrow: {
    color: colors.cyan500,
    fontWeight: "800",
    letterSpacing: 1.5,
    textTransform: "uppercase",
  },
  title: { color: colors.paper50, fontSize: 31, fontWeight: "900" },
  amountCard: {
    alignItems: "center",
    gap: 8,
    padding: 28,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: colors.ink700,
    backgroundColor: colors.ink900,
  },
  label: { color: colors.paper300 },
  amount: { color: colors.paper50, fontSize: 48, fontWeight: "900" },
  test: {
    color: colors.green500,
    fontSize: 11,
    fontWeight: "900",
    letterSpacing: 1,
  },
  body: { color: colors.paper300, lineHeight: 22 },
  error: { color: colors.red500 },
});
