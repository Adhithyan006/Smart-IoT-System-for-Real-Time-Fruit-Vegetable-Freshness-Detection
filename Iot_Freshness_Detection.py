#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <ESP8266WiFi.h>

#define DHTPIN D4
#define DHTTYPE DHT11
#define LED_PIN D3  
#define LED_RED D5

const float TEMP_THRESHOLD = 2;   // in °C
const float HUM_THRESHOLD  = 25;  

DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Wi-Fi credentials
const char* ssid = "YOUR_USERNAME";
const char* password = "YOUR_PASSWORD";

WiFiServer server(80); // TCP server on port 80

void setup() {
  Serial.begin(115200);

  // Initialize I2C
  Wire.begin(D2, D1);

  // Initialize LCD
  lcd.begin(16, 2);
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Sensor Initiated");
  delay(1000);

  dht.begin();
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Connected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.begin(); // start TCP server
}

void loop() {
  delay(2000);

  // Read DHT11 sensor
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    lcd.clear();
    lcd.print("Sensor Error!");
    return;
  }

  // Prepare data string
  String dataString = "Temp: " + String(temperature, 2) + "C  Hum: " + String(humidity, 2) + "%\n";

  // Print to Serial and LCD
  Serial.print(dataString);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(temperature, 2);
  lcd.print((char)223);
  lcd.print("C");
  lcd.setCursor(0, 1);
  lcd.print("Hum: ");
  lcd.print(humidity, 2);
  lcd.print("%");

  // LED warning
  if (temperature > TEMP_THRESHOLD || humidity > HUM_THRESHOLD) {
    digitalWrite(LED_PIN, LOW);
    digitalWrite(LED_RED, HIGH);  // Red LED ON
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("stay Alert");  
  } else {
    lcd.clear();
    digitalWrite(LED_PIN, HIGH);
    digitalWrite(LED_RED, LOW);
    lcd.print("Relax-enjoy"); // Green LED ON
  }

  // Check for incoming client
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");
    client.print(dataString); // send data to laptop
    client.stop();
    Serial.println("Client disconnected");
  }
}
