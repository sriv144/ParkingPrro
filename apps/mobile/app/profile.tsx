import type { Vehicle } from "@parkingpro/api-contracts";
import { colors } from "@parkingpro/design-tokens";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { router } from "expo-router";
import { useState } from "react";
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { apiRequest } from "../src/lib/api";
import { useAuthStore } from "../src/state/auth-store";
import { PrimaryButton, Screen } from "../src/ui/primitives";

export default function ProfileScreen() {
  const user = useAuthStore((state) => state.user);
  const signOut = useAuthStore((state) => state.signOut);
  const queryClient = useQueryClient();
  const [registration, setRegistration] = useState("");
  const [label, setLabel] = useState("");
  const [vehicleType, setVehicleType] =
    useState<Vehicle["vehicle_type"]>("car");
  const [editing, setEditing] = useState<Vehicle | null>(null);
  const [editRegistration, setEditRegistration] = useState("");
  const [editLabel, setEditLabel] = useState("");
  const [editType, setEditType] = useState<Vehicle["vehicle_type"]>("car");
  const vehicles = useQuery({
    queryKey: ["vehicles"],
    queryFn: () => apiRequest<Vehicle[]>("/api/v1/vehicles"),
  });
  const createVehicle = useMutation({
    mutationFn: () =>
      apiRequest<Vehicle>("/api/v1/vehicles", {
        method: "POST",
        body: JSON.stringify({
          registration_number: registration,
          vehicle_type: vehicleType,
          label: label || null,
        }),
      }),
    onSuccess: async () => {
      setRegistration("");
      setLabel("");
      setVehicleType("car");
      await queryClient.invalidateQueries({ queryKey: ["vehicles"] });
    },
  });
  const updateVehicle = useMutation({
    mutationFn: (id: string) =>
      apiRequest<Vehicle>(`/api/v1/vehicles/${id}`, {
        method: "PATCH",
        body: JSON.stringify({
          registration_number: editRegistration,
          vehicle_type: editType,
          label: editLabel || null,
        }),
      }),
    onSuccess: async () => {
      setEditing(null);
      await queryClient.invalidateQueries({ queryKey: ["vehicles"] });
    },
  });
  const removeVehicle = useMutation({
    mutationFn: (id: string) =>
      apiRequest(`/api/v1/vehicles/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["vehicles"] }),
  });

  return (
    <Screen>
      <ScrollView contentContainerStyle={styles.content}>
        <Pressable
          accessibilityLabel="Back to parking map"
          accessibilityRole="button"
          onPress={() => router.back()}
        >
          <Text style={styles.back}>← Map</Text>
        </Pressable>
        <Text style={styles.title}>Vehicles & profile</Text>
        <View style={styles.profile}>
          <Text style={styles.name}>{user?.full_name}</Text>
          <Text style={styles.meta}>{user?.email}</Text>
        </View>
        <Text style={styles.section}>Your vehicles</Text>
        <View style={styles.vehicles}>
          {vehicles.data?.map((item) => (
            <View key={item.id} style={styles.vehicle}>
              <View>
                <Text style={styles.vehicleName}>{item.label}</Text>
                <Text style={styles.meta}>
                  {item.registration_number} · {item.vehicle_type}
                </Text>
              </View>
              <View style={styles.vehicleActions}>
                <Pressable
                  accessibilityLabel={`Edit vehicle ${item.registration_number}`}
                  accessibilityRole="button"
                  onPress={() => {
                    setEditing(item);
                    setEditRegistration(item.registration_number);
                    setEditLabel(item.label ?? "");
                    setEditType(item.vehicle_type);
                  }}
                >
                  <Text style={styles.edit}>Edit</Text>
                </Pressable>
                <Pressable
                  accessibilityLabel={`Remove vehicle ${item.registration_number}`}
                  accessibilityRole="button"
                  onPress={() => removeVehicle.mutate(item.id)}
                >
                  <Text style={styles.remove}>Remove</Text>
                </Pressable>
              </View>
            </View>
          ))}
        </View>
        {editing ? (
          <View style={styles.editor}>
            <Text style={styles.section}>Edit vehicle</Text>
            <TextInput
              autoCapitalize="characters"
              accessibilityLabel="Edit vehicle registration"
              style={styles.input}
              value={editRegistration}
              onChangeText={setEditRegistration}
            />
            <TextInput
              accessibilityLabel="Edit vehicle label"
              placeholder="Optional label"
              placeholderTextColor={colors.ink600}
              style={styles.input}
              value={editLabel}
              onChangeText={setEditLabel}
            />
            <View style={styles.typeOptions}>
              {(["car", "bike", "ev", "accessible"] as const).map((type) => (
                <Pressable
                  accessibilityLabel={`Set edited vehicle type to ${type}`}
                  accessibilityRole="radio"
                  accessibilityState={{ checked: editType === type }}
                  key={type}
                  onPress={() => setEditType(type)}
                  style={[
                    styles.typeOption,
                    editType === type && styles.typeOptionActive,
                  ]}
                >
                  <Text style={styles.typeOptionText}>
                    {type.toUpperCase()}
                  </Text>
                </Pressable>
              ))}
            </View>
            <PrimaryButton
              disabled={editRegistration.length < 4 || updateVehicle.isPending}
              label={
                updateVehicle.isPending ? "Saving vehicle…" : "Save vehicle"
              }
              onPress={() => updateVehicle.mutate(editing.id)}
            />
            <Pressable
              accessibilityRole="button"
              onPress={() => setEditing(null)}
              style={styles.cancelEdit}
            >
              <Text style={styles.back}>Cancel edit</Text>
            </Pressable>
          </View>
        ) : null}
        <View style={styles.add}>
          <TextInput
            autoCapitalize="characters"
            accessibilityLabel="Vehicle registration"
            placeholder="KA01AB1234"
            placeholderTextColor={colors.ink600}
            style={styles.input}
            value={registration}
            onChangeText={setRegistration}
          />
          <TextInput
            accessibilityLabel="Vehicle label"
            placeholder="Optional label, for example Daily car"
            placeholderTextColor={colors.ink600}
            style={styles.input}
            value={label}
            onChangeText={setLabel}
          />
          <View style={styles.typeOptions}>
            {(["car", "bike", "ev", "accessible"] as const).map((type) => (
              <Pressable
                accessibilityLabel={`New vehicle type ${type}`}
                accessibilityRole="radio"
                accessibilityState={{ checked: vehicleType === type }}
                key={type}
                onPress={() => setVehicleType(type)}
                style={[
                  styles.typeOption,
                  vehicleType === type && styles.typeOptionActive,
                ]}
              >
                <Text style={styles.typeOptionText}>{type.toUpperCase()}</Text>
              </Pressable>
            ))}
          </View>
          <PrimaryButton
            disabled={registration.length < 4 || createVehicle.isPending}
            label="Add vehicle"
            onPress={() => createVehicle.mutate()}
          />
        </View>
        <Pressable
          accessibilityRole="button"
          onPress={async () => {
            await signOut();
            router.replace("/sign-in");
          }}
          style={styles.signOut}
        >
          <Text style={styles.remove}>Sign out securely</Text>
        </Pressable>
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: { padding: 22, paddingBottom: 48, gap: 18 },
  back: { color: colors.cyan500, fontWeight: "800" },
  title: { color: colors.paper50, fontSize: 31, fontWeight: "900" },
  profile: {
    backgroundColor: colors.ink900,
    borderWidth: 1,
    borderColor: colors.ink700,
    borderRadius: 16,
    padding: 18,
  },
  name: { color: colors.paper50, fontSize: 20, fontWeight: "800" },
  meta: { color: colors.paper300, marginTop: 4 },
  section: { color: colors.paper50, fontWeight: "800", fontSize: 17 },
  vehicles: { gap: 2 },
  vehicle: {
    borderBottomWidth: 1,
    borderColor: colors.ink700,
    paddingVertical: 13,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  vehicleName: { color: colors.paper50, fontWeight: "800" },
  vehicleActions: { flexDirection: "row", gap: 14 },
  edit: { color: colors.cyan500, fontWeight: "800" },
  remove: { color: colors.red500, fontWeight: "800" },
  add: { gap: 10 },
  editor: {
    gap: 10,
    borderWidth: 1,
    borderColor: colors.cyan500,
    borderRadius: 14,
    padding: 14,
    backgroundColor: colors.ink900,
  },
  typeOptions: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  typeOption: {
    minHeight: 38,
    borderWidth: 1,
    borderColor: colors.ink600,
    borderRadius: 999,
    paddingHorizontal: 12,
    alignItems: "center",
    justifyContent: "center",
  },
  typeOptionActive: { borderColor: colors.cyan500, backgroundColor: "#063B49" },
  typeOptionText: { color: colors.paper50, fontSize: 12, fontWeight: "800" },
  cancelEdit: { alignItems: "center", padding: 6 },
  input: {
    minHeight: 52,
    borderWidth: 1,
    borderColor: colors.ink600,
    borderRadius: 12,
    color: colors.paper50,
    backgroundColor: colors.ink800,
    paddingHorizontal: 15,
    fontSize: 17,
  },
  signOut: { alignItems: "center", padding: 12 },
});
