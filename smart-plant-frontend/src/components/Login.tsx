import { useState } from "react";
import { Link } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
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
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await onSubmit(email, password);
  }

  return (
    <div className="auth-layout">
      <form className="card auth-card" onSubmit={handleSubmit}>
        <Link to="/" className="auth-home-link">
          Smart Plant Monitor info
        </Link>
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
          <span className="password-field">
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="******"
              required
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword((current) => !current)}
              aria-label={showPassword ? t("auth.hidePassword") : t("auth.showPassword")}
              title={showPassword ? t("auth.hidePassword") : t("auth.showPassword")}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </span>
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
      <p className="auth-copyright">
        © 2026 Smart Plant Monitor. Certificate No. 73639.
      </p>
    </div>
  );
}
