import { Navigate, createBrowserRouter } from "react-router-dom";
import { ProtectedLayout } from "./layouts/ProtectedLayout";
import { AlertsPage } from "./pages/AlertsPage";
import { AdminPage } from "./pages/AdminPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { PlantDetailsPage } from "./pages/PlantDetailsPage";
import { PlantsIndexPage } from "./pages/PlantsIndexPage";
import { ProfilePage } from "./pages/ProfilePage";
import { RegisterPage } from "./pages/RegisterPage";
import { SensorsPage } from "./pages/SensorsPage";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  {
    path: "/",
    element: <ProtectedLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "plants", element: <PlantsIndexPage /> },
      { path: "plants/:plantId", element: <PlantDetailsPage /> },
      { path: "analytics", element: <AnalyticsPage /> },
      { path: "sensors", element: <SensorsPage /> },
      { path: "alerts", element: <AlertsPage /> },
      { path: "admin", element: <AdminPage /> },
      { path: "profile", element: <ProfilePage /> },
      { path: "settings", element: <Navigate to="/profile" replace /> },
    ],
  },
]);
