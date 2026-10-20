import asyncio
import logging

from .. import fhem, generic, utils
from . import protocol

SCAN_TIME = 10
SEARCH_TIME = 20
# Xiaomi: reconnect attempts while waiting for the power button
MI_PAIRING_ATTEMPTS = 12
NB_PAIRING_TIMEOUT = 60
CONNECT_TIMEOUT = 20


class scooter(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        logging.getLogger("bleak.backends.bluezdbus.manager").setLevel(logging.WARNING)
        self._errors = utils.ErrorLogger(logger)
        self._loop_task = None
        self._wakeup = asyncio.Event()
        self._lock = asyncio.Lock()
        self._address = ""
        self._pairing_key = b""
        self._static_read = False
        self._pair_now = False
        self._client = None

    @staticmethod
    def validate_define(args, argsh):
        if len(args) > 4:
            return "Usage: define my_scooter fhempy scooter"
        return None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        error = self.validate_define(args, argsh)
        if error:
            return error

        attr_config = {
            "interval": {
                "default": 60,
                "format": "int",
                "help": "Seconds between two updates while the scooter is nearby "
                "and between two searches while it is away, default 60.",
            },
            "protocol": {
                "default": "auto",
                "options": "auto,xiaomi,xiaomi_plain,ninebot",
                "help": "auto detects the protocol. xiaomi: Xiaomi scooters with "
                "new BLE firmware, xiaomi_plain: Xiaomi scooters with old BLE "
                "firmware, ninebot: Ninebot/Segway scooters and Xiaomi 4.",
            },
        }
        await self.set_attr_config(attr_config)
        await self.set_set_config(
            {
                "update": {"help": "Read the values now."},
                "pair": {
                    "help": "Pair again, e.g. after the scooter was paired with "
                    "another app. Press the power button when the scooter beeps."
                },
                "search": {
                    "help": "Forget the current scooter and search for a new one. "
                    "Switch on the scooter and keep it close to FHEM."
                },
            }
        )

        name = hash["NAME"]
        self._address = (
            args[3].upper()
            if len(args) > 3
            else await fhem.ReadingsVal(name, ".address", "")
        )
        self._pairing_key = bytes.fromhex(
            await fhem.ReadingsVal(name, ".pairing_key", "")
        )
        if self._address:
            self.hash["MAC"] = self._address

        if self._loop_task:
            self.cancel_async_task(self._loop_task)
        self._loop_task = self.create_async_task(self._run())

    # FHEM FUNCTION
    async def Undefine(self, hash):
        await super().Undefine(hash)
        if self._client:
            try:
                await self._client.disconnect()
            except Exception:
                self.logger.debug("Disconnect failed", exc_info=True)

    async def set_update(self, hash, params):
        self._wakeup.set()

    async def set_pair(self, hash, params):
        self._pair_now = True
        await self._save_pairing_key(b"")
        self._wakeup.set()

    async def set_search(self, hash, params):
        self._address = ""
        self._static_read = False
        await self._save_address("")
        await self._save_pairing_key(b"")
        self._wakeup.set()

    async def set_attr_interval(self, hash):
        self._wakeup.set()

    async def _state(self, state):
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", state, 1)

    async def _save_address(self, address):
        self._address = address
        self.hash["MAC"] = address
        await fhem.readingsSingleUpdate(self.hash, ".address", address, 0)

    async def _save_pairing_key(self, key):
        self._pairing_key = key
        await fhem.readingsSingleUpdate(self.hash, ".pairing_key", key.hex(), 0)

    async def _sleep(self, seconds):
        try:
            await asyncio.wait_for(self._wakeup.wait(), seconds)
        except TimeoutError:
            pass
        self._wakeup.clear()

    async def _run(self):
        while True:
            try:
                if not self._address:
                    await self._search()
                else:
                    await self._update()
                self._errors.success()
            except Exception:
                self._errors.failed("Scooter update failed")
            await self._sleep(self._attr_interval)

    async def _scan(self, timeout, match):
        """Returns {address: (device, advertisement)} of matching devices,
        stops as soon as wanted_address was found."""
        from bleak import BleakScanner

        found = {}
        done = asyncio.Event()

        def detected(device, adv):
            if match(device, adv):
                found[device.address.upper()] = (device, adv)
                if device.address.upper() == self._address:
                    done.set()

        async with BleakScanner(detection_callback=detected):
            try:
                await asyncio.wait_for(done.wait(), timeout)
            except TimeoutError:
                pass
        return found

    async def _address_in_use(self, address):
        """Another scooter device uses this scooter already"""
        cmd = (
            "foreach my $d (keys %main::defs) {"
            f"  next if $d eq {fhem.perlString(self.hash['NAME'])};;"
            "  return 1 if (($main::defs{$d}{FHEMPYTYPE} // '') eq 'scooter'"
            f" && ReadingsVal($d, '.address', '') eq {fhem.perlString(address)});;"
            "}"
            "return 0;;"
        )
        return str(await fhem.sendCommandHash(self.hash, cmd)) == "1"

    async def _search(self):
        await self._state("searching, switch on the scooter")
        found = await self._scan(
            SEARCH_TIME,
            lambda d, adv: protocol.is_scooter(
                adv.local_name or d.name, adv.manufacturer_data
            ),
        )
        candidates = []
        for address, (device, adv) in found.items():
            if await self._address_in_use(address):
                continue
            candidates.append((adv.rssi, address, adv.local_name or device.name))
        if not candidates:
            return
        candidates.sort(reverse=True)
        rssi, address, name = candidates[0]
        self.logger.info(f"Found scooter {name} ({address}), rssi {rssi}")
        if len(candidates) > 1:
            self.logger.info(
                "Other scooters nearby: "
                + ", ".join(f"{c[2]} ({c[1]})" for c in candidates[1:])
            )
        await self._save_address(address)
        await fhem.readingsSingleUpdate(self.hash, "name", name or "", 1)
        await self._save_pairing_key(b"")
        self._pair_now = True
        self._wakeup.set()

    async def _update(self):
        found = await self._scan(
            SCAN_TIME, lambda d, adv: d.address.upper() == self._address
        )
        if self._address not in found:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "presence", "absent", 1)
            await self._state("absent")
            return
        device, adv = found[self._address]
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "presence", "present")
        await fhem.readingsBulkUpdate(self.hash, "rssi", adv.rssi)
        await fhem.readingsEndUpdate(self.hash, 1)

        async with self._lock:
            readings = await self._read(device, adv)
        await fhem.readingsBeginUpdate(self.hash)
        for reading, value in readings.items():
            await fhem.readingsBulkUpdate(self.hash, reading, value)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "state", f"{readings['battery']}%"
        )
        await fhem.readingsEndUpdate(self.hash, 1)

    async def _connect(self, device):
        from bleak import BleakClient

        client = BleakClient(device, timeout=CONNECT_TIMEOUT)
        await client.connect()
        return client

    def _protocol(self, client, device, adv):
        if self._attr_protocol != "auto":
            return self._attr_protocol
        characteristics = {
            char.uuid.lower()
            for service in client.services
            for char in service.characteristics
        }
        return protocol.detect_protocol(
            adv.local_name or device.name, adv.manufacturer_data, characteristics
        )

    async def _read(self, device, adv):
        if not self._pairing_key:
            self._pair_now = True
        self._client = await self._connect(device)
        try:
            proto = self._protocol(self._client, device, adv)
            await fhem.readingsSingleUpdateIfChanged(self.hash, "protocol", proto, 1)
            if proto == protocol.XIAOMI:
                transport = await self._xiaomi_login(device)
            elif proto == protocol.NINEBOT:
                transport = await self._ninebot_login(device, adv)
            else:
                transport = protocol.XiaomiPlainTransport(self._client, self.logger)
                await transport.start()
            values = await protocol.read_values(transport, static=not self._static_read)
            self._static_read = True
            return values
        finally:
            await self._client.disconnect()

    async def _xiaomi_login(self, device):
        transport = protocol.XiaomiTransport(
            self._client, self.logger, self._pairing_key or None
        )
        await transport.start()
        if transport.token and not self._pair_now:
            try:
                await transport.login()
                return transport
            except protocol.PairingRequired:
                self.logger.warning("Scooter doesn't accept the pairing, pair again")
                if not self._pair_now:
                    await self._state("pairing lost, use set pair")
                    raise protocol.ScooterError(
                        "Pairing lost, scooter was probably paired with another "
                        "app. Use set pair and press the power button."
                    )
        # registration: the scooter beeps, the power button has to be pressed
        # and the registration has to start again within a few seconds
        for _ in range(MI_PAIRING_ATTEMPTS):
            await self._state("pairing, press the power button when it beeps")
            try:
                token = await transport.register()
                break
            except protocol.PairingRequired:
                await self._client.disconnect()
                await asyncio.sleep(5)
                self._client = await self._connect(device)
                transport = protocol.XiaomiTransport(self._client, self.logger)
                await transport.start()
        else:
            await self._state("pairing failed, use set pair to try again")
            self._pair_now = False
            raise protocol.ScooterError("Pairing failed, power button not pressed")
        await self._save_pairing_key(token)
        self._pair_now = False
        await self._state("paired")
        await transport.login()
        return transport

    async def _ninebot_login(self, device, adv):
        transport = protocol.NinebotTransport(
            self._client,
            self.logger,
            adv.local_name or device.name,
            self._pairing_key or None,
        )
        await transport.start()
        if self._pair_now:
            await self._state("pairing, press the power button")
        try:
            await transport.login(NB_PAIRING_TIMEOUT if self._pair_now else 0)
        except protocol.PairingRequired:
            if self._pair_now:
                await self._state("pairing failed, use set pair to try again")
                self._pair_now = False
                raise protocol.ScooterError("Pairing failed, power button not pressed")
            await self._state("pairing lost, use set pair")
            raise protocol.ScooterError(
                "Pairing lost, scooter was probably paired with another app. "
                "Use set pair and press the power button."
            )
        if transport.app_key != self._pairing_key:
            await self._save_pairing_key(transport.app_key)
        self._pair_now = False
        return transport
