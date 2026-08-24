import type {
  OperatorOverview,
  ParkingLotSummary,
} from "@parkingpro/api-contracts";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { apiRequest } from "../lib/api";

export function ReportsPage() {
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
  const chartData =
    lots.data?.map((lot) => ({
      name: lot.name,
      occupied: lot.total_spots - lot.available_spots,
      available: lot.available_spots,
    })) ?? [];
  return (
    <section className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Verified operational data</p>
          <h1>Occupancy & revenue</h1>
        </div>
      </div>
      <div className="metric-strip">
        <div>
          <strong>{overview.data?.occupancy_percent ?? 0}%</strong>
          <span>occupancy</span>
        </div>
        <div>
          <strong>
            ₹
            {((overview.data?.revenue_today_paise ?? 0) / 100).toLocaleString(
              "en-IN",
            )}
          </strong>
          <span>captured today</span>
        </div>
        <div>
          <strong>{overview.data?.completed_today ?? 0}</strong>
          <span>completed today</span>
        </div>
        <div>
          <strong>{overview.data?.active_reservations ?? 0}</strong>
          <span>active reservations</span>
        </div>
      </div>
      <div className="chart-panel" aria-label="Facility occupancy chart">
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={chartData}>
            <CartesianGrid stroke="#26343c" vertical={false} />
            <XAxis dataKey="name" stroke="#aeb9bf" />
            <YAxis stroke="#aeb9bf" />
            <Tooltip
              contentStyle={{ background: "#111c22", borderColor: "#46545d" }}
            />
            <Bar dataKey="occupied" stackId="spots" fill="#08c7f4" />
            <Bar dataKey="available" stackId="spots" fill="#26343c" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
