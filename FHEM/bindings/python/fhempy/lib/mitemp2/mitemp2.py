from ..core.ble import BTLEConnection
from .. import generic
from .. import fhem


class mitemp2(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 4:
            return "Usage: define mitemp fhempy mitemp2 <MAC>"
        self._mac = args[3]
        self.hash["MAC"] = self._mac
        self._conn = BTLEConnection(
            self._mac,
            keep_connected=True,
            connection_established_callback=self.connection_setup,
        )

    def connection_setup(self, mac):
        self.create_async_task(self.async_connection_setup(mac))

    async def async_connection_setup(self, mac):
        await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)
        # enable notifications
        self._conn.write_characteristic(0x0038, b"\x01\x00")
        # enable lower power mode
        self._conn.write_characteristic(0x0046, b"\xf4\x01\x00")
        self._conn.set_callback("all", self.received_notification)

    def received_notification(self, data):
        self.create_async_task(self.update_data(data))

    async def update_data(self, data):
        temp = int.from_bytes(data[0:2], byteorder="little", signed=True) / 100
        humidity = int.from_bytes(data[2:3], byteorder="little")
        voltage = int.from_bytes(data[3:5], byteorder="little") / 1000.0
        batteryLevel = min(
            int(round((voltage - 2.1), 2) * 100), 100
        )  # 3.1 or above --> 100% 2.1 --> 0 %
        if batteryLevel < 10:
            low_bat = "low"
        else:
            low_bat = "ok"

        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, "temperature", temp)
        await fhem.readingsBulkUpdate(self.hash, "humidity", humidity)
        await fhem.readingsBulkUpdate(self.hash, "voltage", voltage)
        await fhem.readingsBulkUpdate(self.hash, "batteryLevel", batteryLevel)
        await fhem.readingsBulkUpdate(self.hash, "battery", low_bat)
        await fhem.readingsEndUpdate(self.hash, 1)
