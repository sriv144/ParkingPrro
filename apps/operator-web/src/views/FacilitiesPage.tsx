import type { ParkingLotSummary, ParkingSpot } from "@parkingpro/api-contracts";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";

import { ApiError, apiRequest } from "../lib/api";

export function FacilitiesPage() {
  const queryClient = useQueryClient();
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [selectedLot, setSelectedLot] = useState<string | null>(null);
  const lots = useQuery({
    queryKey: ["operator", "lots"],
    queryFn: () => apiRequest<ParkingLotSummary[]>("/api/v1/operator/lots"),
  });
  const create = useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      apiRequest<ParkingLotSummary>("/api/v1/operator/lots", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["operator", "lots"] }),
  });
  const updateLot = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      apiRequest<ParkingLotSummary>(`/api/v1/operator/lots/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["operator", "lots"] });
      setNotice("Facility settings saved.");
    },
  });
  const spots = useQuery({
    queryKey: ["operator", "spots", selectedLot],
    queryFn: () =>
      apiRequest<ParkingSpot[]>(`/api/v1/operator/lots/${selectedLot}/spots`),
    enabled: Boolean(selectedLot),
  });
  const updateSpot = useMutation({
    mutationFn: (spot: ParkingSpot) =>
      apiRequest<ParkingSpot>(`/api/v1/operator/spots/${spot.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          state: spot.state === "active" ? "out_of_service" : "active",
        }),
      }),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["operator", "spots", selectedLot],
      }),
  });

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      await create.mutateAsync({
        name: form.get("name"),
        address: form.get("address"),
        latitude: Number(form.get("latitude")),
        longitude: Number(form.get("longitude")),
        base_rate_paise: Number(form.get("rate")) * 100,
        capacity: Number(form.get("capacity")),
      });
      event.currentTarget.reset();
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Could not create the facility.",
      );
    }
  }

  async function submitEdit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedLot) return;
    setError("");
    setNotice("");
    const form = new FormData(event.currentTarget);
    try {
      await updateLot.mutateAsync({
        id: selectedLot,
        data: {
          name: form.get("name"),
          address: form.get("address"),
          opens_at: form.get("opens_at"),
          closes_at: form.get("closes_at"),
          base_rate_paise: Number(form.get("rate")) * 100,
          state: form.get("state"),
        },
      });
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Could not update the facility.",
      );
    }
  }

  const selected = lots.data?.find((lot) => lot.id === selectedLot);

  return (
    <section className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Inventory</p>
          <h1>Facilities & spots</h1>
        </div>
      </div>
      <div className="split-workspace">
        <section>
          <div className="section-heading">
            <h2>Assigned facilities</h2>
            <span>{lots.data?.length ?? 0} locations</span>
          </div>
          <ul className="data-list">
            {lots.data?.map((lot) => (
              <li key={lot.id}>
                <button
                  className="row-button"
                  onClick={() => setSelectedLot(lot.id)}
                >
                  <span>
                    {lot.name}
                    <small>{lot.address}</small>
                  </span>
                  <strong>
                    {lot.available_spots}/{lot.total_spots}
                  </strong>
                </button>
              </li>
            ))}
          </ul>
          {selectedLot && (
            <div className="spot-grid" aria-label="Parking spots">
              {spots.data?.map((spot) => (
                <button
                  key={spot.id}
                  className={`spot-cell ${spot.state}`}
                  onClick={() => updateSpot.mutate(spot)}
                >
                  <strong>{spot.code}</strong>
                  <span>{spot.spot_type}</span>
                </button>
              ))}
            </div>
          )}
          {selected ? (
            <form
              className="panel-form compact-form"
              key={selected.id}
              onSubmit={(event) => void submitEdit(event)}
            >
              <p className="eyebrow">Facility editor</p>
              <h2>{selected.name}</h2>
              <label>
                Name
                <input defaultValue={selected.name} name="name" required />
              </label>
              <label>
                Address
                <input
                  defaultValue={selected.address}
                  name="address"
                  required
                />
              </label>
              <div className="form-grid">
                <label>
                  Opens
                  <input
                    defaultValue={selected.opens_at}
                    name="opens_at"
                    pattern="(?:[01][0-9]|2[0-3]):[0-5][0-9]"
                    required
                  />
                </label>
                <label>
                  Closes
                  <input
                    defaultValue={selected.closes_at}
                    name="closes_at"
                    pattern="(?:[01][0-9]|2[0-3]):[0-5][0-9]"
                    required
                  />
                </label>
              </div>
              <div className="form-grid">
                <label>
                  ₹ per hour
                  <input
                    defaultValue={selected.base_rate_paise / 100}
                    min="1"
                    name="rate"
                    type="number"
                    required
                  />
                </label>
                <label>
                  Operational state
                  <select defaultValue={selected.state} name="state">
                    <option value="active">Active</option>
                    <option value="out_of_service">Out of service</option>
                  </select>
                </label>
              </div>
              {notice ? (
                <p className="form-success" role="status">
                  {notice}
                </p>
              ) : null}
              <button
                className="secondary-action"
                disabled={updateLot.isPending}
                type="submit"
              >
                {updateLot.isPending ? "Saving…" : "Save facility"}
              </button>
            </form>
          ) : null}
        </section>
        <form className="panel-form" onSubmit={(event) => void submit(event)}>
          <p className="eyebrow">Add facility</p>
          <h2>New Bengaluru inventory</h2>
          <label>
            Name
            <input name="name" required />
          </label>
          <label>
            Address
            <input name="address" required />
          </label>
          <div className="form-grid">
            <label>
              Latitude
              <input
                name="latitude"
                type="number"
                step="any"
                defaultValue="12.9716"
                required
              />
            </label>
            <label>
              Longitude
              <input
                name="longitude"
                type="number"
                step="any"
                defaultValue="77.5946"
                required
              />
            </label>
          </div>
          <div className="form-grid">
            <label>
              ₹ per hour
              <input
                name="rate"
                type="number"
                min="1"
                defaultValue="60"
                required
              />
            </label>
            <label>
              Capacity
              <input
                name="capacity"
                type="number"
                min="1"
                max="1000"
                defaultValue="20"
                required
              />
            </label>
          </div>
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}
          <button
            className="primary-action"
            disabled={create.isPending}
            type="submit"
          >
            Create facility
          </button>
        </form>
      </div>
    </section>
  );
}
