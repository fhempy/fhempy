"""Passive BLE monitor integration."""
import asyncio
from threading import Thread

import aioblescan as aiobs
from datetime import datetime

from bleparser import BleParser

from fhempy.lib.ble_monitor.bt_helpers import reset_bluetooth, BT_INTERFACES

from .const import (
    CONF_DEVICES,
    CONF_ACTIVE_SCAN,
    CONF_BT_AUTO_RESTART,
    CONF_BT_INTERFACE,
    CONF_DEVICE_ENCRYPTION_KEY,
    CONF_DEVICE_TRACK,
    CONF_HCI_INTERFACE,
    CONF_GATEWAY_ID,
    CONF_REPORT_UNKNOWN,
    CONF_DISCOVERY,
    MEASUREMENT_DICT,
)

from .helper import dict_get_or_clean, dict_get_or, identifier_clean


class HCIdump(Thread):
    """Mimic deprecated hcidump tool."""

    def __init__(self, logger, config, dataqueue):
        """Initiate HCIdump thread."""
        Thread.__init__(self)
        self.logger = logger
        self.logger.debug("HCIdump thread: Init")
        self.dataqueue_bin = dataqueue["binary"]
        self.dataqueue_meas = dataqueue["measuring"]
        self.dataqueue_tracker = dataqueue["tracker"]
        self._event_loop = None
        self._joining = False
        self.evt_cnt = 0
        self.config = config
        self._interfaces = config[CONF_HCI_INTERFACE]
        self._active = int(config[CONF_ACTIVE_SCAN] is True)
        self.discovery = True
        self.filter_duplicates = True
        self.aeskeys = {}
        self.sensor_whitelist = []
        self.tracker_whitelist = []
        self.report_unknown = False
        self.last_bt_reset = datetime.now()
        if self.config[CONF_REPORT_UNKNOWN]:
            self.report_unknown = self.config[CONF_REPORT_UNKNOWN]
            self.logger.info(
                "Attention! Option report_unknown is enabled for %s sensors, "
                "be ready for a huge output",
                self.report_unknown,
            )
        # prepare device:key lists to speedup parser
        if self.config[CONF_DEVICES]:
            for device in self.config[CONF_DEVICES]:
                if (
                    CONF_DEVICE_ENCRYPTION_KEY in device
                    and device[CONF_DEVICE_ENCRYPTION_KEY]
                ):
                    p_id = bytes.fromhex(dict_get_or_clean(device).lower())
                    p_key = bytes.fromhex(device[CONF_DEVICE_ENCRYPTION_KEY].lower())
                    self.aeskeys[p_id] = p_key
                else:
                    continue
        self.logger.debug("%s encryptors mac:key pairs loaded", len(self.aeskeys))

        # prepare sensor whitelist to speedup parser
        if (
            isinstance(self.config[CONF_DISCOVERY], bool)
            and self.config[CONF_DISCOVERY] is False
        ):
            self.discovery = False
            if self.config[CONF_DEVICES]:
                for device in self.config[CONF_DEVICES]:
                    self.sensor_whitelist.append(dict_get_or(device))

        # remove duplicates from sensor whitelist
        self.sensor_whitelist = list(dict.fromkeys(self.sensor_whitelist))
        self.logger.debug(
            "sensor whitelist: [%s]", ", ".join(self.sensor_whitelist).upper()
        )
        for i, key in enumerate(self.sensor_whitelist):
            self.sensor_whitelist[i] = bytes.fromhex(identifier_clean(key))
        self.logger.debug(
            "%s sensor whitelist item(s) loaded", len(self.sensor_whitelist)
        )

        # prepare device tracker list to speedup parser
        if self.config[CONF_DEVICES]:
            for device in self.config[CONF_DEVICES]:
                if CONF_DEVICE_TRACK in device and device[CONF_DEVICE_TRACK]:
                    track_key = bytes.fromhex(dict_get_or_clean(device))
                    self.tracker_whitelist.append(track_key)
                else:
                    continue
        self.logger.debug(
            "%s device tracker(s) being monitored", len(self.tracker_whitelist)
        )

        # prepare the ble_parser
        self.ble_parser = BleParser(
            report_unknown=self.report_unknown,
            discovery=self.discovery,
            filter_duplicates=self.filter_duplicates,
            sensor_whitelist=self.sensor_whitelist,
            tracker_whitelist=self.tracker_whitelist,
            aeskeys=self.aeskeys,
        )

    def process_hci_events(self, data, gateway_id=""):
        """Parse HCI events."""
        self.evt_cnt += 1
        if len(data) < 12:
            return
        sensor_msg, tracker_msg = self.ble_parser.parse_data(data)
        if sensor_msg:
            measurements = list(sensor_msg.keys())
            device_type = sensor_msg["type"]
            sensor_list = (
                MEASUREMENT_DICT[device_type][0] + MEASUREMENT_DICT[device_type][1]
            )
            binary_list = MEASUREMENT_DICT[device_type][2] + ["battery"]
            measuring = any(x in measurements for x in sensor_list)
            binary = any(x in measurements for x in binary_list)
            if binary == measuring:
                self.dataqueue_bin.sync_q.put_nowait(sensor_msg)
                self.dataqueue_meas.sync_q.put_nowait(sensor_msg)
            else:
                if binary is True:
                    self.dataqueue_bin.sync_q.put_nowait(sensor_msg)
                if measuring is True:
                    self.dataqueue_meas.sync_q.put_nowait(sensor_msg)
        if tracker_msg:
            tracker_msg[CONF_GATEWAY_ID] = gateway_id
            self.dataqueue_tracker.sync_q.put_nowait(tracker_msg)

    def run(self):
        """Run HCIdump thread."""
        while True:
            self.logger.debug("HCIdump thread: Run")
            mysocket = {}
            fac = {}
            conn = {}
            btctrl = {}
            interface_is_ok = {}
            interfaces_to_reset = []
            initialized_evt = {}
            if self._event_loop is None:
                self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
            if "disable" not in self.config[CONF_BT_INTERFACE]:
                for hci in self._interfaces:
                    interface_is_ok[hci] = False
                    try:
                        mysocket[hci] = aiobs.create_bt_socket(hci)
                    except OSError as error:
                        self.logger.error(
                            "HCIdump thread: OS error (hci%i): %s", hci, error
                        )
                    else:
                        fac[hci] = getattr(
                            self._event_loop, "_create_connection_transport"
                        )(mysocket[hci], aiobs.BLEScanRequester, None, None)
                        conn[hci], btctrl[hci] = self._event_loop.run_until_complete(
                            fac[hci]
                        )
                        # Wait up to five seconds for aioblescan BLEScanRequester to initialize
                        initialized_evt[hci] = getattr(btctrl[hci], "_initialized")
                        self.logger.debug(
                            "HCIdump thread: BLEScanRequester._initialized is %s for hci%i, "
                            " waiting for connection...",
                            initialized_evt[hci].is_set(),
                            hci,
                        )
                        try:
                            self._event_loop.run_until_complete(
                                asyncio.wait_for(initialized_evt[hci].wait(), 5)
                            )
                        except asyncio.TimeoutError:
                            self.logger.error(
                                "HCIdump thread: Something wrong - interface hci%i not ready,"
                                " and will be skipped for current scan period.",
                                hci,
                            )
                        else:
                            btctrl[hci].process = self.process_hci_events
                            self.logger.debug("HCIdump thread: connected to hci%i", hci)
                            try:
                                self._event_loop.run_until_complete(
                                    btctrl[hci].send_scan_request(self._active)
                                )
                            except RuntimeError as error:
                                self.logger.error(
                                    "HCIdump thread: Runtime error while sending scan request on hci%i: %s.",
                                    hci,
                                    error,
                                )
                            else:
                                interface_is_ok[hci] = True
                                self.logger.debug(
                                    "HCIdump thread: BLEScanRequester._initialized is %s for hci%i, "
                                    " connection established, send_scan_request succeeded.",
                                    initialized_evt[hci].is_set(),
                                    hci,
                                )
                    if (interface_is_ok[hci] is False) and (
                        self.config[CONF_BT_AUTO_RESTART] is True
                    ):
                        interfaces_to_reset.append(hci)
                if interfaces_to_reset:
                    ts_now = datetime.now()
                    if (ts_now - self.last_bt_reset).seconds > 60:
                        for iface in interfaces_to_reset:
                            self.logger.error(
                                "HCIdump thread: Trying to power cycle Bluetooth adapter hci%i %s,"
                                " will try to use it next scan period.",
                                iface,
                                BT_INTERFACES[iface],
                            )
                            reset_bluetooth(iface)
                        self.last_bt_reset = ts_now
            self.logger.debug("HCIdump thread: start main event_loop")
            try:
                self._event_loop.run_forever()
            finally:
                self.logger.debug("HCIdump thread: main event_loop stopped, finishing.")
                if "disable" not in self.config[CONF_BT_INTERFACE]:
                    for hci in self._interfaces:
                        if interface_is_ok[hci] is True:
                            try:
                                self._event_loop.run_until_complete(
                                    btctrl[hci].stop_scan_request()
                                )
                            except RuntimeError as error:
                                self.logger.error(
                                    "HCIdump thread: Runtime error while stop scan request on hci%i: %s.",
                                    hci,
                                    error,
                                )
                            except KeyError:
                                self.logger.debug(
                                    "HCIdump thread: Key error while stop scan request on hci%i",
                                    hci,
                                )
                        try:
                            conn[hci].close()
                        except KeyError:
                            self.logger.debug(
                                "HCIdump thread: Key error while closing connection on hci%i",
                                hci,
                            )
                self._event_loop.run_until_complete(asyncio.sleep(0))
            if self._joining is True:
                break
            self.logger.debug("HCIdump thread: Scanning will be restarted")
            self.logger.debug(
                "%i HCI events processed for previous period", self.evt_cnt
            )
            self.evt_cnt = 0
        self._event_loop.close()
        self.logger.debug("HCIdump thread: Run finished")

    def join(self, timeout=1):
        """Join HCIdump thread."""
        self.logger.debug("HCIdump thread: joining")
        self._joining = True
        try:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        except AttributeError as error:
            self.logger.debug("%s", error)
        finally:
            Thread.join(self, timeout)
            self.logger.debug("HCIdump thread: joined")

    def restart(self):
        """Restarting scanner."""
        try:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        except AttributeError as error:
            self.logger.debug("%s", error)
