import asyncio
import functools
import os
import shutil
import signal
import subprocess

import netifaces
from fhempy.lib.generic import FhemModule
from git import Repo

from .. import fhem, utils


class zigbee2mqtt(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.proc = None
        self._set_list = {"start": {}, "stop": {}, "restart": {}, "update": {}}
        self.set_set_config(self._set_list)
        attr_conf = {"disable": {"options": "0,1", "default": "0", "format": "int"}}
        self.set_attr_config(attr_conf)

        self.check_process_task = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        if self._attr_disable == 1:
            return

        self.create_async_task(self.run_z2m())

    async def run_z2m(self):
        res = await self.check_node_installation()
        if res is False:
            return

        res = await self.check_npm_installation()
        if res is False:
            return

        res = await self.install_z2m()
        if res is False:
            return

        await self.start_process()

    async def update_z2m(self):
        try:
            await fhem.readingsSingleUpdate(
                self.hash, "update", "started, may take a few minutes", 1
            )
            current_directory = os.getcwd()
            z2m_directory = os.path.join(current_directory, r".fhempy/zigbee2mqtt")

            await self.stop_process()
            try:
                await utils.run_blocking(
                    functools.partial(
                        shutil.copytree,
                        z2m_directory + "/data",
                        z2m_directory + "/data-backup",
                    )
                )
            except FileExistsError:
                shutil.rmtree(z2m_directory + "/data-backup")
                await utils.run_blocking(
                    functools.partial(
                        shutil.copytree,
                        z2m_directory + "/data",
                        z2m_directory + "/data-backup",
                    )
                )

            rep = Repo(z2m_directory)
            o = rep.remotes.origin
            await utils.run_blocking(functools.partial(o.pull))

            await utils.run_blocking(
                functools.partial(subprocess.call, ["npm", "ci"], cwd=z2m_directory)
            )

            source_folder = z2m_directory + "/data-backup"
            destination_folder = z2m_directory + "/data"
            for file in os.listdir(source_folder):
                file_path = os.path.join(source_folder, file)
                if os.path.isfile(file_path):
                    await utils.run_blocking(
                        functools.partial(shutil.copy, file_path, destination_folder)
                    )

            await fhem.readingsSingleUpdate(self.hash, "update", "successful", 1)
            await self.start_process()
        except Exception:
            self.logger.exception("Failed to update")
            await fhem.readingsSingleUpdate(
                self.hash, "update", "failed to update, check log", 1
            )

    async def install_z2m(self):
        GIT_URL = "https://github.com/Koenkk/zigbee2mqtt.git"

        current_directory = os.getcwd()
        install_directory = os.path.join(current_directory, r".fhempy")
        if not os.path.exists(install_directory):
            os.makedirs(install_directory)
        z2m_directory = os.path.join(current_directory, r".fhempy/zigbee2mqtt")
        clone_needed = True
        if not os.path.exists(z2m_directory):
            os.makedirs(z2m_directory)
        else:
            try:
                Repo(z2m_directory)
                clone_needed = False
            except Exception:
                pass

        try:
            if clone_needed:
                await fhem.readingsSingleUpdate(
                    self.hash,
                    "installation",
                    "downloading zigbee2mqtt",
                    1,
                )
                await utils.run_blocking(
                    functools.partial(Repo.clone_from, GIT_URL, z2m_directory)
                )

            if (
                await fhem.ReadingsVal(self.hash["NAME"], "installation", "nok")
                != "successful"
            ):
                await fhem.readingsSingleUpdate(
                    self.hash,
                    "installation",
                    "installing dependencies, might take some minutes",
                    1,
                )
                await utils.run_blocking(
                    functools.partial(subprocess.call, ["npm", "ci"], cwd=z2m_directory)
                )

                z2m_conf = (
                    "homeassistant: false\n"
                    "permit_join: false\n"
                    "mqtt:\n"
                    "  base_topic: zigbee2mqtt\n"
                    "  server: 'mqtt://localhost'\n"
                    "  client_id: 'zigbee_pi'\n"
                    "serial:\n"
                    "  port: /dev/ttyUSB0\n"
                    "frontend:\n"
                    "  port: 8080\n"
                )
                with open(z2m_directory + "/data/configuration.yaml", "w") as file:
                    file.writelines(z2m_conf)

                await self.create_weblink()
                await fhem.readingsSingleUpdate(
                    self.hash, "installation", "successful", 1
                )
        except Exception:
            self.logger.exception("Failed to clone repo")
            await fhem.readingsSingleUpdate(
                self.hash,
                "state",
                "failed to install, check fhempy log",
                1,
            )
            return False

        await fhem.readingsSingleUpdate(self.hash, "state", "ready", 1)

        return True

    async def check_node_installation(self):
        try:
            ver = await utils.run_blocking(
                functools.partial(subprocess.check_output, ["node", "--version"])
            )
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "node", ver.decode("ascii").rstrip(), 1
            )
            return True
        except Exception:
            await fhem.readingsSingleUpdate(
                self.hash, "node", "nodejs installation missing", 1
            )
            return False

    async def check_npm_installation(self):
        try:
            ver = await utils.run_blocking(
                functools.partial(subprocess.check_output, ["npm", "--version"])
            )
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "npm", ver.decode("ascii").rstrip(), 1
            )
            return True
        except Exception:
            await fhem.readingsSingleUpdate(
                self.hash, "npm", "npm installation missing", 1
            )
            return False

    async def start_process(self):
        current_directory = os.getcwd()
        z2m_directory = os.path.join(current_directory, r".fhempy/zigbee2mqtt")

        try:
            self.proc = subprocess.Popen(["node", "./index.js"], cwd=z2m_directory)
            await fhem.readingsSingleUpdate(self.hash, "state", "running", 1)
            if self.check_process_task is None:
                self.check_process_task = self.create_async_task(self.check_process())
        except Exception:
            self.logger.exception("Failed to start zigbee2mqtt with npm start")

    async def check_process(self):
        while True:
            try:
                if self.proc is not None:
                    poll = self.proc.poll()
                    if poll is None:
                        await fhem.readingsSingleUpdateIfChanged(
                            self.hash, "state", "running", 1
                        )
                    elif poll != 0:
                        await fhem.readingsSingleUpdate(
                            self.hash, "state", "error, check log file", 1
                        )
                        await asyncio.sleep(10)
                        await self.start_process()
                    elif poll == 0:
                        await fhem.readingsSingleUpdate(
                            self.hash, "state", "stopped", 1
                        )
                        await asyncio.sleep(10)
                        await self.start_process()
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                return

    async def stop_process(self):
        if self.check_process_task:
            self.cancel_async_task(self.check_process_task)
            self.check_process_task = None
        if self.proc:
            await fhem.readingsSingleUpdate(self.hash, "state", "stopping", 1)
            self.proc.send_signal(signal.SIGINT)

            stop_tries = 0
            # give zigbee2mqtt some time to stop
            await asyncio.sleep(15)
            while self.proc.poll is None and stop_tries < 5:
                await asyncio.sleep(5)
                self.proc.kill()
                stop_tries += 1

            if self.proc.poll is None:
                self.logger.error("Failed to stop zigbee2mqtt process")
                await fhem.readingsSingleUpdate(self.hash, "state", "failed to stop", 1)
            else:
                # this should never block, as poll says process finished already
                # this should prevent zombie processes
                self.proc.wait(0.1)
                self.proc = None
                await fhem.readingsSingleUpdate(self.hash, "state", "stopped", 1)

    async def create_weblink(self):
        ip_list = [
            netifaces.ifaddresses(iface)[netifaces.AF_INET][0]["addr"]
            for iface in netifaces.interfaces()
            if netifaces.AF_INET in netifaces.ifaddresses(iface) and iface != "lo"
        ]
        await fhem.CommandDefine(
            self.hash, "z2m_frontend weblink iframe http://" + ip_list[0] + ":8080/"
        )
        await fhem.CommandAttr(
            self.hash,
            (
                "z2m_frontend htmlattr width='100%' height='90%' "
                "frameborder='0' marginheight='0' marginwidth='0'"
            ),
        )
        await fhem.CommandAttr(self.hash, "z2m_frontend room Zigbee2MQTT")

    # FHEM FUNCTION
    async def Undefine(self, hash):
        await self.stop_process()
        return await super().Undefine(hash)

    async def set_attr_disable(self, hash):
        if self._attr_disable == 0:
            self.create_async_task(self.start_process())
        else:
            self.create_async_task(self.stop_process())

    async def set_start(self, hash, params):
        self.create_async_task(self._restart())
        return ""

    async def set_stop(self, hash, params):
        self.create_async_task(self.stop_process())
        return ""

    async def set_restart(self, hash, params):
        self.create_async_task(self._restart())

    async def _restart(self):
        await self.stop_process()
        # wait for z2m to release hardware connection
        await asyncio.sleep(10)
        await self.start_process()

    async def set_update(self, hash, params):
        self.create_async_task(self.update_z2m())
