import type { ParkingLotSummary, Vehicle } from "@parkingpro/api-contracts";
import { colors } from "@parkingpro/design-tokens";
import { useQuery } from "@tanstack/react-query";
import { router, useLocalSearchParams } from "expo-router";
import { useMemo, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { apiRequest } from "../../src/lib/api";
import { PrimaryButton, Screen } from "../../src/ui/primitives";

function nextSlot() {
  const value = new Date(Date.now() + 60 * 60 * 1000);
  value.setSeconds(0, 0);
  value.setMinutes(value.getMinutes() < 30 ? 30 : 0);
  if (value.getMinutes() === 0) value.setHours(value.getHours() + 1);
  return value;
}

export default function FacilityScreen() {
  const {
    id,
    startsAt: startsAtParam,
    duration: durationParam,
    spotType: spotTypeParam,
  } = useLocalSearchParams<{
    id: string;
    startsAt?: string;
    duration?: string;
    spotType?: Vehicle["vehicle_type"];
  }>();
  const initialStart = useMemo(() => {
    const parsed = startsAtParam ? new Date(startsAtParam) : nextSlot();
    return Number.isNaN(parsed.getTime()) ? nextSlot() : parsed;
  }, [startsAtParam]);
  const initialDuration = Number(durationParam);
  const [startOffsetMinutes, setStartOffsetMinutes] = useState(0);
  const [duration, setDuration] = useState(
    Number.isFinite(initialDuration) &&
      initialDuration >= 30 &&
      initialDuration <= 1_440
      ? Math.round(initialDuration / 30) * 30
      : 60,
  );
  const [spotType, setSpotType] = useState<Vehicle["vehicle_type"]>(
    spotTypeParam && ["car", "bike", "ev", "accessible"].includes(spotTypeParam)
      ? spotTypeParam
      : "car",
  );
  const [vehicleId, setVehicleId] = useState<string | null>(null);
  const startsAt = useMemo(
    () => new Date(initialStart.getTime() + startOffsetMinutes * 60_000),
    [initialStart, startOffsetMinutes],
  );
  const endsAt = useMemo(
    () => new Date(startsAt.getTime() + duration * 60_000),
    [duration, startsAt],
  );

  const lot = useQuery({
    queryKey: ["lot", id],
    queryFn: () => apiRequest<ParkingLotSummary>(`/api/v1/lots/${id}`),
    enabled: Boolean(id),
  });
  const vehicles = useQuery({
    queryKey: ["vehicles"],
    queryFn: () => apiRequest<Vehicle[]>("/api/v1/vehicles"),
  });
  const selectedVehicle = vehicleId ?? vehicles.data?.[0]?.id;

  if (lot.isLoading || vehicles.isLoading) {
    return (
      <Screen>
        <ActivityIndicator
          style={styles.center}
          size="large"
          color={colors.cyan500}
        />
      </Screen>
    );
  }
  if (!lot.data) {
    return (
      <Screen>
        <View style={styles.center}>
          <Text style={styles.error}>Facility details are unavailable.</Text>
        </View>
      </Screen>
    );
  }

  return (
    <Screen>
      <ScrollView contentContainerStyle={styles.content}>
        <Pressable
          accessibilityLabel="Back to parking map"
          accessibilityRole="button"
          onPress={() => router.back()}
        >
          <Text style={styles.back}>← Back to map</Text>
        </Pressable>
        <View style={styles.hero}>
          <Text style={styles.eyebrow}>
            Bengaluru · {lot.data.available_spots} spots available
          </Text>
          <Text style={styles.title}>{lot.data.name}</Text>
          <Text style={styles.address}>{lot.data.address}</Text>
        </View>
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Arrival</Text>
          <View style={styles.stepperRow}>
            <Text style={styles.time}>
              {startsAt.toLocaleString([], {
                weekday: "short",
                day: "numeric",
                month: "short",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </Text>
            <View style={styles.stepperActions}>
              <Pressable
                accessibilityLabel="Move arrival 30 minutes earlier"
                accessibilityRole="button"
                accessibilityState={{ disabled: startOffsetMinutes === 0 }}
                disabled={startOffsetMinutes === 0}
                onPress={() =>
                  setStartOffsetMinutes((value) => Math.max(0, value - 30))
                }
                style={styles.stepperButton}
              >
                <Text style={styles.stepperButtonText}>−</Text>
              </Pressable>
              <Pressable
                accessibilityLabel="Move arrival 30 minutes later"
                accessibilityRole="button"
                onPress={() =>
                  setStartOffsetMinutes((value) =>
                    Math.min(7 * 24 * 60, value + 30),
                  )
                }
                style={styles.stepperButton}
              >
                <Text style={styles.stepperButtonText}>+</Text>
              </Pressable>
            </View>
          </View>
          <Text style={styles.sectionTitle}>Duration</Text>
          <View style={styles.options}>
            {[30, 60, 120, 240, 720, 1_440].map((minutes) => (
              <Pressable
                accessibilityLabel={`${minutes} minute duration`}
                accessibilityRole="radio"
                accessibilityState={{ checked: duration === minutes }}
                key={minutes}
                onPress={() => setDuration(minutes)}
                style={[
                  styles.option,
                  duration === minutes && styles.optionActive,
                ]}
              >
                <Text
                  style={
                    duration === minutes
                      ? styles.optionTextActive
                      : styles.optionText
                  }
                >
                  {minutes < 60 ? "30 min" : `${minutes / 60} hr`}
                </Text>
              </Pressable>
            ))}
          </View>
          <View style={styles.durationStepper}>
            <Text style={styles.durationValue}>
              Exact duration: {duration < 60 ? "30 min" : `${duration / 60} hr`}
            </Text>
            <View style={styles.stepperActions}>
              <Pressable
                accessibilityLabel="Reduce duration by 30 minutes"
                accessibilityRole="button"
                accessibilityState={{ disabled: duration === 30 }}
                disabled={duration === 30}
                onPress={() => setDuration((value) => Math.max(30, value - 30))}
                style={styles.stepperButton}
              >
                <Text style={styles.stepperButtonText}>−</Text>
              </Pressable>
              <Pressable
                accessibilityLabel="Increase duration by 30 minutes"
                accessibilityRole="button"
                accessibilityState={{ disabled: duration === 1_440 }}
                disabled={duration === 1_440}
                onPress={() =>
                  setDuration((value) => Math.min(1_440, value + 30))
                }
                style={styles.stepperButton}
              >
                <Text style={styles.stepperButtonText}>+</Text>
              </Pressable>
            </View>
          </View>
          <Text style={styles.sectionTitle}>Spot type</Text>
          <View style={styles.options}>
            {(["car", "bike", "ev", "accessible"] as const).map((value) => (
              <Pressable
                accessibilityLabel={`${value} parking spot`}
                accessibilityRole="radio"
                accessibilityState={{ checked: spotType === value }}
                key={value}
                onPress={() => setSpotType(value)}
                style={[
                  styles.option,
                  spotType === value && styles.optionActive,
                ]}
              >
                <Text
                  style={
                    spotType === value
                      ? styles.optionTextActive
                      : styles.optionText
                  }
                >
                  {value.toUpperCase()}
                </Text>
              </Pressable>
            ))}
          </View>
          <Text style={styles.sectionTitle}>Vehicle</Text>
          {vehicles.data?.length ? (
            <View style={styles.vehicleList}>
              {vehicles.data.map((vehicle) => (
                <Pressable
                  accessibilityLabel={`Vehicle ${vehicle.label ?? vehicle.registration_number}, ${vehicle.registration_number}, ${vehicle.vehicle_type}`}
                  accessibilityRole="radio"
                  accessibilityState={{
                    checked: selectedVehicle === vehicle.id,
                  }}
                  key={vehicle.id}
                  onPress={() => setVehicleId(vehicle.id)}
                  style={[
                    styles.vehicle,
                    selectedVehicle === vehicle.id && styles.vehicleActive,
                  ]}
                >
                  <Text style={styles.vehicleName}>
                    {vehicle.label ?? vehicle.registration_number}
                  </Text>
                  <Text style={styles.vehicleMeta}>
                    {vehicle.registration_number} · {vehicle.vehicle_type}
                  </Text>
                </Pressable>
              ))}
            </View>
          ) : (
            <Pressable
              accessibilityRole="link"
              onPress={() => router.push("/profile")}
            >
              <Text style={styles.back}>Add a vehicle to continue →</Text>
            </Pressable>
          )}
        </View>
        <View style={styles.priceRow}>
          <Text style={styles.address}>Estimated total</Text>
          <Text style={styles.price}>
            ₹{Math.ceil((lot.data.base_rate_paise * duration) / 60 / 100)}
          </Text>
        </View>
        <PrimaryButton
          accessibilityHint="Opens the final quote and reservation details"
          disabled={!selectedVehicle}
          label="Review reservation"
          onPress={() =>
            router.push({
              pathname: "/review",
              params: {
                lotId: id,
                vehicleId: selectedVehicle,
                startsAt: startsAt.toISOString(),
                endsAt: endsAt.toISOString(),
                spotType,
              },
            })
          }
          testID="review-reservation-button"
        />
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: { padding: 22, gap: 20 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  error: { color: colors.red500 },
  back: { color: colors.cyan500, fontWeight: "700" },
  hero: { gap: 8, paddingVertical: 14 },
  eyebrow: { color: colors.green500, fontWeight: "800", letterSpacing: 0.6 },
  title: {
    color: colors.paper50,
    fontSize: 34,
    fontWeight: "900",
    letterSpacing: -1.2,
  },
  address: { color: colors.paper300, fontSize: 15, lineHeight: 22 },
  card: {
    backgroundColor: colors.ink900,
    borderColor: colors.ink700,
    borderWidth: 1,
    borderRadius: 18,
    padding: 18,
    gap: 13,
  },
  sectionTitle: { color: colors.paper300, fontWeight: "700", marginTop: 4 },
  time: { color: colors.paper50, fontSize: 20, fontWeight: "800" },
  stepperRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
  },
  stepperActions: { flexDirection: "row", gap: 8 },
  stepperButton: {
    width: 42,
    height: 42,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.ink600,
    alignItems: "center",
    justifyContent: "center",
  },
  stepperButtonText: { color: colors.cyan500, fontSize: 22, fontWeight: "900" },
  durationStepper: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
  },
  durationValue: { color: colors.paper50, fontWeight: "800", flex: 1 },
  options: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  option: {
    borderWidth: 1,
    borderColor: colors.ink600,
    borderRadius: 999,
    paddingVertical: 9,
    paddingHorizontal: 13,
  },
  optionActive: { borderColor: colors.cyan500, backgroundColor: "#063B49" },
  optionText: { color: colors.paper300, fontWeight: "700" },
  optionTextActive: { color: colors.cyan500, fontWeight: "800" },
  vehicleList: { gap: 8 },
  vehicle: {
    borderWidth: 1,
    borderColor: colors.ink600,
    borderRadius: 12,
    padding: 13,
  },
  vehicleActive: { borderColor: colors.cyan500 },
  vehicleName: { color: colors.paper50, fontWeight: "800" },
  vehicleMeta: { color: colors.paper300, marginTop: 3 },
  priceRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  price: { color: colors.paper50, fontSize: 26, fontWeight: "900" },
});
