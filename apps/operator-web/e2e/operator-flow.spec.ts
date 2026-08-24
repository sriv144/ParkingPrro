import { expect, test } from "@playwright/test";

const lotId = "11111111-1111-4111-8111-111111111111";
const spotId = "22222222-2222-4222-8222-222222222222";
const reservationId = "33333333-3333-4333-8333-333333333333";

test("operator completes inventory, scan, check-in, checkout, and reporting flows", async ({
  page,
}) => {
  let reservationStatus = "confirmed";
  let spotState = "active";
  let spotPatchCount = 0;
  let lotName = "Marina Central";
  let lotPatchCount = 0;

  await page.route("http://localhost:5000/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    const method = request.method();
    const lot = {
      id: lotId,
      name: lotName,
      address: "MG Road",
      latitude: 12.97,
      longitude: 77.6,
      distance_m: null,
      timezone: "Asia/Kolkata",
      opens_at: "00:00",
      closes_at: "23:59",
      base_rate_paise: 6000,
      state: "active",
      total_spots: 24,
      available_spots: reservationStatus === "completed" ? 24 : 23,
    };
    const reservation = {
      id: reservationId,
      lot_id: lotId,
      lot_name: lot.name,
      spot_code: "A-01",
      vehicle_id: "44444444-4444-4444-8444-444444444444",
      registration_number: "KA01PP2026",
      starts_at: "2026-08-22T04:30:00Z",
      ends_at: "2026-08-22T05:30:00Z",
      quoted_amount_paise: 6000,
      status: reservationStatus,
      hold_expires_at: null,
      qr_payload: null,
    };
    let body: unknown = {};

    if (path === "/api/v1/auth/login") {
      body = {
        access_token: "demo-token",
        refresh_token: null,
        csrf_token: "demo-csrf",
        expires_in: 900,
        user: {
          id: "55555555-5555-4555-8555-555555555555",
          email: "operator@parkingpro.demo",
          full_name: "Demo Operator",
          phone: null,
          role: "operator",
        },
      };
    } else if (path === "/api/v1/operator/overview") {
      body = {
        occupied_spots: reservationStatus === "checked_in" ? 1 : 0,
        total_spots: 24,
        occupancy_percent: reservationStatus === "checked_in" ? 4.2 : 0,
        active_reservations: reservationStatus === "completed" ? 0 : 1,
        revenue_today_paise: 6000,
        completed_today: reservationStatus === "completed" ? 1 : 0,
      };
    } else if (path === "/api/v1/operator/lots") {
      body = [lot];
    } else if (
      path === `/api/v1/operator/lots/${lotId}` &&
      method === "PATCH"
    ) {
      const update = request.postDataJSON() as { name: string };
      lotName = update.name;
      lotPatchCount += 1;
      body = { ...lot, name: lotName };
    } else if (path === `/api/v1/operator/lots/${lotId}/spots`) {
      body = [{ id: spotId, code: "A-01", spot_type: "car", state: spotState }];
    } else if (
      path === `/api/v1/operator/spots/${spotId}` &&
      method === "PATCH"
    ) {
      spotState = spotState === "active" ? "out_of_service" : "active";
      spotPatchCount += 1;
      body = { id: spotId, code: "A-01", spot_type: "car", state: spotState };
    } else if (path === "/api/v1/operator/scan" && method === "POST") {
      body = reservation;
    } else if (path.endsWith("/check-in") && method === "POST") {
      reservationStatus = "checked_in";
      body = { ...reservation, status: reservationStatus };
    } else if (path.endsWith("/check-out") && method === "POST") {
      reservationStatus = "completed";
      body = { ...reservation, status: reservationStatus };
    } else if (path === "/api/v1/operator/reservations") {
      body = [{ ...reservation, status: reservationStatus }];
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(body),
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: "Use demo operator" }).click();
  await expect(
    page.getByRole("heading", { name: "Occupancy overview" }),
  ).toBeVisible();
  await expect(page.getByText("Marina Central").first()).toBeVisible();

  await page.getByRole("link", { name: "Facilities", exact: true }).click();
  await page.getByRole("button", { name: /Marina Central/ }).click();
  const facilityEditor = page
    .getByRole("heading", { name: "Marina Central", exact: true })
    .locator("..");
  await facilityEditor.getByLabel("Name").fill("Marina Central Updated");
  await facilityEditor.getByRole("button", { name: "Save facility" }).click();
  await expect.poll(() => lotPatchCount).toBe(1);
  await expect(page.getByText("Facility settings saved.")).toBeVisible();
  await page.getByRole("button", { name: /A-01/ }).click();
  await expect.poll(() => spotPatchCount).toBe(1);

  await page.getByRole("link", { name: "Scanner" }).click();
  await page.getByLabel("Signed QR code").fill("signed-demo-parking-pass");
  await page.getByRole("button", { name: "Validate pass" }).click();
  await expect(page.getByText("VALID PASS")).toBeVisible();
  await page.getByRole("button", { name: "Check vehicle in" }).click();
  await expect(page.getByRole("button", { name: "checked in" })).toBeDisabled();

  await page.getByRole("link", { name: "Reservations" }).click();
  await expect(page.getByText("KA01PP2026")).toBeVisible();
  await page.getByRole("button", { name: "Check out" }).click();
  await expect(page.getByText("completed", { exact: true })).toBeVisible();

  await page.getByRole("link", { name: "Reports" }).click();
  await expect(
    page.getByRole("heading", { name: "Occupancy & revenue" }),
  ).toBeVisible();
  await expect(page.getByText("₹60", { exact: true })).toBeVisible();
});
