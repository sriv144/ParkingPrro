import { spawnSync } from "node:child_process";

const npmCli = process.env.npm_execpath;
if (!npmCli)
  throw new Error("npm_execpath is unavailable; run this check through npm.");
const result = spawnSync(
  process.execPath,
  [npmCli, "audit", "--omit=dev", "--json"],
  {
    encoding: "utf8",
    shell: false,
  },
);

if (!result.stdout) {
  process.stderr.write(result.stderr || "npm audit returned no report.\n");
  process.exit(1);
}

const report = JSON.parse(result.stdout);
const vulnerabilities = report.vulnerabilities ?? {};
const allowedPackages = new Set([
  // npm propagates Expo's reviewed build-time advisory to this direct native plugin.
  "@maplibre/maplibre-react-native",
  "@expo/cli",
  "@expo/config",
  "@expo/config-plugins",
  "@expo/inline-modules",
  "@expo/local-build-cache-provider",
  "@expo/metro",
  "@expo/metro-config",
  "@expo/prebuild-config",
  "expo",
  "expo-splash-screen",
  "image-size",
  "metro",
  "metro-config",
  "metro-transform-worker",
  "uuid",
  "xcode",
]);
const allowedAdvisories = new Set([1119441]);

const unexpectedPackages = Object.keys(vulnerabilities).filter(
  (name) => !allowedPackages.has(name),
);
const advisoryIds = new Set(
  Object.values(vulnerabilities)
    .flatMap((entry) => entry.via ?? [])
    .filter((via) => typeof via === "object")
    .map((via) => via.source),
);
const unexpectedAdvisories = [...advisoryIds].filter(
  (source) => !allowedAdvisories.has(source),
);
const missingReviewedAdvisories = [...allowedAdvisories].filter(
  (source) => !advisoryIds.has(source),
);

if (
  report.metadata?.vulnerabilities?.critical > 0 ||
  unexpectedPackages.length ||
  unexpectedAdvisories.length ||
  missingReviewedAdvisories.length
) {
  console.error("Dependency audit requires security review.", {
    unexpectedPackages,
    unexpectedAdvisories,
    missingReviewedAdvisories,
    totals: report.metadata?.vulnerabilities,
  });
  process.exit(1);
}

console.log(
  "Dependency audit contains only the reviewed Expo build-tool advisory documented in docs/security.md.",
);
