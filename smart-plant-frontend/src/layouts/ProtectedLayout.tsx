import { Navigate } from "react-router-dom";
import { useAppState } from "../context/AppStateContext";
import { useI18n } from "../i18n";
import { MainLayout } from "./MainLayout";

export function ProtectedLayout() {
  const { token, user, isAuthLoading } = useAppState();
  const { t } = useI18n();
  if (token && !user && isAuthLoading) {
    return <p className="muted page-lead">{t("common.loading")}</p>;
  }
  if (!token || !user) {
    return <Navigate to="/" replace />;
  }
  return <MainLayout />;
}
