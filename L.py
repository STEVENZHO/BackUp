from bluepy.btle import Peripheral, DefaultDelegate
import time
import threading

addresses = ["E0:5A:1B:CA:00:42", "E0:5A:1B:CB:03:92", "44:09:E7:36:CE:8F", "01:2F:7B:97:7E:AF"]
characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
total_bytes_received = [0, 0, 0, 0]
start_time = None

class MyDelegate(DefaultDelegate):
    def __init__(self, index):
        DefaultDelegate.__init__(self)
        self.index = index

    def handleNotification(self, cHandle, data):
        global total_bytes_received, start_time
        total_bytes_received[self.index] += len(data)
        current_time = time.time()
        elapsed_time = current_time - start_time
        transfer_rate = (total_bytes_received[self.index] / elapsed_time) / 1024
        print(f"Device {self.index} - Total data received: {total_bytes_received[self.index] / 1024} KB, Transfer rate: {transfer_rate} KB/s")

def run(address, index):
    global start_time
    p = Peripheral()
    p.setDelegate(MyDelegate(index))

    try:
        p.connect(address)
        start_time = start_time or time.time()
        svc = p.getServiceByUUID(characteristic_uuid)

        while total_bytes_received[index] < 1e6:
            if p.waitForNotifications(1.0):
                continue

            print("Waiting...")

    except Exception as e:
        print(e)

    finally:
        p.disconnect()

# Run the run function for each address concurrently
threads = []

for i, address in enumerate(addresses):
    thread = threading.Thread(target=run, args=(address, i))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()
