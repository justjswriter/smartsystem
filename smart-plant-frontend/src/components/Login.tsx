import { useState } from "react";
import { useI18n } from "../i18n";

type LoginProps = {
  isLoading: boolean;
  error: string;
  onSubmit: (email: string, password: string) => Promise<void>;
  onSwitchToRegister: () => void;
};

export function Login({ isLoading, error, onSubmit, onSwitchToRegister }: LoginProps) {
  const { t } = useI18n();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await onSubmit(email, password);
  }

  return (
    <div className="auth-layout">
      <form className="card auth-card" onSubmit={handleSubmit}>
        <h1>{t("auth.login.title")}</h1>
        <p className="muted">{t("auth.login.subtitle")}</p>

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

        {error ? <div className="error">{error}</div> : null}

        <button type="submit" disabled={isLoading}>
          {isLoading ? t("auth.signingIn") : t("auth.signIn")}
        </button>

        <p className="switch-text">
          {t("auth.noAccount")}{" "}
          <button type="button" className="link-btn" onClick={onSwitchToRegister}>
            {t("auth.register")}
          </button>
        </p>
      </form>
    </div>
  );
}
