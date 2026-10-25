"""Defines the autodiscovery device once on the local fhempy, also for
installations which existed before autodiscovery. Deleting the device is
respected, it isn't defined again."""

import asyncio

from .. import fhem

KEY = "fhempy_autodiscovery_defined"
NAME = "fhempy_discovery"
TYPES = "autodiscovery|discover_mdns|discover_ble|discover_upnp"
# FHEM might still define the devices of fhem.cfg
DELAY = 60


def define_command():
    return (
        f'my ($e, $v) = getKeyValue("{KEY}");; return "" if ($v);; '
        f'setKeyValue("{KEY}", 1);; '
        "my @d = grep { ($main::defs{$_}{FHEMPYTYPE} // '') =~ "
        f"/^({TYPES})$/ }} keys %main::defs;; "
        'return "" if (@d || defined($main::defs{"' + NAME + '"}));; '
        f'CommandDefine(undef, "{NAME} fhempy autodiscovery") // "defined"'
    )


async def define_once(logger):
    await asyncio.sleep(DELAY)
    try:
        ret = await fhem.sendCommandName(NAME, define_command())
        if ret == "defined":
            logger.info(f"Defined {NAME}, it offers the devices found in the network")
        elif ret:
            logger.error(f"Failed to define {NAME}: {ret}")
    except Exception:
        logger.exception(f"Failed to define {NAME}")
