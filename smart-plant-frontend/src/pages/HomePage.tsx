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
import { CustomSelect } from "../components/CustomSelect";
import { useAppState } from "../context/AppStateContext";
import { useI18n, type Language } from "../i18n";

const homeText = {
  kk: {
    location: "Астана және Қазақстан бойынша",
    title: "Ақылды өсімдік күтімі жүйесі",
    description:
      "Smart Plant Monitor өсімдіктің топырақ ылғалын, температурасын, ауа ылғалдығын және жарық деңгейін IoT сенсор арқылы бақылап, деректерді веб-қосымшада нақты уақытқа жақын көрсетеді.",
    join: "Жүйеге қосылу",
    hasAccount: "Менде аккаунт бар",
    signIn: "Sign in",
    signUp: "Sign up",
    dashboard: "Dashboard",
    soil: "Топырақ ылғалы",
    light: "Жарық деңгейі",
    temperature: "Температура",
    humidity: "Ауа ылғалы",
    signal: "Arduino Uno сенсорынан деректер backend арқылы PostgreSQL базасына сақталады.",
    sectionTitle: "Жүйе не істейді?",
    sectionText: "Үйдегі, кеңседегі немесе оқу жобасындағы өсімдіктерді жүйелі бақылауға арналған веб-қосымша.",
    featureIot: "IoT мониторинг",
    featureIotText: "Arduino сенсоры USB gateway арқылы backend-ке өлшемдерді жібереді.",
    featureAlerts: "Ескертулер",
    featureAlertsText: "Қауіпті көрсеткіштер байқалса, жүйе сайт ішінде notification көрсетеді.",
    featureCare: "Күтім ұсыныстары",
    featureCareText: "Rule-based логика өсімдікке су, жарық және орналасу бойынша кеңес береді.",
    featureHistory: "Тарих және аналитика",
    featureHistoryText: "Өлшемдер PostgreSQL базасында сақталып, графиктерде көрсетіледі.",
    bandTitle: "Қазақстандағы демо және оқу жобаларына ыңғайлы",
    bandText:
      "Жүйе Астана қаласынан бастап Қазақстан бойынша интернеті бар кез келген жерде ашылады. IoT gateway ноутбукта жұмыс істейді, ал сайт пен база Bult cloud инфрақұрылымында орналасқан.",
    contact: "Байланыс",
    rights: "© 2026 Smart Plant Monitor. Барлық құқықтар қорғалған.",
    certificate:
      "Авторлық құқық туралы куәлік № 73639: Smart System with IoT Integration and Artificial Intelligence Technologies for Plant Condition Monitoring.",
    city: "Астана, Қазақстан.",
  },
  ru: {
    location: "Астана и весь Казахстан",
    title: "Умная система ухода за растениями",
    description:
      "Smart Plant Monitor отслеживает влажность почвы, температуру, влажность воздуха и уровень освещения через IoT-сенсор и показывает данные в веб-приложении почти в реальном времени.",
    join: "Начать пользоваться",
    hasAccount: "У меня уже есть аккаунт",
    signIn: "Sign in",
    signUp: "Sign up",
    dashboard: "Dashboard",
    soil: "Влажность почвы",
    light: "Уровень света",
    temperature: "Температура",
    humidity: "Влажность воздуха",
    signal: "Данные с Arduino Uno через backend сохраняются в PostgreSQL.",
    sectionTitle: "Что делает система?",
    sectionText: "Веб-приложение для регулярного контроля растений дома, в офисе или в учебном проекте.",
    featureIot: "IoT мониторинг",
    featureIotText: "Сенсор Arduino отправляет измерения на backend через USB gateway.",
    featureAlerts: "Уведомления",
    featureAlertsText: "Если показатели становятся опасными, система показывает уведомления внутри сайта.",
    featureCare: "Рекомендации по уходу",
    featureCareText: "Rule-based логика дает советы по поливу, свету и расположению растения.",
    featureHistory: "История и аналитика",
    featureHistoryText: "Измерения сохраняются в PostgreSQL и отображаются на графиках.",
    bandTitle: "Подходит для демо и учебных проектов в Казахстане",
    bandText:
      "Система доступна из Астаны и любого региона Казахстана, где есть интернет. IoT gateway работает на ноутбуке, а сайт и база размещены в Bult cloud.",
    contact: "Контакты",
    rights: "© 2026 Smart Plant Monitor. Все права защищены.",
    certificate:
      "Свидетельство об авторском праве № 73639: Smart System with IoT Integration and Artificial Intelligence Technologies for Plant Condition Monitoring.",
    city: "Астана, Казахстан.",
  },
  en: {
    location: "Astana and across Kazakhstan",
    title: "Smart plant care system",
    description:
      "Smart Plant Monitor tracks soil moisture, temperature, air humidity, and light level through an IoT sensor and shows near real-time readings in the web app.",
    join: "Get started",
    hasAccount: "I already have an account",
    signIn: "Sign in",
    signUp: "Sign up",
    dashboard: "Dashboard",
    soil: "Soil moisture",
    light: "Light level",
    temperature: "Temperature",
    humidity: "Air humidity",
    signal: "Arduino Uno readings are sent through the backend and stored in PostgreSQL.",
    sectionTitle: "What does the system do?",
    sectionText: "A web app for regular plant monitoring at home, in an office, or as an educational project.",
    featureIot: "IoT monitoring",
    featureIotText: "The Arduino sensor sends measurements to the backend through a USB gateway.",
    featureAlerts: "Notifications",
    featureAlertsText: "When values become risky, the system shows notifications inside the site.",
    featureCare: "Care recommendations",
    featureCareText: "Rule-based logic gives advice on watering, light, and plant placement.",
    featureHistory: "History and analytics",
    featureHistoryText: "Measurements are stored in PostgreSQL and displayed in charts.",
    bandTitle: "Convenient for demos and educational projects in Kazakhstan",
    bandText:
      "The system is available from Astana and any region of Kazakhstan with internet access. The IoT gateway runs on a laptop, while the site and database are hosted on Bult cloud.",
    contact: "Contact",
    rights: "© 2026 Smart Plant Monitor. All rights reserved.",
    certificate:
      "Copyright certificate No. 73639: Smart System with IoT Integration and Artificial Intelligence Technologies for Plant Condition Monitoring.",
    city: "Astana, Kazakhstan.",
  },
} satisfies Record<Language, Record<string, string>>;

export function HomePage() {
  const { token, user } = useAppState();
  const { language, setLanguage } = useI18n();
  const isSignedIn = Boolean(token && user);
  const text = homeText[language];

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
              <small>IoT &amp; AI-Powered System</small>
            </span>
          </Link>
          <div className="public-nav-actions">
            <CustomSelect
              value={language}
              ariaLabel="Language"
              className="public-language-select"
              onChange={(value) => setLanguage(value as Language)}
              options={[
                { value: "kk", label: "KK" },
                { value: "ru", label: "RU" },
                { value: "en", label: "EN" },
              ]}
            />
            {isSignedIn ? (
              <Link to="/dashboard" className="public-button">
                {text.dashboard}
              </Link>
            ) : (
              <>
                <Link to="/login" className="public-link">
                  {text.signIn}
                </Link>
                <Link to="/register" className="public-button">
                  {text.signUp}
                </Link>
              </>
            )}
          </div>
        </div>

        <div className="public-hero-grid">
          <div className="public-hero-copy">
            <span className="public-kicker">
              <MapPin size={18} />
              {text.location}
            </span>
            <h1>{text.title}</h1>
            <p>{text.description}</p>
            <div className="public-hero-actions">
              <Link to="/register" className="public-button large">
                {text.join}
              </Link>
              <Link to="/login" className="public-outline">
                {text.hasAccount}
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
                <span>{text.soil}</span>
                <strong>48%</strong>
              </div>
              <div className="public-metric warn">
                <span>{text.light}</span>
                <strong>36</strong>
              </div>
              <div className="public-metric good">
                <span>{text.temperature}</span>
                <strong>26°C</strong>
              </div>
              <div className="public-metric good">
                <span>{text.humidity}</span>
                <strong>57%</strong>
              </div>
            </div>
            <div className="public-signal">
              <Activity size={18} />
              {text.signal}
            </div>
          </div>
        </div>
      </section>

      <section className="public-section">
        <div className="public-section-head">
          <h2>{text.sectionTitle}</h2>
          <p>{text.sectionText}</p>
        </div>
        <div className="public-feature-grid">
          <article className="public-feature">
            <Radio />
            <h3>{text.featureIot}</h3>
            <p>{text.featureIotText}</p>
          </article>
          <article className="public-feature">
            <Bell />
            <h3>{text.featureAlerts}</h3>
            <p>{text.featureAlertsText}</p>
          </article>
          <article className="public-feature">
            <Sprout />
            <h3>{text.featureCare}</h3>
            <p>{text.featureCareText}</p>
          </article>
          <article className="public-feature">
            <Database />
            <h3>{text.featureHistory}</h3>
            <p>{text.featureHistoryText}</p>
          </article>
        </div>
      </section>

      <section className="public-band">
        <div>
          <h2>{text.bandTitle}</h2>
          <p>{text.bandText}</p>
        </div>
        <div className="public-contact">
          <ShieldCheck size={24} />
          <div>
            <strong>{text.contact}</strong>
            <a href="mailto:zaremabazarova11@gmail.com">
              zaremabazarova11@gmail.com
            </a>
          </div>
          <Mail size={24} />
        </div>
      </section>

      <footer className="public-footer">
        <p>{text.rights}</p>
        <p>{text.certificate}</p>
        <p>{text.city}</p>
      </footer>
    </main>
  );
}
