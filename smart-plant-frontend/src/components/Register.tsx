import { useState } from "react";
import { useI18n } from "../i18n";

type RegisterProps = {
  isLoading: boolean;
  error: string;
  onSubmit: (
    fullName: string,
    email: string,
    password: string,
    passwordConfirm: string
  ) => Promise<void>;
  onSwitchToLogin: () => void;
};

export function Register({ isLoading, error, onSubmit, onSwitchToLogin }: RegisterProps) {
  const { t } = useI18n();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await onSubmit(fullName, email, password, passwordConfirm);
  }

  return (
    <div className="auth-layout">
      <form className="card auth-card" onSubmit={handleSubmit}>
        <h1>{t("auth.register.title")}</h1>
        <p className="muted">{t("auth.register.subtitle")}</p>

        <label>
          {t("auth.fullName")}
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Saniya"
            required
          />
        </label>

        <label>
          {t("auth.email")}
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@email.com"
            required
          />
        </label>

        <label>
          {t("auth.password")}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="******"
            required
          />
        </label>
        <label>
          {t("auth.confirmPassword")}
          <input
            type="password"
            value={passwordConfirm}
            onChange={(e) => setPasswordConfirm(e.target.value)}
            placeholder="******"
            required
          />
        </label>

        {error ? <div className="error">{error}</div> : null}

        <button type="submit" disabled={isLoading}>
          {isLoading ? t("auth.creating") : t("auth.createAccount")}
        </button>

        <p className="switch-text">
          {t("auth.hasAccount")}{" "}
          <button type="button" className="link-btn" onClick={onSwitchToLogin}>
            {t("auth.login.title")}
          </button>
        </p>
      </form>
    </div>
  );
}
