from bluepy.btle import Peripheral, DefaultDelegate, BTLEException
import time

class MyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        global total_bytes_received, start_time
        total_bytes_received += len(data)
        current_time = time.time()
        elapsed_time = current_time - start_time
        transfer_rate = (total_bytes_received / elapsed_time) / 1024  # Convert to KB/s
        print(f"Total data received: {total_bytes_received / 1024} KB, Transfer rate: {transfer_rate} KB/s") 

addresses = ["E0:5A:1B:CA:00:42", "E0:5A:1B:CB:03:92", "44:09:E7:36:CE:8F", "01:2F:7B:97:7E:AF"]  # replace with your devices addresses
total_bytes_received = 0
start_time = time.time()

for index, address in enumerate(addresses):
    try:
        p = Peripheral(address)
        p.setDelegate(MyDelegate())

        services=p.getServices()
        for service in services:
            if service.uuid == "4fafc201-1fb5-459e-8fcc-c5c9c331914b":
                characteristics = service.getCharacteristics()
                for characteristic in characteristics:
                    if characteristic.uuid == "beb5483e-36e1-4688-b7f5-ea07361b26a8":
                        while total_bytes_received < 1e6: # while total data received is less than 1 MB
                            data = characteristic.read()
                            total_bytes_received += len(data)
                            current_time = time.time()
                            elapsed_time = current_time - start_time
                            transfer_rate = (total_bytes_received / elapsed_time) / 1024  # Convert to KB/s
                            print(f"Device {index} - Total data received: {total_bytes_received / 1024} KB, Transfer rate: {transfer_rate} KB/s") 
        p.disconnect()

    except BTLEException as e:
        print(e)
