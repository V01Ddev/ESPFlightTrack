#include <Wire.h>
#include <MS5611.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>

// MS5611 / GY-63
MS5611 ms5611(0x77);  // change to 0x76 if needed

// MPU6050
Adafruit_MPU6050 mpu;

// Filtered angles
float roll = 0.0;
float pitch = 0.0;
float yaw = 0.0;

// Timing
unsigned long lastTime = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin(21, 22);

  Serial.println("Starting sensors...");

  if (!ms5611.begin()) {
    Serial.println("MS5611 / GY-63 not found. Check wiring and I2C address.");
    while (1) delay(1000);
  }
  Serial.println("GY-63 (MS5611) found!");

  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) delay(1000);
  }
  Serial.println("MPU6050 found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("All sensors initialized.");
  Serial.println("Format for Serial Plotter:");
  Serial.println("roll:0 pitch:0 yaw:0 altitude:0");
  Serial.println("-----------------------------");

  lastTime = millis();
}

void loop() {
  // ===== Read MS5611 =====
  float altitudeM = 0.0;

  int result = ms5611.read();
  if (result == MS5611_READ_OK) {
    float pressurePa = ms5611.getPressure() * 100.0;
    const float seaLevelPressure = 101325.0;
    altitudeM = 44330.0 * (1.0 - pow(pressurePa / seaLevelPressure, 0.1903));
  }

  // ===== Read MPU6050 =====
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // Time delta
  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0;
  lastTime = now;

  if (dt <= 0 || dt > 1.0) dt = 0.01;

  // Accelerometer angles
  float accRoll = atan2(a.acceleration.y, a.acceleration.z) * 180.0 / PI;
  float accPitch = atan2(-a.acceleration.x,
                         sqrt(a.acceleration.y * a.acceleration.y + a.acceleration.z * a.acceleration.z))
                   * 180.0 / PI;

  // Gyro rates (convert rad/s to deg/s)
  float gyroX = g.gyro.x * 180.0 / PI;
  float gyroY = g.gyro.y * 180.0 / PI;
  float gyroZ = g.gyro.z * 180.0 / PI;

  // Complementary filter
  const float alpha = 0.98;
  roll = alpha * (roll + gyroX * dt) + (1.0 - alpha) * accRoll;
  pitch = alpha * (pitch + gyroY * dt) + (1.0 - alpha) * accPitch;

  // Yaw from gyro only -> drifts over time
  yaw += gyroZ * dt;

  // Print in Serial Plotter-friendly format
  Serial.print("roll:");
  Serial.print(roll, 2);
  Serial.print(" pitch:");
  Serial.print(pitch, 2);
  Serial.print(" yaw:");
  Serial.print(yaw, 2);
  Serial.print(" altitude:");
  Serial.println(altitudeM, 2);

  delay(20);  // ~50 Hz
}