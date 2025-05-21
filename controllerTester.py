import asyncio

from bleak import BleakClient, BleakScanner

from ComboSequence import ComboSequence
from FadeSequence import FadeSequence
from LEDController import LEDController
from LightRunner import LightRunner
from SingleFlash import SingleFlash
from StrobeSequence import StrobeSequence


async def run_multiple():
    controller = LEDController(char_uuid="FFD9")
    devices = await BleakScanner.discover()
    print("devices: " + str(devices))

    address = ""

    for i in range(len(devices)):
        if devices[i].name != None and devices[i].name.__contains__("QHM-"):
            address = devices[i]
            print(address)
            break

    async with BleakClient(address) as client:

        colors = ["white", "black"]

        i = 0

        # await asyncio.sleep(3)

        runner = LightRunner(client, controller)

        await runner.start()

        await runner.setCommand(SingleFlash("f white", 3))

        await asyncio.sleep(3)


        for i in range(40):
            # await runner.setCommand(ComboSequence([FadeSequence([255, 0, 225], [0, 255, 0], 2), SingleFlash("black", 3)]))

            await runner.playCommand((ComboSequence([FadeSequence([255, 0, 225], [0, 255, 0], 0.5), SingleFlash("white", 3)])), 5)

            # await asyncio.sleep(3)


        await asyncio.sleep(100)

        await client.disconnect()

        quit()

        # print("Properly disconnecting Bluetooth")


asyncio.run(run_multiple())
