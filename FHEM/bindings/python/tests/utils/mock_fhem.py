import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

function_active = []
update_locks = {}
wsconnection = None

readings = {}
attributes = {}
internals = {}
command_define = []
command_attr = []


def mock_module(mocker):
    mocker.patch("fhempy.lib.fhem.updateConnection", updateConnection)
    mocker.patch("fhempy.lib.fhem.setFunctionActive", setFunctionActive)
    mocker.patch("fhempy.lib.fhem.getUniqueId", getUniqueId)
    mocker.patch("fhempy.lib.fhem.ReadingsVal", ReadingsVal)
    mocker.patch("fhempy.lib.fhem.AttrVal", AttrVal)
    mocker.patch("fhempy.lib.fhem.InternalVal", InternalVal)
    mocker.patch("fhempy.lib.fhem.addToDevAttrList", addToDevAttrList)
    mocker.patch("fhempy.lib.fhem.setDevAttrList", setDevAttrList)
    mocker.patch("fhempy.lib.fhem.readingsBeginUpdate", readingsBeginUpdate)
    mocker.patch(
        "fhempy.lib.fhem.readingsBulkUpdateIfChanged", readingsBulkUpdateIfChanged
    )
    mocker.patch("fhempy.lib.fhem.readingsBulkUpdate", readingsBulkUpdate)
    mocker.patch("fhempy.lib.fhem.readingsEndUpdate", readingsEndUpdate)
    mocker.patch("fhempy.lib.fhem.readingsSingleUpdate", readingsSingleUpdate)
    mocker.patch(
        "fhempy.lib.fhem.readingsSingleUpdateIfChanged", readingsSingleUpdateIfChanged
    )
    mocker.patch("fhempy.lib.fhem.CommandDefine", CommandDefine)
    mocker.patch("fhempy.lib.fhem.CommandAttr", CommandAttr)
    mocker.patch("fhempy.lib.fhem.CommandDeleteReading", CommandDeleteReading)
    mocker.patch("fhempy.lib.fhem.checkIfDeviceExists", checkIfDeviceExists)
    mocker.patch("fhempy.lib.fhem.convertValue", convertValue)
    mocker.patch("fhempy.lib.fhem.send_version", send_version)
    mocker.patch("fhempy.lib.fhem.setFunctionInactive", do_nothing)
    mocker.patch("fhempy.lib.fhem.init_done", init_done)


def do_nothing(param):
    return


def updateConnection(ws):
    return


def setFunctionActive(hash):
    function_active.append(hash["NAME"])


def setFunctionInactive(hash):
    element = function_active.pop()
    if element != hash["NAME"]:
        logger.error(
            f"Set wrong function inactive, tried {hash['NAME']}, current function_active: {function_active},{element}"
        )


async def init_done(hash):
    return 1


async def getUniqueId(hash):
    return "12345678901234567890123456789012"


async def ReadingsVal(name, reading, default):
    if name in readings and reading in readings[name]:
        return readings[name][reading]
    return default


async def AttrVal(name, attr, default):
    if name in attributes and attr in attributes[name]:
        return attributes[name][attr]
    return default


async def InternalVal(name, internal, default):
    if name in internals and internal in internals[name]:
        return internals[name][internal]
    return default


async def addToDevAttrList(name, attr_list):
    return


async def setDevAttrList(name, attr_list):
    return


async def readingsBeginUpdate(hash):
    return


async def readingsBulkUpdateIfChanged(hash, reading, value):
    if hash["NAME"] not in readings:
        readings[hash["NAME"]] = {}
    readings[hash["NAME"]][reading] = value


async def readingsBulkUpdate(hash, reading, value, changed=None):
    if hash["NAME"] not in readings:
        readings[hash["NAME"]] = {}
    readings[hash["NAME"]][reading] = value


async def readingsEndUpdate(hash, do_trigger):
    return


async def readingsSingleUpdate(hash, reading, value, do_trigger):
    if hash["NAME"] not in readings:
        readings[hash["NAME"]] = {}
    readings[hash["NAME"]][reading] = value


async def readingsSingleUpdateIfChanged(hash, reading, value, do_trigger):
    if hash["NAME"] not in readings:
        readings[hash["NAME"]] = {}
    readings[hash["NAME"]][reading] = value


async def CommandDefine(hash, definition):
    command_define.append(definition)


async def CommandAttr(hash, attrdef):
    command_attr.append(attrdef)


async def CommandDeleteReading(hash, deldef):
    return


async def checkIfDeviceExists(hash, typeinternal, typevalue, internal, value):
    return False


def convertValue(value):
    if value == None:
        value = ""
    if value == True:
        value = 1
    if value == False:
        value = 0

    return str(value)


async def send_version():
    return
