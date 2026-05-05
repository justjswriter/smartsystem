/**
 * Plant monitor — ESP32 (Arduino IDE)
 * Soil moisture: analog GPIO 34, LDR: GPIO 35, DHT: GPIO 4
 * Posts JSON to POST /api/v1/ingest/sensors/{device_id}/data every 10s
 * with X-Device-Token authentication.
 *
 * Libraries: DHT sensor library (Adafruit) + Adafruit Unified Sensor
 * Board: select your ESP32 variant under Tools
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include "DHT.h"

// ============ Wi-Fi and backend (change for your network / deployment) ============
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// HTTP/HTTPS origin only, no path. The sketch appends /api/v1/ingest/sensors/{device_id}/data.
//
// — Production / class demo: set this to your deployed API base (e.g. "https://your-api.onrender.com"
//   from Render or Railway). No path after the host.
// — Local testing: run uvicorn on your PC, then use this machine's LAN IP, NOT "localhost" or
//   127.0.0.1 (the ESP32 cannot reach your computer's "localhost"). Example: "http://192.168.1.20:8001"
//   (same Wi‑Fi, port must match your running backend).
// For HTTPS, cert validation is disabled below for demo use; pin a proper CA in production.
const char* BACKEND_BASE  = "http://192.168.0.0:8001";

// One-time token returned by POST /api/v1/sensors or token rotation endpoint.
const char* DEVICE_TOKEN = "replace_with_device_token";

// Register the same id in the backend sensors table.
const char* DEVICE_ID = "esp32-plant-001";

// ============== Pins (ESP32) ======================================================
#define PIN_SOIL   34   // soil moisture (ADC1)
#define PIN_LDR    35   // light sensor
#define DHT_PIN     4
#define DHT_TYPE DHT11  // change to DHT22 if you use DHT22

DHT dht(DHT_PIN, DHT_TYPE);

// ================= Interval ======================================================
const unsigned long POST_INTERVAL_MS = 10000;
unsigned long lastPost = 0;

// Forward declarations
void connectWifi();
void sendSample(int soilRaw, int lightRaw, float t, float h);
float moisturePercentFromRaw(int raw);
float lightLuxFromRaw(int raw);
float clampf(float value, float minValue, float maxValue);

void setup() {
  Serial.begin(115200);
  delay(200);
  dht.begin();
  analogSetAttenuation(ADC_11db);  // 0–~3.3V range on most ESP32
  connectWifi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost; reconnecting...");
    connectWifi();
  }

  unsigned long now = millis();
  if (now - lastPost < POST_INTERVAL_MS) {
    return;
  }
  lastPost = now;

  int soilRaw = analogRead(PIN_SOIL);
  int lightRaw = analogRead(PIN_LDR);

  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (isnan(h) || isnan(t)) {
    Serial.println("DHT read failed; skip POST this cycle (soil/LDR still read above).");
    return;
  }

  sendSample(soilRaw, lightRaw, t, h);
}

void connectWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("OK, IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi connect failed, will retry in loop");
  }
}

void sendSample(int soilRaw, int lightRaw, float t, float h) {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }

  float moisture = moisturePercentFromRaw(soilRaw);
  float light = lightLuxFromRaw(lightRaw);

  String url = String(BACKEND_BASE) + "/api/v1/ingest/sensors/" + String(DEVICE_ID) + "/data";
  String body = "{";
  body += "\"moisture\":" + String(moisture, 1) + ",";
  body += "\"temperature\":" + String(t, 1) + ",";
  body += "\"humidity\":" + String(h, 1) + ",";
  body += "\"light\":" + String(light, 1);
  body += "}";

  Serial.println("POST body:");
  Serial.println(body);

  HTTPClient http;
  if (url.startsWith("https")) {
    WiFiClientSecure client;
    client.setInsecure();  // demo only: skip cert verification
    if (!http.begin(client, url)) {
      Serial.println("http.begin failed");
      return;
    }
  } else {
    WiFiClient client;
    if (!http.begin(client, url)) {
      Serial.println("http.begin failed");
      return;
    }
  }

  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);
  int code = http.POST(body);
  Serial.print("Response code: ");
  Serial.println(code);
  if (code > 0) {
    String payload = http.getString();
    if (payload.length() > 0) {
      Serial.println(payload);
    }
  } else {
    Serial.print("Error: ");
    Serial.println(http.errorToString(code));
  }
  http.end();
}

float moisturePercentFromRaw(int raw) {
  // Adjust these calibration points for your sensor:
  // lower raw value is typically wetter on common capacitive sensors.
  const int wetRaw = 1200;
  const int dryRaw = 3200;
  float percent = (float)(dryRaw - raw) * 100.0f / (float)(dryRaw - wetRaw);
  return clampf(percent, 0.0f, 100.0f);
}

float lightLuxFromRaw(int raw) {
  // Simple linear mapping for LDR ADC range to approximate lux.
  return clampf(((float)raw / 4095.0f) * 1000.0f, 0.0f, 1000.0f);
}

float clampf(float value, float minValue, float maxValue) {
  if (value < minValue) return minValue;
  if (value > maxValue) return maxValue;
  return value;
}
