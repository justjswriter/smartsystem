import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiGet, type Plant } from '../api';
import { useAuth } from '../AuthContext';

export default function Plants() {
  const { user, ready, logout } = useAuth();
  const [plants, setPlants] = useState<Plant[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    if (!ready) return;
    if (!user) {
      nav('/login', { replace: true });
      return;
    }
    apiGet<Plant[]>('/api/plants')
      .then(setPlants)
      .catch((e) => setErr(e instanceof Error ? e.message : 'Failed'));
  }, [user, ready, nav]);

  if (!user) return null;

  return (
    <div className="page">
      <header className="bar">
        <h1>Your plants</h1>
        <button type="button" className="ghost" onClick={() => { logout(); nav('/login'); }}>
          Log out
        </button>
      </header>
      {err && <p className="err">{err}</p>}
      <ul className="grid">
        {plants.map((p) => (
          <li key={p.id} className="card plant-card">
            <Link to={`/plants/${p.id}`}>
              <h2>{p.name}</h2>
              {p.location && <p className="muted">{p.location}</p>}
            </Link>
          </li>
        ))}
      </ul>
      {plants.length === 0 && !err && <p className="muted">No plants yet. Create one with the API or seed script in README.</p>}
    </div>
  );
}
