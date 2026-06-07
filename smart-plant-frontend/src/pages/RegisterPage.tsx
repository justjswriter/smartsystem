import { Navigate, useNavigate } from "react-router-dom";
import { Register } from "../components/Register";
import { useAppState } from "../context/AppStateContext";

export function RegisterPage() {
  const {
    registerAccount,
    loginWithCredentials,
    isAuthLoading,
    authError,
    setAuthError,
    token,
    user,
  } = useAppState();
  const navigate = useNavigate();

  if (token && user) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(
    fullName: string,
    email: string,
    password: string,
    passwordConfirm: string
  ) {
    const ok = await registerAccount(fullName, email, password, passwordConfirm);
    if (ok) {
      await loginWithCredentials(email, password);
      navigate("/dashboard", { replace: true });
    }
  }

  return (
    <Register
      isLoading={isAuthLoading}
      error={authError}
      onSubmit={handleSubmit}
      onSwitchToLogin={() => {
        setAuthError("");
        navigate("/login");
      }}
    />
  );
}
