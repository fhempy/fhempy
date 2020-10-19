
import asyncio
import logging
import concurrent.futures
from cryptography.fernet import Fernet
from codecs import encode, decode
from functools import reduce
import base64

def encrypt_string(plain_text, fhem_unique_id):
  key = base64.b64encode(fhem_unique_id.encode('utf-8'))
  cipher_suite = Fernet(key)
  encrypted_text = cipher_suite.encrypt(plain_text.encode("utf-8"))
  return reduce(encode, ('zlib', 'base64'),encrypted_text).decode("utf-8")

def decrypt_string(encrypted_text, fhem_unique_id):
  key = base64.b64encode(fhem_unique_id.encode('utf-8'))
  encrypted_text = encrypted_text.encode("utf-8")
  uncompressed_text = reduce(decode, ('base64', 'zlib'),encrypted_text)
  cipher_suite = Fernet(key)
  return cipher_suite.decrypt(uncompressed_text).decode("utf-8")

async def run_blocking(function):
  try:
    with concurrent.futures.ThreadPoolExecutor() as pool:
      return await asyncio.get_event_loop().run_in_executor(
          pool, function)
  except:
    logging.getLogger(__name__).exception("Error in asyncio thread")
    raise

def run_blocking_task(function):
  asyncio.create_task(run_blocking(function))

# example config
# set_list_conf = {
#    "mode": { "args": ["mode"], "argsh": ["mode"], "params": { "mode": { "default": "eco", "optional": False }}, "format": "eco,comfort" },
#    "desiredTemp": { "args": ["temperature"], "format": "slider,10,1,30"},
#    "holidayMode": { "args": ["start", "end", "temperature"], "params": { "start": {"default": "Monday"}, "end": {"default": "23:59"}}},
#    "on": { "args": ["seconds"], "params": { "seconds": {"optional": True}}},
#    "off": {}
# }
async def handle_set(set_list_conf, obj, hash, args, argsh):
  fhem_set_list = []
  if len(args) < 2 or (len(argsh) == 0 and args[1] == "?"): 
    for cmd in set_list_conf:
      if "format" in set_list_conf[cmd]:
        fhem_format = ":" + set_list_conf[cmd]["format"]
      elif "args" in set_list_conf[cmd] or "argsh" in set_list_conf[cmd]:
        fhem_format = ""
      else:
        fhem_format = ":noArg"
      fhem_set_list.append(cmd + fhem_format)
    return "Unknown argument ?, choose one of " + " ".join(fhem_set_list)
  else:
    # get cmd
    cmd = args[1]
    if cmd in set_list_conf:
      all_args = {}
      if "argsh" in set_list_conf[cmd]:
        all_args = set_list_conf[cmd]["argsh"]
      cmd_def = set_list_conf[cmd]
      # map arguments to params
      # add args to all_args
      if "args" in cmd_def and (len(args) - 2) > len(cmd_def["args"]):
        return f"Too many args provided. Usage: set {hash['NAME']} {cmd} " + " ".join(cmd_def["args"])
      i=0
      for arg in args[2:]:
        # arg ... mode
        # all_args[mode] = mode argument
        all_args[cmd_def["args"][i]] = arg
        i+=1
      # get default values for other params
      final_params = all_args
      if "params" in cmd_def:
        # add value to params
        for arg in all_args:
          if arg in cmd_def["params"]:
            cmd_def["params"][arg]["value"] = all_args[arg]
        for param in cmd_def["params"]:
          # check if value is available or default value
          # check if all required params are availble
          if "default" in cmd_def["params"][param] and "value" not in cmd_def["params"][param]:
            final_params[param] = cmd_def["params"][param]["default"]
          elif "value" in cmd_def["params"][param]:
            final_params[param] = cmd_def["params"][param]["value"]
          elif "optional" not in cmd_def["params"][param] or cmd_def["params"][param]["optional"] is False:
            # no value found, check if optional
            return f"Required argument {param} missing."

      # call function with params
      fct_name = "set_" + cmd
      fct_call = getattr(obj, fct_name)
      if len(final_params) > 0:
        return await fct_call(hash, final_params)
      
      return await fct_call(hash)
    else:
      return f"Command not available for this device."