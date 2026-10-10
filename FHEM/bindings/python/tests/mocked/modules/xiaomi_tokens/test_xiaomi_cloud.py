import asyncio
import base64
import json
import logging

import pytest
import requests_mock
from fhempy.lib.xiaomi_tokens import xiaomi_cloud
from fhempy.lib.xiaomi_tokens.xiaomi_cloud import (
    CaptchaRequired,
    VerificationRequired,
    XiaomiCloud,
    XiaomiCloudError,
)
from tests.utils import mock_fhem

ACCOUNT = "https://account.xiaomi.com"
SSECURITY = base64.b64encode(b"0123456789abcdef").decode()
NONCE = base64.b64encode(b"nonce-123456").decode()
STEP1 = '&&&START&&&{"_sign": "sign123"}'
LOGIN_OK = "&&&START&&&" + json.dumps(
    {
        "ssecurity": SSECURITY,
        "userId": 1234,
        "location": "https://sts.api.io.mi.com/sts?token=1",
    }
)
DEVICE = {
    "did": "123456",
    "name": "Vacuum",
    "token": "abcdef0123456789",
    "model": "roborock.vacuum.a10",
    "localip": "192.168.1.10",
}


def encrypted(cloud, payload):
    signed_nonce = cloud._signed_nonce(NONCE)
    return cloud._encrypt_rc4(signed_nonce, json.dumps(payload))


def mock_login(mock):
    mock.get(f"{ACCOUNT}/pass/serviceLogin?sid=xiaomiio&_json=true", text=STEP1)
    mock.post(f"{ACCOUNT}/pass/serviceLoginAuth2", text=LOGIN_OK)
    mock.get(
        "https://sts.api.io.mi.com/sts?token=1",
        text="ok",
        headers={"Set-Cookie": "serviceToken=service123; Path=/"},
    )


def mock_devices(mock, cloud, server="de"):
    base = f"https://{server}.api.io.mi.com/app"
    mock.post(
        f"{base}/v2/homeroom/gethome",
        text=lambda req, ctx: encrypted(cloud, {"result": {"homelist": [{"id": 99}]}}),
    )
    mock.post(
        f"{base}/v2/user/get_device_cnt",
        text=lambda req, ctx: encrypted(
            cloud, {"result": {"share": {"share_family": []}}}
        ),
    )
    mock.post(
        f"{base}/v2/home/home_device_list",
        text=lambda req, ctx: encrypted(cloud, {"result": {"device_info": [DEVICE]}}),
    )


def test_password_login_and_devices(mocker):
    mocker.patch.object(XiaomiCloud, "_generate_nonce", return_value=NONCE)
    cloud = XiaomiCloud()
    with requests_mock.Mocker() as mock:
        mock_login(mock)
        cloud.login("user@example.com", "secret")
        assert cloud.logged_in
        mock_devices(mock, cloud)
        assert cloud.get_devices("de") == [DEVICE]


def test_wrong_password():
    cloud = XiaomiCloud()
    with requests_mock.Mocker() as mock:
        mock.get(f"{ACCOUNT}/pass/serviceLogin?sid=xiaomiio&_json=true", text=STEP1)
        mock.post(
            f"{ACCOUNT}/pass/serviceLoginAuth2",
            text='&&&START&&&{"code": 70016, "desc": "wrong password"}',
        )
        with pytest.raises(XiaomiCloudError, match="wrong password"):
            cloud.login("user@example.com", "wrong")


def test_captcha():
    cloud = XiaomiCloud()
    with requests_mock.Mocker() as mock:
        mock.get(f"{ACCOUNT}/pass/serviceLogin?sid=xiaomiio&_json=true", text=STEP1)
        mock.post(
            f"{ACCOUNT}/pass/serviceLoginAuth2",
            [
                {"text": '&&&START&&&{"code": 87001, "captchaUrl": "/pass/getCode"}'},
                {"text": LOGIN_OK},
            ],
        )
        mock.get(f"{ACCOUNT}/pass/getCode", content=b"jpegdata")
        mock.get(
            "https://sts.api.io.mi.com/sts?token=1",
            text="ok",
            headers={"Set-Cookie": "serviceToken=service123; Path=/"},
        )
        with pytest.raises(CaptchaRequired) as captcha:
            cloud.login("user@example.com", "secret")
        assert captcha.value.image == b"jpegdata"
        cloud.submit_captcha("abcd")
        assert cloud.logged_in
        assert "captCode=abcd" in mock.request_history[-2].url


def test_email_verification():
    cloud = XiaomiCloud()
    notification = f"{ACCOUNT}/identity/authStart?sid=xiaomiio&context=ctx1"
    with requests_mock.Mocker() as mock:
        mock.get(f"{ACCOUNT}/pass/serviceLogin?sid=xiaomiio&_json=true", text=STEP1)
        mock.post(
            f"{ACCOUNT}/pass/serviceLoginAuth2",
            text='&&&START&&&{"code": 0, "notificationUrl": "' + notification + '"}',
        )
        mock.get(notification, text="")
        mock.get(f"{ACCOUNT}/identity/list", text="")
        mock.post(f"{ACCOUNT}/identity/auth/sendEmailTicket", json={"code": 0})
        with pytest.raises(VerificationRequired):
            cloud.login("user@example.com", "secret")

        mock.post(
            f"{ACCOUNT}/identity/auth/verifyEmail",
            json={"code": 0, "location": f"{ACCOUNT}/identity/result/check?x=1"},
        )
        mock.get(
            f"{ACCOUNT}/identity/result/check?x=1",
            status_code=302,
            headers={"Location": f"{ACCOUNT}/pass/serviceLoginAuth2/end?x=1"},
        )
        mock.get(
            f"{ACCOUNT}/pass/serviceLoginAuth2/end?x=1",
            status_code=302,
            headers={
                "extension-pragma": json.dumps({"ssecurity": SSECURITY}),
                "Location": "https://sts.api.io.mi.com/sts?token=2",
            },
        )
        mock.get(
            "https://sts.api.io.mi.com/sts?token=2",
            text="ok",
            headers={"Set-Cookie": "serviceToken=service456; Path=/"},
        )
        cloud.submit_verification_code("123456")
        assert cloud.logged_in


@pytest.mark.asyncio
async def test_module_get_tokens(mocker):
    mock_fhem.mock_module(mocker)
    mocker.patch.object(XiaomiCloud, "_generate_nonce", return_value=NONCE)
    mocker.patch.object(xiaomi_cloud, "SERVERS", ["de"])
    from fhempy.lib.xiaomi_tokens.xiaomi_tokens import xiaomi_tokens

    testhash = {"NAME": "testtokens", "FHEMPYTYPE": "xiaomi_tokens"}
    mock_fhem.readings.pop("testtokens", None)
    module = xiaomi_tokens(logging.getLogger(__name__))
    await module.Define(testhash, ["testtokens", "fhempy", "xiaomi_tokens"], {})
    module._attr_servers = "de"
    module._username = "user@example.com"
    module._password = "secret"

    with requests_mock.Mocker() as mock:
        mock_login(mock)
        module._cloud = None
        original = XiaomiCloud.login

        def login_and_mock(cloud, username, password):
            mock_devices(mock, cloud)
            return original(cloud, username, password)

        mocker.patch.object(XiaomiCloud, "login", login_and_mock)
        await module.obtain_tokens()

    readings = mock_fhem.readings["testtokens"]
    assert readings["123456_de_token"] == "abcdef0123456789"
    assert readings["state"] == "1 devices found"
    assert (
        "123456_de_(Vacuum)" in module._set_list_conf["create_miio_device"]["options"]
    )
    await asyncio.sleep(0)
