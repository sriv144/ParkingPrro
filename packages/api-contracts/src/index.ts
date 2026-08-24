export type UserRole = "driver" | "operator" | "admin";
export type { components, operations, paths } from "./schema";
export type ReservationStatus =
  "held" | "confirmed" | "checked_in" | "completed" | "cancelled" | "expired";

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    request_id: string;
    fields: Record<string, string[]>;
  };
}

export interface ParkingLotSummary {
  id: string;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  distance_m: number | null;
  available_spots: number;
  total_spots: number;
  base_rate_paise: number;
  state: "active" | "out_of_service";
  timezone: string;
  opens_at: string;
  closes_at: string;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  role: UserRole;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string | null;
  csrf_token: string | null;
  expires_in: number;
  user: UserProfile;
}

export interface Vehicle {
  id: string;
  registration_number: string;
  label: string | null;
  vehicle_type: "car" | "bike" | "ev" | "accessible";
}

export interface ParkingSpot {
  id: string;
  lot_id: string;
  code: string;
  spot_type: "car" | "bike" | "ev" | "accessible";
  state: "active" | "out_of_service";
}

export interface Quote {
  lot_id: string;
  starts_at: string;
  ends_at: string;
  duration_minutes: number;
  amount_paise: number;
  currency: "INR";
  available_spots: number;
}

export interface Reservation {
  id: string;
  lot_id: string;
  lot_name: string;
  spot_code: string;
  vehicle_id: string;
  registration_number: string;
  starts_at: string;
  ends_at: string;
  quoted_amount_paise: number;
  status: ReservationStatus;
  hold_expires_at: string | null;
  qr_payload: string | null;
}

export interface OperatorOverview {
  occupied_spots: number;
  total_spots: number;
  occupancy_percent: number;
  active_reservations: number;
  revenue_today_paise: number;
  completed_today: number;
}
