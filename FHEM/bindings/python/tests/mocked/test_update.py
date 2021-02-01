import json
import logging
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
    fhempy = fhem_pythonbinding.PyBinding(websocket)

    update_msg = {
        "id": "123",
        "msgtype": "update",
        "NAME": "testdevice",
        "args": [],
        "argsh": {},
        "defargs": [],
        "defargsh": {},
    }
    update_text = json.dumps(update_msg)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        await fhempy.onMessage(update_text)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    assert is_installed("fhempy")
