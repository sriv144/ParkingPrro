import type { Reservation } from "@parkingpro/api-contracts";
import { colors } from "@parkingpro/design-tokens";
import { useQuery } from "@tanstack/react-query";
import * as SecureStore from "expo-secure-store";
import { router, useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import QRCode from "react-native-qrcode-svg";

import { apiRequest } from "../../src/lib/api";
import { Screen } from "../../src/ui/primitives";

export default function PassScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [offline, setOffline] = useState<Reservation | null>(null);
  const key = `parkingpro.pass.${id}`;
  const reservation = useQuery({
    queryKey: ["reservation", id],
    queryFn: () => apiRequest<Reservation>(`/api/v1/reservations/${id}`),
    retry: 1,
  });

  useEffect(() => {
    if (reservation.data?.qr_payload) {
      void SecureStore.setItemAsync(key, JSON.stringify(reservation.data));
    } else if (reservation.isError) {
      void SecureStore.getItemAsync(key).then((value) => {
        if (value) setOffline(JSON.parse(value) as Reservation);
      });
    }
  }, [key, reservation.data, reservation.isError]);

  const pass = reservation.data?.qr_payload ? reservation.data : offline;
  return (
    <Screen>
      <View style={styles.content}>
        <Text style={styles.eyebrow}>
          {offline ? "Offline cached pass" : "Reservation confirmed"}
        </Text>
        <Text style={styles.title}>
          {pass?.lot_name ?? "Loading parking pass…"}
        </Text>
        {pass?.qr_payload ? (
          <View
            accessibilityLabel={`Parking pass for ${pass.lot_name}, spot ${pass.spot_code}, vehicle ${pass.registration_number}`}
            accessible
            style={styles.qrCard}
            testID="qr-parking-pass"
          >
            <QRCode
              value={pass.qr_payload}
              size={220}
              backgroundColor="#FFFFFF"
              color="#050B0F"
            />
            <Text style={styles.spot}>SPOT {pass.spot_code}</Text>
            <Text style={styles.registration}>{pass.registration_number}</Text>
          </View>
        ) : (
          <Text style={styles.error}>
            No offline pass is available on this device.
          </Text>
        )}
        <Text style={styles.body}>
          The QR contains only a signed reservation ID and nonce. The operator
          validates its live state before check-in.
        </Text>
        <Pressable
          accessibilityRole="button"
          onPress={() => router.replace("/map")}
          style={styles.link}
        >
          <Text style={styles.linkText}>Return to map</Text>
        </Pressable>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: {
    flex: 1,
    padding: 24,
    justifyContent: "center",
    gap: 20,
    alignItems: "center",
  },
  eyebrow: {
    color: colors.green500,
    fontWeight: "900",
    letterSpacing: 1.4,
    textTransform: "uppercase",
  },
  title: {
    color: colors.paper50,
    fontSize: 29,
    fontWeight: "900",
    textAlign: "center",
  },
  qrCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 22,
    padding: 24,
    alignItems: "center",
    gap: 10,
  },
  spot: { color: colors.ink950, fontSize: 24, fontWeight: "900", marginTop: 8 },
  registration: { color: colors.ink600, fontWeight: "800" },
  body: { color: colors.paper300, textAlign: "center", lineHeight: 21 },
  error: { color: colors.red500 },
  link: { minHeight: 48, justifyContent: "center" },
  linkText: { color: colors.cyan500, fontWeight: "800" },
});
