import { zodResolver } from "@hookform/resolvers/zod";
import { colors } from "@parkingpro/design-tokens";
import { Controller, useForm } from "react-hook-form";
import { router } from "expo-router";
import { useState } from "react";
import { ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { z } from "zod";

import { ApiError, apiRequest } from "../src/lib/api";
import { useAuthStore } from "../src/state/auth-store";
import { Brand, PrimaryButton, Screen } from "../src/ui/primitives";

const schema = z.object({
  full_name: z.string().min(2, "Enter your name."),
  email: z.email("Enter a valid email."),
  phone: z.string().max(24).optional(),
  password: z.string().min(10, "Use at least 10 characters."),
});
type FormData = z.infer<typeof schema>;

export default function RegisterScreen() {
  const signIn = useAuthStore((state) => state.signIn);
  const [serverError, setServerError] = useState("");
  const { control, handleSubmit, formState } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { full_name: "", email: "", phone: "", password: "" },
  });

  async function submit(data: FormData) {
    setServerError("");
    try {
      await apiRequest("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
      });
      await signIn(data.email, data.password);
      router.replace("/map");
    } catch (error) {
      setServerError(
        error instanceof ApiError
          ? error.message
          : "Could not create the account.",
      );
    }
  }

  return (
    <Screen>
      <ScrollView
        contentContainerStyle={styles.form}
        keyboardShouldPersistTaps="handled"
      >
        <Brand />
        <View>
          <Text style={styles.eyebrow}>Driver registration</Text>
          <Text style={styles.title}>Create your account</Text>
          <Text style={styles.body}>
            Operator privileges can only be issued from the server CLI.
          </Text>
        </View>
        {(["full_name", "email", "phone", "password"] as const).map((name) => (
          <View key={name} style={styles.field}>
            <Text style={styles.label}>
              {
                {
                  full_name: "Full name",
                  email: "Email",
                  phone: "Phone",
                  password: "Password",
                }[name]
              }
            </Text>
            <Controller
              control={control}
              name={name}
              render={({ field: { onBlur, onChange, value } }) => (
                <TextInput
                  accessibilityLabel={name}
                  autoCapitalize={name === "email" ? "none" : "sentences"}
                  keyboardType={
                    name === "email"
                      ? "email-address"
                      : name === "phone"
                        ? "phone-pad"
                        : "default"
                  }
                  onBlur={onBlur}
                  onChangeText={onChange}
                  secureTextEntry={name === "password"}
                  style={styles.input}
                  value={value}
                />
              )}
            />
            {formState.errors[name] && (
              <Text style={styles.error}>
                {formState.errors[name]?.message}
              </Text>
            )}
          </View>
        ))}
        {serverError ? (
          <Text accessibilityRole="alert" style={styles.error}>
            {serverError}
          </Text>
        ) : null}
        <PrimaryButton
          disabled={formState.isSubmitting}
          label="Create account"
          onPress={() => void handleSubmit(submit)()}
        />
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  form: { padding: 28, gap: 18 },
  eyebrow: {
    color: colors.cyan500,
    fontWeight: "800",
    letterSpacing: 1.4,
    textTransform: "uppercase",
  },
  title: {
    color: colors.paper50,
    fontSize: 31,
    fontWeight: "800",
    marginTop: 8,
  },
  body: { color: colors.paper300, lineHeight: 22, marginTop: 8 },
  field: { gap: 7 },
  label: { color: colors.paper300 },
  input: {
    minHeight: 52,
    borderWidth: 1,
    borderColor: colors.ink600,
    borderRadius: 12,
    backgroundColor: colors.ink800,
    color: colors.paper50,
    paddingHorizontal: 15,
    fontSize: 16,
  },
  error: { color: colors.red500 },
});
