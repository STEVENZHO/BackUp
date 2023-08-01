import asyncio
from bleak import BleakClient
import time

address = "E0:5A:1B:CB:03:92"  # replace with your device address
characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"  # replace with your characteristic UUID
total_bytes_received = 0
start_time = None
MB = 1048576  # 1MB in bytes

async def run(address, loop):
    global total_bytes_received, start_time

    client = BleakClient(address, loop=loop)

    while True:
        try:
            await client.connect()
            start_time = time.time()
            while True:
                if total_bytes_received >= MB:  # If received 1MB or more, break loop
                    break
                value = await client.read_gatt_char(characteristic_uuid)
                total_bytes_received += len(value)
                current_time = time.time()
                elapsed_time = current_time - start_time
                transfer_rate = (total_bytes_received / elapsed_time) / 1024  # Convert to KB/s
                print(f"Data received: {len(value)} bytes, Total data: {total_bytes_received} bytes, Transfer rate: {transfer_rate} KB/s")
                await asyncio.sleep(1)  # Sleep for a while before next reading

        except Exception as e:
            print(e)
            pass

        finally:
            if client.is_connected:
                await client.disconnect()

        if total_bytes_received >= MB:  # If received 1MB or more, break loop
            break

    total_time = time.time() - start_time
    print(f"Time taken to receive 1MB of data: {total_time} seconds")

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, loop))
