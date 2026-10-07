import asyncio

from .. import fhem, generic


class huawei_modbus(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.bridge = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "interval": {
                "default": 30,
                "format": "int",
                "help": "Update interval in seconds",
            },
        }
        await self.set_attr_config(attr_config)

        set_config = {}
        await self.set_set_config(set_config)

        if len(args) < 4:
            return "Usage: define my_sun2000 fhempy fusionsolar_modbus IP PORT SLAVE_ID"

        self.ip = args[3]
        self.port = 502
        self.slave_id = 1

        if len(args) >= 5:
            self.port = int(args[4])

            if len(args) >= 6:
                self.slave_id = int(args[5])

        self.hash["IP"] = self.ip
        self.hash["PORT"] = self.port
        self.hash["SLAVE_ID"] = self.slave_id

        self.create_async_task(self.start())

    async def Undefine(self, hash):
        try:
            if self.bridge:
                await self.bridge.stop()
        except Exception:
            self.logger.exception("Failed to stop modbus connection")
        finally:
            self.bridge = None
            await super().Undefine(hash)

    async def start(self):
        # try to connect until successful
        while not self.bridge:
            try:
                await self.connect()
            except Exception as e:
                self.logger.error(e)
                await asyncio.sleep(10)

        while True:
            try:
                await self.update()
            except Exception as e:
                self.logger.error(e)
                # try to reconnect
                try:
                    if self.bridge:
                        await self.bridge.stop()
                except Exception:
                    self.logger.debug("Failed to stop modbus connection", exc_info=True)
                self.bridge = None
                while not self.bridge:
                    await asyncio.sleep(60)
                    try:
                        await self.connect()
                    except Exception as e:
                        self.logger.error(e)
                continue

            await asyncio.sleep(self._attr_interval)

    async def connect(self):
        from huawei_solar import (
            SUN2000Device,
            create_device_instance,
            create_tcp_client,
        )

        client = create_tcp_client(host=self.ip, port=self.port, unit_id=self.slave_id)
        device = await create_device_instance(client)
        if not isinstance(device, SUN2000Device):
            await device.stop()
            raise Exception(f"Unsupported device {device.model_name}, only SUN2000")
        self.bridge = device

    def _registers(self):
        # huawei-solar 3 dropped the bridge with its default register set,
        # so we request the same registers as HuaweiSolarBridge.update() did
        from huawei_solar import register_names as rn
        from huawei_solar.register_values import StorageProductModel

        registers = [
            rn.INPUT_POWER,
            rn.LINE_VOLTAGE_A_B,
            rn.LINE_VOLTAGE_B_C,
            rn.LINE_VOLTAGE_C_A,
            rn.PHASE_A_VOLTAGE,
            rn.PHASE_B_VOLTAGE,
            rn.PHASE_C_VOLTAGE,
            rn.PHASE_A_CURRENT,
            rn.PHASE_B_CURRENT,
            rn.PHASE_C_CURRENT,
            rn.DAY_ACTIVE_POWER_PEAK,
            rn.ACTIVE_POWER,
            rn.REACTIVE_POWER,
            rn.POWER_FACTOR,
            rn.GRID_FREQUENCY,
            rn.EFFICIENCY,
            rn.INTERNAL_TEMPERATURE,
            rn.INSULATION_RESISTANCE,
            rn.DEVICE_STATUS,
            rn.FAULT_CODE,
            rn.STARTUP_TIME,
            rn.SHUTDOWN_TIME,
            rn.ACCUMULATED_YIELD_ENERGY,
            rn.DAILY_YIELD_ENERGY,
            rn.STATE_1,
            rn.STATE_2,
            rn.STATE_3,
            rn.ALARM_1,
            rn.ALARM_2,
            rn.ALARM_3,
        ]
        for idx in range(1, self.bridge.pv_string_count + 1):
            registers.append(getattr(rn, f"PV_{idx:02}_VOLTAGE"))
            registers.append(getattr(rn, f"PV_{idx:02}_CURRENT"))
        if self.bridge.has_optimizers:
            registers.append(rn.NB_ONLINE_OPTIMIZERS)
        if self.bridge.battery_type != StorageProductModel.NONE:
            registers += [
                rn.STORAGE_STATE_OF_CAPACITY,
                rn.STORAGE_RUNNING_STATUS,
                rn.STORAGE_BUS_VOLTAGE,
                rn.STORAGE_BUS_CURRENT,
                rn.STORAGE_CHARGE_DISCHARGE_POWER,
                rn.STORAGE_TOTAL_CHARGE,
                rn.STORAGE_TOTAL_DISCHARGE,
                rn.STORAGE_CURRENT_DAY_CHARGE_CAPACITY,
                rn.STORAGE_CURRENT_DAY_DISCHARGE_CAPACITY,
            ]
        return registers

    def _meter_registers(self):
        from huawei_solar import register_names as rn

        return [
            rn.METER_STATUS,
            rn.GRID_A_VOLTAGE,
            rn.GRID_B_VOLTAGE,
            rn.GRID_C_VOLTAGE,
            rn.ACTIVE_GRID_A_CURRENT,
            rn.ACTIVE_GRID_B_CURRENT,
            rn.ACTIVE_GRID_C_CURRENT,
            rn.POWER_METER_ACTIVE_POWER,
            rn.POWER_METER_REACTIVE_POWER,
            rn.ACTIVE_GRID_POWER_FACTOR,
            rn.ACTIVE_GRID_FREQUENCY,
            rn.GRID_EXPORTED_ENERGY,
            rn.GRID_ACCUMULATED_ENERGY,
            rn.GRID_ACCUMULATED_REACTIVE_POWER,
            rn.METER_TYPE,
            rn.ACTIVE_GRID_A_B_VOLTAGE,
            rn.ACTIVE_GRID_B_C_VOLTAGE,
            rn.ACTIVE_GRID_C_A_VOLTAGE,
            rn.ACTIVE_GRID_A_POWER,
            rn.ACTIVE_GRID_B_POWER,
            rn.ACTIVE_GRID_C_POWER,
        ]

    async def update(self):
        data = await self.bridge.batch_update(self._registers())
        if self.bridge.power_meter_type is not None:
            try:
                data.update(await self.bridge.batch_update(self._meter_registers()))
            except Exception:
                self.logger.info("Power meter registers not available")

        await fhem.readingsBeginUpdate(self.hash)
        try:
            for key in data:
                await fhem.readingsBulkUpdateIfChanged(self.hash, key, data[key].value)
        except Exception as e:
            self.logger.error(e)
        await fhem.readingsEndUpdate(self.hash, 1)
