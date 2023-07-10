#include <ArduinoBLE.h>

class HardwareBLESerial {
public:
  HardwareBLESerial() {}
  void write(char** arr, int size);
  bool beginAndSetupBLE(const char* name);
  operator bool();

private:
  HardwareBLESerial(HardwareBLESerial const& other) = delete;  // disable copy constructor
  void operator=(HardwareBLESerial const& other) = delete;    // disable assign constructor
  BLEService uartService = BLEService("12345678-1234-1234-1234-123456789abc");
  BLECharacteristic transmitCharacteristic = BLECharacteristic("87654321-4321-4321-4321-bac987654321", BLERead | BLEWrite | BLENotify, 1024); // Increase characteristic value length to 1024
};

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

void HardwareBLESerial::write(char** arr, int size) {
  if(size <= 0)
    return;
  this->transmitCharacteristic.writeValue(*arr, strlen(*arr)); 
  if (BLE.connected()) {
    this->transmitCharacteristic.broadcast(); 
  }
  delay(100);
  this->write(arr+1, size-1);
}

HardwareBLESerial::operator bool() {
  return BLE.connected();
}

HardwareBLESerial bleSerial;

char* array[1024]; 

void generate(char* arr) {
  for (int i = 0; i < 1024; i++)
    arr[i] = 'A' + (rand() % 26); 
  arr[1023] = '\0'; 
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  while (!bleSerial.beginAndSetupBLE("Echo"))
    Serial.println("Failed to set up BLE!");
  Serial.println("Setup Done!");
}

void loop() {
  BLEDevice central = BLE.central();
  auto fill = [] (char** arr){
    for(int i = 0; i<1024; i++){
      arr[i] = (char*)malloc(1024 * sizeof(char));
      generate(arr[i]);
    }
  };
  if (central) {
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("Connected!");
    fill(array);
    while (central.connected()) {
      bleSerial.write(array, 1024);
      delay(1000);
    }
    Serial.println("Disconnected!");
    digitalWrite(LED_BUILTIN, LOW);
  }
}