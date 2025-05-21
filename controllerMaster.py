import asyncio

from bleak import BleakClient, BleakScanner

from LEDController import LEDController


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

        colors = ["red", "green", "blue"]

        i = 0

        # await asyncio.sleep(3)

        while(i<25):
            await controller.send_cmd(client, colors[i%3])
            i = i + 1
            await asyncio.sleep(0.03)

        i = 0
        red = 255
        while(i<20):
            rgb = str(red) + " 0 0"
            red = red - 12
            await controller.send_cmd(client, rgb)
            i = i + 1
            await asyncio.sleep(0.01)
        await controller.send_cmd(client, "0 0 0")

        await asyncio.sleep(0.25)

        i = 0
        green = 255
        while(i<20):
            rgb = "0 " + str(green) + " 0"
            green = green - 12
            await controller.send_cmd(client, rgb)
            i = i + 1
            await asyncio.sleep(0.01)
        await controller.send_cmd(client, "0 0 0")

        await asyncio.sleep(0.25)

        i = 0
        blue = 255
        while(i<20):
            rgb =  "0 0 " + str(blue);
            blue = blue - 12
            await controller.send_cmd(client, rgb)
            i = i + 1
            await asyncio.sleep(0.01)
        await controller.send_cmd(client, "0 0 0")


        i = 0
        blue = 255
        while(i<20):
            rgb =  str(255 - blue) + " 0 " + str(blue);
            blue = blue - 12
            await controller.send_cmd(client, rgb)
            i = i + 1
            await asyncio.sleep(0.01)
        await controller.send_cmd(client, "0 0 0")



        i = 0
        blue = 255
        while(i<20):
            rgb =  str(0) + " "+str(255 - blue)+" " + str(blue);
            blue = blue - 12
            await controller.send_cmd(client, rgb)
            i = i + 1
            await asyncio.sleep(0.01)
        await controller.send_cmd(client, "0 0 0")



        i = 0
        blue = 255
        while(i<20):
            rgb =  str(blue) + " "+str(255 - blue)+" " + str(0);
            blue = blue - 12
            await controller.send_cmd(client, rgb)
            i = i + 1
            await asyncio.sleep(0.01)
        await controller.send_cmd(client, "0 0 0")

        await client.disconnect()
        # print("Properly disconnecting Bluetooth")


asyncio.run(run_multiple())
