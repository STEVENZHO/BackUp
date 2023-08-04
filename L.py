import pygatt
from binascii import hexlify
import time

addresses = ["E0:5A:1B:CA:00:42", "E0:5A:1B:CB:03:92", "44:09:E7:36:CE:8F", "01:2F:7B:97:7E:AF"]  # replace with your devices addresses
total_bytes_received = 0
start_time = time.time()

def data_handler(sender, data):
    global total_bytes_received, start_time
    total_bytes_received += len(data)
    current_time = time.time()
    elapsed_time = current_time - start_time
    transfer_rate = (total_bytes_received / elapsed_time) / 1024  # Convert to KB/s
    print(f"Total data received: {total_bytes_received / 1024} KB, Transfer rate: {transfer_rate} KB/s") 

adapter = pygatt.GATTToolBackend()

try:
    adapter.start()
    for index, address in enumerate(addresses):
        try:
            print(f"Connecting to {address}...")
            device = adapter.connect(address)
            device.subscribe("beb5483e-36e1-4688-b7f5-ea07361b26a8", callback=data_handler)
            while total_bytes_received < 1e6:  # while total data received is less than 1 MB
                time.sleep(1)  # Wait and let the handler receive data
            device.disconnect()
        except Exception as e:
            print(f"Failed to connect to {address}: {e}")
finally:
    adapter.stop()
