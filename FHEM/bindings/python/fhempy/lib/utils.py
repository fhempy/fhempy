import asyncio
import base64
import concurrent.futures
import json
import socket
from codecs import decode, encode
from datetime import datetime
from functools import partial, reduce

from cryptography.fernet import Fernet

from . import fhem


def encrypt_string(plain_text, fhem_unique_id):
    key = base64.b64encode(fhem_unique_id.encode("utf-8"))
    cipher_suite = Fernet(key)
    encrypted_text = cipher_suite.encrypt(plain_text.encode("utf-8"))
    return reduce(encode, ("zlib", "base64"), encrypted_text).decode("utf-8")


def decrypt_string(encrypted_text, fhem_unique_id):
    key = base64.b64encode(fhem_unique_id.encode("utf-8"))
    encrypted_text = encrypted_text.encode("utf-8")
    uncompressed_text = reduce(decode, ("base64", "zlib"), encrypted_text)
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(uncompressed_text).decode("utf-8")


async def run_blocking(function):
    if isinstance(function, partial) is False:
        raise Exception("Use functools.partial to call run_blocking")

    with concurrent.futures.ThreadPoolExecutor() as pool:
        return await asyncio.get_event_loop().run_in_executor(pool, function)


def run_blocking_task(function):
    return asyncio.create_task(run_blocking(function))


# example config
# attr_list = {
#   "attribute1": {"default": 10, "format": "int", "options":"1,2,3"}
# }
async def handle_attr(attr_list, obj, hash, args, argsh):
    cmd = args[0]
    name = args[1]
    attr_name = args[2]
    attr_val = args[3]
    if attr_name in attr_list:
        if cmd == "set":
            setattr(
                obj,
                "_attr_" + attr_name,
                convert2format(attr_val, attr_list[attr_name]),
            )
        else:
            if "default" in attr_list[attr_name]:
                setattr(obj, "_attr_" + attr_name, attr_list[attr_name]["default"])
            else:
                setattr(obj, "_attr_" + attr_name, "")

    # call set_attr_....
    fct_name = "set_attr_" + attr_name
    ret = None
    if attr_name in attr_list and "function" in attr_list[attr_name]:
        fct_name = attr_list[attr_name]["function"]
    try:
        fct_call = getattr(obj, fct_name)
        ret = await fct_call(hash)
    except AttributeError:
        pass

    return ret


def get_local_ip():
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Use Google Public DNS server to determine own IP
        sock.connect(("8.8.8.8", 80))

        return sock.getsockname()[0]  # type: ignore
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            return "127.0.0.1"
    finally:
        if sock is not None:
            sock.close()


async def handle_define_attr(attr_list, obj, hash):
    add_to_list = []
    for attr in attr_list:
        if "options" in attr_list[attr]:
            attr_opt = attr + ":" + attr_list[attr]["options"]
        else:
            attr_opt = attr
        add_to_list.append(attr_opt)
    await fhem.setDevAttrList(hash["NAME"], " ".join(add_to_list))

    for attr in attr_list:
        curr_val = await fhem.AttrVal(hash["NAME"], attr, "")
        if curr_val == "" and "default" in attr_list[attr]:
            curr_val = attr_list[attr]["default"]
        setattr(obj, "_attr_" + attr, convert2format(curr_val, attr_list[attr]))

        # call set_attr_....
        # fct_name = "set_attr_" + attr
        # if "function" in attr_list[attr]:
        #    fct_name = attr_list[attr]["function"]
        # try:
        #    fct_call = getattr(obj, fct_name)
        #    await fct_call(hash)
        # except AttributeError:
        #    pass

    return


def flatten_json(y):
    out = {}
    if type(y) is str:
        y = json.loads(y)

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def gen_fhemdev_name(devname):
    return remove_umlaut(devname.replace(" ", "_").replace("-", "_"))


def remove_umlaut(string):
    """
    Removes umlauts from strings and replaces them with the letter+e convention
    :param string: string to remove umlauts from
    :return: unumlauted string
    """
    u_enc = "ü".encode()
    U_enc = "Ü".encode()
    a_enc = "ä".encode()
    A_enc = "Ä".encode()
    o_enc = "ö".encode()
    O_enc = "Ö".encode()
    ss_enc = "ß".encode()

    string = string.encode()
    string = string.replace(u_enc, b"ue")
    string = string.replace(U_enc, b"Ue")
    string = string.replace(a_enc, b"ae")
    string = string.replace(A_enc, b"Ae")
    string = string.replace(o_enc, b"oe")
    string = string.replace(O_enc, b"Oe")
    string = string.replace(ss_enc, b"ss")

    string = string.decode("utf-8")
    return string


def convert2format(value, list_def):
    target_format = "none"
    if "format" in list_def:
        target_format = list_def["format"]

    if target_format == "int":
        return int(value)
    elif target_format == "float":
        return float(value)
    elif target_format == "str":
        return str(value)
    elif target_format == "bool":
        if value == "on":
            return True
        else:
            return False
    elif target_format == "json":
        try:
            return json.loads(value)
        except Exception:
            return {}
    elif target_format == "time":
        try:
            return datetime.strptime(value, "%H:%M")
        except Exception:
            return None
    elif target_format == "array":
        return value.split(",")
    return value


# example config
# set_list_conf = {
#    "mode": { "args": ["mode"], "argsh": ["mode"], "params": { "mode": { "default": "eco", "optional": False }}, "options": "eco,comfort" },
#    "desiredTemp": { "args": ["temperature"], "options": "slider,10,1,30"},
#    "holidayMode": { "args": ["start", "end", "temperature"], "params": { "start": {"default": "Monday"}, "end": {"default": "23:59"}}},
#    "on": { "args": ["seconds"], "params": { "seconds": {"optional": True}}},
#    "off": {}
# }
async def handle_set(set_list_conf, obj, hash, args, argsh):
    fhem_set_list = []
    if len(args) < 2 or (len(argsh) == 0 and args[1] == "?"):
        for cmd in set_list_conf:
            if "options" in set_list_conf[cmd]:
                fhem_options = ":" + set_list_conf[cmd]["options"]
            elif "args" in set_list_conf[cmd] or "argsh" in set_list_conf[cmd]:
                fhem_options = ""
            else:
                fhem_options = ":noArg"
            fhem_set_list.append(cmd + fhem_options)
        return "Unknown argument ?, choose one of " + " ".join(fhem_set_list)
    else:
        # get cmd
        cmd = args[1]
        if cmd in set_list_conf:
            all_args = {}
            if "argsh" in set_list_conf[cmd]:
                all_args = argsh
            cmd_def = set_list_conf[cmd]
            # map arguments to params
            # add args to all_args
            if ("args" in cmd_def and (len(args) - 2) > len(cmd_def["args"])) or (
                len(args) > 2 and args[2] == "?"
            ):
                return f"Usage: set {hash['NAME']} {cmd} " + " ".join(cmd_def["args"])
            i = 0
            for arg in args[2:]:
                # arg ... mode
                # all_args[mode] = mode argument
                if "args" in cmd_def and i < len(cmd_def["args"]):
                    all_args[cmd_def["args"][i]] = arg
                else:
                    return f"Too many parameters provided: {arg}"
                i += 1
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
                    if "value" in cmd_def["params"][param]:
                        final_params[param] = cmd_def["params"][param]["value"]
                    elif "default" not in cmd_def["params"][param] and (
                        "optional" not in cmd_def["params"][param]
                        or cmd_def["params"][param]["optional"] is False
                    ):
                        # no value found, check if optional
                        return f"Required argument {param} missing."
                    elif (
                        "default" in cmd_def["params"][param]
                        and "value" not in cmd_def["params"][param]
                    ):
                        final_params[param] = cmd_def["params"][param]["default"]
                    if "format" in cmd_def["params"][param] and param in final_params:
                        final_params[param] = convert2format(
                            final_params[param], cmd_def["params"][param]
                        )

            # call function with params
            if "function_param" in set_list_conf[cmd]:
                final_params["function_param"] = set_list_conf[cmd]["function_param"]
            if "function" in set_list_conf[cmd]:
                fct_name = set_list_conf[cmd]["function"]
                final_params["cmd"] = cmd
            else:
                fct_name = "set_" + cmd
            fct_call = getattr(obj, fct_name)
            return await fct_call(hash, final_params)
        else:
            return "Command not available for this device."
