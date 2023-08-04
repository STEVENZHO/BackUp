import asyncio
from bleak import BleakClient
import time

addresses = ["E0:5A:1B:CA:00:42", "E0:5A:1B:CB:03:92", "44:09:E7:36:CE:8F", "01:2F:7B:97:7E:AF"]  # replace with your devices addresses
characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"  # replace with your characteristic UUID

total_bytes_received = [0, 0, 0, 0]
start_time = None

async def run(address, index, loop):
    global total_bytes_received, start_time

    client = BleakClient(address, loop=loop)
    
    try:
        await client.connect()
        start_time = time.time()

        while total_bytes_received[index] < 1e6:  # while total data received is less than 1 MB
            value = await client.read_gatt_char(characteristic_uuid)
            total_bytes_received[index] += len(value)
            current_time = time.time()
            elapsed_time = current_time - start_time
            transfer_rate = (total_bytes_received[index] / elapsed_time) / 1024  # Convert to KB/s
            print(f"Device {index} - Total data received: {total_bytes_received[index] / 1024} KB, Transfer rate: {transfer_rate} KB/s")  # short delay to avoid flooding
            
    except Exception as e:
        print(e)

    finally:
        if client.is_connected:
            await client.disconnect()

loop = asyncio.get_event_loop()

# Run the run function for each address concurrently
loop.run_until_complete(asyncio.gather(*(run(address, i, loop) for i, address in enumerate(addresses))))
