#include "Arduino.h"
#include "SoilMoisture.h"
#include "DHT.h"
#include "LDR.h"

// Pin definitions.
#define SOILMOISTURE_5V_PIN_SIG A1
#define DHT_PIN_DATA 2
#define LDR_PIN_SIG A3

// Use DHT22 here if the physical sensor is DHT22 instead of DHT11.
#define DHTTYPE DHT11

const unsigned long SERIAL_BAUD_RATE = 9600;
const unsigned long READ_INTERVAL_MS = 5000;

SoilMoisture soilMoisture_5v(SOILMOISTURE_5V_PIN_SIG);
DHT dht(DHT_PIN_DATA, DHTTYPE);
LDR ldr(LDR_PIN_SIG);

unsigned long lastReadAt = 0;

void printNullableFloat(float value)
{
    if (isnan(value))
    {
        Serial.print(F("null"));
    }
    else
    {
        Serial.print(value, 1);
    }
}

void printSensorReading()
{
    int soilRaw = soilMoisture_5v.read();
    float humidity = dht.readHumidity();
    float temperature = dht.readTempC();
    int lightRaw = ldr.read();

    Serial.print(F("{\"soil_raw\":"));
    Serial.print(soilRaw);
    Serial.print(F(",\"humidity\":"));
    printNullableFloat(humidity);
    Serial.print(F(",\"temperature\":"));
    printNullableFloat(temperature);
    Serial.print(F(",\"light_raw\":"));
    Serial.print(lightRaw);
    Serial.println(F("}"));
}

void setup()
{
    Serial.begin(SERIAL_BAUD_RATE);
    dht.begin();
    lastReadAt = millis() - READ_INTERVAL_MS;
}

void loop()
{
    unsigned long now = millis();
    if (now - lastReadAt >= READ_INTERVAL_MS)
    {
        lastReadAt = now;
        printSensorReading();
    }
}
