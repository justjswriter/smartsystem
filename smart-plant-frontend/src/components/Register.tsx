import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
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
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

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
        <label>
          {t("auth.confirmPassword")}
          <span className="password-field">
            <input
              type={showPasswordConfirm ? "text" : "password"}
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              placeholder="******"
              required
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPasswordConfirm((current) => !current)}
              aria-label={showPasswordConfirm ? t("auth.hidePassword") : t("auth.showPassword")}
              title={showPasswordConfirm ? t("auth.hidePassword") : t("auth.showPassword")}
            >
              {showPasswordConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </span>
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
      <p className="auth-copyright">
        © 2026 Smart Plant Monitor. Certificate No. 73639.
      </p>
    </div>
  );
}
