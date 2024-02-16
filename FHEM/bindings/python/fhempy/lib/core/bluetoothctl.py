# Based on ReachView code from Egor Fedorov (egor.fedorov@emlid.com)
# Updated for Python 3.6.8 on a Raspberry  Pi


import subprocess
import time

import pexpect


class Bluetoothctl:
    """A wrapper for bluetoothctl utility."""

    def __init__(self, logger):
        self.logger = logger
        # try to unblock bluetooth with rfkill, it doesn't matter if it fails
        try:
            subprocess.check_output(
                "rfkill unblock bluetooth",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            self.logger.debug("rfkill is not present")
        self.process = pexpect.spawn("bluetoothctl", echo=False, encoding="utf-8")

    def stop(self):
        """Stop bluetoothctl utility only if it is running."""
        if self.process.isalive():
            self.process.terminate(force=True)

    def send(self, command, pause=0):
        self.process.send(f"{command}\n")
        time.sleep(pause)
        if self.process.expect(["#", pexpect.EOF]):
            raise Exception(f"failed after {command}")

    def get_output(self, *args, **kwargs):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.send(*args, **kwargs)
        return self.process.before.split("\r\n")

    def exit(self):
        """Exit bluetoothctl prompt."""
        self.send("exit")

    def power_on(self):
        """Power on."""
        try:
            self.send("power on")
        except Exception as e:
            self.logger.error(e)

    def power_off(self):
        """Power off."""
        try:
            self.send("power off")
        except Exception as e:
            self.logger.error(e)

    def default_agent(self):
        """Default agent."""
        try:
            self.send("default-agent")
        except Exception as e:
            self.logger.error(e)

    def agent_on(self):
        """Agent on."""
        try:
            self.send("agent on")
        except Exception as e:
            self.logger.error(e)

    def start_scan(self):
        """Start bluetooth scanning process."""
        try:
            self.send("scan on")
        except Exception as e:
            self.logger.error(e)

    def stop_scan(self):
        """Stop bluetooth scanning process."""
        try:
            self.send("scan off")
        except Exception as e:
            self.logger.error(e)

    def make_discoverable(self):
        """Make device discoverable."""
        try:
            self.send("discoverable on")
        except Exception as e:
            self.logger.error(e)

    def parse_device_info(self, info_string):
        """Parse a string corresponding to a device."""
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        if not any(keyword in info_string for keyword in block_list):
            try:
                device_position = info_string.index("Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(" ", 2)
                    device = {
                        "mac_address": attribute_list[1],
                        "name": attribute_list[2],
                    }
        return device

    def get_available_devices(self):
        """Return a list of tuples of paired and discoverable devices."""
        available_devices = []
        try:
            out = self.get_output("devices")
        except Exception as e:
            self.logger.error(e)
        else:
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    available_devices.append(device)
        return available_devices

    def get_paired_devices(self):
        """Return a list of tuples of paired devices."""
        paired_devices = []
        try:
            out = self.get_output("paired-devices")
            # add output of devices Paired command
            out += self.get_output("devices Paired")
        except Exception as e:
            self.logger.error(e)
        else:
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    paired_devices.append(device)
        return paired_devices

    def get_discoverable_devices(self):
        """Filter paired devices out of available."""
        available = self.get_available_devices()
        paired = self.get_paired_devices()
        return [d for d in available if d not in paired]

    def get_device_info(self, mac_address):
        """Get device info by mac address."""
        try:
            out = self.get_output(f"info {mac_address}")
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            return out

    def pair(self, mac_address, pin="0000"):
        """Try to pair with a device by mac address."""
        try:
            self.send(f"pair {mac_address}", 4)
        except Exception as e:
            self.logger.error(e)
            return PairingState.FAILED
        else:
            try:
                res = self.process.expect(
                    [
                        "Pairing successful",
                        "Request passkey",
                        "Failed to pair",
                        pexpect.TIMEOUT,
                    ],
                    timeout=60,
                )
                if res == 1:
                    self.send(pin, 4)
                    res = self.process.expect(
                        [
                            "Pairing successful",
                            "Failed to pair",
                            "AuthenticationFailed",
                            pexpect.TIMEOUT,
                        ],
                        timeout=60,
                    )
                    if res == 2:
                        return PairingState.WRONG_PIN
                    elif res == 3:
                        return PairingState.TIMEOUT
                    elif res == 1:
                        return PairingState.FAILED
                    return PairingState.SUCCESS

                elif res == 0:
                    return PairingState.SUCCESS
                elif res == 2:
                    return PairingState.FAILED
            except pexpect.TIMEOUT:
                return PairingState.TIMEOUT

    def trust(self, mac_address):
        try:
            self.send(f"trust {mac_address}", 4)
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["failed", "succeeded", pexpect.TIMEOUT],
                timeout=60,
            )
            return res == 1

    def remove(self, mac_address):
        """Remove paired device by mac address, return success of the operation."""
        try:
            self.send(f"remove {mac_address}", 3)
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["not available", "Device has been removed", pexpect.EOF]
            )
            return res == 1

    def connect(self, mac_address):
        """Try to connect to a device by mac address."""
        try:
            self.send(f"connect {mac_address}", 2)
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["Failed to connect", "Connection successful", pexpect.TIMEOUT],
                timeout=60,
            )
            return res == 1

    def disconnect(self, mac_address):
        """Try to disconnect to a device by mac address."""
        try:
            self.send(f"disconnect {mac_address}", 2)
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["Failed to disconnect", "Successful disconnected", pexpect.TIMEOUT],
                timeout=60,
            )
            return res == 1


# Enum class with the possible pairing states
class PairingState:
    SUCCESS = 0
    WRONG_PIN = 1
    TIMEOUT = 2
    FAILED = 3
