import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, CarFront } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { Navigate, useNavigate } from "react-router-dom";
import { z } from "zod";

import { ApiError, wakeService } from "../lib/api";
import { useAuth } from "../state/AuthContext";

const loginSchema = z.object({
  email: z.email("Enter a valid operator email."),
  password: z.string().min(8, "Password must contain at least 8 characters."),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginPage() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [demoBusy, setDemoBusy] = useState(false);
  const [serviceState, setServiceState] = useState<
    "checking" | "starting" | "ready" | "unavailable"
  >("checking");
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });
  const busy = demoBusy || isSubmitting;

  const connect = useCallback(async () => {
    setServiceState("checking");
    setError("");
    try {
      await wakeService(() => setServiceState("starting"));
      setServiceState("ready");
    } catch (caught) {
      setServiceState("unavailable");
      setError(
        caught instanceof ApiError
          ? caught.message
          : "The demo service is unavailable.",
      );
    }
  }, []);

  useEffect(() => {
    const task = window.setTimeout(() => void connect(), 0);
    return () => window.clearTimeout(task);
  }, [connect]);

  if (user) return <Navigate to="/app" replace />;

  async function submit(values: LoginForm) {
    setError("");
    try {
      await login(values.email, values.password);
      navigate("/app", { replace: true });
    } catch (caught) {
      setError(
        caught instanceof ApiError ? caught.message : "Could not sign in.",
      );
    }
  }

  async function demo() {
    setDemoBusy(true);
    setError("");
    try {
      await login(
        import.meta.env.VITE_DEMO_OPERATOR_EMAIL || "operator@parkingpro.demo",
        import.meta.env.VITE_DEMO_OPERATOR_PASSWORD ||
          "ParkingPro-Operator-2026",
      );
      navigate("/app", { replace: true });
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Demo sign-in is unavailable.",
      );
    } finally {
      setDemoBusy(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-intro">
        <p className="brand">
          Parking<span>Pro</span>
        </p>
        <div>
          <p className="eyebrow">Operator console</p>
          <h1>Run the complete parking workflow.</h1>
          <p>Manage inventory, verify passes, and keep arrivals moving.</p>
        </div>
        <a
          className="secondary-action"
          href={import.meta.env.VITE_DRIVER_BUILD_URL || "#driver-build"}
        >
          <CarFront size={18} /> Open driver build
        </a>
      </section>
      <section className="login-form-wrap" aria-labelledby="sign-in-title">
        <form
          className="login-form"
          onSubmit={(event) => void handleSubmit(submit)(event)}
        >
          <p className="eyebrow">Secure workspace</p>
          <h2 id="sign-in-title">Operator sign in</h2>
          {serviceState !== "ready" ? (
            <div className={`service-banner ${serviceState}`} role="status">
              <strong>
                {serviceState === "unavailable"
                  ? "Demo service unavailable"
                  : "Starting demo service"}
              </strong>
              <span>
                {serviceState === "unavailable"
                  ? "The API could not be reached. No operator action was submitted."
                  : "The free preview may take up to a minute to wake; retries are automatic."}
              </span>
              {serviceState === "unavailable" ? (
                <button
                  className="text-action"
                  onClick={() => void connect()}
                  type="button"
                >
                  Retry service
                </button>
              ) : null}
            </div>
          ) : null}
          <label>
            Email
            <input
              aria-invalid={Boolean(errors.email)}
              required
              type="email"
              autoComplete="username"
              {...register("email")}
            />
            {errors.email ? (
              <small className="field-error">{errors.email.message}</small>
            ) : null}
          </label>
          <label>
            Password
            <input
              aria-invalid={Boolean(errors.password)}
              required
              type="password"
              autoComplete="current-password"
              {...register("password")}
            />
            {errors.password ? (
              <small className="field-error">{errors.password.message}</small>
            ) : null}
          </label>
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}
          <button
            className="primary-action"
            disabled={busy || serviceState !== "ready"}
            type="submit"
          >
            {busy ? "Signing in…" : "Sign in"} <ArrowRight size={18} />
          </button>
          <button
            type="button"
            disabled={busy || serviceState !== "ready"}
            className="text-action"
            onClick={() => void demo()}
          >
            Use demo operator
          </button>
        </form>
      </section>
    </main>
  );
}
