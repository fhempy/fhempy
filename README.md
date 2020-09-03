# FHEM Python Binding (BETA, might not be stable!)

FHEM Python binding allows the usage of Python 3 (NOT 2!) language to write FHEM modules

This repository includes following examples:
 - helloworld
 - googlecast
 - mdnsscanner
 - blescanner

## Installation
Python >=3.7 is required, Python 2 won't work!

sudo apt install python3 python3-pip

sudo cpan Protocol::WebSocket

sudo pip3 install asyncio websockets importlib_metadata

All further requirements are installed automatically via pip as soon as the specific module is used the first time.
 
## Usage in FHEM
 1. update add https://raw.githubusercontent.com/dominikkarall/fhem_pythonbinding/master/controls_pythonbinding.txt
 2. update
 3. define pythonbinding BindingsIo Python
 4. define castdevice PythonModule googlecast "Living Room"
 5. set castdevice play url="https://www.youtube.com/watch?v=oHg5SJYRHA0"

## Functionality

### 10_BindingsIo
This module is a DevIo device which builds a language neutral communicaton bridge in JSON via websockets.
### 10_PythonBinding
This module just starts the fhem_pythonbinding server instance
### 10_PythonModule
This module is used as the bridge to BindingsIo. It calls BindingsIo with IOWrite.
### fhem_pythonbinding
This is the Python server instance which handles JSON websocket messages from BindingsIo. Based on the message it executes the proper function and replies to BindingsIo via websocket.

### Call flow
This example shows how Define function is called from the Python module.
 1. define castdevice PythonModule googlecast "Living Room"
 2. PythonModule sends IOWrite to BindingsIo
 3. BindingsIo sends a JSON websocket message to fhem_pythonbinding
 4. fhem_pythonbinding loads the corresponding module (e.g. googlecast), creates an instance of the object (e.g. googlecast) and calls the Define function on that instance
 5. Define function is executed within the Python context, as long as the function is executed, FHEM waits for the answer the same way as it does for Perl modules
 6. Python Define returns the result via JSON via websocket to BindingsIo

At any time within the functions FHEM functons like readingsSingleUpdate(...) can be called by using the fhem.py module (fhem.readingsSingleUpdate(...)). There are just a few functions supported at the moment.

![Flow Chart](/flowchart.png)

## Write own module
Check helloworld example for writing an own module. Be aware that no function which is called from FHEM is allowed to run longer than 1s. In general no blocking code should be used with asyncio. If you want to call blocking code, use run_in_executor (see googlecast code).
