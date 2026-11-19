import asyncio
import functools
import hashlib
import json
import os
import shutil
import signal
import subprocess

import aiofiles
import ifaddr
from git import Repo

from fhempy.lib.generic import FhemModule

from .. import fhem, utils
from ..core import child_process, pending_restore
from ..core.shell_env import interactive_shell_env

DEFAULT_CONFIG = (
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


# pnpm asks before it removes node_modules (e.g. after a pnpm major update),
# without a terminal it aborts. CI=true and confirmModulesPurge=false make
# it reinstall without asking.
PNPM_INSTALL = "pnpm install --frozen-lockfile --config.confirm-modules-purge=false"
PNPM_BUILD = "pnpm run build"
# written after dependencies were installed and built successfully, holds
# the state of the checkout they were installed for
INSTALL_MARKER = "node_modules/.fhempy_installed"
OUTPUT_TAIL_LINES = 30


def install_signature(z2m_directory):
    """Fingerprint of the files the installed node_modules depend on."""
    digest = hashlib.sha256()
    for name in ["package.json", "pnpm-lock.yaml"]:
        path = os.path.join(z2m_directory, name)
        digest.update(name.encode())
        if os.path.exists(path):
            with open(path, "rb") as file:
                digest.update(file.read())
    return digest.hexdigest()


def dependencies_up_to_date(z2m_directory):
    """True if node_modules was installed for the current checkout."""
    marker = os.path.join(z2m_directory, INSTALL_MARKER)
    if not os.path.exists(marker):
        return False
    with open(marker) as file:
        return file.read().strip() == install_signature(z2m_directory)


def write_install_marker(z2m_directory):
    marker = os.path.join(z2m_directory, INSTALL_MARKER)
    os.makedirs(os.path.dirname(marker), exist_ok=True)
    with open(marker, "w") as file:
        file.write(install_signature(z2m_directory) + "\n")


def remove_install_marker(z2m_directory):
    marker = os.path.join(z2m_directory, INSTALL_MARKER)
    if os.path.exists(marker):
        os.remove(marker)


def remove_node_modules(z2m_directory):
    shutil.rmtree(os.path.join(z2m_directory, "node_modules"), ignore_errors=True)


def write_default_config(conf_file):
    """Write the default configuration, return False if one exists already."""
    if os.path.exists(conf_file):
        return False
    os.makedirs(os.path.dirname(conf_file), exist_ok=True)
    with open(conf_file, "w") as file:
        file.write(DEFAULT_CONFIG)
    return True


class zigbee2mqtt(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.proc = None
        self.check_process_task = None
        self._shell_env = None

    async def _get_shell_env(self):
        if self._shell_env is None:
            self._shell_env = await utils.run_blocking(
                functools.partial(interactive_shell_env)
            )
        return self._shell_env

    async def _shell(self, func, command, **kwargs):
        # run command in bash with the PATH of an interactive shell
        env = await self._get_shell_env()
        return await utils.run_blocking(
            functools.partial(
                func,
                ["bash", "-c", command],
                env=env,
                stdin=subprocess.DEVNULL,
                **kwargs,
            )
        )

    async def _run_step(self, command, cwd):
        """Run command, log its output and raise if it fails."""
        env = dict(await self._get_shell_env())
        env["CI"] = "true"
        self.logger.info(f"zigbee2mqtt: running '{command}'")
        result = await utils.run_blocking(
            functools.partial(
                subprocess.run,
                ["bash", "-c", command],
                env=env,
                cwd=cwd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
        )
        output = result.stdout.decode(errors="replace").strip().splitlines()
        tail = "\n".join(output[-OUTPUT_TAIL_LINES:])
        if result.returncode != 0:
            self.logger.error(
                f"zigbee2mqtt: '{command}' failed with exit code "
                f"{result.returncode}:\n{tail}"
            )
            raise RuntimeError(f"'{command}' failed with exit code {result.returncode}")
        self.logger.info(f"zigbee2mqtt: '{command}' finished")
        if tail:
            self.logger.debug(tail)

    async def install_dependencies(self, z2m_directory, reading):
        """Install node_modules and build zigbee2mqtt like its update.sh."""
        # an interrupted install must not look like a finished one
        await utils.run_blocking(
            functools.partial(remove_install_marker, z2m_directory)
        )
        await fhem.readingsSingleUpdate(
            self.hash, reading, "installing dependencies, may take a few minutes", 1
        )
        try:
            await self._run_step(PNPM_INSTALL, z2m_directory)
        except RuntimeError:
            # a broken or incompatible node_modules can't always be
            # repaired in place, start from scratch once
            self.logger.warning(
                "zigbee2mqtt: removing node_modules and installing again"
            )
            await utils.run_blocking(
                functools.partial(remove_node_modules, z2m_directory)
            )
            await self._run_step(PNPM_INSTALL, z2m_directory)
        await fhem.readingsSingleUpdate(
            self.hash, reading, "building zigbee2mqtt, may take a few minutes", 1
        )
        await self._run_step(PNPM_BUILD, z2m_directory)
        await utils.run_blocking(functools.partial(write_install_marker, z2m_directory))
        self.logger.info("zigbee2mqtt: dependencies installed and built")

    async def pull_z2m(self, z2m_directory):
        rep = Repo(z2m_directory)
        old = rep.head.commit.hexsha
        try:
            await utils.run_blocking(functools.partial(rep.remotes.origin.pull))
        except Exception:
            # local changes to tracked files (e.g. a lockfile written by an
            # older install) block the pull, data/ is not tracked by git
            self.logger.exception(
                "zigbee2mqtt: git pull failed, resetting to the remote branch"
            )
            await utils.run_blocking(functools.partial(rep.remotes.origin.fetch))
            await utils.run_blocking(functools.partial(rep.git.reset, "--hard", "@{u}"))
        new = rep.head.commit.hexsha
        if old == new:
            self.logger.info(f"zigbee2mqtt: already up to date ({new[:8]})")
        else:
            self.logger.info(f"zigbee2mqtt: updated {old[:8]} -> {new[:8]}")

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        self._set_list = {"start": {}, "stop": {}, "restart": {}, "update": {}}
        await self.set_set_config(self._set_list)
        attr_conf = {"disable": {"options": "0,1", "default": "0", "format": "int"}}
        await self.set_attr_config(attr_conf)

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

        res = await self.check_pnpm_installation()
        if res is False:
            return

        res = await self.install_z2m()
        if res is False:
            return

        await self.start_process()

    async def update_z2m(self):
        stopped = False
        try:
            await fhem.readingsSingleUpdate(
                self.hash, "update", "started, may take a few minutes", 1
            )
            current_directory = os.getcwd()
            z2m_directory = os.path.join(current_directory, r".fhempy/zigbee2mqtt")

            if not await self.stop_process():
                # a second zigbee2mqtt can't open the serial port while the
                # old one is still running
                await fhem.readingsSingleUpdate(
                    self.hash, "update", "failed, zigbee2mqtt did not stop", 1
                )
                return
            stopped = True
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

            await fhem.readingsSingleUpdate(
                self.hash, "update", "downloading zigbee2mqtt", 1
            )
            await self.pull_z2m(z2m_directory)
            # always reinstall, the new version might need other node_modules
            await self.install_dependencies(z2m_directory, "update")

            source_folder = z2m_directory + "/data-backup"
            destination_folder = z2m_directory + "/data"
            for file in os.listdir(source_folder):
                file_path = os.path.join(source_folder, file)
                if os.path.isfile(file_path):
                    await utils.run_blocking(
                        functools.partial(shutil.copy, file_path, destination_folder)
                    )

            await fhem.readingsSingleUpdate(self.hash, "update", "successful", 1)
        except Exception:
            self.logger.exception("Failed to update")
            await fhem.readingsSingleUpdate(
                self.hash, "update", "failed to update, check log", 1
            )
        if stopped:
            # start zigbee2mqtt again, also if the update failed
            await self._wait_for_port_release()
            await self.start_process()

    async def _install_needed(self, z2m_directory, clone_needed):
        # a fresh clone always needs to be installed
        if clone_needed:
            return True
        # an interrupted or failed update leaves node_modules that don't
        # fit the checkout
        if not await utils.run_blocking(
            functools.partial(dependencies_up_to_date, z2m_directory)
        ):
            self.logger.warning(
                "zigbee2mqtt: node_modules doesn't match the installed "
                "version, installing dependencies again"
            )
            return True
        # the installation reading might come from a restored fhem.save
        installation = await fhem.ReadingsVal(self.hash["NAME"], "installation", "nok")
        return installation != "successful"

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

            if await self._install_needed(z2m_directory, clone_needed):
                await self.install_dependencies(z2m_directory, "installation")

                # never replace an existing configuration, it holds the
                # network key and PAN ID of the paired zigbee network
                z2m_conf_file = os.path.join(z2m_directory, "data/configuration.yaml")
                if not await utils.run_blocking(
                    functools.partial(write_default_config, z2m_conf_file)
                ):
                    self.logger.info(
                        "Keep existing zigbee2mqtt configuration " + z2m_conf_file
                    )

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
            # call subprocess and respect the users PATH from .bashrc
            ver = await self._shell(subprocess.check_output, "node --version")
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
            ver = await self._shell(subprocess.check_output, "npm --version")
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "npm", ver.decode("ascii").rstrip(), 1
            )
            return True
        except Exception:
            await fhem.readingsSingleUpdate(
                self.hash, "npm", "npm installation missing", 1
            )
            return False

    async def check_pnpm_installation(self):
        try:
            ver = await self._shell(subprocess.check_output, "pnpm --version")
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "pnpm", ver.decode("ascii").rstrip(), 1
            )
            return True
        except Exception:
            await fhem.readingsSingleUpdate(
                self.hash, "pnpm", "pnpm installation missing", 1
            )
            return False

    async def apply_restored_backup(self, z2m_directory):
        # data restored by github_restore is applied after the installation
        # and before zigbee2mqtt starts, otherwise it would be overwritten
        try:
            applied = await utils.run_blocking(
                functools.partial(pending_restore.apply_z2m_restore, z2m_directory)
            )
        except Exception:
            self.logger.exception("Failed to apply restored zigbee2mqtt backup")
            await fhem.readingsSingleUpdate(
                self.hash, "restore", "failed to apply backup, check log", 1
            )
            return
        if applied:
            self.logger.info(f"Applied restored zigbee2mqtt backup: {applied}")
            await fhem.readingsSingleUpdate(
                self.hash, "restore", "backup applied: " + ", ".join(applied), 1
            )

    async def start_process(self):
        current_directory = os.getcwd()
        z2m_directory = os.path.join(current_directory, r".fhempy/zigbee2mqtt")

        await self.apply_restored_backup(z2m_directory)

        # Load the package.json file
        async with aiofiles.open(z2m_directory + "/package.json", "r") as f:
            package_data = json.loads(await f.read())

        # Extract the version number
        version = package_data["version"]
        await fhem.readingsSingleUpdate(self.hash, "z2m_version", version, 1)

        try:
            self.proc = child_process.start(
                ["bash", "-c", "exec node ./index.js"],
                cwd=z2m_directory,
                env=await self._get_shell_env(),
                stdin=subprocess.DEVNULL,
                output_log=child_process.OutputLog(
                    child_process.log_path(self.hash["NAME"]), self.logger
                ),
            )
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
                            self.hash,
                            "state",
                            "error, check "
                            + os.path.relpath(
                                child_process.log_path(self.hash["NAME"])
                            ),
                            1,
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
                raise

    async def stop_process(self):
        if self.check_process_task:
            self.cancel_async_task(self.check_process_task)
            self.check_process_task = None
        if self.proc is None:
            return True
        # stop the process before talking to FHEM, FHEM might not answer
        # anymore during fhempy update or shutdown
        # give zigbee2mqtt some time to stop
        if await child_process.stop(self.proc, signal.SIGINT, timeout=15):
            self.proc = None
            await fhem.readingsSingleUpdate(self.hash, "state", "stopped", 1)
            return True
        self.logger.error("Failed to stop zigbee2mqtt process")
        await fhem.readingsSingleUpdate(self.hash, "state", "failed to stop", 1)
        return False

    async def create_weblink(self):
        ip_list = [
            ip.ip
            for adapter in ifaddr.get_adapters()
            if adapter.name != "lo"
            for ip in adapter.ips
            if ip.is_IPv4
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
        if not await self.stop_process():
            return
        await self._wait_for_port_release()
        await self.start_process()

    async def _wait_for_port_release(self):
        # wait for z2m to release hardware connection
        await asyncio.sleep(10)

    async def set_update(self, hash, params):
        self.create_async_task(self.update_z2m())
