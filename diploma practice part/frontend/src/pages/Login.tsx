import { useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function Login() {
  const { login, user } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [err, setErr] = useState<string | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    if (user) nav('/plants', { replace: true });
  }, [user, nav]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      await login(email, password);
      nav('/plants');
    } catch (x) {
      setErr(x instanceof Error ? x.message : 'Login failed');
    }
  }

  return (
    <div className="page narrow">
      <h1>Plant monitor</h1>
      <p className="sub">Sign in to the IoT plant dashboard (JWT).</p>
      <form onSubmit={onSubmit} className="card form">
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            autoComplete="current-password"
          />
        </label>
        {err && <p className="err">{err}</p>}
        <button type="submit">Sign in</button>
      </form>
    </div>
  );
}
