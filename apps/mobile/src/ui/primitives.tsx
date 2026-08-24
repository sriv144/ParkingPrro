import type { PropsWithChildren } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { colors } from "@parkingpro/design-tokens";

export function Screen({ children }: PropsWithChildren) {
  return <SafeAreaView style={styles.screen}>{children}</SafeAreaView>;
}

export function Brand() {
  return (
    <Text accessibilityRole="header" style={styles.brand}>
      Parking<Text style={styles.accent}>Pro</Text>
    </Text>
  );
}

export function PrimaryButton({
  label,
  onPress,
  disabled = false,
  accessibilityHint,
  testID,
}: {
  label: string;
  onPress(): void;
  disabled?: boolean;
  accessibilityHint?: string;
  testID?: string;
}) {
  return (
    <Pressable
      accessibilityHint={accessibilityHint}
      accessibilityRole="button"
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.primary,
        disabled && styles.disabled,
        pressed && styles.pressed,
      ]}
      testID={testID}
    >
      <Text style={styles.primaryText}>{label}</Text>
    </Pressable>
  );
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <View style={styles.empty}>
      <Text style={styles.emptyTitle}>{title}</Text>
      <Text style={styles.emptyBody}>{body}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.ink950 },
  brand: {
    color: colors.paper50,
    fontSize: 26,
    fontWeight: "800",
    letterSpacing: -1,
  },
  accent: { color: colors.cyan500 },
  primary: {
    minHeight: 54,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.cyan500,
    borderRadius: 12,
    paddingHorizontal: 20,
  },
  disabled: { opacity: 0.45 },
  pressed: { opacity: 0.75 },
  primaryText: { color: colors.ink950, fontSize: 16, fontWeight: "800" },
  empty: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 28,
    gap: 8,
  },
  emptyTitle: {
    color: colors.paper50,
    fontSize: 21,
    fontWeight: "800",
    textAlign: "center",
  },
  emptyBody: {
    color: colors.paper300,
    fontSize: 15,
    lineHeight: 22,
    textAlign: "center",
  },
});
