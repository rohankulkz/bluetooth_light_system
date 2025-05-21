import asyncio
from bleak import BleakClient, BleakScanner

from LEDController import LEDController
from LightRunner import LightRunner
from LiveSequence import LiveSequence
from SingleFlash import SingleFlash


class LiveLightingApp:
    def __init__(self, device_name="BlackHole 2ch"):
        self.visualizer = LiveSequence(device_name=device_name)
        self.controller = LEDController(char_uuid="FFD9")
        self.current_state = 'black'
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def start(self):
        self.loop.create_task(self.visualizer.run())
        self.loop.create_task(self.poll_visualizer())
        self.loop.create_task(self.connect_and_run())

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            print("🎧 Exiting...")
        finally:
            self.loop.close()

    async def poll_visualizer(self):
        while True:
            await asyncio.sleep(1 / LiveSequence.freq)
            try:
                self.current_state = next(self.visualizer)
                # print(self.current_state)
            except StopIteration:
                self.current_state = 'black'

    async def connect_and_run(self):
        devices = await BleakScanner.discover()
        print("🔍 Devices found:", devices)

        address = None
        for dev in devices:
            if dev.name and "QHM-" in dev.name:
                address = dev
                print("✅ Found QHM device:", address)
                break

        if not address:
            print("❌ No QHM device found.")
            return

        async with BleakClient(address) as client:

            laststate = "black"

            while True:
                await self.controller.send_cmd(client, self.current_state)
                laststate = self.current_state
                await asyncio.sleep(1 / LiveSequence.freq)


# Example usage
if __name__ == "__main__":
    app = LiveLightingApp(device_name="BlackHole 2ch")
    app.start()



