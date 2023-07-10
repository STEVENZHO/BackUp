import asyncio
from bleak import BleakClient
import time

device_address = "01:2f:7b:97:7e:af"  # replace this with your device's address
characteristic_uuid = "87654321-4321-4321-4321-bac987654321"  # replace this with your characteristic's UUID
data_size = 0  # in bytes

async def run(address):
    global data_size
    client = BleakClient(address)

    def callback(sender: int, data: bytearray):
        global data_size
        data_size += len(data)
        print(f"Received data: {data}")

    print(f"Connecting to {address}...")
    await client.connect()
    print(f"Connected: {client.is_connected}")

    await client.start_notify(characteristic_uuid, callback)

    print("Receiving data for 10 seconds...")
    start_time = time.time()

    await asyncio.sleep(10)
    elapsed_time = time.time() - start_time
    await client.stop_notify(characteristic_uuid)
    await client.disconnect()

    data_rate = data_size / elapsed_time  # bytes per second

    print(f"Data rate: {data_rate} bytes/second")

loop = asyncio.get_event_loop()
loop.run_until_complete(run(device_address))
