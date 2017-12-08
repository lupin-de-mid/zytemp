import unittest

import asyncio

from zytempy.zytemp import ZyTemp, decrypt, is_valid, key, convert_raw_temperature


class MyTestCase(unittest.TestCase):
    def test_check_is_valid(self):
        decrypted = [65, 0, 0, 65, 13, 0, 0, 0]
        valid = is_valid(decrypted)
        self.assertEqual(True, valid)

    def test_decrypt(self):
        data = [0x5B, 0x32, 0x30, 0x31, 0x34, 0x2D, 0x31, 0x30]
        res = decrypt(key, data)
        self.assertEqual(122, res[0])

    def test_decrypt2(self):
        data = [112, 228, 238, 32, 252, 70, 191, 42]
        res = decrypt(key, data)
        self.assertEqual([65, 0, 0, 65, 13, 0, 0, 0], res)

    def test_creation(self):
        x = ZyTemp("/dev/hidraw0")
        self.assertEqual("/dev/hidraw0", x.device)

    #TODO i don't know hot to write this tests
    # def test_not_wait_temperature(self):
    #     event_loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(event_loop)
    #     dev = ZyTemp("")
    #     dev.set_temperature(5)
    #     temp = dev.get_latest_temperature()
    #     f = asyncio.ensure_future(temp)
    #     self.assertEqual(True, f.done())
    #     self.assertEqual(5, temp)
    def test_set_temperature_raw(self):
        raw = 4760
        real = convert_raw_temperature(raw)
        self.assertAlmostEqual(24.35, real)

    def test_wait_temperature(self):
        """Test iterating over lines from a file."""
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        dev = ZyTemp("")

        async def run_test():
            temp = await dev.get_latest_temperature()
            self.assertEqual(5, temp)

        dev.set_temperature(5)
        coro = asyncio.coroutine(run_test)

        event_loop.run_until_complete(coro())
        event_loop.close()


if __name__ == '__main__':
    unittest.main()
