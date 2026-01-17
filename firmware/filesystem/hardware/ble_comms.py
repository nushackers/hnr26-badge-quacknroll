import sys

# ruff: noqa: E402
sys.path.append("")

from micropython import const
import asyncio
import aioble
import bluetooth

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

# Advertising interval
_ADV_INTERVAL_US = 250_000



class BLETextClient:
    def __init__(
        self,
        target_name="mpy-temp",
        scan_time_ms=5000,
        scan_interval_us=30_000,
        scan_window_us=30_000,
    ):
        self.target_name = target_name
        self.scan_time_ms = scan_time_ms
        self.scan_interval_us = scan_interval_us
        self.scan_window_us = scan_window_us

        self.device = None
        self.connection = None
        self.characteristic = None

    async def find_server(self):
        async with aioble.scan(
            self.scan_time_ms,
            interval_us=self.scan_interval_us,
            window_us=self.scan_window_us,
            active=True,
        ) as scanner:
            async for result in scanner:
                if (
                    result.name() == self.target_name
                    and _ENV_SENSE_UUID in result.services()
                ):
                    return result.device
        return None

    async def connect(self):
        self.device = await self.find_server()
        if not self.device:
            print("BLETextServer not found")
            return False

        try:
            print("Connecting to", self.device)
            self.connection = await self.device.connect()
        except asyncio.TimeoutError:
            print("Timeout during connection")
            return False

        try:
            service = await self.connection.service(_ENV_SENSE_UUID)
            self.characteristic = await service.characteristic(
                _ENV_SENSE_TEMP_UUID
            )
            return True
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return False

    async def run(self):
        """
        Connect, subscribe, and listen for notifications.
        """
        print("BLE: Connecting")
        total_final_data = b""
        
        ok = await self.connect()
        if not ok:
            return

        async with self.connection:
            await self.characteristic.subscribe(notify=True)
            try:
                while True:
                    data = await self.characteristic.notified()
                    print("notif:", data)
                    total_final_data += data
            except aioble.DeviceDisconnectedError:
                return total_final_data

class BLETextServer:
    def __init__(
        self,
        name="mpy-temp",
        chunk_size=20,
        adv_interval_us=_ADV_INTERVAL_US,
        text="hello world",
    ):
        self.name = name
        self.chunk_size = chunk_size
        self.adv_interval_us = adv_interval_us
        self.text = text

        # GATT service & characteristic
        self.service = aioble.Service(_ENV_SENSE_UUID)
        self.characteristic = aioble.Characteristic(
            self.service,
            _ENV_SENSE_TEMP_UUID,
            read=True,
            notify=True,
        )
        aioble.register_services(self.service)

    @staticmethod
    def chunk_text(text, chunk_size):
        """
        Split a string or bytes into a list of chunks of at most chunk_size bytes.
        """
        if isinstance(text, str):
            data = text.encode()
        else:
            data = text

        return [
            data[i : i + chunk_size]
            for i in range(0, len(data), chunk_size)
        ]

    async def sensor_task(self):
        """
        Periodically sends a message as BLE notifications.
        """
        print("sending message")
        await asyncio.sleep_ms(1000)

        msg = self.text
        chunks = self.chunk_text(msg, self.chunk_size)

        for chunk in chunks:
            self.characteristic.write(chunk, send_update=True)
            await asyncio.sleep_ms(500)

    async def peripheral_task(self):
        """
        Advertise and handle a single connection at a time.
        """
        print("Advertising")
        while True:
            async with await aioble.advertise(
                self.adv_interval_us,
                name=self.name,
                services=[_ENV_SENSE_UUID],
                appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
            ) as connection:
                print("Connection from", connection.device)
                await self.sensor_task()
                await connection.disconnect()
                await connection.disconnected(timeout_ms=None)
                break

    async def run(self):
        """
        Entry point for the BLE server.
        """
        await self.peripheral_task()


# ---- main ----

async def test():
    client = BLETextClient()
    value = await client.run()
    print(value)
    server = BLETextServer()
    await server.run()


#asyncio.run(test())
