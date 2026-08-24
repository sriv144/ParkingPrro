import { zodResolver } from "@hookform/resolvers/zod";
import { colors } from "@parkingpro/design-tokens";
import { Controller, useForm } from "react-hook-form";
import { router } from "expo-router";
import { useState } from "react";
import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { z } from "zod";

import { ApiError } from "../src/lib/api";
import { useAuthStore } from "../src/state/auth-store";
import { Brand, PrimaryButton, Screen } from "../src/ui/primitives";

const schema = z.object({
  email: z.email("Enter a valid email address."),
  password: z.string().min(1, "Enter your password."),
});
type FormData = z.infer<typeof schema>;

export default function SignInScreen() {
  const signIn = useAuthStore((state) => state.signIn);
  const demoSignIn = useAuthStore((state) => state.useDemo);
  const [serverError, setServerError] = useState("");
  const { control, handleSubmit, formState } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });

  async function submit(data: FormData) {
    setServerError("");
    try {
      await signIn(data.email, data.password);
      router.replace("/map");
    } catch (error) {
      setServerError(
        error instanceof ApiError ? error.message : "Could not sign in.",
      );
    }
  }

  async function demo() {
    setServerError("");
    try {
      await demoSignIn();
      router.replace("/map");
    } catch (error) {
      setServerError(
        error instanceof ApiError
          ? error.message
          : "Demo sign-in is unavailable.",
      );
    }
  }

  return (
    <Screen>
      <View style={styles.form}>
        <Brand />
        <View>
          <Text style={styles.eyebrow}>Driver account</Text>
          <Text accessibilityRole="header" style={styles.title}>
            Welcome back
          </Text>
        </View>
        <View style={styles.fields}>
          <Text style={styles.label}>Email</Text>
          <Controller
            control={control}
            name="email"
            render={({ field: { onBlur, onChange, value } }) => (
              <TextInput
                accessibilityLabel="Email"
                autoCapitalize="none"
                autoComplete="email"
                keyboardType="email-address"
                onBlur={onBlur}
                onChangeText={onChange}
                value={value}
                style={styles.input}
              />
            )}
          />
          {formState.errors.email && (
            <Text style={styles.error}>{formState.errors.email.message}</Text>
          )}
          <Text style={styles.label}>Password</Text>
          <Controller
            control={control}
            name="password"
            render={({ field: { onBlur, onChange, value } }) => (
              <TextInput
                accessibilityLabel="Password"
                autoComplete="current-password"
                onBlur={onBlur}
                onChangeText={onChange}
                secureTextEntry
                value={value}
                style={styles.input}
              />
            )}
          />
          {formState.errors.password && (
            <Text style={styles.error}>
              {formState.errors.password.message}
            </Text>
          )}
        </View>
        {serverError ? (
          <Text accessibilityRole="alert" style={styles.error}>
            {serverError}
          </Text>
        ) : null}
        <PrimaryButton
          disabled={formState.isSubmitting}
          label={formState.isSubmitting ? "Signing in…" : "Sign in"}
          onPress={() => void handleSubmit(submit)()}
        />
        <Pressable
          accessibilityRole="button"
          onPress={() => void demo()}
          style={styles.secondary}
        >
          <Text style={styles.secondaryText}>Use demo driver</Text>
        </Pressable>
        <Pressable
          accessibilityRole="link"
          onPress={() => router.push("/register")}
        >
          <Text style={styles.register}>
            New to ParkingPro? Create an account
          </Text>
        </Pressable>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  form: { flex: 1, padding: 28, justifyContent: "center", gap: 24 },
  eyebrow: {
    color: colors.cyan500,
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 1.6,
    textTransform: "uppercase",
  },
  title: {
    color: colors.paper50,
    fontSize: 34,
    fontWeight: "800",
    letterSpacing: -1.3,
    marginTop: 8,
  },
  fields: { gap: 8 },
  label: { color: colors.paper300, fontSize: 14, marginTop: 6 },
  input: {
    minHeight: 54,
    color: colors.paper50,
    backgroundColor: colors.ink800,
    borderColor: colors.ink600,
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
  },
  error: { color: colors.red500, lineHeight: 20 },
  secondary: { minHeight: 46, alignItems: "center", justifyContent: "center" },
  secondaryText: { color: colors.cyan500, fontSize: 16, fontWeight: "700" },
  register: {
    color: colors.paper300,
    textAlign: "center",
    textDecorationLine: "underline",
  },
});
