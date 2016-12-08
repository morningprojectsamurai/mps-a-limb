#include <ArduinoJson.h>

int ACC_X_PIN = 3;
int ACC_Y_PIN = 4;
int ACC_Z_PIN = 5;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  long accX = analogRead(ACC_X_PIN);
  long accY = analogRead(ACC_Y_PIN);
  long accZ = analogRead(ACC_Z_PIN);

  StaticJsonBuffer<200> outputJsonBuffer;
  JsonObject& outputJson = outputJsonBuffer.createObject();
  outputJson["accX"] = 0.0049 * accX - 2.5 + 0.02;
  outputJson["accY"] = 0.0049 * accY - 2.5 + 0.12;
  outputJson["accZ"] = 0.0049 * accZ - 2.5 + 0.01;

  outputJson.printTo(Serial);
  Serial.println();
}
