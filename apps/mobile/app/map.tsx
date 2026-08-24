import type { ParkingLotSummary } from "@parkingpro/api-contracts";
import { colors } from "@parkingpro/design-tokens";
import Mapbox from "@rnmapbox/maps";
import { useQuery } from "@tanstack/react-query";
import Constants from "expo-constants";
import * as Location from "expo-location";
import { router } from "expo-router";
import { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import Animated, { FadeInDown, FadeOutDown } from "react-native-reanimated";

import { apiRequest } from "../src/lib/api";
import { Brand, Screen } from "../src/ui/primitives";

const token =
  (Constants.expoConfig?.extra?.mapboxAccessToken as string | undefined) ?? "";
Mapbox.setAccessToken(token);

type SpotFilter = "" | "car" | "bike" | "ev" | "accessible";

function nextSlot() {
  const value = new Date(Date.now() + 30 * 60 * 1000);
  value.setSeconds(0, 0);
  value.setMinutes(value.getMinutes() < 30 ? 30 : 0);
  if (value.getMinutes() === 0) value.setHours(value.getHours() + 1);
  return value;
}

export default function MapScreen() {
  const [coordinates, setCoordinates] = useState<[number, number]>([
    77.5946, 12.9716,
  ]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [radiusM, setRadiusM] = useState(10_000);
  const [spotType, setSpotType] = useState<SpotFilter>("");
  const [arrivalOffsetMinutes, setArrivalOffsetMinutes] = useState(0);
  const [durationMinutes, setDurationMinutes] = useState(60);
  const baseSlot = useMemo(() => nextSlot(), []);
  const startsAt = useMemo(
    () => new Date(baseSlot.getTime() + arrivalOffsetMinutes * 60_000),
    [arrivalOffsetMinutes, baseSlot],
  );
  const endsAt = useMemo(
    () => new Date(startsAt.getTime() + durationMinutes * 60_000),
    [durationMinutes, startsAt],
  );

  useEffect(() => {
    void Location.requestForegroundPermissionsAsync().then(
      async ({ granted }) => {
        if (!granted) return;
        const location = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.Balanced,
        });
        setCoordinates([location.coords.longitude, location.coords.latitude]);
      },
    );
  }, []);

  const lots = useQuery({
    queryKey: [
      "lots",
      coordinates[0].toFixed(3),
      coordinates[1].toFixed(3),
      radiusM,
      startsAt.toISOString(),
      endsAt.toISOString(),
      spotType,
    ],
    queryFn: () =>
      apiRequest<ParkingLotSummary[]>(
        `/api/v1/lots?longitude=${coordinates[0]}&latitude=${coordinates[1]}&radius_m=${radiusM}&starts_at=${encodeURIComponent(startsAt.toISOString())}&ends_at=${encodeURIComponent(endsAt.toISOString())}${spotType ? `&spot_type=${spotType}` : ""}`,
        {},
        { retries: 3 },
      ),
    refetchInterval: 10_000,
  });
  const visibleLots = useMemo(() => {
    const normalized = search.trim().toLocaleLowerCase();
    if (!normalized) return lots.data;
    return lots.data?.filter((lot) =>
      `${lot.name} ${lot.address}`.toLocaleLowerCase().includes(normalized),
    );
  }, [lots.data, search]);
  const selected = useMemo(
    () => visibleLots?.find((lot) => lot.id === selectedId) ?? visibleLots?.[0],
    [selectedId, visibleLots],
  );

  return (
    <Screen>
      <View style={styles.header}>
        <View style={styles.brandRow}>
          <Brand />
          <View style={styles.nav}>
            <Pressable
              accessibilityLabel="Active reservation"
              accessibilityRole="button"
              onPress={() => router.push("/active")}
            >
              <Text style={styles.navText}>Active</Text>
            </Pressable>
            <Pressable
              accessibilityLabel="Reservation history"
              accessibilityRole="button"
              onPress={() => router.push("/history")}
            >
              <Text style={styles.navText}>Trips</Text>
            </Pressable>
            <Pressable
              accessibilityLabel="Vehicles and profile"
              accessibilityRole="button"
              onPress={() => router.push("/profile")}
            >
              <Text style={styles.navText}>Profile</Text>
            </Pressable>
          </View>
        </View>
        <TextInput
          accessibilityLabel="Destination"
          accessibilityHint="Filters facilities by name or address"
          placeholder="Where are you going?"
          placeholderTextColor={colors.paper300}
          style={styles.search}
          value={search}
          onChangeText={setSearch}
        />
        <Pressable
          accessibilityLabel="Parking search filters"
          accessibilityRole="button"
          accessibilityState={{ expanded: filtersOpen }}
          onPress={() => setFiltersOpen((value) => !value)}
          style={styles.filterTrigger}
          testID="parking-filter-button"
        >
          <Text style={styles.filterTriggerText}>
            Filters · {radiusM / 1000} km · {durationMinutes / 60} hr
            {spotType ? ` · ${spotType.toUpperCase()}` : " · Any spot"}
          </Text>
          <Text style={styles.filterTriggerIcon}>
            {filtersOpen ? "−" : "+"}
          </Text>
        </Pressable>
        {filtersOpen ? (
          <Animated.View
            entering={FadeInDown.springify().damping(20)}
            exiting={FadeOutDown.duration(140)}
            style={styles.filterSheet}
          >
            <Text style={styles.filterLabel}>Search radius</Text>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.filterOptions}
            >
              {[2_000, 5_000, 10_000, 50_000].map((value) => (
                <Pressable
                  accessibilityRole="radio"
                  accessibilityState={{ checked: radiusM === value }}
                  key={value}
                  onPress={() => setRadiusM(value)}
                  style={[
                    styles.filterPill,
                    radiusM === value && styles.filterPillActive,
                  ]}
                >
                  <Text style={styles.filterPillText}>{value / 1000} km</Text>
                </Pressable>
              ))}
            </ScrollView>
            <Text style={styles.filterLabel}>Spot type</Text>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.filterOptions}
            >
              {(["", "car", "bike", "ev", "accessible"] as SpotFilter[]).map(
                (value) => (
                  <Pressable
                    accessibilityRole="radio"
                    accessibilityState={{ checked: spotType === value }}
                    key={value || "any"}
                    onPress={() => setSpotType(value)}
                    style={[
                      styles.filterPill,
                      spotType === value && styles.filterPillActive,
                    ]}
                  >
                    <Text style={styles.filterPillText}>
                      {value ? value.toUpperCase() : "ANY"}
                    </Text>
                  </Pressable>
                ),
              )}
            </ScrollView>
            <View style={styles.stepperRow}>
              <View style={styles.stepperCopy}>
                <Text style={styles.filterLabel}>Arrival</Text>
                <Text style={styles.stepperValue}>
                  {startsAt.toLocaleString([], {
                    weekday: "short",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </Text>
              </View>
              <View style={styles.stepperActions}>
                <Pressable
                  accessibilityLabel="Move arrival 30 minutes earlier"
                  accessibilityRole="button"
                  accessibilityState={{ disabled: arrivalOffsetMinutes === 0 }}
                  disabled={arrivalOffsetMinutes === 0}
                  onPress={() =>
                    setArrivalOffsetMinutes((value) => Math.max(0, value - 30))
                  }
                  style={styles.stepperButton}
                >
                  <Text style={styles.stepperButtonText}>−</Text>
                </Pressable>
                <Pressable
                  accessibilityLabel="Move arrival 30 minutes later"
                  accessibilityRole="button"
                  onPress={() =>
                    setArrivalOffsetMinutes((value) =>
                      Math.min(7 * 24 * 60, value + 30),
                    )
                  }
                  style={styles.stepperButton}
                >
                  <Text style={styles.stepperButtonText}>+</Text>
                </Pressable>
              </View>
            </View>
            <View style={styles.stepperRow}>
              <View style={styles.stepperCopy}>
                <Text style={styles.filterLabel}>Duration</Text>
                <Text style={styles.stepperValue}>
                  {durationMinutes < 60
                    ? "30 min"
                    : `${durationMinutes / 60} hr`}
                </Text>
              </View>
              <View style={styles.stepperActions}>
                <Pressable
                  accessibilityLabel="Reduce duration by 30 minutes"
                  accessibilityRole="button"
                  accessibilityState={{ disabled: durationMinutes === 30 }}
                  disabled={durationMinutes === 30}
                  onPress={() =>
                    setDurationMinutes((value) => Math.max(30, value - 30))
                  }
                  style={styles.stepperButton}
                >
                  <Text style={styles.stepperButtonText}>−</Text>
                </Pressable>
                <Pressable
                  accessibilityLabel="Increase duration by 30 minutes"
                  accessibilityRole="button"
                  accessibilityState={{ disabled: durationMinutes === 1_440 }}
                  disabled={durationMinutes === 1_440}
                  onPress={() =>
                    setDurationMinutes((value) => Math.min(1_440, value + 30))
                  }
                  style={styles.stepperButton}
                >
                  <Text style={styles.stepperButtonText}>+</Text>
                </Pressable>
              </View>
            </View>
            <Pressable
              accessibilityRole="button"
              onPress={() => setFiltersOpen(false)}
              style={styles.applyFilters}
            >
              <Text style={styles.applyFiltersText}>
                Show {visibleLots?.length ?? 0} available facilities
              </Text>
            </Pressable>
          </Animated.View>
        ) : null}
      </View>
      <View
        style={styles.map}
        accessibilityLabel="Map of Bengaluru demo parking facilities"
      >
        {!token ? (
          <View style={styles.mapMessage}>
            <Text style={styles.error}>
              Set EXPO_PUBLIC_MAPBOX_ACCESS_TOKEN to load the map.
            </Text>
          </View>
        ) : (
          <Mapbox.MapView
            style={StyleSheet.absoluteFill}
            styleURL={Mapbox.StyleURL.Dark}
            logoEnabled={false}
            attributionEnabled={false}
          >
            <Mapbox.Camera
              centerCoordinate={coordinates}
              zoomLevel={12.5}
              animationMode="flyTo"
            />
            <Mapbox.PointAnnotation
              id="current-location"
              coordinate={coordinates}
            >
              <View style={styles.currentLocation} />
            </Mapbox.PointAnnotation>
            {visibleLots?.map((lot) => (
              <Mapbox.PointAnnotation
                key={lot.id}
                id={lot.id}
                coordinate={[lot.longitude, lot.latitude]}
                onSelected={() => setSelectedId(lot.id)}
              >
                <View
                  style={selected?.id === lot.id ? styles.pin : styles.pinMuted}
                >
                  <Text style={styles.pinText}>P</Text>
                </View>
              </Mapbox.PointAnnotation>
            ))}
          </Mapbox.MapView>
        )}
        {lots.isLoading && (
          <ActivityIndicator
            style={styles.loader}
            size="large"
            color={colors.cyan500}
          />
        )}
        {lots.isError && (
          <Text accessibilityRole="alert" style={styles.floatingError}>
            Could not refresh facilities.
          </Text>
        )}
      </View>
      {selected ? (
        <Animated.View
          entering={FadeInDown.springify().damping(20)}
          style={styles.sheet}
        >
          <View style={styles.handle} />
          <Text style={styles.title}>{selected.name}</Text>
          <Text style={styles.meta}>{selected.address}</Text>
          <View style={styles.availability}>
            <Text style={styles.available}>
              ● {selected.available_spots} spots
            </Text>
            <Text style={styles.price}>
              ₹{Math.round(selected.base_rate_paise / 100)}/hr
            </Text>
          </View>
          <Pressable
            accessibilityHint={`Opens booking options for ${selected.name}`}
            accessibilityRole="button"
            onPress={() =>
              router.push({
                pathname: "/facility/[id]",
                params: {
                  id: selected.id,
                  startsAt: startsAt.toISOString(),
                  duration: String(durationMinutes),
                  spotType: spotType || "car",
                },
              })
            }
            style={styles.action}
            testID="choose-time-button"
          >
            <Text style={styles.actionText}>Choose a time</Text>
          </Pressable>
        </Animated.View>
      ) : lots.isSuccess ? (
        <View style={styles.emptySheet}>
          <Text style={styles.title}>No matching availability</Text>
          <Text style={styles.meta}>
            Expand the radius, change the time, or clear the destination search.
          </Text>
        </View>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { padding: 18, gap: 14, zIndex: 2 },
  brandRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  nav: { flexDirection: "row", gap: 18 },
  navText: { color: colors.paper300, fontWeight: "700" },
  search: {
    minHeight: 50,
    color: colors.paper50,
    backgroundColor: colors.ink800,
    borderColor: colors.ink600,
    borderWidth: 1,
    borderRadius: 14,
    paddingHorizontal: 16,
    fontSize: 16,
  },
  filterTrigger: {
    minHeight: 42,
    paddingHorizontal: 14,
    borderRadius: 12,
    backgroundColor: colors.ink900,
    borderWidth: 1,
    borderColor: colors.ink700,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  filterTriggerText: { color: colors.paper300, fontWeight: "700", flex: 1 },
  filterTriggerIcon: { color: colors.cyan500, fontSize: 22, fontWeight: "900" },
  filterSheet: {
    padding: 16,
    gap: 10,
    borderRadius: 16,
    backgroundColor: colors.ink900,
    borderWidth: 1,
    borderColor: colors.cyan500,
  },
  filterLabel: {
    color: colors.paper300,
    fontSize: 12,
    fontWeight: "800",
    letterSpacing: 0.5,
    textTransform: "uppercase",
  },
  filterOptions: { gap: 8 },
  filterPill: {
    minHeight: 38,
    paddingHorizontal: 13,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: colors.ink600,
    justifyContent: "center",
  },
  filterPillActive: { borderColor: colors.cyan500, backgroundColor: "#063B49" },
  filterPillText: { color: colors.paper50, fontWeight: "800" },
  stepperRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
  },
  stepperCopy: { flex: 1, gap: 3 },
  stepperValue: { color: colors.paper50, fontSize: 16, fontWeight: "800" },
  stepperActions: { flexDirection: "row", gap: 8 },
  stepperButton: {
    width: 40,
    height: 40,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.ink600,
    alignItems: "center",
    justifyContent: "center",
  },
  stepperButtonText: { color: colors.cyan500, fontSize: 22, fontWeight: "900" },
  applyFilters: {
    minHeight: 46,
    borderRadius: 12,
    backgroundColor: colors.cyan500,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 4,
  },
  applyFiltersText: { color: colors.ink950, fontWeight: "900" },
  map: {
    flex: 1,
    backgroundColor: "#0A141A",
    borderTopWidth: 1,
    borderColor: colors.ink700,
    overflow: "hidden",
  },
  mapMessage: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 30,
  },
  error: { color: colors.red500, textAlign: "center" },
  loader: { position: "absolute", alignSelf: "center", top: "45%" },
  floatingError: {
    position: "absolute",
    top: 12,
    alignSelf: "center",
    color: colors.paper50,
    backgroundColor: colors.red500,
    borderRadius: 8,
    padding: 8,
  },
  pin: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.cyan500,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 5,
    borderColor: "#06495B",
  },
  pinMuted: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.ink800,
    borderWidth: 1,
    borderColor: colors.paper300,
    alignItems: "center",
    justifyContent: "center",
  },
  pinText: { color: colors.paper50, fontSize: 16, fontWeight: "800" },
  currentLocation: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: colors.paper50,
    borderWidth: 4,
    borderColor: colors.cyan500,
  },
  sheet: {
    padding: 22,
    paddingTop: 12,
    gap: 8,
    backgroundColor: colors.ink900,
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    borderTopWidth: 1,
    borderColor: colors.ink700,
  },
  emptySheet: {
    padding: 22,
    gap: 8,
    backgroundColor: colors.ink900,
    borderTopWidth: 1,
    borderColor: colors.ink700,
  },
  handle: {
    width: 42,
    height: 5,
    borderRadius: 3,
    backgroundColor: colors.ink600,
    alignSelf: "center",
    marginBottom: 8,
  },
  title: {
    color: colors.paper50,
    fontSize: 26,
    fontWeight: "800",
    letterSpacing: -0.8,
  },
  meta: { color: colors.paper300, fontSize: 14 },
  availability: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginVertical: 12,
  },
  available: { color: colors.green500, fontSize: 19, fontWeight: "800" },
  price: { color: colors.paper50, fontSize: 22, fontWeight: "800" },
  action: {
    minHeight: 54,
    backgroundColor: colors.cyan500,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
  },
  actionText: { color: colors.ink950, fontSize: 17, fontWeight: "800" },
});
