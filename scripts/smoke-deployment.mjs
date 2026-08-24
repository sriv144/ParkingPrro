const apiUrl = process.env.PARKINGPRO_API_URL?.replace(/\/$/, "");
const webUrl = process.env.PARKINGPRO_WEB_URL?.replace(/\/$/, "");
const email = process.env.PARKINGPRO_DEMO_DRIVER_EMAIL;
const password = process.env.PARKINGPRO_DEMO_DRIVER_PASSWORD;

if (!apiUrl || !webUrl || !email || !password) {
  throw new Error(
    "Deployment smoke-test URLs and demo driver credentials are required.",
  );
}

async function request(path, init = {}) {
  const response = await fetch(`${apiUrl}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...init.headers,
    },
  });
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return response.json();
}

async function waitUntilReady() {
  let lastError;
  for (let attempt = 1; attempt <= 30; attempt += 1) {
    try {
      const ready = await request("/health/ready");
      if (ready.status === "ready") return;
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, 10_000));
  }
  throw lastError ?? new Error("API did not become ready within five minutes.");
}

await waitUntilReady();
const live = await request("/health/live");
if (live.service !== "parkingpro-api")
  throw new Error("Unexpected live-check payload.");

const session = await request("/api/v1/auth/login", {
  method: "POST",
  body: JSON.stringify({
    email,
    password,
    client_type: "mobile",
    device_name: "post-deployment-smoke",
  }),
});
const authorization = { Authorization: `Bearer ${session.access_token}` };
const lots = await request(
  "/api/v1/lots?latitude=12.9716&longitude=77.5946&radius_m=50000",
  {
    headers: authorization,
  },
);
if (!Array.isArray(lots) || lots.length < 5) {
  throw new Error("Expected at least five seeded Bengaluru facilities.");
}

const forbidden = await fetch(`${apiUrl}/api/v1/operator/overview`, {
  headers: { Accept: "application/json", ...authorization },
});
if (forbidden.status !== 403)
  throw new Error("Driver role-isolation smoke test failed.");

const web = await fetch(webUrl, { redirect: "follow" });
if (!web.ok || !(await web.text()).includes("ParkingPro Operator")) {
  throw new Error("Operator console smoke test failed.");
}

console.log(
  `Deployment smoke test passed for API ${live.version}, ${lots.length} facilities.`,
);
