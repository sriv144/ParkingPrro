export const colors = {
  ink950: "#050B0F",
  ink900: "#081117",
  ink800: "#111C22",
  ink700: "#26343C",
  ink600: "#46545D",
  paper50: "#F4F7F8",
  paper300: "#AEB9BF",
  cyan500: "#08C7F4",
  green500: "#2EDB84",
  amber500: "#F6B84A",
  red500: "#EF5B63",
} as const;

export const spacing = {
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 20,
  6: 24,
  8: 32,
  10: 40,
  12: 48,
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 18,
  pill: 999,
} as const;

export const motion = {
  fastMs: 140,
  standardMs: 220,
  deliberateMs: 360,
  easing: [0.2, 0.8, 0.2, 1],
} as const;
