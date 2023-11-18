import json
import logging
import os
import sys
from unittest.mock import MagicMock

import pytest
from fhempy.lib import fhem_pythonbinding
from fhempy.lib.pkg_installer import is_installed

from ..utils import mock_fhem

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_update(mocker):

    # monkey patch MagicMock
    async def async_magic():
        pass

    MagicMock.__await__ = lambda x: async_magic().__await__()

    mock_fhem.mock_module(mocker)
    websocket = MagicMock()
    fhempy = fhem_pythonbinding.fhempy(websocket)

    update_msg = {
        "id": "123",
        "msgtype": "update",
        "NAME": "testdevice",
        "PYTHONTYPE": "testname",
        "FHEMPYTYPE": "testname",
        "args": [],
        "argsh": {},
        "defargs": [],
        "defargsh": {},
    }
    update_text = json.dumps(update_msg)
    await fhempy.onMessage(update_text)

    assert fhem_pythonbinding.exit_code == 1
    assert fhem_pythonbinding.stop_event.is_set() is True
    assert is_installed("fhempy")
