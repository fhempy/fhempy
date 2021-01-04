import os
import pytest
import logging
import importlib
from unittest.mock import MagicMock

from . import mock_fhem
from fhempy.lib import utils
from fhempy.lib.generic import FhemModule
from fhempy.lib.pkg_installer import check_and_install_dependencies

logger = logging.getLogger(__name__)


def pytest_generate_tests(metafunc):
    modules = []
    directory = "FHEM/bindings/python/fhempy/lib"
    for module_name in next(os.walk(directory))[1]:
        if module_name != "core" and module_name != "__pycache__":
            modules.append(module_name)
    metafunc.parametrize("module_name", modules, ids=modules)


@pytest.mark.asyncio
async def test_basic(module_name, mocker):
    mock_fhem.mock_module(mocker)
    testinstance = MagicMock()

    def asyncio_create_task(coroutine):
        assert False, "Use self.create_async_task() instead of asyncio.create_task()."

    mocker.patch("asyncio.create_task", asyncio_create_task)

    async def async_startstop_search(classinstance):
        return

    # disable create_async_task, otherwise it fails as it uses asyncio.create_task()
    mocker.patch("fhempy.lib.generic.FhemModule.create_async_task", return_value=0)
    mocker.patch("fhempy.lib.core.ssdp.ssdp.start_search", async_startstop_search)
    mocker.patch("fhempy.lib.core.ssdp.ssdp.stop_search", async_startstop_search)

    # TODO uninstall all dependencies

    await check_and_install_dependencies(module_name)
    module_object = importlib.import_module(
        "fhempy.lib." + module_name + "." + module_name
    )
    target_class = getattr(module_object, module_name)
    assert issubclass(target_class, FhemModule) == True, (
        "Use FhemModule as base class for your module " + module_name
    )

    class_instance = target_class(logger)
    assert isinstance(class_instance.logger, logging.Logger) == True

    testhash = {"NAME": "testname"}
    def_res = await class_instance.Define(
        testhash, ["test", "PythonModule", module_name], {}
    )
    if def_res is not None:
        assert (
            isinstance(def_res, str) == True
        ), "Return value of Define is not a string and not None"
        assert (
            def_res[:6] == "Usage:"
        ), "Return 'Usage: define ...' if no parameters are provided"
    ret_unknown = await utils.handle_set(
        class_instance._conf_set, testinstance, testhash, ["test", "?"], {}
    )
    ret = await class_instance.Set(testhash, ["test", "?"], {})
    assert ret == ret_unknown


# create testcase to check if super().__init__ was called
@pytest.mark.asyncio
async def test_super_init(module_name, mocker):
    mock_fhem.mock_module(mocker)
    testinstance = MagicMock()

    called = 0

    def initcall(classinstance, logger):
        nonlocal called
        called = 1

    mocker.patch("fhempy.lib.generic.FhemModule.__init__", initcall)

    module_object = importlib.import_module(
        "fhempy.lib." + module_name + "." + module_name
    )
    target_class = getattr(module_object, module_name)
    class_instance = target_class(logger)
    assert called == 1, (
        "Please call super().__init__(logger) in __init__(logger) in " + module_name
    )


# create testcase to check if await super().Define was called
@pytest.mark.asyncio
async def test_super_define(module_name, mocker):
    mock_fhem.mock_module(mocker)
    testinstance = MagicMock()

    called = 0

    async def definecall(classinstance, hash, args, argsh):
        classinstance.hash = hash
        await utils.handle_define_attr(classinstance._conf_attr, classinstance, hash)
        nonlocal called
        called = 1

    mocker.patch("fhempy.lib.generic.FhemModule.Define", definecall)

    module_object = importlib.import_module(
        "fhempy.lib." + module_name + "." + module_name
    )
    target_class = getattr(module_object, module_name)
    class_instance = target_class(logger)
    testhash = {"NAME": "testname"}
    await class_instance.Define(testhash, ["test", "PythonModule", module_name], {})
    assert called == 1, (
        "Please call await super().Define(hash, args, argh) in Define() in "
        + module_name
    )


# create testcase to check if Undefine calls FhemModule.Undefine()
@pytest.mark.asyncio
async def test_super_undefine(module_name, mocker):
    mock_fhem.mock_module(mocker)
    testinstance = MagicMock()

    called = 0

    async def undefinecall(classinstance, hash):
        nonlocal called
        called = 1

    mocker.patch("fhempy.lib.generic.FhemModule.Undefine", undefinecall)

    async def async_startstop_search(classinstance):
        return

    # disable create_async_task, otherwise it fails as it uses asyncio.create_task()
    mocker.patch("fhempy.lib.core.ssdp.ssdp.start_search", async_startstop_search)
    mocker.patch("fhempy.lib.core.ssdp.ssdp.stop_search", async_startstop_search)

    module_object = importlib.import_module(
        "fhempy.lib." + module_name + "." + module_name
    )
    target_class = getattr(module_object, module_name)
    class_instance = target_class(logger)
    testhash = {"NAME": "testname"}
    await class_instance.Undefine(testhash)
    assert called == 1, (
        "Please call await super().Undefine(hash) in Undefine(hash) in " + module_name
    )
