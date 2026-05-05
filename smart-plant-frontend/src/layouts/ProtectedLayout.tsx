import { Navigate } from "react-router-dom";
import { useAppState } from "../context/AppStateContext";
import { MainLayout } from "./MainLayout";

export function ProtectedLayout() {
  const { token, user } = useAppState();
  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }
  return <MainLayout />;
}
