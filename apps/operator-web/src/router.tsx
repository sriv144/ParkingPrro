import { lazy, Suspense, type ReactNode } from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import { OperatorShell } from "./shell/OperatorShell";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./views/LoginPage";

const FacilitiesPage = lazy(() =>
  import("./views/FacilitiesPage").then((module) => ({
    default: module.FacilitiesPage,
  })),
);
const OverviewPage = lazy(() =>
  import("./views/OverviewPage").then((module) => ({
    default: module.OverviewPage,
  })),
);
const ReportsPage = lazy(() =>
  import("./views/ReportsPage").then((module) => ({
    default: module.ReportsPage,
  })),
);
const ReservationsPage = lazy(() =>
  import("./views/ReservationsPage").then((module) => ({
    default: module.ReservationsPage,
  })),
);
const ScannerPage = lazy(() =>
  import("./views/ScannerPage").then((module) => ({
    default: module.ScannerPage,
  })),
);

function deferred(element: ReactNode) {
  return (
    <Suspense
      fallback={
        <section className="page">
          <p className="eyebrow">Loading workspace</p>
        </section>
      }
    >
      {element}
    </Suspense>
  );
}

export const router = createBrowserRouter([
  { path: "/", element: <LoginPage /> },
  {
    path: "/app",
    element: (
      <ProtectedRoute>
        <OperatorShell />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: deferred(<OverviewPage />) },
      { path: "facilities", element: deferred(<FacilitiesPage />) },
      { path: "reservations", element: deferred(<ReservationsPage />) },
      { path: "scanner", element: deferred(<ScannerPage />) },
      { path: "reports", element: deferred(<ReportsPage />) },
      { path: "*", element: <Navigate to="/app" replace /> },
    ],
  },
  { path: "*", element: <Navigate to="/" replace /> },
]);
