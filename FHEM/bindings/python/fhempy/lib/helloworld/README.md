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
- `desiredTemp`: demonstrates a slider and writes the `desiredTemp` reading;
  a whole number from 10 to 30 is required, including for direct commands.
- `holidayMode`: demonstrates multiple positional arguments and defaults.

    ```
    set hello_fhempy holidayMode 24.12.2030 18:30 19
    ```

    In FHEMWEB, select `holidayMode` and enter **`24.12.2030 18:30 19`** in the single
    input field. The arguments are separated by spaces: end date, end time and
    temperature. The `args` configuration maps these values to parameter names;
    it does not create a separate widget for each argument.

    The command validates a calendar date (`DD.MM.YYYY`, including leap years),
    a time (`HH:MM`, 00:00 to 23:59) and a whole-number temperature from 10 to 30.
    Day, month, hour and minute require exactly two digits; the year requires four.
    Only after all arguments are valid does it write the `endday`, `endtime` and
    `temperature` readings. Invalid input returns an explanation without changing
    readings. This example does not schedule heating or require a future end date.
    Omitted trailing arguments use the defaults configured in `set_config`:

    ```
    set hello_fhempy holidayMode 24.12.2030
    set hello_fhempy holidayMode
    ```

    Previous calls do not change those defaults.

- `on [seconds]`: writes `on`, or `on <seconds>`, to `state`. This demonstrates
  an optional non-negative integer parameter; it does not start an automatic off timer.
- `off`: writes `off` to `state` and starts a background task which later changes
  it to `long running off` without blocking the event loop.

## Attributes

- `interval`: a positive integer attribute demonstrating configuration and the
  `set_attr_interval` callback. `get info` displays its current value;
  this example does not run a periodic polling loop.

## Validating input in your own module

GUI `options` configure a widget, not input validation: commands can also arrive
through the command field, Telnet or an automation. Declare required parameters
in `params` and validate them before changing readings or controlling a device.

`format` accepts built-in names such as `"int"` and `"float"`, or a synchronous
callable. A callable returns the converted value or raises `ValueError` with a
short explanation. It must not perform I/O or change device state. For example,
`_endday` checks real calendar dates; `_integer` checks integer ranges. The same
temperature converter is used for both temperature commands, and the limits
also configure the slider.

Set/Get parameter conversion and attribute assignment return conversion errors
to FHEM without running the command or attribute callback. Missing required
parameters, extra positional values, unknown named parameters and duplicate
positional/named parameters are rejected too. Optional defaults are validated
on each command and are never replaced by values from a previous call.

Invalid attributes already stored in FHEM at startup are reported in the log;
the module uses its validated default internally. Correct or delete the stored
attribute in FHEM. Invalid defaults are programming errors and must be fixed in
the module configuration.
