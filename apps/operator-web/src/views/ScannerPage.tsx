import type { Reservation } from "@parkingpro/api-contracts";
import { useQueryClient } from "@tanstack/react-query";
import { BrowserQRCodeReader } from "@zxing/browser";
import { ScanLine } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

import { ApiError, apiRequest } from "../lib/api";

export function ScannerPage() {
  const queryClient = useQueryClient();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [manual, setManual] = useState("");
  const [reservation, setReservation] = useState<Reservation | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const validate = useCallback(
    async (value: string) => {
      if (!value || busy) return;
      setBusy(true);
      setError("");
      try {
        setReservation(
          await apiRequest<Reservation>("/api/v1/operator/scan", {
            method: "POST",
            body: JSON.stringify({ qr_payload: value }),
          }),
        );
        setCameraOn(false);
      } catch (caught) {
        setError(
          caught instanceof ApiError
            ? caught.message
            : "The pass could not be validated.",
        );
      } finally {
        setBusy(false);
      }
    },
    [busy],
  );

  useEffect(() => {
    if (!cameraOn || !videoRef.current) return;
    const reader = new BrowserQRCodeReader();
    let active = true;
    let controls: { stop(): void } | undefined;
    void reader
      .decodeFromVideoDevice(undefined, videoRef.current, (result) => {
        if (active && result) void validate(result.getText());
      })
      .then((value) => {
        controls = value;
      })
      .catch(() =>
        setError("Camera access failed. Use the manual code fallback."),
      );
    return () => {
      active = false;
      controls?.stop();
    };
  }, [cameraOn, validate]);

  async function checkIn() {
    if (!reservation) return;
    setBusy(true);
    try {
      const checkedIn = await apiRequest<Reservation>(
        `/api/v1/operator/reservations/${reservation.id}/check-in`,
        { method: "POST" },
      );
      setReservation(checkedIn);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["operator", "overview"] }),
        queryClient.invalidateQueries({ queryKey: ["operator", "lots"] }),
        queryClient.invalidateQueries({
          queryKey: ["operator", "reservations"],
        }),
      ]);
    } catch (caught) {
      setError(
        caught instanceof ApiError ? caught.message : "Check-in failed.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="page scanner-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Secure gate workflow</p>
          <h1>Scan parking pass</h1>
        </div>
      </div>
      <div className="scanner-grid">
        <section className="scanner-stage">
          {cameraOn ? (
            <video ref={videoRef} muted playsInline />
          ) : (
            <div className="camera-placeholder">
              <ScanLine size={72} />
              <p>Camera starts only after operator consent.</p>
            </div>
          )}
          <button
            className="secondary-action"
            type="button"
            onClick={() => setCameraOn((value) => !value)}
          >
            {cameraOn ? "Stop camera" : "Start camera scanner"}
          </button>
        </section>
        <aside className="inspector">
          <p className="eyebrow">Manual fallback</p>
          <label>
            Signed QR code
            <textarea
              value={manual}
              onChange={(event) => setManual(event.target.value)}
              rows={4}
            />
          </label>
          <button
            className="primary-action"
            disabled={!manual || busy}
            type="button"
            onClick={() => void validate(manual)}
          >
            Validate pass
          </button>
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}
          {reservation && (
            <div className="pass-result">
              <p className="success">VALID PASS</p>
              <h2>{reservation.registration_number}</h2>
              <p>
                {reservation.lot_name} · Spot {reservation.spot_code}
              </p>
              <p>{new Date(reservation.starts_at).toLocaleString()}</p>
              <button
                className="primary-action"
                disabled={reservation.status !== "confirmed" || busy}
                onClick={() => void checkIn()}
              >
                {reservation.status === "confirmed"
                  ? "Check vehicle in"
                  : reservation.status.replace("_", " ")}
              </button>
            </div>
          )}
        </aside>
      </div>
    </section>
  );
}
