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

# Dictionary with supported sensors
# Format {device: [averaging sensor list], [instantly updating sensor list],[binary sensor list]}:
# - [averaging sensor list]:            sensors that update the state after avering of the data
# - [instantly updating sensor list]:   sensors that update the state instantly after new data
# - [binary sensor list]:               binary sensors
MEASUREMENT_DICT = {
    "LYWSDCGQ": [["temperature", "humidity", "battery", "rssi"], [], []],
    "LYWSD02": [["temperature", "humidity", "battery", "rssi"], [], []],
    "LYWSD03MMC": [["temperature", "humidity", "battery", "voltage", "rssi"], [], []],
    "XMWSDJ04MMC": [["temperature", "humidity", "battery", "rssi"], [], []],
    "XMMF01JQD": [["rssi"], ["button"], []],
    "HHCCJCY01": [
        ["temperature", "moisture", "conductivity", "illuminance", "battery", "rssi"],
        [],
        [],
    ],
    "GCLS002": [
        ["temperature", "moisture", "conductivity", "illuminance", "rssi"],
        [],
        [],
    ],
    "HHCCPOT002": [["moisture", "conductivity", "rssi"], [], []],
    "WX08ZM": [["consumable", "battery", "rssi"], [], ["switch"]],
    "MCCGQ02HL": [["battery", "rssi"], [], ["opening", "light"]],
    "YM-K1501": [["rssi"], ["temperature"], ["switch"]],
    "YM-K1501EU": [["rssi"], ["temperature"], ["switch"]],
    "V-SK152": [["rssi"], ["temperature"], ["switch"]],
    "SJWS01LM": [["battery", "rssi"], ["button"], ["moisture"]],
    "MJYD02YL": [["battery", "rssi"], [], ["light", "motion"]],
    "MUE4094RT": [["rssi"], [], ["motion"]],
    "RTCGQ02LM": [["battery", "rssi"], ["button"], ["light", "motion"]],
    "MMC-T201-1": [["temperature", "battery", "rssi"], [], []],
    "M1S-T500": [["battery", "rssi"], [], ["toothbrush"]],
    "ZNMS16LM": [["battery", "rssi"], [], ["lock", "fingerprint"]],
    "ZNMS17LM": [["battery", "rssi"], [], ["lock", "fingerprint"]],
    "MJZNMSQ01YD": [["battery", "rssi"], [], ["lock", "fingerprint"]],
    "XMZNMST02YD": [["battery", "rssi"], [], ["lock", "fingerprint"]],
    "CGC1": [["temperature", "humidity", "battery", "rssi"], [], []],
    "CGD1": [["temperature", "humidity", "battery", "rssi"], [], []],
    "CGDK2": [["temperature", "humidity", "battery", "rssi"], [], []],
    "CGG1": [["temperature", "humidity", "battery", "voltage", "rssi"], [], []],
    "CGG1-ENCRYPTED": [
        ["temperature", "humidity", "battery", "voltage", "rssi"],
        [],
        [],
    ],
    "CGH1": [["battery", "rssi"], [], ["opening"]],
    "CGP1W": [["temperature", "humidity", "battery", "pressure", "rssi"], [], []],
    "CGPR1": [["illuminance", "battery", "rssi"], [], ["light", "motion"]],
    "CGDN1": [["temperature", "humidity", "co2", "pm2.5", "pm10", "rssi"], [], []],
    "MHO-C401": [["temperature", "humidity", "battery", "voltage", "rssi"], [], []],
    "MHO-C303": [["temperature", "humidity", "battery", "rssi"], [], []],
    "JQJCY01YM": [
        ["temperature", "humidity", "battery", "formaldehyde", "rssi"],
        [],
        [],
    ],
    "JTYJGD03MI": [["rssi"], ["button", "battery"], ["smoke detector"]],
    "K9B-1BTN": [["rssi"], ["one btn switch"], []],
    "K9B-2BTN": [["rssi"], ["two btn switch left", "two btn switch right"], []],
    "K9B-3BTN": [
        ["rssi"],
        ["three btn switch left", "three btn switch middle", "three btn switch right"],
        [],
    ],
    "YLAI003": [["rssi", "battery"], ["button"], []],
    "YLYK01YL": [["rssi"], ["remote"], ["remote single press", "remote long press"]],
    "YLYK01YL-FANCL": [["rssi"], ["fan remote"], []],
    "YLYK01YL-VENFAN": [["rssi"], ["ventilator fan remote"], []],
    "YLYB01YL-BHFRC": [["rssi"], ["bathroom heater remote"], []],
    "YLKG07YL/YLKG08YL": [["rssi"], ["dimmer"], []],
    "ATC": [
        ["temperature", "humidity", "battery", "voltage", "rssi"],
        [],
        ["switch", "opening"],
    ],
    "Mi Scale V1": [["rssi"], ["weight", "non-stabilized weight"], ["weight removed"]],
    "Mi Scale V2": [
        ["rssi"],
        ["weight", "non-stabilized weight", "impedance"],
        ["weight removed"],
    ],
    "TZC4": [["rssi"], ["weight", "non-stabilized weight", "impedance"], []],
    "Kegtron KT-100": [["rssi"], ["volume dispensed port 1"], []],
    "Kegtron KT-200": [
        ["rssi"],
        ["volume dispensed port 1", "volume dispensed port 2"],
        [],
    ],
    "Smart hygrometer": [
        ["temperature", "humidity", "battery", "voltage", "rssi"],
        [],
        [],
    ],
    "Lanyard/mini hygrometer": [
        ["temperature", "humidity", "battery", "voltage", "rssi"],
        [],
        [],
    ],
    "T201": [["temperature", "humidity", "battery", "voltage", "rssi"], [], []],
    "H5072/H5075": [["temperature", "humidity", "battery", "rssi"], [], []],
    "H5101/H5102/H5177": [["temperature", "humidity", "battery", "rssi"], [], []],
    "H5051": [["temperature", "humidity", "battery", "rssi"], [], []],
    "H5074": [["temperature", "humidity", "battery", "rssi"], [], []],
    "H5178": [
        [
            "temperature",
            "temperature outdoor",
            "humidity",
            "humidity outdoor",
            "battery",
            "rssi",
        ],
        [],
        [],
    ],
    "H5179": [["temperature", "humidity", "battery", "rssi"], [], []],
    "H5183": [["temperature probe 1", "temperature alarm", "rssi"], [], []],
    "Ruuvitag": [
        ["temperature", "humidity", "pressure", "battery", "voltage", "rssi"],
        ["acceleration"],
        ["motion"],
    ],
    "iNode Energy Meter": [["battery", "voltage", "rssi"], ["energy", "power"], []],
    "iNode Care Sensor 1": [
        ["temperature", "battery", "voltage", "rssi"],
        ["acceleration"],
        ["motion"],
    ],
    "iNode Care Sensor 2": [
        ["temperature", "battery", "voltage", "rssi"],
        ["acceleration"],
        ["motion"],
    ],
    "iNode Care Sensor 3": [
        ["temperature", "humidity", "battery", "voltage", "rssi"],
        ["acceleration"],
        ["motion"],
    ],
    "iNode Care Sensor 4": [
        ["temperature", "battery", "voltage", "rssi"],
        ["acceleration"],
        ["motion"],
    ],
    "iNode Care Sensor 5": [
        ["temperature", "battery", "voltage", "rssi"],
        ["acceleration", "magnetic field", "magnetic field direction"],
        ["motion"],
    ],
    "iNode Care Sensor 6": [
        ["temperature", "battery", "voltage", "rssi"],
        ["acceleration"],
        ["motion"],
    ],
    "iNode Care Sensor T": [["temperature", "battery", "voltage", "rssi"], [], []],
    "iNode Care Sensor HT": [
        ["temperature", "humidity", "battery", "voltage", "rssi"],
        [],
        [],
    ],
    "iNode Care Sensor PT": [
        ["temperature", "pressure", "battery", "voltage", "rssi"],
        [],
        [],
    ],
    "iNode Care Sensor PHT": [
        ["temperature", "humidity", "pressure", "battery", "voltage", "rssi"],
        [],
        [],
    ],
    "Blue Puck T": [["temperature", "rssi"], [], []],
    "Blue Coin T": [["temperature", "rssi"], [], []],
    "Blue Puck RHT": [["temperature", "humidity", "rssi"], [], []],
    "HTP.xw": [["temperature", "humidity", "pressure", "rssi"], [], []],
    "HT.w": [["temperature", "humidity", "pressure", "rssi"], [], []],
    "Moat S2": [["temperature", "humidity", "battery", "rssi"], [], []],
    "Tempo Disc THD": [
        ["temperature", "humidity", "dewpoint", "battery", "rssi"],
        [],
        [],
    ],
    "Tempo Disc THPD": [
        ["temperature", "humidity", "pressure", "battery", "rssi"],
        [],
        [],
    ],
    "b-parasite V1.0.0": [
        ["temperature", "humidity", "moisture", "voltage", "rssi"],
        [],
        [],
    ],
    "b-parasite V1.1.0": [
        ["temperature", "humidity", "moisture", "voltage", "rssi", "illuminance"],
        [],
        [],
    ],
    "SmartSeries 7000": [["rssi"], [], ["toothbrush"]],
    "iBBQ-1": [["temperature probe 1", "rssi"], [], []],
    "iBBQ-2": [["temperature probe 1", "temperature probe 2", "rssi"], [], []],
    "iBBQ-4": [
        [
            "temperature probe 1",
            "temperature probe 2",
            "temperature probe 3",
            "temperature probe 4",
            "rssi",
        ],
        [],
        [],
    ],
    "iBBQ-6": [
        [
            "temperature probe 1",
            "temperature probe 2",
            "temperature probe 3",
            "temperature probe 4",
            "temperature probe 5",
            "temperature probe 6",
            "rssi",
        ],
        [],
        [],
    ],
    "IBS-TH": [["temperature", "humidity", "battery", "rssi"], [], []],
    "BEC07-5": [["temperature", "humidity", "rssi"], [], []],
    "iBeacon": [
        ["rssi", "measured power", "cypress temperature", "cypress humidity"],
        ["uuid", "mac", "major", "minor"],
        [],
    ],  # mac can be dynamic
    "AltBeacon": [
        ["rssi", "measured power"],
        ["uuid", "mac", "major", "minor"],
        [],
    ],  # mac can be dynamic
    "MyCO2": [["temperature", "humidity", "co2", "rssi"], [], []],
    "HA BLE DIY": [["temperature", "rssi"], [], []],
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
