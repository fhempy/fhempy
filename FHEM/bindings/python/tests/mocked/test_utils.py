import functools

import pytest
from fhempy.lib import utils


def test_local_ip():
    ip = utils.get_local_ip()
    assert ip != "127.0.0.1"


def test_encrypt_decrypt():
    teststring = "This is a test string"
    fhem_unique_id = "a3e36c8ec8622a0de0e11191dc430a34"
    encrypted_string = utils.encrypt_string(teststring, fhem_unique_id)
    decrypted_string = utils.decrypt_string(encrypted_string, fhem_unique_id)
    assert teststring == decrypted_string
    return decrypted_string


@pytest.mark.asyncio
async def test_run_blocking():
    test_string = await utils.run_blocking(functools.partial(test_encrypt_decrypt))
    assert "This is a test string" == test_string


@pytest.mark.asyncio
async def test_run_blocking_task():
    foo = None

    def set_foo():
        nonlocal foo
        foo = "bar"

    task = utils.run_blocking_task(functools.partial(set_foo))
    await task
    assert foo == "bar"


@pytest.mark.asyncio
async def test_handle_define_attr(mocker):
    async def setDevAttrList(hashname, attrlist):
        assert hashname == "test"
        assert str(attrlist) == "attr1 attr2 attr3 attr4 attr5:on,off,test"

    async def AttrVal(hashname, attr, default):
        if attr == "attr3":
            return "test33"
        return ""

    mocker.patch("fhempy.lib.fhem.setDevAttrList", setDevAttrList)
    mocker.patch("fhempy.lib.fhem.AttrVal", AttrVal)

    class TestClass:
        async def set_attr(self, hash):
            assert self._attr_attr4 == "test4"

    testinstance = TestClass()
    attr_conf = {
        "attr1": {},
        "attr2": {"default": 1, "format": "int"},
        "attr3": {"default": "test3"},
        "attr4": {"default": "test4", "function": "set_attr"},
        "attr5": {"default": "test5", "options": "on,off,test"},
    }
    hash = {"NAME": "test"}
    await utils.handle_define_attr(attr_conf, testinstance, hash)
    assert testinstance._attr_attr1 == ""
    assert testinstance._attr_attr2 == 1
    assert testinstance._attr_attr3 == "test33"
    assert testinstance._attr_attr4 == "test4"
    assert testinstance._attr_attr5 == "test5"


@pytest.mark.asyncio
async def test_handle_attr():
    class TestClass:
        async def set_attr(self, hash):
            assert self._attr_attr4 == "asdf"

    testinstance = TestClass()
    attr_conf = {
        "attr1": {},
        "attr2": {"default": 1, "format": "int"},
        "attr3": {"default": "test3"},
        "attr4": {"default": "test4", "function": "set_attr"},
        "attr5": {"default": "test5", "options": "on,off,test"},
    }
    hash = {"NAME": "test"}
    # set new value
    await utils.handle_attr(
        attr_conf, testinstance, hash, ["set", "test", "attr1", "NEWVALUE"], {}
    )
    assert testinstance._attr_attr1 == "NEWVALUE"

    # set integer
    await utils.handle_attr(
        attr_conf, testinstance, hash, ["set", "test", "attr2", "2"], {}
    )
    assert testinstance._attr_attr2 == 2

    # del attribute
    await utils.handle_attr(
        attr_conf, testinstance, hash, ["del", "test", "attr2", ""], {}
    )
    assert testinstance._attr_attr2 == 1

    await utils.handle_attr(
        attr_conf, testinstance, hash, ["set", "test", "attr4", "asdf"], {}
    )
    assert testinstance._attr_attr4 == "asdf"


def test_flatten_json():
    json = {"asdf": {"nested": {"nested2": "x"}}}
    flat_json = utils.flatten_json(json)
    for element in flat_json:
        assert element == "asdf_nested_nested2"
        assert flat_json[element] == "x"


def test_convert2format():
    listdef = {"format": "int"}
    newval = utils.convert2format("3", listdef)
    assert newval == 3

    listdef = {"format": "int"}
    newval = utils.convert2format("3", listdef)
    assert newval == 3
    assert isinstance(newval, int) == True

    listdef = {"format": "str"}
    newval = utils.convert2format("3", listdef)
    assert newval == "3"
    assert isinstance(newval, str) == True

    listdef = {"format": "float"}
    newval = utils.convert2format("3", listdef)
    assert newval == 3.0
    assert isinstance(newval, float) == True

    listdef = {}
    newval = utils.convert2format("3", listdef)
    assert newval == "3"

    listdef = {}
    newval = utils.convert2format(3, listdef)
    assert newval == 3


@pytest.mark.asyncio
async def test_handle_set():
    set_list_conf = {
        "mode": {
            "args": ["mode"],
            "argsh": ["mode"],
            "params": {"mode": {"optional": False}},
            "options": "eco,comfort",
        },
        "desiredTemp": {"args": ["temperature"], "options": "slider,10,1,30"},
        "holidayMode": {
            "args": ["temperature", "till", "end"],
            "params": {"till": {"default": "31.12.2030"}, "end": {"default": "23:59"}},
        },
        "on": {
            "args": ["seconds"],
            "params": {"seconds": {"optional": True, "format": "int"}},
        },
        "off": {},
    }

    newstate = None

    class TestClass:
        def __init__(self):
            pass

        async def set_on(self, hash, params):
            nonlocal newstate
            if len(params) == 0:
                newstate = "on"
            else:
                newstate = params

        async def set_off(self, hash, params):
            assert hash["NAME"] == "testhash"
            nonlocal newstate
            newstate = "off"

        async def set_mode(self, hash, params):
            nonlocal newstate
            newstate = params

        async def set_holidayMode(self, hash, params):
            nonlocal newstate
            newstate = params

    testhash = {"NAME": "testhash"}

    testinstance = TestClass()
    retval = await utils.handle_set(
        set_list_conf, testinstance, testhash, ["testhash"], {}
    )
    assert (
        retval
        == "Unknown argument ?, choose one of mode:eco,comfort desiredTemp:slider,10,1,30 holidayMode on off:noArg"
    )

    retval = await utils.handle_set(
        set_list_conf, testinstance, testhash, ["testhash", "?"], {}
    )
    assert (
        retval
        == "Unknown argument ?, choose one of mode:eco,comfort desiredTemp:slider,10,1,30 holidayMode on off:noArg"
    )

    retval = await utils.handle_set(
        set_list_conf,
        testinstance,
        testhash,
        ["testhash", "mode"],
        {},
    )
    assert retval == "Required argument mode missing."

    retval = await utils.handle_set(
        set_list_conf, testinstance, testhash, ["testhash", "nopossiblecommand"], {}
    )
    assert retval == "Command not available for this device."

    retval = await utils.handle_set(
        set_list_conf,
        testinstance,
        testhash,
        ["testhash", "off", "toomanyarguments"],
        {},
    )
    assert retval == "Too many parameters provided: toomanyarguments"

    retval = await utils.handle_set(
        set_list_conf,
        testinstance,
        testhash,
        ["testhash", "off"],
        {},
    )
    assert newstate == "off"

    retval = await utils.handle_set(
        set_list_conf,
        testinstance,
        testhash,
        ["testhash", "mode", "eco"],
        {},
    )
    assert newstate == {"mode": "eco"}

    newstate = None
    retval = await utils.handle_set(
        set_list_conf,
        testinstance,
        testhash,
        ["testhash", "mode"],
        {"mode": "eco"},
    )
    assert newstate == {"mode": "eco"}

    newstate = None
    retval = await utils.handle_set(
        set_list_conf,
        testinstance,
        testhash,
        ["testhash", "mode", "nonexistent"],
        {},
    )
    assert retval == None
    assert newstate == {"mode": "nonexistent"}

    newstate = None
    retval = await utils.handle_set(
        set_list_conf,
        testinstance,
        testhash,
        ["testhash", "holidayMode", "21"],
        {},
    )
    assert retval == None
    assert newstate == {"till": "31.12.2030", "end": "23:59", "temperature": "21"}

    newstate = None
    retval = await utils.handle_set(
        set_list_conf,
        testinstance,
        testhash,
        ["testhash", "holidayMode", "21", "31.12.2040", "23:38"],
        {},
    )
    assert retval == None
    assert newstate == {"till": "31.12.2040", "end": "23:38", "temperature": "21"}

    newstate = None
    retval = await utils.handle_set(
        set_list_conf,
        testinstance,
        testhash,
        ["testhash", "on"],
        {},
    )
    assert retval == None
    assert newstate == "on"

    newstate = None
    retval = await utils.handle_set(
        set_list_conf,
        testinstance,
        testhash,
        ["testhash", "on", "300"],
        {},
    )
    assert retval == None
    assert newstate == {"seconds": 300}
