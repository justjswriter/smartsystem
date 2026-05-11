import { useMemo, useState } from "react";
import { Bell } from "lucide-react";
import { NavLink } from "react-router-dom";
import { useI18n } from "../i18n";
import type { Notification } from "../types";

type NotificationsPanelProps = {
  notifications: Notification[];
  onMarkRead: (notificationId: number) => Promise<void>;
  onMarkAllRead: () => Promise<void>;
};

export function NotificationsPanel({
  notifications,
  onMarkRead,
  onMarkAllRead,
}: NotificationsPanelProps) {
  const { t, label, formatDateTime } = useI18n();
  const [open, setOpen] = useState(false);
  const unreadCount = notifications.filter((item) => !item.read_at).length;
  const latest = useMemo(() => notifications.slice(0, 8), [notifications]);

  function renderText(key: string, fallback: string | null, params: Notification["params"]) {
    const translated = t(key, params ?? undefined);
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
                <strong>{renderText(notification.title_key, notification.title, notification.params)}</strong>
                <span>{renderText(notification.message_key, notification.message, notification.params)}</span>
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
