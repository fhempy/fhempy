# THANKS to https://github.com/AlexxIT/XiaomiGateway3 for the HASS implementation
# which I used as a base for the FHEM implementation

import base64
import json
import asyncio
import socket
import re
import functools
from telnetlib import Telnet
import time
from asyncio_mqtt import Client, MqttError

from .miio_fix import Device
from .unqlite import Unqlite

from .utils import GLOBAL_PROP
from . import utils

from .. import fhem
from .. import utils as fpyutils

class xiaomi_gateway3:

  def __init__(self, logger):
    self.logger = logger
    return

  # FHEM FUNCTION
  async def Define(self, hash, args, argsh):
    self.hash = hash
    await fhem.readingsBeginUpdate(hash)
    await fhem.readingsBulkUpdateIfChanged(hash, "state", "disconnected")
    await fhem.readingsEndUpdate(hash, 1)

    hash["HOST"] = args[3]
    hash["TOKEN"] = args[4]

    self.host = args[3]
    self.token = args[4]

    asyncio.create_task(self.connect_gw())
    
    return ""

  # FHEM FUNCTION
  async def Undefine(self, hash, args, argsh):
    return

  # FHEM FUNCTION
  async def Set(self, hash, args, argsh):
    set_conf_list = {
      "reconnect": {}
    }
    return await fpyutils.handle_set(set_conf_list, self, hash, args, argsh)
  
  async def set_reconnect(self, params):
    return

  def register_device(self, did, upd_listener):
    self.gw.register_device(did, upd_listener)
  
  def get_device(self, did):
    return self.gw.get_device(did)

  async def connect_gw(self):
    self.gw = Gateway(self.logger, self.hash, self.host, self.token)
    # connect to gateway
    await self.gw.connect()
    # create task which handles MQTT messages
    asyncio.create_task(self.gw.connect_mqtt())

class Gateway:

  def __init__(self, logger, hash, host, token):
    self.hash = hash
    self.logger = logger
    self.host = host
    self.token = token
    self.devices = {}
    self.miio = Device(host, token)
    self.child_devices = {}

  def register_device(self, did, upd_listener):
    if did not in self.child_devices:
      self.child_devices[did] = []
    self.child_devices[did].append(upd_listener)
    # report initial states
    asyncio.create_task(self.report(did))

  def get_device(self, did):
    if did in self.devices:
      return self.devices[did]
    return None

  async def connect(self):
    await fpyutils.run_blocking(functools.partial(self.thread_blocking_connect))
    await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connected", 1)
    await self.create_devices()
    await self.report_all()

  def thread_blocking_connect(self):
    while len(self.devices) == 0:
      if self._miio_connect():
          devices = self._get_devices_v3()
          if devices is None:
              self._enable_telnet()
              self._enable_mqtt()
          else:
              self.setup_devices(devices)
      else:
          time.sleep(30)
    # connected

  def setup_devices(self, devices: list):
    """Add devices to hass."""
    for device in devices:
        desc = utils.get_device(device['model'])
        if not desc:
            self.logger.debug(f"Unsupported model: {device}")
            continue

        self.logger.debug(f"{self.host} | Setup device {device['model']}")

        device.update(desc)

        # update params from config
        default_config = self.devices.get(device['mac'])
        if default_config:
            device.update(default_config)

        self.devices[device['did']] = device

  async def create_devices(self):
    for did in self.devices:
      if not await fhem.checkIfDeviceExists(self.hash, "PYTHONTYPE", "xiaomi_gateway3_device", "DID", did):
        await fhem.CommandDefine(self.hash, "".join(filter(str.isalnum, did)) + " PythonModule xiaomi_gateway3_device " + self.hash["NAME"] + " " + did)
        # avoid fhem commands overload
        await asyncio.sleep(3)
      # avoid fhem commands overload
      await asyncio.sleep(1)

  async def report(self, did):
    if did in self.devices:
      device = self.devices[did]
      if "init" in device:
        if did in self.child_devices:
          for listener in self.child_devices[did]:
            await listener.update(device['init'])

  async def report_all(self):
    for did in self.devices:
      await self.report(did)

  def _miio_connect(self) -> bool:
    try:
        self.miio.send_handshake()
        return True
    except:
        self.logger.debug(f"{self.host} | Can't send handshake")
        return False

  def _enable_telnet(self):
      self.logger.debug(f"{self.host} | Try enable telnet")
      try:
          resp = self.miio.send("enable_telnet_service")
          return resp[0] == 'ok'
      except Exception as e:
          self.logger.exception(f"Can't enable telnet: {e}")
          return False

  def _enable_mqtt(self):
    self.logger.debug(f"{self.host} | Try run public MQTT")
    try:
        telnet = Telnet(self.host)
        telnet.read_until(b"login: ")
        telnet.write(b"admin\r\n")
        telnet.read_until(b"\r\n# ")  # skip greeting

        # enable public mqtt
        telnet.write(b"killall mosquitto\r\n")
        telnet.read_until(b"\r\n")  # skip command
        time.sleep(.5)  # it's important to wait
        telnet.write(b"mosquitto -d\r\n")
        telnet.read_until(b"\r\n")  # skip command
        time.sleep(.5)  # it's important to wait

        # fix CPU 90% full time bug
        telnet.write(b"killall zigbee_gw\r\n")
        telnet.read_until(b"\r\n")  # skip command
        time.sleep(.5)  # it's important to wait

        telnet.close()
        return True
    except Exception as e:
        self.logger.debug(f"Can't run MQTT: {e}")
        return False

  async def connect_mqtt(self):
    try:
      async with Client(self.host) as client:
        self.mqttclient = client
        async with client.filtered_messages("#") as messages:
          await client.subscribe("#")
          async for message in messages:
            self.logger.debug("Message from MQTT: " + message.payload.decode())
            if message.topic == 'zigbee/send':
              try:
                payload = json.loads(message.payload.decode())
                # convert to miio msg
                msg = self.process_message(payload)
                if msg['did'] in self.child_devices:
                  for listener in self.child_devices[msg['did']]:
                    await listener.update(msg['data'])
              except:
                self.logger.exception("Failed to handle MQTT message")
    except:
      self.logger.exception("Failed to connect to MQTT server: " + self.host)

  def _get_devices_v3(self):
        """Load device list via Telnet."""
        self.logger.debug(f"{self.host} | Read devices")
        try:
            telnet = Telnet(self.host, timeout=5)
            telnet.read_until(b"login: ")
            telnet.write(b"admin\r\n")
            telnet.read_until(b'\r\n# ')  # skip greeting

            # https://github.com/AlexxIT/XiaomiGateway3/issues/14
            # fw 1.4.6_0012 and below have one zigbee_gw.db file
            # fw 1.4.6_0030 have many json files in this folder
            telnet.write(b"cat /data/zigbee_gw/* | base64\r\n")
            telnet.read_until(b'\r\n')  # skip command
            raw = telnet.read_until(b'# ')
            raw = base64.b64decode(raw)
            if raw.startswith(b'unqlite'):
                db = Unqlite(raw)
                data = db.read_all()
            else:
                raw = re.sub(br'}\s+{', b',', raw)
                data = json.loads(raw)

            devices = []

            # data = {} or data = {'dev_list': 'null'}
            dev_list = json.loads(data.get('dev_list', 'null')) or []
            self.logger.debug(f"{self.host} | Load {len(dev_list)} zigbee devices")

            for did in dev_list:
                model = data[did + '.model']
                desc = utils.get_device(model)

                # skip unknown model
                if desc is None:
                    self.logger.debug(f"Unsupported model: {model}")
                    continue

                retain = json.loads(data[did + '.prop'])['props']
                self.logger.debug(f"{self.host} | {model} retain: {retain}")

                params = {
                    p[2]: retain.get(p[1])
                    for p in desc['params']
                    if p[1] is not None
                }

                # fix some param values
                for k, v in params.items():
                    if k in ('temperature', 'humidity', 'pressure'):
                        params[k] = v / 100.0
                    elif k in ('voltage'):
                        params[k] = v / 1000.0
                    elif v in ('on', 'open'):
                        params[k] = 1
                    elif v in ('off', 'close'):
                        params[k] = 0
                    elif k == 'battery' and v and v > 1000:
                        params['batteryPercentage'] = round((min(v, 3200) - 2500) / 7)
                        params['battery'] = "low" if params['batteryPercentage'] < 25 else "ok"

                device = {
                    'did': did,
                    'sid': did.split(".")[1],
                    'mac': '0x' + data[did + '.mac'],
                    'model': data[did + '.model'],
                    'type': 'zigbee',
                    'zb_ver': data[did + '.version'],
                    'init': params
                }
                devices.append(device)

            telnet.write(b"cat /data/zigbee/coordinator.info\r\n")
            telnet.read_until(b'\r\n')  # skip command
            raw = telnet.read_until(b'# ')

            device = json.loads(raw[:-2])

            return devices

        except (ConnectionRefusedError, socket.timeout):
            return None

        except Exception as e:
            self.logger.debug(f"Can't read devices: {e}")
            return None

  def process_message(self, data: dict):
        cmd = data['cmd']
        if data['cmd'] == 'heartbeat':
            # don't know if only one item
            assert len(data['params']) == 1, data

            data = data['params'][0]
            pkey = 'res_list'
        elif data['cmd'] == 'report':
            pkey = 'params' if 'params' in data else 'mi_spec'
        elif data['cmd'] == 'write_rsp':
            pkey = 'results'
        else:
            raise Exception(f"Unsupported cmd: {data}")

        did = data['did']

        # skip without callback
        #if did not in self.updates:
        #    return

        device = self.devices[did]
        payload = {}

        # convert codes to names
        for param in data[pkey]:
            if param.get('error_code', 0) != 0:
                continue

            prop = param['res_name'] if 'res_name' in param else \
                f"{param['siid']}.{param['piid']}"

            if prop in GLOBAL_PROP:
                prop = GLOBAL_PROP[prop]
            else:
                prop = next((p[2] for p in device['params']
                             if p[0] == prop), prop)

            if prop in ('temperature', 'humidity', 'pressure'):
                payload[prop] = param['value'] / 100.0
            elif prop == 'voltage':
                payload[prop] = param['value'] / 1000.0
            elif prop == 'battery' and param['value'] > 1000:
                # xiaomi light sensor
                payload['batteryPercentage'] = round((min(param['value'], 3200) - 2500) / 7)
                payload['battery'] = "low" if payload['batteryPercentage'] < 25 else "ok"
            elif prop == 'angle':
                # xiaomi cube 100 points = 360 degrees
                payload[prop] = param['value'] * 4
            elif prop == 'duration':
                # xiaomi cube
                payload[prop] = param['value'] / 1000.0
            else:
                payload[prop] = param['value']

        self.logger.debug(f"{self.host} | {device['did']} {device['model']} <= "
                      f"{payload}")

        return {
          "did": did,
          "sid": device['sid'],
          "model": device['model'],
          "cmd": cmd,
          "data": payload
        }
