#include <Arduino.h>
#include <DHT.h>
#include <Adafruit_Sensor.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <PubSubClient.h>

// DEFINICIÓN DE PINES

#define DHT_PIN 17
#define DHTTYPE DHT11
#define WATER_PIN 35
#define HUMIDITY_PIN 34
#define INTERVAL 60000
#define HUMIDITY_LIMIT 2000
#define RELAY_PIN 13

//  CREDENCIALES WIFI

const char* SSID = "keco_wifi";
const char* PASSWORD = "kevincr28";

// BROKER INFO (IP DE LA MAQUINA CORRIENDO EL BROKER)

const char* BROKER_URL = "192.168.191.196";
const int BROKER_PORT = 1883;

// TOPICOS

const char* WATER_LEVEL_TOPIC = "water_level";
const char* HUMIDITY_TEMPERATURE_TOPIC = "humidity_temperature";
const char* WATERED_TOPIC = "watered";
const char* INBOUND_TOPIC = "water_button";

// INICIALIZACIÓN DE VARIABLES

WiFiClient espClient;
PubSubClient client(espClient);

int WaterValue = 0;
int HumidityValue = 0;
DHT dht(DHT_PIN, DHTTYPE);
unsigned long previousMillis = 0;

// FUNCIONES

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    messageTemp += (char)payload[i];
  }
  Serial.println(messageTemp);

  // Activar el relay 500 milisegundos

  digitalWrite(RELAY_PIN, HIGH);
  delay(500);
  digitalWrite(RELAY_PIN, LOW);
}

void setup_wifi() {
  WiFi.begin(SSID, PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Serial.println("Connected to WiFi");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESPIClient")) {
      Serial.println("connected");
      client.subscribe(INBOUND_TOPIC);
    } else {
      Serial.print("failed connection");
      delay(5000);
    }
  }
}

void setup() {

  // Inicio de la conexion a wifi y al broker

  setup_wifi();
  client.setServer(BROKER_URL, BROKER_PORT);
  client.setCallback(callback);

  // inicio de los sensores

  Serial.begin(9600);
  dht.begin();
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
}


void loop() {

  // Conectar a el broker

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // sensor de agua

  delay(3000);
  WaterValue = analogRead(WATER_PIN);
  Serial.print("Water Level: ");
  Serial.println(WaterValue);

  client.publish(WATER_LEVEL_TOPIC, String(WaterValue).c_str());


  //sensor de humedad

  HumidityValue = analogRead(HUMIDITY_PIN);
  Serial.print("Soil Humidity: ");
  Serial.println(HumidityValue);

  //sensor de temperatura

  float temperature = dht.readTemperature();
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println("°C");

  String payload = String(HumidityValue) + ", " + String(temperature);
  client.publish(HUMIDITY_TEMPERATURE_TOPIC, payload.c_str());

  // Activar el relay si la humedad es baja

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= INTERVAL) {
    previousMillis = currentMillis;

    if (HumidityValue > HUMIDITY_LIMIT) {
      digitalWrite(RELAY_PIN, HIGH);
      if (temperature < 25) {
        delay(500);
      } else if (temperature < 32) {
        delay(600);
      } else {
        delay(800);
      }
      client.publish(WATERED_TOPIC, "Watered");
      digitalWrite(RELAY_PIN, LOW);
    }
  }

}
