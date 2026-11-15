from .upstream_const import MEASUREMENT_DICT as UPSTREAM_MEASUREMENT_DICT

CONF_DEVICES = "devices"
CONF_NAME = "name"
CONF_MAC = "mac"
CONF_DISCOVERY = "discovery"

# Configuration options
CONF_BT_AUTO_RESTART = "bt_auto_restart"
CONF_DECIMALS = "decimals"
CONF_PERIOD = "period"
CONF_LOG_SPIKES = "log_spikes"
CONF_USE_MEDIAN = "use_median"
CONF_ACTIVE_SCAN = "active_scan"
CONF_HCI_INTERFACE = "hci_interface"
CONF_BT_INTERFACE = "bt_interface"
CONF_BATT_ENTITIES = "batt_entities"
CONF_REPORT_UNKNOWN = "report_unknown"
CONF_RESTORE_STATE = "restore_state"
CONF_DEVICE_ENCRYPTION_KEY = "encryption_key"
CONF_DEVICE_DECIMALS = "decimals"
CONF_DEVICE_USE_MEDIAN = "use_median"
CONF_DEVICE_RESTORE_STATE = "restore_state"
CONF_DEVICE_RESET_TIMER = "reset_timer"
CONF_DEVICE_TRACK = "track_device"
CONF_DEVICE_TRACKER_SCAN_INTERVAL = "tracker_scan_interval"
CONF_DEVICE_TRACKER_CONSIDER_HOME = "consider_home"
CONF_DEVICE_DELETE_DEVICE = "delete device"
CONF_PACKET = "packet"
CONF_GATEWAY_ID = "gateway_id"
CONF_UUID = "uuid"

# Default values for configuration options
DEFAULT_BT_AUTO_RESTART = True
DEFAULT_DECIMALS = 1
DEFAULT_PERIOD = 60
DEFAULT_LOG_SPIKES = False
DEFAULT_USE_MEDIAN = False
DEFAULT_ACTIVE_SCAN = False
DEFAULT_BATT_ENTITIES = True
DEFAULT_REPORT_UNKNOWN = "Off"
DEFAULT_DISCOVERY = False
DEFAULT_RESTORE_STATE = False
DEFAULT_DEVICE_MAC = ""
DEFAULT_DEVICE_UUID = ""
DEFAULT_DEVICE_ENCRYPTION_KEY = None
DEFAULT_DEVICE_DECIMALS = "default"
DEFAULT_DEVICE_USE_MEDIAN = "default"
DEFAULT_DEVICE_RESTORE_STATE = "default"
DEFAULT_DEVICE_RESET_TIMER = 35
DEFAULT_DEVICE_TRACKER_SCAN_INTERVAL = 20
DEFAULT_DEVICE_TRACKER_CONSIDER_HOME = 180
DEFAULT_DEVICE_TRACK = False
DEFAULT_DEVICE_DELETE_DEVICE = False

# regex constants for configuration schema
MAC_REGEX = "(?i)^(?:[0-9A-F]{2}[:]){5}(?:[0-9A-F]{2})$"
# MiBeacon V2/V3 uses 24 character long key
AES128KEY24_REGEX = "(?i)^[A-F0-9]{24}$"
# MiBeacon V4/V5 uses 32 character long key
AES128KEY32_REGEX = "(?i)^[A-F0-9]{32}$"

# Dictionary with supported sensors, copied from ble_monitor together with the
# parser (tools/sync_ble_parser.py).
# Format {device: [averaging sensor list], [instantly updating sensor list],[binary sensor list]}:
# - [averaging sensor list]:            sensors that update the state after avering of the data
# - [instantly updating sensor list]:   sensors that update the state instantly after new data
# - [binary sensor list]:               binary sensors
MEASUREMENT_DICT = {
    **UPSTREAM_MEASUREMENT_DICT,
    # ble_monitor handles ThermoPro without an entry here
    "TP357": [["temperature", "humidity", "battery", "rssi"], [], []],
    "TP359": [["temperature", "humidity", "battery", "rssi"], [], []],
}


# Sensor manufacturer dictionary
MANUFACTURER_DICT = {
    "LYWSDCGQ": "Xiaomi",
    "LYWSD02": "Xiaomi",
    "LYWSD03MMC": "Xiaomi",
    "XMWSDJ04MMC": "Xiaomi",
    "XMMF01JQD": "Xiaomi",
    "HHCCJCY01": "Xiaomi",
    "GCLS002": "Xiaomi",
    "HHCCPOT002": "Xiaomi",
    "WX08ZM": "Xiaomi",
    "MCCGQ02HL": "Xiaomi",
    "YM-K1501": "Xiaomi",
    "YM-K1501EU": "Xiaomi",
    "V-SK152": "Viomi",
    "SJWS01LM": "Xiaomi",
    "MJYD02YL": "Xiaomi",
    "MUE4094RT": "Xiaomi",
    "RTCGQ02LM": "Xiaomi",
    "MMC-T201-1": "Xiaomi",
    "M1S-T500": "Xiaomi Soocas",
    "ZNMS16LM": "Xiaomi Aqara",
    "ZNMS17LM": "Xiaomi Aqara",
    "MJZNMSQ01YD": "Xiaomi",
    "XMZNMST02YD": "Xiaomi",
    "CGC1": "Qingping",
    "CGD1": "Qingping",
    "CGDK2": "Qingping",
    "CGG1": "Qingping",
    "CGG1-ENCRYPTED": "Qingping",
    "CGH1": "Qingping",
    "CGP1W": "Qingping",
    "CGPR1": "Qingping",
    "CGDN1": "Qingping",
    "MHO-C401": "Miaomiaoce",
    "MHO-C303": "Miaomiaoce",
    "JQJCY01YM": "Honeywell",
    "JTYJGD03MI": "Honeywell",
    "YLAI003": "Yeelight",
    "YLYK01YL": "Yeelight",
    "YLYK01YL-FANCL": "Yeelight",
    "YLYK01YL-VENFAN": "Yeelight",
    "YLYB01YL-BHFRC": "Yeelight",
    "YLKG07YL/YLKG08YL": "Yeelight",
    "K9B-1BTN": "Linptech",
    "K9B-2BTN": "Linptech",
    "K9B-3BTN": "Linptech",
    "ATC": "ATC",
    "Mi Scale V1": "Xiaomi",
    "Mi Scale V2": "Xiaomi",
    "TZC4": "Xiaogui",
    "Kegtron KT-100": "Kegtron",
    "Kegtron KT-200": "Kegtron",
    "Smart hygrometer": "Thermoplus",
    "Lanyard/mini hygrometer": "Thermoplus",
    "T201": "Brifit",
    "H5072/H5075": "Govee",
    "H5101/H5102/H5177": "Govee",
    "H5051": "Govee",
    "H5074": "Govee",
    "H5178": "Govee",
    "H5179": "Govee",
    "H5183": "Govee",
    "Ruuvitag": "Ruuvitag",
    "iNode Energy Meter": "iNode",
    "iNode Care Sensor 1": "iNode",
    "iNode Care Sensor 2": "iNode",
    "iNode Care Sensor 3": "iNode",
    "iNode Care Sensor 4": "iNode",
    "iNode Care Sensor 5": "iNode",
    "iNode Care Sensor 6": "iNode",
    "iNode Care Sensor T": "iNode",
    "iNode Care Sensor HT": "iNode",
    "iNode Care Sensor PT": "iNode",
    "iNode Care Sensor PHT": "iNode",
    "Blue Puck T": "Teltonika",
    "Blue Coin T": "Teltonika",
    "Blue Puck RHT": "Teltonika",
    "HTP.xw": "SensorPush",
    "HT.w": "SensorPush",
    "MyCO2": "Sensirion",
    "Moat S2": "Moat",
    "Tempo Disc THD": "BlueMaestro",
    "Tempo Disc THPD": "BlueMaestro",
    "b-parasite V1.0.0": "rbaron",
    "b-parasite V1.1.0": "rbaron",
    "SmartSeries 7000": "Oral-B",
    "iBBQ-1": "Inkbird",
    "iBBQ-2": "Inkbird",
    "iBBQ-4": "Inkbird",
    "iBBQ-6": "Inkbird",
    "IBS-TH": "Inkbird",
    "BEC07-5": "Jinou",
    "iBeacon": "Apple",
    "AltBeacon": "Radius Networks",
    "HA BLE DIY": "Home Assistant DIY",
}

# Renamed model dictionary
RENAMED_MODEL_DICT = {
    "H5051/H5074": "H5074",
    "IBS-TH2": "IBS-TH",
}

# Selection list for report_uknown
REPORT_UNKNOWN_LIST = [
    "ATC",
    "BlueMaestro",
    "Brifit",
    "Govee",
    "HA BLE",
    "Inkbird",
    "iNode",
    "iBeacon",
    "Jinou" "Kegtron",
    "Mi Scale",
    "Moat",
    "Oral-B",
    "Qingping",
    "rbaron",
    "Ruuvitag",
    "Sensirion",
    "SensorPush",
    "Teltonika",
    "Thermoplus",
    "Xiaogui",
    "Xiaomi",
    "Other",
    "Off",
    False,
]
