import importlib
import logging
import os
from unittest.mock import MagicMock

import pytest
from fhempy.lib import utils
from fhempy.lib.generic import FhemModule
from fhempy.lib.pkg_installer import (check_and_install_dependencies,
                                      check_dependencies)

from ..utils import mock_fhem

logger = logging.getLogger(__name__)


def pytest_generate_tests(metafunc):
    modules = []
    directory = "FHEM/bindings/python/fhempy/lib"
    dirs = os.walk(directory)
    dirs = next(dirs)[1]
    for module_name in dirs:
        if module_name != "core" and module_name != "__pycache__":
            modules.append(module_name)
    metafunc.parametrize("module_name", modules, ids=modules)


# install dependencies
@pytest.mark.asyncio
async def test_basics(module_name, mocker):
    # TODO uninstall all dependencies

    await check_and_install_dependencies(module_name)
    module_object = importlib.import_module(
        "fhempy.lib." + module_name + "." + module_name
    )
    assert check_dependencies(module_name) == True

    # check FhemModule
    target_class = getattr(module_object, module_name)
    assert issubclass(target_class, FhemModule) == True, (
        "Use FhemModule as base class for your module " + module_name
    )

    # check logger
    mock_fhem.mock_module(mocker)
    testinstance = MagicMock()

    class_instance = target_class(logger)
    assert isinstance(class_instance.logger, logging.Logger) == True

    # check define usage
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

    # check set response with ?
    ret_unknown = await utils.handle_set(
        class_instance._conf_set, testinstance, testhash, ["test", "?"], {}
    )
    ret = await class_instance.Set(testhash, ["test", "?"], {})
    assert ret == ret_unknown

    ret = await class_instance.Undefine(testhash)
    assert ret == None
