import { useMemo, useState } from "react";
import { Bell } from "lucide-react";
import { NavLink } from "react-router-dom";
import { useI18n } from "../i18n";
import type { Notification, Plant } from "../types";

type NotificationsPanelProps = {
  notifications: Notification[];
  plants: Plant[];
  onMarkRead: (notificationId: number) => Promise<void>;
  onMarkAllRead: () => Promise<void>;
};

export function NotificationsPanel({
  notifications,
  plants,
  onMarkRead,
  onMarkAllRead,
}: NotificationsPanelProps) {
  const { t, label, formatDateTime } = useI18n();
  const [open, setOpen] = useState(false);
  const unreadCount = notifications.filter((item) => !item.read_at).length;
  const latest = useMemo(() => notifications.slice(0, 8), [notifications]);

  function plantNameFor(notification: Notification) {
    const fromParams = notification.params?.plant_name;
    if (typeof fromParams === "string" && fromParams.trim()) {
      return fromParams;
    }
    const plant = plants.find((item) => item.id === notification.related_plant_id);
    return plant?.name ?? null;
  }

  function renderText(notification: Notification, key: string, fallback: string | null) {
    const params = notification.params;
    const plantName = plantNameFor(notification);
    const normalizedParams = params
      ? {
          ...params,
          plant_name: plantName ?? params.plant_name,
          metric: typeof params.metric === "string" ? label("metric", params.metric) : params.metric,
        }
      : plantName
        ? { plant_name: plantName }
        : undefined;
    const translated = t(key, normalizedParams);
    return translated === key ? fallback ?? translated : translated;
  }

  function linkFor(notification: Notification) {
    if (notification.related_plant_id) {
      return `/plants/${notification.related_plant_id}`;
    }
    return "/alerts";
  }

  return (
    <div className="notification-menu">
      <button
        type="button"
        className="icon-btn"
        title={t("notifications.title")}
        aria-label={t("notifications.title")}
        onClick={() => setOpen((current) => !current)}
      >
        <Bell size={20} />
        {unreadCount > 0 ? <span className="notification-count">{unreadCount}</span> : null}
      </button>

      {open ? (
        <div className="notification-panel">
          <div className="notification-panel-head">
            <h3>{t("notifications.title")}</h3>
            <button type="button" onClick={() => void onMarkAllRead()} disabled={unreadCount === 0}>
              {t("notifications.markAllRead")}
            </button>
          </div>

          {latest.length === 0 ? <p className="muted">{t("notifications.empty")}</p> : null}

          {latest.map((notification) => (
            <div
              key={notification.id}
              className={`notification-item ${notification.read_at ? "read" : "unread"}`}
            >
              <NavLink
                to={linkFor(notification)}
                onClick={() => {
                  setOpen(false);
                  if (!notification.read_at) {
                    void onMarkRead(notification.id);
                  }
                }}
              >
                <strong>{renderText(notification, notification.title_key, notification.title)}</strong>
                <span>{renderText(notification, notification.message_key, notification.message)}</span>
              </NavLink>
              <div className="notification-meta">
                <span>{label("notificationSeverity", notification.severity)}</span>
                <span>{formatDateTime(notification.created_at)}</span>
              </div>
              {!notification.read_at ? (
                <button type="button" onClick={() => void onMarkRead(notification.id)}>
                  {t("notifications.markRead")}
                </button>
              ) : null}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
