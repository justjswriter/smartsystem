import { useEffect, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { apiGet, type PlantDashboard, type Reading, type AlertRow, type RecItem } from '../api';
import { useAuth } from '../AuthContext';

type AlertList = { total: number; items: AlertRow[] };
type RecList = { items: RecItem[] };

export default function PlantDetail() {
  const { id } = useParams();
  const plantId = Number(id);
  const { user, ready } = useAuth();
  const nav = useNavigate();
  const [dash, setDash] = useState<PlantDashboard | null>(null);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [alerts, setAlerts] = useState<AlertRow[]>([]);
  const [recs, setRecs] = useState<RecItem[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!ready) return;
    if (!user) {
      nav('/login', { replace: true });
      return;
    }
    if (!Number.isFinite(plantId)) return;
    setErr(null);
    Promise.all([
      apiGet<PlantDashboard>(`/api/plants/${plantId}/dashboard`),
      apiGet<Reading[]>(`/api/plants/${plantId}/readings?limit=100`),
      apiGet<AlertList>(`/api/alerts?limit=50`),
      apiGet<RecList>(`/api/plants/${plantId}/recommendations`),
    ])
      .then(([d, r, a, rec]) => {
        setDash(d);
        setReadings(
          [...r].sort(
            (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime()
          )
        );
        setAlerts(a.items.filter((x) => x.plant_id === plantId));
        setRecs(rec.items);
      })
      .catch((e) => setErr(e instanceof Error ? e.message : 'Error'));
  }, [user, ready, plantId, nav]);

  if (!user) return null;

  const latest = dash?.latest;
  const health = latest?.health_status || '—';
  const healthClass =
    health === 'critical' ? 'badge crit' : health === 'warning' ? 'badge warn' : 'badge ok';

  const chartData = readings.slice(-50).map((r) => ({
    t: new Date(r.recorded_at).toLocaleTimeString(),
    soil: r.soil_moisture_percent,
    temp: r.temperature,
    hum: r.humidity,
    light: r.light_percent,
  }));

  return (
    <div className="page">
      <p>
        <Link to="/plants">← Plants</Link>
      </p>
      <h1>{dash?.plant_name || `Plant #${plantId}`}</h1>
      {err && <p className="err">{err}</p>}

      <section className="card">
        <h2>Latest status</h2>
        <p>
          <span className={healthClass}>{health}</span>
          {latest?.abnormal_codes?.length
            ? ` — ${latest.abnormal_codes.join(', ')}`
            : null}
        </p>
        <div className="stats">
          <div className="stat">
            <span>Soil</span>
            <strong>
              {latest?.soil_moisture_percent != null
                ? `${latest.soil_moisture_percent.toFixed(0)}%`
                : '—'}
            </strong>
          </div>
          <div className="stat">
            <span>Temp</span>
            <strong>
              {latest?.temperature != null
                ? `${latest.temperature.toFixed(1)}°C`
                : '—'}
            </strong>
          </div>
          <div className="stat">
            <span>Humidity</span>
            <strong>
              {latest?.humidity != null
                ? `${latest.humidity.toFixed(0)}%`
                : '—'}
            </strong>
          </div>
          <div className="stat">
            <span>Light</span>
            <strong>
              {latest?.light_percent != null
                ? `${latest.light_percent.toFixed(0)}%`
                : '—'}
            </strong>
          </div>
        </div>
        <p className="muted small">
          Readings in DB: {dash?.recent_readings_count ?? 0} — Open alerts: {dash?.open_alerts ?? 0}
        </p>
      </section>

      <section className="card">
        <h2>History (chart)</h2>
        {chartData.length > 0 ? (
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="t" minTickGap={20} />
                <YAxis domain={['auto', 'auto']} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="soil" name="Soil %" stroke="#2d6a4f" dot={false} />
                <Line type="monotone" dataKey="temp" name="°C" stroke="#d62828" dot={false} />
                <Line type="monotone" dataKey="hum" name="Hum %" stroke="#5c4d7d" dot={false} />
                <Line type="monotone" dataKey="light" name="Light %" stroke="#e9c46a" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="muted">No readings yet. Send data from the ESP32 or curl.</p>
        )}
      </section>

      <section className="card">
        <h2>Recent readings (table)</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Soil %</th>
                <th>°C</th>
                <th>Hum %</th>
                <th>Light %</th>
              </tr>
            </thead>
            <tbody>
              {readings
                .slice()
                .reverse()
                .slice(0, 20)
                .map((r) => (
                  <tr key={r.id}>
                    <td>{new Date(r.recorded_at).toLocaleString()}</td>
                    <td>{r.soil_moisture_percent?.toFixed(0) ?? '—'}</td>
                    <td>{r.temperature?.toFixed(1) ?? '—'}</td>
                    <td>{r.humidity?.toFixed(0) ?? '—'}</td>
                    <td>{r.light_percent?.toFixed(0) ?? '—'}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="two-col">
        <section className="card">
          <h2>Alerts (this plant)</h2>
          {alerts.length === 0 ? (
            <p className="muted">No alerts for this plant.</p>
          ) : (
            <ul className="alert-list">
              {alerts.map((a) => (
                <li key={a.id} className={`sev sev-${a.severity}`}>
                  <strong>{a.severity}</strong> — {a.status}
                  <pre>{a.message}</pre>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="card">
          <h2>Recommendations</h2>
          {recs.length === 0 ? (
            <p className="muted">No rule-based recommendations yet (generated on ingest).</p>
          ) : (
            <ul>
              {recs.map((r) => (
                <li key={r.id} className="rec">
                  <p>{r.text}</p>
                  {r.explanation && <p className="muted small">{r.explanation}</p>}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
