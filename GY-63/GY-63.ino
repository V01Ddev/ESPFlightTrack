#include <Wire.h>
#include <MS5611.h>

MS5611 ms5611(0x77);   // try 0x76 if this one doesn't work

void setup() {
  Serial.begin(115200);
  delay(1000);

  // ESP32 I2C pins
  Wire.begin(21, 22);

  if (!ms5611.begin()) {
    Serial.println("MS5611 / GY-63 not found. Check wiring and I2C address.");
    while (1) {
      delay(1000);
    }
  }

  Serial.println("GY-63 (MS5611) found!");
}

void loop() {
  // Read sensor
  int result = ms5611.read();

  if (result != MS5611_READ_OK) {
    Serial.print("Read error: ");
    Serial.println(result);
    delay(1000);
    return;
  }

  float temperatureC = ms5611.getTemperature();
  float pressurePa   = ms5611.getPressure();

  // Approx altitude from sea-level pressure
  const float seaLevelPressure = 101325.0; // Pa
  float altitudeM = 44330.0 * (1.0 - pow(pressurePa / seaLevelPressure, 0.1903));

  Serial.print("Temperature: ");
  Serial.print(temperatureC, 2);
  Serial.println(" C");

  Serial.print("Pressure: ");
  Serial.print(pressurePa, 2);
  Serial.println(" Pa");

  Serial.print("Altitude: ");
  Serial.print(altitudeM, 2);
  Serial.println(" m");

  Serial.println("---------------------");
  delay(1000);
}
