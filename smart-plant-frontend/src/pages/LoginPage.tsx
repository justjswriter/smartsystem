import { Navigate, useNavigate } from "react-router-dom";
import { Login } from "../components/Login";
import { useAppState } from "../context/AppStateContext";

export function LoginPage() {
  const { loginWithCredentials, isAuthLoading, authError, setAuthError, token, user } =
    useAppState();
  const navigate = useNavigate();

  if (token && user) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(email: string, password: string) {
    try {
      await loginWithCredentials(email, password);
      navigate("/dashboard", { replace: true });
    } catch {
      // Error already in context
    }
  }

  return (
    <Login
      isLoading={isAuthLoading}
      error={authError}
      onSubmit={handleSubmit}
      onSwitchToRegister={() => {
        setAuthError("");
        navigate("/register");
      }}
    />
  );
}
