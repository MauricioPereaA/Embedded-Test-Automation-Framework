#include <ArduinoJson.h>
#include <Servo.h>
#include <LiquidCrystal.h>

const int JSON_BUFFER_SIZE = 256;

// Configuration of LCD pines
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

Servo myservo;

void setup() {
  Serial.begin(9600);
  myservo.attach(10);
  lcd.begin(16, 2);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    lcd.clear();
    lcd.print(command);

    if (command.startsWith("DO")) {
      digitalWriteCommand(command);
    } else if (command.startsWith("DI")) {
      digitalReadCommand(command);
    } else if (command.startsWith("AN")) {
      analogReadCommand(command);
    } else if (command.startsWith("servo")) {
      servoCommand(command);
    } else if (command == "$INFO") {
      sendInfo();
    } else {
      Serial.println("Message: " + command);
    }
  }
}

void digitalWriteCommand(String command) {
  int separator1 = command.indexOf(',');
  int separator2 = command.lastIndexOf(',');

  int pin = command.substring(separator1 + 1, separator2).toInt();
  int value = command.substring(separator2 + 1).toInt();

  pinMode(pin, OUTPUT);
  digitalWrite(pin, value);
  Serial.println("ACK");
}

void digitalReadCommand(String command) {
  int separator1 = command.indexOf(',');

  int pin = command.substring(separator1 + 1).toInt();

  pinMode(pin, INPUT);
  int value = digitalRead(pin);
  Serial.println(value);
}

void analogReadCommand(String command) {
  int separator1 = command.indexOf(',');

  int pin = command.substring(separator1 + 1).toInt();

  pinMode(pin, INPUT);
  float value = analogRead(pin) * (5.0 / 1023.0);
  Serial.println(value, 2);
}

void sendInfo() {
  StaticJsonDocument<JSON_BUFFER_SIZE> jsonDoc;

  jsonDoc["Procesador"] = "ATMEL MEGA2560";
  jsonDoc["Modelo de Unidad"] = "2560x333";
  jsonDoc["Version de Firmware"] = "2305.01.23";
  jsonDoc["Power State"] = "ON";
  jsonDoc["Status"] = "OK";

  serializeJson(jsonDoc, Serial);
  Serial.println();
}

void servoCommand(String command) {
  int separator1 = command.indexOf(',');

  int angle = command.substring(separator1 + 1).toInt();

  myservo.write(angle);
  Serial.println("ACK");
}
