#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

std::string sentence;
hw_timer_t *TimerCfg = NULL;
class MyServerCallbacks: public BLEServerCallbacks {
    public:
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
    }
    static bool deviceConnected;
};

bool MyServerCallbacks::deviceConnected = false;

void generate(std::string& sentence, int number){
  sentence.clear();
  for(int i = 0; i<number;i++)
    sentence += 'A' + rand()%26;
}

void setup() {
  Serial.begin(115200);
  TimerCfg = timerBegin(0, 80, true);
  timerAttachInterrupt(TimerCfg, &ISR, true);
  timerAlarmWrite(TimerCfg, 50000, true);
  timerAlarmEnable(TimerCfg);

  // Create the BLE Device
  BLEDevice::init("ESP32_BLE");
  
  // Set MTU size
  BLEDevice::setMTU(517);
  
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
                     CHARACTERISTIC_UUID,
                     BLECharacteristic::PROPERTY_READ |
                     BLECharacteristic::PROPERTY_WRITE |
                     BLECharacteristic::PROPERTY_NOTIFY
                   );

  pCharacteristic->addDescriptor(new BLE2902());

  pService->start();

  pServer->getAdvertising()->start();
  Serial.println("Waiting a client connection to notify...");
}

void loop() {
  if (MyServerCallbacks::deviceConnected) {
    while (MyServerCallbacks::deviceConnected) { // while connected, keep sending
      generate(sentence, 510);
      pCharacteristic->setValue(sentence);
      pCharacteristic->notify();
    }
  }
}
