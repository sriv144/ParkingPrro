import type {
  OperatorOverview,
  ParkingLotSummary,
  Reservation,
} from "@parkingpro/api-contracts";
import { useQuery } from "@tanstack/react-query";
import { motion, useReducedMotion } from "framer-motion";
import { Link } from "react-router-dom";

import { apiRequest } from "../lib/api";

export function OverviewPage() {
  const reducedMotion = useReducedMotion();
  const overview = useQuery({
    queryKey: ["operator", "overview"],
    queryFn: () => apiRequest<OperatorOverview>("/api/v1/operator/overview"),
    refetchInterval: 10_000,
  });
  const lots = useQuery({
    queryKey: ["operator", "lots"],
    queryFn: () => apiRequest<ParkingLotSummary[]>("/api/v1/operator/lots"),
    refetchInterval: 10_000,
  });
  const reservations = useQuery({
    queryKey: ["operator", "reservations"],
    queryFn: () => apiRequest<Reservation[]>("/api/v1/operator/reservations"),
    refetchInterval: 10_000,
  });
  const data = overview.data;
  const metrics = [
    [String(data?.total_spots ?? "—"), "total spots"],
    [String(data?.occupied_spots ?? "—"), "occupied"],
    [String(data ? data.total_spots - data.occupied_spots : "—"), "available"],
    [
      data
        ? `₹${(data.revenue_today_paise / 100).toLocaleString("en-IN")}`
        : "—",
      "today",
    ],
  ] as const;

  return (
    <section className="page" aria-labelledby="overview-title">
      <div className="page-heading">
        <div>
          <p className="eyebrow">10-second snapshot</p>
          <h1 id="overview-title">Occupancy overview</h1>
        </div>
        <Link className="secondary-action" to="/app/facilities">
          View facilities
        </Link>
      </div>
      {overview.isError && (
        <p className="form-error" role="alert">
          Live metrics could not be refreshed.
        </p>
      )}
      <div className="metric-strip">
        {metrics.map(([value, label], index) => (
          <motion.div
            key={label}
            initial={reducedMotion ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: reducedMotion ? 0 : index * 0.06 }}
          >
            <strong>{value}</strong>
            <span>{label}</span>
          </motion.div>
        ))}
      </div>
      <div className="overview-grid">
        <section aria-labelledby="facilities-title">
          <div className="section-heading">
            <h2 id="facilities-title">Facilities</h2>
            <span>Availability</span>
          </div>
          <ul className="data-list">
            {lots.data?.slice(0, 5).map((lot) => (
              <li key={lot.id}>
                <span>
                  <i
                    className={`dot ${lot.available_spots ? "available" : "attention"}`}
                  />
                  {lot.name}
                  <small>{lot.address}</small>
                </span>
                <strong>
                  {lot.available_spots} / {lot.total_spots}
                </strong>
              </li>
            ))}
          </ul>
        </section>
        <section aria-labelledby="activity-title">
          <div className="section-heading">
            <h2 id="activity-title">Reservation queue</h2>
            <span>Latest</span>
          </div>
          <ul className="data-list compact">
            {reservations.data?.slice(0, 5).map((item) => (
              <li key={item.id}>
                <span>
                  {item.status.replace("_", " ")}
                  <small>
                    {item.lot_name} · {item.spot_code}
                  </small>
                </span>
                <time>
                  {new Date(item.starts_at).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </time>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </section>
  );
}
