import { useState } from "react";

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
        <h1>Register</h1>
        <p className="muted">Create an account for plant monitoring</p>

        <label>
          Full name
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Saniya"
            required
          />
        </label>

        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@email.com"
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="******"
            required
          />
        </label>
        <label>
          Confirm password
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
          {isLoading ? "Creating..." : "Create account"}
        </button>

        <p className="switch-text">
          Already have an account?{" "}
          <button type="button" className="link-btn" onClick={onSwitchToLogin}>
            Login
          </button>
        </p>
      </form>
    </div>
  );
}
