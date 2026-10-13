import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest.mark.asyncio
async def test_expired_login_asks_for_relogin(mocker, caplog):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("tuya_smartlife")
    from tuya_sharing.exceptions import ApiRequestException

    from fhempy.lib.tuya_smartlife import tuya_smartlife_setup as tss

    mock_fhem.readings.pop("testsmartlife", None)
    fhemdev = mocker.Mock()
    fhemdev.usercode = "123"
    fhemdev.hash = {"NAME": "testsmartlife"}
    setup = tss.tuya_smartlife_setup(logging.getLogger(__name__), fhemdev)
    setup.terminal_id = "t"
    setup.endpoint = "https://example.invalid"
    setup.token_info = {}
    manager = mocker.patch.object(tss, "Manager")
    manager.return_value.update_device_cache.side_effect = ApiRequestException(
        error_code=-9999999, error_message="sign invalid"
    )

    await setup.connect_to_smartlife()

    assert not setup.ready
    assert "relogin" in mock_fhem.readings["testsmartlife"]["state"]
    assert not [r for r in caplog.records if r.exc_info]
