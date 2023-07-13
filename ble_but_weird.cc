#include <Arduino.h>
#include <ArduinoBLE.h>

void generate(char* arr);
class HardwareBLESerial {
public:
  HardwareBLESerial() {}
  void write(char* arr, int size);
  bool beginAndSetupBLE(const char* name);
  operator bool();

private:
  HardwareBLESerial(HardwareBLESerial const& other) = delete;  // disable copy constructor
  void operator=(HardwareBLESerial const& other) = delete;    // disable assign constructor
  BLEService uartService = BLEService("12345678-1234-1234-1234-123456789abc");
  BLECharacteristic transmitCharacteristic = BLECharacteristic("87654321-4321-4321-4321-bac987654321", BLERead | BLEWrite | BLENotify, 200); // Increase characteristic value length to 1024
}; //the maximum bytes per connection cycle is 200 bytes, arduino takes time to ditch the non-used data

bool HardwareBLESerial::beginAndSetupBLE(const char* name) {
  if (!BLE.begin()) { return false; }
  BLE.setLocalName(name);
  BLE.setDeviceName(name);
  BLE.setAdvertisedService(uartService);
  uartService.addCharacteristic(transmitCharacteristic);
  BLE.addService(uartService);
  BLE.advertise();
  return true;
}

void HardwareBLESerial::write(char* arr, int size) {
  if(size <= 0)
    return;
  generate(arr);
  this->transmitCharacteristic.writeValue(arr, strlen(arr)); 
  if (BLE.connected()) {
    this->transmitCharacteristic.broadcast(); 
  }
  this->write(arr, size-1);
}

HardwareBLESerial::operator bool() {
  return BLE.connected();
}

HardwareBLESerial bleSerial;

char array[200]; 

void generate(char* arr) {
  for (int i = 0; i < 200; i++)
    arr[i] = 'A' + (rand() % 26); 
  arr[199] = '\0'; 
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  while (!bleSerial.beginAndSetupBLE("Echo")){
    Serial.println("Failed to set up BLE!");
  }
  Serial.println("Setup Done!");
}

void loop() {
  BLEDevice central = BLE.central();
  if (central) {
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("Connected!");
    while (central.connected()) {
      bleSerial.write(array, 1024);
    }
    Serial.println("Disconnected!");
    digitalWrite(LED_BUILTIN, LOW);
  }
}
