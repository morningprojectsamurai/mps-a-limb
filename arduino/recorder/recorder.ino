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
  outputJson["accX"] = accX;
  outputJson["accY"] = accY;
  outputJson["accZ"] = accZ;

  outputJson.printTo(Serial);
  Serial.println();
}
