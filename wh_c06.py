# Use:
#
# 1. Start this script
#
#   > python wh_c06.py | tee xxx.csv
#
# 2. Turn on the crane scale - logging will commence immediately
# 3. Turn scale off - logging will pause
# 4. Restart script
#
# Make sure HOLD mode is turned off using the TARE button long-press menu
#
# In theory the WH-C06 refresh rate is 10Hz, but the BLE advertising
# is irregular and nowhere near this fast.

import asyncio
from bleak import BleakScanner
import time


async def discover():
    print("Scanning for devices...")
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Found: {device.name} ({device.address})")

#asyncio.run(discover())

def get_weight_from_bytes(bytes):
    # first 10 bytes are constant (at least for the one device i have)
    # 02 03 11 2a c0 19 11 22 e2 01
    #print(bytes.hex())
    wt =     (bytes[10] << 8) | bytes[11]
    stable = (bytes[14] & 0xf0 ) >> 4
    units = bytes[14] & 0x0f
    #print(wt, stable, units)

    assert stable==0, "HOLD enabled (using TARE long press : L_OF)"
    assert units==1, "not using kg"
    
    return wt*0.01 # kg


async def log():
    stop_event = asyncio.Event()

    # TODO: add something that calls stop_event.set()

    def callback(device, advertising_data):
        # TODO: do something with incoming data
        if device.name=="IF_B7":
            #print(device.name, advertising_data)
            #assert advertising_data.local_name=='IF_B7'
            data = advertising_data.manufacturer_data[256]
            wt = get_weight_from_bytes(data)
            #rssi = advertising_data.rssi  # signal strength
            print(",".join(map(str, (time.time(), wt, data.hex()))))

    async with BleakScanner(callback) as scanner:
        #...
        # Important! Wait for an event to trigger stop, otherwise scanner
        # will stop immediately.
        await stop_event.wait()

    # scanner stops when block exits
    #...



if __name__=="__main__":
    print("t, kg, raw")
    asyncio.run(log())
