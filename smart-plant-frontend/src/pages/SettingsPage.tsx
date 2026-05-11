import { Sensors } from "../components/Sensors";
import { useAppState } from "../context/AppStateContext";
import { useI18n } from "../i18n";

export function SettingsPage() {
  const { t } = useI18n();
  const {
    plants,
    sensors,
    isSensorsLoading,
    sensorsError,
    loadSensors,
    createSensorEntry,
    rotateSensorDeviceToken,
    attachSensorToPlant,
    detachSensorFromPlant,
  } = useAppState();

  return (
    <div className="page-stack">
      <div className="page-head">
        <div>
          <h1 className="page-title">{t("settings.title")}</h1>
          <p className="muted page-lead">{t("settings.subtitle")}</p>
        </div>
      </div>
      <Sensors
        plants={plants}
        sensors={sensors}
        isLoading={isSensorsLoading}
        error={sensorsError}
        onRefresh={() => loadSensors()}
        onCreate={createSensorEntry}
        onAttach={attachSensorToPlant}
        onDetach={detachSensorFromPlant}
        onRotateToken={rotateSensorDeviceToken}
      />
    </div>
  );
}
