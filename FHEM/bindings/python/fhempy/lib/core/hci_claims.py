"""
Exclusive use of a local Bluetooth adapter (hciX) by one module.

Some modules drive an adapter directly via HCI, e.g. ble_monitor scans
with its own parameters and the Matter server (Node.js) resets the adapter
when it starts with Bluetooth. A module which needs the adapter for a while
claims it, others leave it alone until it is released and then set it up
again (listeners are called on claim and release).

Only covers modules in the same fhempy process.
"""

import logging

logger = logging.getLogger(__name__)

_claims = {}
_listeners = []


def claim(adapter, owner):
    """owner uses hci<adapter> exclusively until release()"""
    owners = _claims.setdefault(int(adapter), set())
    if owner in owners:
        return
    owners.add(owner)
    logger.debug(f"hci{adapter} claimed by {owner}")
    _notify(int(adapter), True)


def release(adapter, owner):
    owners = _claims.get(int(adapter))
    if not owners or owner not in owners:
        return
    owners.discard(owner)
    logger.debug(f"hci{adapter} released by {owner}")
    if not owners:
        del _claims[int(adapter)]
        _notify(int(adapter), False)


def is_claimed(adapter):
    return bool(_claims.get(int(adapter)))


def add_listener(listener):
    """listener(adapter, claimed) is called when a claim starts or ends"""
    if listener not in _listeners:
        _listeners.append(listener)


def remove_listener(listener):
    if listener in _listeners:
        _listeners.remove(listener)


def _notify(adapter, claimed):
    for listener in list(_listeners):
        try:
            listener(adapter, claimed)
        except Exception:
            logger.exception("hci claim listener failed")
