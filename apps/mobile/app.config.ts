import type { ConfigContext, ExpoConfig } from "expo/config";

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: "ParkingPro",
  slug: "parkingpro",
  version: "0.1.0",
  orientation: "portrait",
  userInterfaceStyle: "dark",
  scheme: "parkingpro",
  android: {
    package: "com.sriv144.parkingpro",
    adaptiveIcon: {
      backgroundColor: "#050B0F",
    },
    permissions: [
      "ACCESS_COARSE_LOCATION",
      "ACCESS_FINE_LOCATION",
      "CAMERA",
      "POST_NOTIFICATIONS",
    ],
  },
  plugins: [
    "expo-router",
    "expo-splash-screen",
    "expo-status-bar",
    "expo-secure-store",
    [
      "expo-camera",
      {
        cameraPermission: "Allow ParkingPro operators to scan parking passes.",
      },
    ],
    [
      "expo-location",
      {
        locationWhenInUsePermission:
          "Allow ParkingPro to show nearby demo facilities.",
      },
    ],
    "expo-notifications",
    "@maplibre/maplibre-react-native",
  ],
  experiments: { typedRoutes: true },
  extra: {
    eas: {
      projectId: process.env.EXPO_PUBLIC_EAS_PROJECT_ID ?? "",
    },
    apiUrl: process.env.EXPO_PUBLIC_API_URL ?? "http://10.0.2.2:5000",
    razorpayKeyId: process.env.EXPO_PUBLIC_RAZORPAY_KEY_ID ?? "",
  },
});
