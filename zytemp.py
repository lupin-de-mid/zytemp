import asyncio
from aiofiles.threadpool import open as aioopen

absolute_zero = 273.15

key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]


def convert_raw_temperature(raw_temp):
    return raw_temp / 16 - absolute_zero


def decrypt(actuak_key, data):
    cstate = [0x48, 0x74, 0x65, 0x6D, 0x70, 0x39, 0x39, 0x65]
    shuffle = [2, 4, 0, 7, 1, 6, 5, 3]

    phase1 = [0] * 8
    for i, o in enumerate(shuffle):
        phase1[o] = data[i]

    phase2 = [0] * 8
    for i in range(8):
        phase2[i] = phase1[i] ^ actuak_key[i]

    phase3 = [0] * 8
    for i in range(8):
        phase3[i] = ((phase2[i] >> 3) | (phase2[(i - 1 + 8) % 8] << 5)) & 0xff

    ctmp = [0] * 8
    for i in range(8):
        ctmp[i] = ((cstate[i] >> 4) | (cstate[i] << 4)) & 0xff

    out = [0] * 8
    for i in range(8):
        out[i] = (0x100 + phase3[i] - ctmp[i]) & 0xff

    return out


def is_valid(decrypted):
    return decrypted[4] == 0x0d and (sum(decrypted[:3]) & 0xff) == decrypted[3]


class ZyTemp:
    """A simple example class"""
    i = 12345

    def __init__(self, device) -> None:
        self.co2 = 0
        self.temperature = None
        self.device = device
        self.has_read_temperature = asyncio.Event()
        self.has_read_co2 = asyncio.Event()

        super().__init__()

    async def get_latest_temperature(self):
        if self.temperature is None:
            await self.has_read_temperature.wait()
        return self.temperature

    async def get_latest_co2(self):
        if self.co2 is None:
            await self.has_read_co2.wait()
        return self.co2

    def set_temperature_raw(self, raw_temp):
        self.set_temperature(convert_raw_temperature(raw_temp))

    def set_temperature(self, temp):
        if self.temperature is None:
            self.temperature = temp
            self.has_read_temperature.set()
        else:
            self.temperature = temp

    def set_co2(self, val):
        if self.co2 is None:
            self.co2 = val
            self.has_read_co2.set()
        else:
            self.co2 = val

    async def start(self, filename):
        async with aioopen(filename, mode="a+b", buffering=0) as file:
            while True:
                data = await file.read(8)
                decrypted = decrypt(key, data)
                if is_valid(decrypted):
                    op = decrypted[0]
                    val = decrypted[1] << 8 | decrypted[2]
                    if op == 0x50:
                        self.set_co2(val)
                    if op == 0x42:
                        self.set_temperature_raw(val)
