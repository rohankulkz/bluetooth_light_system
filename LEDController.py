import asyncio
import os
import time
import ast
from bleak import BleakScanner, BleakClient

class LEDController:
    def __init__(self, char_uuid="FFD9"):
        self.char_uuid = char_uuid
        self.manual = True
        self.step = 0
        self.proceed = True
        self.cmds = []
        self.stepmax = 0
        self.validColours = {
            'red': [255, 0, 0], 'green': [0, 255, 0], 'blue': [0, 0, 255],
            'yellow': [255, 255, 0], 'cyan': [0, 255, 255], 'magenta': [255, 0, 255],
            'black': [0, 0, 0], 'white': [255, 255, 255], 'gray': [128, 128, 128],
            'orange': [255, 45, 0], 'purple': [128, 0, 128], 'pink': [255, 0, 40],
            'brown': [165, 42, 42], 'lime': [0, 255, 0], 'navy': [0, 0, 128],
            'gold': [255, 215, 0], 'silver': [192, 192, 192], 'teal': [0, 128, 128],
            'maroon': [128, 0, 0], 'olive': [128, 128, 0], 'skyblue': [135, 206, 235],
            'violet': [238, 130, 238], 'indigo': [75, 0, 130], 'coral': [255, 127, 80]
        }
        self.validPulseCode = {
            'gb': 0x2F, 'rb': 0x2E, 'rg': 0x2D, 'white': 0x2C, 'purple': 0x2B,
            'cyan': 0x2A, 'yellow': 0x29, 'blue': 0x28, 'green': 0x27, 'red': 0x26,
            'rgb': 0x61, 'all': 0x25
        }
        self.validFlashCode = {
            'rgb': 0x62, 'all': 0x38, 'white': 0x37, 'purple': 0x36, 'cyan': 0x35,
            'yellow': 0x34, 'blue': 0x33, 'green': 0x32, 'red': 0x31, 'eyesore': 0x30
        }

    async def scan_and_select_device(self):
        print("🔍 Scanning for BLE devices...")
        devices = await BleakScanner.discover()
        for i, device in enumerate(devices):
            print(f"[{i}] {device.name or 'Unknown'} - {device.address}")
        idx = int(input("Enter the number of the device to connect: "))
        return devices[idx].address

    def extract_cmd(self, line):
        line = line.split()
        if not line:
            return "red", 0
        delay = float(line[0])
        cmd = " ".join(line[1:])
        return cmd, delay

    def is_valid_repeat(self, dataList):
        return dataList[0] in ['r', 'repeat'] and dataList[1].isnumeric()

    def is_valid_flash(self, dataList):
        return len(dataList) >= 2 and dataList[0] in ['f', 'flash'] and dataList[1] in self.validFlashCode

    def is_valid_pulse(self, dataList):
        return len(dataList) >= 2 and dataList[0] in ['p', 'pulse'] and dataList[1] in self.validPulseCode

    def is_valid_hex(self, dataList):
        return len(dataList) == 3 and all(0 <= int(i) < 256 for i in dataList)

    def set_interval(self, dataList):
        if len(dataList) >= 3 and dataList[2].isnumeric():
            var = int(dataList[2])
            return 0x0 << 4 | (10 - var if 1 <= var <= 10 else 0x00)
        return 0x00

    async def repeat(self, client, datalist, times):
        for _ in range(times):
            for j in ast.literal_eval(datalist):
                cmd, delay = self.extract_cmd(j)
                if self.proceed:
                    await self.send_cmd(client, cmd)
                    time.sleep(delay)
                else:
                    break

    async def send_cmd_interface(self, message):
        print(message)
        async with BleakClient(address) as client:
            await self.send_cmd(client, "red")

    async def send_cmd(self, client, base, is_manual=False):
        baseList = base.split()
        # print(base)
        if base == 'on':
            await client.write_gatt_char(self.char_uuid, bytearray([0xcc, 0x23, 0x33]))
        elif base == 'off':
            await client.write_gatt_char(self.char_uuid, bytearray([0xcc, 0x24, 0x33]))
        elif self.is_valid_pulse(baseList):
            data_packet = bytearray([0xbb, self.validPulseCode[baseList[1]], self.set_interval(baseList), 0x44])
            await client.write_gatt_char(self.char_uuid, data_packet)
        elif self.is_valid_flash(baseList):
            data_packet = bytearray([0xbb, self.validFlashCode[baseList[1]], self.set_interval(baseList), 0x44])
            await client.write_gatt_char(self.char_uuid, data_packet)
        elif self.is_valid_repeat(baseList) and is_manual:
            await self.repeat(client, base[base.find('['):], int(baseList[1]))
        else:
            try:
                if base in self.validColours:
                    r, g, b = self.validColours[base]
                elif self.is_valid_hex(baseList):
                    r, g, b = map(int, baseList)
                else:
                    print("Invalid Command. Try Again!")
                    return
                data_packet = bytearray([0x56, r, g, b, 0x00, 0xf0, 0xaa])
                await client.write_gatt_char(self.char_uuid, data_packet)
            except Exception as e:
                print(f"❌ Failed to send color data: {str(e)}")

    async def interactive_control(self, address):
        async with BleakClient(address) as client:
            while True:
                if self.manual:
                    user_input = input("Enter Command (or 'exit' to quit): ").lower()
                    if user_input in ['exit', 'quit']:
                        break
                    await self.send_cmd(client, user_input, True)
                else:
                    if self.step != self.stepmax:
                        base, delay = self.extract_cmd(self.cmds[self.step])
                        self.step += 1
                        time.sleep(delay)
                        await self.send_cmd(client, base)
                    else:
                        self.step = 0
                        self.manual = True


