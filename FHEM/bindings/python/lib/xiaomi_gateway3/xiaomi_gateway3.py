
import asyncio

from .. import fhem
from .. import utils

class xiaomi_gateway3:

  def __init__(self, logger):
    self.logger = logger
    return

  # FHEM FUNCTION
  async def Define(self, hash, args, argsh):
    await fhem.readingsBeginUpdate(hash)
    await fhem.readingsBulkUpdateIfChanged(hash, "state", "disconnected")
    await fhem.readingsEndUpdate(hash, 1)

    # start mqttudp bidir gate
    
    return ""

  # FHEM FUNCTION
  async def Undefine(self, hash, args, argsh):
    return

  # FHEM FUNCTION
  async def Set(self, hash, args, argsh):
    set_conf_list = {
      "connect": {}
    }
    return await utils.handle_set(set_conf_list, self, hash, args, argsh)
  
  async def set_connect(self, params):
    return
