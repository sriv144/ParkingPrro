// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from "vitest";

import { csrfToken, setCsrfToken, wakeService } from "./api";

describe("web session CSRF state", () => {
  beforeEach(() => sessionStorage.clear());

  it("uses tab-scoped storage rather than localStorage", () => {
    setCsrfToken("csrf-value");
    expect(csrfToken()).toBe("csrf-value");
    setCsrfToken(null);
    expect(csrfToken()).toBe("");
  });

  it("checks service health before enabling operator actions", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal("fetch", fetchMock);

    await expect(wakeService()).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:5000/health/live",
      expect.objectContaining({ headers: { Accept: "application/json" } }),
    );

    vi.unstubAllGlobals();
  });
});
