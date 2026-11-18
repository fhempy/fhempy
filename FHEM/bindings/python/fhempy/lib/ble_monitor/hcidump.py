"""Passive BLE monitor integration."""

import asyncio
import collections
import functools
import os
import sys
import time
from threading import Thread

import aioblescan as aiobs
from datetime import datetime

from fhempy.lib.ble_monitor.bt_helpers import reset_bluetooth, BT_INTERFACES
from fhempy.lib.core import hci_claims

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

from .parser import FhempyBleParser
from .helper import dict_get_or_clean, dict_get_or, identifier_clean

CAP_NET_RAW = 13

HCI_EVENT_PKT = 0x04
HCI_EV_CMD_COMPLETE = 0x0E
# commands which reset or change the scan of the adapter. Another program
# sending one of them (e.g. the Matter server resets the adapter when it
# starts with Bluetooth, BlueZ enables its scan with duplicate filtering)
# leaves ble_monitor without advertisements.
SCAN_CHANGING_OPCODES = {
    0x0C01: "Set Event Mask",
    0x0C03: "Reset",
    0x2001: "LE Set Event Mask",
    0x200B: "LE Set Scan Parameters",
    0x200C: "LE Set Scan Enable",
    0x2041: "LE Set Extended Scan Parameters",
    0x2042: "LE Set Extended Scan Enable",
}
# commands sent by aioblescan's send_scan_request
OWN_SCAN_OPCODES = {True: (0x2041, 0x2042), False: (0x200B, 0x200C)}
# wait for the other program to finish its command sequence
REARM_DELAY = 2
# protection against two programs taking over the scan from each other
MAX_REARMS = 5
REARM_PERIOD = 300


def command_complete_opcode(data):
    """Opcode of an HCI Command Complete event, None for other packets"""
    if len(data) >= 6 and data[0] == HCI_EVENT_PKT and data[1] == HCI_EV_CMD_COMPLETE:
        return data[4] | (data[5] << 8)
    return None


def missing_net_raw_hint(status_file="/proc/self/status", euid=None, python=None):
    """Hint how to fix it if the process lacks CAP_NET_RAW, "" otherwise.

    Without CAP_NET_RAW the kernel only lets a raw HCI socket send a few
    informational commands. LE commands (read LE features, scan parameters)
    fail with EPERM, asyncio closes the transport without logging and
    aioblescan never finishes its initialization.
    """
    if euid is None:
        euid = os.geteuid() if hasattr(os, "geteuid") else 0
    if euid == 0:
        return ""
    try:
        with open(status_file, encoding="ascii") as status:
            for line in status:
                if line.startswith("CapEff:"):
                    if int(line.split()[1], 16) & (1 << CAP_NET_RAW):
                        return ""
                    break
            else:
                return ""
    except (OSError, ValueError):
        return ""
    real = os.path.realpath(python or sys.executable)
    return (
        " fhempy has no CAP_NET_RAW, which is needed to scan via hci. Run "
        f"sudo setcap 'cap_net_raw,cap_net_admin+eip' {real} and restart "
        "fhempy (needed again after every Python update), or add "
        "AmbientCapabilities=CAP_NET_ADMIN CAP_NET_RAW to the service which "
        "starts fhempy (sudo systemctl edit fhem)."
    )


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
        # command complete events of our own scan request per hci
        self._own_commands = {}
        self._rearm_handle = None
        self._rearms = collections.deque()
        self._rearm_warned = False
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
        self.ble_parser = FhempyBleParser(
            report_unknown=self.report_unknown,
            discovery=self.discovery,
            filter_duplicates=self.filter_duplicates,
            sensor_whitelist=self.sensor_whitelist,
            tracker_whitelist=self.tracker_whitelist,
            aeskeys=self.aeskeys,
        )

    def process_local_hci_event(self, hci, data):
        """Packet of a local adapter: advertisement or command complete"""
        opcode = command_complete_opcode(data)
        if opcode is None:
            self.process_hci_events(data)
            return
        own = self._own_commands.get(hci)
        if own and own[opcode] > 0:
            own[opcode] -= 1
            return
        if opcode in SCAN_CHANGING_OPCODES:
            self._foreign_command(hci, opcode)

    def _foreign_command(self, hci, opcode):
        if hci_claims.is_claimed(hci):
            # e.g. Matter pairing via Bluetooth, the scan is set up again
            # when the adapter is released
            return
        self.logger.debug(
            "HCIdump thread: hci%i: %s by another program",
            hci,
            SCAN_CHANGING_OPCODES[opcode],
        )
        if self._rearm_handle is not None:
            self._rearm_handle.cancel()
        self._rearm_handle = self._event_loop.call_later(
            REARM_DELAY, functools.partial(self._rearm, hci, opcode)
        )

    def _rearm(self, hci, opcode):
        self._rearm_handle = None
        if hci_claims.is_claimed(hci):
            return
        now = time.monotonic()
        while self._rearms and now - self._rearms[0] > REARM_PERIOD:
            self._rearms.popleft()
        if len(self._rearms) >= MAX_REARMS:
            if self._rearm_warned:
                return
            self._rearm_warned = True
            self.logger.warning(
                "HCIdump thread: another program keeps changing the scan of "
                "hci%i (%s), ble_monitor doesn't set it up again. Stop the "
                "other program from using hci%i or give ble_monitor its own "
                "adapter.",
                hci,
                SCAN_CHANGING_OPCODES[opcode],
                hci,
            )
            return
        self._rearms.append(now)
        self._rearm_warned = False
        self.logger.info(
            "HCIdump thread: another program changed hci%i (%s), "
            "setting up the scan again",
            hci,
            SCAN_CHANGING_OPCODES[opcode],
        )
        # run() starts the scan again
        self._event_loop.stop()

    def process_hci_events(self, data, gateway_id=""):
        """Parse HCI events."""
        self.evt_cnt += 1
        if len(data) < 12:
            return
        try:
            # extended advertising events can hold several reports, each of
            # them may come from another device
            reports = self.ble_parser.parse_raw_data_reports(data)
        except Exception as exc:
            # bleparser expects well formed payloads, e.g. a too short
            # service data raises struct.error: skip the packet
            self.logger.debug(f"Ignored malformed advertisement: {exc!r}")
            return
        for sensor_msg, tracker_msg in reports:
            self._queue_report(sensor_msg, tracker_msg, gateway_id)

    def _queue_report(self, sensor_msg, tracker_msg, gateway_id):
        if sensor_msg:
            measurements = list(sensor_msg.keys())
            device_type = sensor_msg["type"]
            if device_type not in MEASUREMENT_DICT:
                # bleparser knows more sensor types than MEASUREMENT_DICT:
                # deliver the readings instead of crashing the scanner
                self.dataqueue_meas.sync_q.put_nowait(sensor_msg)
            else:
                self._queue_sensor_msg(sensor_msg, measurements, device_type)
        if tracker_msg:
            tracker_msg[CONF_GATEWAY_ID] = gateway_id
            self.dataqueue_tracker.sync_q.put_nowait(tracker_msg)

    def _queue_sensor_msg(self, sensor_msg, measurements, device_type):
        sensors, extra, binaries = MEASUREMENT_DICT[device_type]
        measuring = any(x in measurements for x in sensors + extra)
        binary = any(x in measurements for x in binaries + ["battery"])
        if binary == measuring:
            self.dataqueue_bin.sync_q.put_nowait(sensor_msg)
            self.dataqueue_meas.sync_q.put_nowait(sensor_msg)
        else:
            if binary is True:
                self.dataqueue_bin.sync_q.put_nowait(sensor_msg)
            if measuring is True:
                self.dataqueue_meas.sync_q.put_nowait(sensor_msg)

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
            stopped_while_starting = False
            try:
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
                            conn[hci], btctrl[hci] = (
                                self._event_loop.run_until_complete(fac[hci])
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
                                    " and will be skipped for current scan period.%s",
                                    hci,
                                    missing_net_raw_hint(),
                                )
                            else:
                                btctrl[hci].process = functools.partial(
                                    self.process_local_hci_event, hci
                                )
                                self._own_commands[hci] = collections.Counter(
                                    OWN_SCAN_OPCODES[
                                        bool(getattr(btctrl[hci], "_use_ext_scan")())
                                    ]
                                )
                                self.logger.debug(
                                    "HCIdump thread: connected to hci%i", hci
                                )
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
            except RuntimeError as error:
                # restart() or join() stopped the loop while an interface
                # was being set up, clean up and start again or finish
                self.logger.debug("HCIdump thread: stopped while starting: %s", error)
                stopped_while_starting = True
            self.logger.debug("HCIdump thread: start main event_loop")
            try:
                if not stopped_while_starting:
                    self._event_loop.run_forever()
            finally:
                self.logger.debug("HCIdump thread: main event_loop stopped, finishing.")
                if self._rearm_handle is not None:
                    self._rearm_handle.cancel()
                    self._rearm_handle = None
                if "disable" not in self.config[CONF_BT_INTERFACE]:
                    for hci in self._interfaces:
                        if interface_is_ok.get(hci) is True:
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
