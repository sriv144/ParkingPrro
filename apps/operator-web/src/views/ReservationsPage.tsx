import type { Reservation } from "@parkingpro/api-contracts";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiRequest } from "../lib/api";

export function ReservationsPage() {
  const queryClient = useQueryClient();
  const reservations = useQuery({
    queryKey: ["operator", "reservations"],
    queryFn: () => apiRequest<Reservation[]>("/api/v1/operator/reservations"),
    refetchInterval: 10_000,
  });
  const transition = useMutation({
    mutationFn: ({
      id,
      action,
    }: {
      id: string;
      action: "check-in" | "check-out";
    }) =>
      apiRequest<Reservation>(`/api/v1/operator/reservations/${id}/${action}`, {
        method: "POST",
      }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: ["operator", "reservations"],
        }),
        queryClient.invalidateQueries({ queryKey: ["operator", "overview"] }),
        queryClient.invalidateQueries({ queryKey: ["operator", "lots"] }),
      ]);
    },
  });

  return (
    <section className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Live operations</p>
          <h1>Reservation queue</h1>
        </div>
        <span className="live-indicator">
          <i /> Refreshes every 10 seconds
        </span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Driver</th>
              <th>Facility</th>
              <th>Time</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {reservations.data?.map((item) => (
              <tr key={item.id}>
                <td>
                  <strong>{item.registration_number}</strong>
                  <small>{item.spot_code}</small>
                </td>
                <td>{item.lot_name}</td>
                <td>{new Date(item.starts_at).toLocaleString()}</td>
                <td>
                  <span className="status-chip">
                    {item.status.replace("_", " ")}
                  </span>
                </td>
                <td>
                  {item.status === "confirmed" ? (
                    <button
                      onClick={() =>
                        transition.mutate({ id: item.id, action: "check-in" })
                      }
                    >
                      Check in
                    </button>
                  ) : item.status === "checked_in" ? (
                    <button
                      onClick={() =>
                        transition.mutate({ id: item.id, action: "check-out" })
                      }
                    >
                      Check out
                    </button>
                  ) : (
                    "—"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
