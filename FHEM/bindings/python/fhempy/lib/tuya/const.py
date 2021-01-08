""" DP ID descriptions """


def convert_to_onoff(val):
    if val is True:
        return "on"
    return "off"


dp_ids = {
    "OutletDevice": {
        "1": {
            "name": "state",
            "convert": convert_to_onoff,
            "set": {
                "on": {"function": "set_onoff", "function_param": "1"},
                "off": {"function": "set_onoff", "function_param": "1"},
            },
        },
        "2": {
            "name": "switch_2",
            "convert": convert_to_onoff,
            "set": {
                "on_switch_2": {"function": "set_onoff", "function_param": "2"},
                "off_switch_2": {"function": "set_onoff", "function_param": "2"},
            },
        },
        "3": {
            "name": "switch_3",
            "convert": convert_to_onoff,
            "set": {
                "on_switch_3": {"function": "set_onoff", "function_param": "3"},
                "off_switch_3": {"function": "set_onoff", "function_param": "3"},
            },
        },
        "4": {
            "name": "switch_4",
            "convert": convert_to_onoff,
            "set": {
                "on_switch_4": {"function": "set_onoff", "function_param": "4"},
                "off_switch_4": {"function": "set_onoff", "function_param": "4"},
            },
        },
        "5": {
            "name": "switch_5",
            "convert": convert_to_onoff,
            "set": {
                "on_switch_5": {"function": "set_onoff", "function_param": "5"},
                "off_switch_5": {"function": "set_onoff", "function_param": "5"},
            },
        },
        "6": {
            "name": "switch_6",
            "convert": convert_to_onoff,
            "set": {
                "on_switch_6": {"function": "set_onoff", "function_param": "6"},
                "off_switch_6": {"function": "set_onoff", "function_param": "6"},
            },
        },
        "7": {
            "name": "switch_7",
            "convert": convert_to_onoff,
            "set": {
                "on_switch_7": {"function": "set_onoff", "function_param": "7"},
                "off_switch_7": {"function": "set_onoff", "function_param": "7"},
            },
        },
        "9": {"name": "countdown_1"},
        "10": {"name": "countdown_2"},
        "11": {"name": "countdown_3"},
        "12": {"name": "countdown_4"},
        "13": {"name": "countdown_5"},
        "14": {"name": "countdown_6"},
        "15": {"name": "countdown_7"},
        "17": {"name": "consumption_kWh", "convert": lambda x: x / 10},
        "18": {"name": "current_mA"},
        "19": {"name": "power_W", "convert": lambda x: x / 10},
        "20": {"name": "voltage_V", "convert": lambda x: x / 10},
        # "21": {"name": "Test Bit"},
        # "22": {"name": "Voltage coe"},
        # "23": {"name": "Current coe"},
        # "24": {"name": "Power coe"},
        # "25": {"name": "Electricity coe"},
        # "26": {"name": "Fault"},
    }
}
