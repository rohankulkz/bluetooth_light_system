import asyncio



freq = 30
class LightRunner:

    def __init__(self, client, controller):
        self.client = client
        self.controller = controller
        self.active = True
        self.cmdBehavior = None

    async def flash(self, val):
        self.active = False
        await self.controller.send_cmd(self.client, val)
        self.active = True

    async def setCommand(self, newCmd):
        # print("new command added")
        self.cmdBehavior = newCmd
        if not self.active:
            await self.start()

    async def playCommand(self, newCmd, total):
        # print("new command added")
        self.cmdBehavior = newCmd
        if not self.active:
            await self.start()
        await asyncio.sleep(total)

    async def start(self):
        self.active = True
        asyncio.create_task(self.mainLoop())  # Correct way to start a background coroutine

    def stop(self):
        self.active = False

    async def mainLoop(self):
        while self.active:
            try:
                if self.cmdBehavior is not None:
                    await asyncio.sleep(1 / self.cmdBehavior.freq)
                    temp = next(self.cmdBehavior)
                    if temp is not None:
                        await self.controller.send_cmd(self.client, temp)
            except StopIteration:
                self.cmdBehavior = None
                # print("Sequence finished")
                self.stop()

