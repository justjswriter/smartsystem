import { Link } from "react-router-dom";
import {
  Activity,
  Bell,
  Database,
  Leaf,
  Mail,
  MapPin,
  Radio,
  ShieldCheck,
  Sprout,
} from "lucide-react";

export function HomePage() {
  return (
    <main className="public-home">
      <section className="public-hero">
        <div className="public-nav">
          <Link to="/" className="public-brand" aria-label="Smart Plant Monitor">
            <span className="public-brand-mark">
              <Leaf size={24} />
            </span>
            <span>
              <strong>Smart Plant Monitor</strong>
              <small>IoT & AI-Powered System</small>
            </span>
          </Link>
          <div className="public-nav-actions">
            <Link to="/login" className="public-link">
              Кіру
            </Link>
            <Link to="/register" className="public-button">
              Аккаунт жасау
            </Link>
          </div>
        </div>

        <div className="public-hero-grid">
          <div className="public-hero-copy">
            <span className="public-kicker">
              <MapPin size={18} />
              Астана және Қазақстан бойынша
            </span>
            <h1>Ақылды өсімдік күтімі жүйесі</h1>
            <p>
              Smart Plant Monitor өсімдіктің топырақ ылғалын, температураны,
              ауа ылғалдылығын және жарық деңгейін IoT сенсор арқылы бақылап,
              веб-қосымшада нақты уақытқа жақын көрсетеді.
            </p>
            <div className="public-hero-actions">
              <Link to="/register" className="public-button large">
                Жүйеге қосылу
              </Link>
              <Link to="/login" className="public-outline">
                Менде аккаунт бар
              </Link>
            </div>
          </div>

          <div className="public-monitor" aria-label="System overview preview">
            <div className="public-monitor-head">
              <span>PlantCareSystem</span>
              <strong>ONLINE</strong>
            </div>
            <div className="public-metric-list">
              <div className="public-metric good">
                <span>Топырақ ылғалы</span>
                <strong>48%</strong>
              </div>
              <div className="public-metric warn">
                <span>Жарық деңгейі</span>
                <strong>36</strong>
              </div>
              <div className="public-metric good">
                <span>Температура</span>
                <strong>26°C</strong>
              </div>
              <div className="public-metric good">
                <span>Ауа ылғалы</span>
                <strong>57%</strong>
              </div>
            </div>
            <div className="public-signal">
              <Activity size={18} />
              Arduino Uno сенсорынан деректер backend арқылы PostgreSQL базасына сақталады.
            </div>
          </div>
        </div>
      </section>

      <section className="public-section">
        <div className="public-section-head">
          <h2>Жүйе не істейді?</h2>
          <p>
            Үйдегі, кеңседегі немесе оқу жобасындағы өсімдіктерді жүйелі бақылауға арналған.
          </p>
        </div>
        <div className="public-feature-grid">
          <article className="public-feature">
            <Radio />
            <h3>IoT мониторинг</h3>
            <p>Arduino сенсоры USB gateway арқылы backend-ке өлшемдерді жібереді.</p>
          </article>
          <article className="public-feature">
            <Bell />
            <h3>Ескертулер</h3>
            <p>Қауіпті көрсеткіштер байқалса, жүйе сайт ішінде notification көрсетеді.</p>
          </article>
          <article className="public-feature">
            <Sprout />
            <h3>Күтім ұсыныстары</h3>
            <p>Rule-based логика өсімдікке су, жарық және орын бойынша кеңес береді.</p>
          </article>
          <article className="public-feature">
            <Database />
            <h3>Тарих және аналитика</h3>
            <p>Өлшемдер PostgreSQL базасында сақталып, графиктерде көрсетіледі.</p>
          </article>
        </div>
      </section>

      <section className="public-band">
        <div>
          <h2>Қазақстандағы демо және оқу жобаларына ыңғайлы</h2>
          <p>
            Жүйе Астана қаласынан бастап Қазақстан бойынша интернеті бар кез келген
            жерде ашылады. IoT gateway ноутбукта жұмыс істейді, ал сайт пен база Bult
            cloud инфрақұрылымында орналасқан.
          </p>
        </div>
        <div className="public-contact">
          <ShieldCheck size={24} />
          <div>
            <strong>Байланыс</strong>
            <a href="mailto:zaremabazarova11@gmail.com">zaremabazarova11@gmail.com</a>
          </div>
          <Mail size={24} />
        </div>
      </section>

      <footer className="public-footer">
        <p>© 2026 Smart Plant Monitor. Барлық құқықтар қорғалған.</p>
        <p>
          Авторлық құқық туралы куәлік № 73639: Smart System with IoT Integration
          and Artificial Intelligence Technologies for Plant Condition Monitoring.
        </p>
        <p>Астана, Қазақстан.</p>
      </footer>
    </main>
  );
}
