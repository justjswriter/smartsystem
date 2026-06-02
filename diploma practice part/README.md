# Smart plant monitoring (diploma project)

> **Archived legacy prototype.** This folder is kept only for historical reference and does not describe the current pre-defense system. The current system lives in the main `practice-backend`, `smart-plant-frontend`, and `iot/serial_gateway` folders and uses Arduino Uno -> USB Serial -> Python Serial Gateway -> FastAPI -> PostgreSQL -> React frontend, Kazakh-first i18n, admin-only sensor provisioning, Golden pothos / Epipremnum aureum knowledge base, and persisted in-app notifications.

**Topic:** *Developing a Smart System with IoT Integration and Artificial Intelligence Technologies for Plant Condition Monitoring*

End-to-end stack: **ESP32 (Arduino)** → **FastAPI** → **PostgreSQL (Supabase)** → **React (Vite) dashboard**

This repository has:

- `backend/` — API, Alembic migrations, JWT (users) and `x-api-key` (devices)
- `frontend/` — login, plants, charts, alerts, recommendations
- `firmware/esp32_plant_monitor/` — sample sketch (soil, LDR, DHT, HTTP ingest)

**Database:** the project is set up to use a **cloud PostgreSQL** on **Supabase** so the whole team shares one database. `backend/.env` holds `DATABASE_URL` (and must not be committed; only `backend/.env.example` is in Git).

---

## A. Create a Supabase project

1. Go to [Supabase](https://supabase.com) and sign in.
2. Create a **new project** (choose region and a strong database password; save the password).
3. Open **Project Settings** → **Database**.
4. Under **Connection string**, choose **URI** and copy the **PostgreSQL** connection string (or build it from host, user, database name, and password shown on the same page).
5. Paste that string into `backend/.env` as `DATABASE_URL=` (one line, no line breaks in the password).

> **Tip:** Use the “direct” / session connection for Alembic and this app unless Supabase’s docs for your case recommend a pooler. If a connection is refused, copy the string exactly as the dashboard provides (it may use `postgresql://` or `postgres://` — both are normalized for Python).

---

## B. Backend setup

```bash
cd backend
cp .env.example .env
# Open .env and set DATABASE_URL to your Supabase string (and set SECRET_KEY, DEVICE_API_KEY to your own values)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

Open:

- **API docs:** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)  
- **Health:** [http://127.0.0.1:8001/health](http://127.0.0.1:8001/health)

If the API returns **503** for database operations, the server cannot connect to the URL in `DATABASE_URL`. Check the string, the Supabase project status, and that your network allows outbound access to the database host.

---

## C. Frontend setup

In a new terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open: [http://localhost:5173](http://localhost:5173)

With `VITE_API_URL` in `frontend/.env`, the app calls the backend directly. You can also leave that variable **empty** to use the Vite dev proxy in `vite.config.ts`.

---

## Test flow (Swagger or UI)

1. **Register** at `POST /api/auth/register` (password min. 8 characters)
2. **Login** at `POST /api/auth/login` (response: `access_token`, `token_type`)
3. In Swagger, **Authorize** with `Bearer <access_token>`
4. **Create plant** — `POST /api/plants`
5. **Ingest (device, no JWT)** — `POST /api/readings/ingest` with:
   - Header `x-api-key` = the same value as `DEVICE_API_KEY` in `backend/.env`
   - Body: `device_id`, `plant_id`, raw soil/light, `temperature`, `humidity`
6. In the app: open the plant and check latest readings, dashboard, alerts, recommendations

Data is stored in the **Supabase** database defined by your team’s `DATABASE_URL`.

---

## Firmware (ESP32, Arduino IDE)

1. Open `firmware/esp32_plant_monitor/esp32_plant_monitor.ino`
2. Set `WIFI_SSID` and `WIFI_PASSWORD`
3. Set `BACKEND_BASE` to the base URL of your **running API** (no path). For **local** tests, use your computer’s **LAN IP** and port `8001` (same Wi-Fi as the ESP32), **not** `http://127.0.0.1` (the device cannot reach your PC’s “localhost”)
4. When you **deploy** the API (e.g. Render, Railway), set `BACKEND_BASE` to that public HTTPS/HTTP base URL
5. Set `DEVICE_API_KEY` to match `DEVICE_API_KEY` in `backend/.env`
6. Set `PLANT_ID` to a real plant from the API

The sketch `POST`s to `BACKEND_BASE + "/api/readings/ingest"` with `x-api-key: …`. Read the comments in the sketch for more detail.

---

## Team shared database (Supabase)

- **Supabase** gives you a **single online PostgreSQL** database. It is not tied to one laptop; it runs in the cloud.
- **All teammates** can use the **same data** by putting the **same** `DATABASE_URL` into each person’s `backend/.env` (and keeping secrets out of Git).
- **Each developer** runs the FastAPI server **on their own machine** (e.g. `uvicorn` on `127.0.0.1:8001`), but every local backend connects to the **same** Supabase database, so you share users, plants, and readings.
- **Later in the project** you can deploy the FastAPI backend to **Render** or **Railway** and the React app to **Vercel** (or similar), still using the same Supabase `DATABASE_URL` in the server environment.

**Security:** do not put production passwords in the repository. Use Supabase and hosting dashboards to manage secrets.

---

## After changing code (verification)

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m compileall app alembic
uvicorn app.main:app --reload --port 8001
```

Then open [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs).

### Repository hygiene

- Never commit `backend/.env` with real `DATABASE_URL` / `SECRET_KEY` / `DEVICE_API_KEY`
- On a fresh clone: `cp .env.example .env`, then fill in values
- Migrations: run `alembic upgrade head` from the `backend` folder

---

## More detail

- Extra curl examples: [backend/README.md](backend/README.md)
- ORM models: `backend/app/models/`
