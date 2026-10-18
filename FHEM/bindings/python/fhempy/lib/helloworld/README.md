# helloworld
This example module demonstrates Define validation, Set/Get commands, attributes,
FHEMWEB help and background tasks. It does not control a real device.

## Usage
```
define hello_fhempy fhempy helloworld
```

No additional Define arguments are accepted. The synchronous
`validate_define(args, argsh)` hook checks arguments without network access or
other side effects. The binding can use it to reject an invalid redefinition
before stopping the existing device. `Define` reuses the same validation for
direct calls; the usage message is defined once in the module.

## Get commands

```
get hello_fhempy info
get hello_fhempy help
```

- `info` reads the current state from FHEM and returns it with the device name
  and the configured interval.
- `help` builds a command and attribute overview from the module configuration.

`await self.set_get_config(get_config)` registers commands and their FHEMWEB
`help` texts. Commands call `get_<command>(hash, params)`. The examples show both
an asynchronous handler (`info`) and a synchronous handler (`help`). The base
class supplies `Get`; a module does not need to implement its own dispatcher.

## Set commands

- `mode`: choose `eco` or `comfort`; writes the `mode` reading. Both positional
  input (`set hello_fhempy mode comfort`) and named input
  (`set hello_fhempy mode mode=comfort`) are supported.
- `desiredTemp`: demonstrates a slider and writes the `desiredTemp` reading.
- `holidayMode`: demonstrates multiple positional arguments and defaults.
- `on [seconds]`: writes `on`, or `on <seconds>`, to `state`. This demonstrates
  an optional integer parameter; it does not start an automatic off timer.
- `off`: writes `off` to `state` and starts a background task which later changes
  it to `long running off` without blocking the event loop.

### holidayMode

```
set hello_fhempy holidayMode 24.12.2030 18:30 19
```

In FHEMWEB, select `holidayMode` and enter **`24.12.2030 18:30 19`** in the single
input field. The arguments are separated by spaces: end date, end time and
temperature. The `args` configuration maps these values to parameter names;
it does not create a separate widget for each argument.

The command writes the `endday`, `endtime` and `temperature` readings. It is a
parameter-handling example, not a heating scheduler or a date/time validator.
Omitted trailing arguments use the defaults configured in `set_config`:

```
set hello_fhempy holidayMode 24.12.2030
set hello_fhempy holidayMode
```

Previous calls do not change those defaults.

## Attributes

- `interval`: an integer attribute demonstrating configuration and the
  `set_attr_interval` callback. `get info` displays its current value;
  this example does not run a periodic polling loop.
