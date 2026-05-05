import { Sensors } from "../components/Sensors";
import { useAppState } from "../context/AppStateContext";

export function SettingsPage() {
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
          <h1 className="page-title">Settings</h1>
          <p className="muted page-lead">Register sensors and attach them to plants (Arduino-ready).</p>
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
