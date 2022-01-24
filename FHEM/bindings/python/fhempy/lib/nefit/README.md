
# Nefit
This module is used to control Nefit devices like:

- Nefit Easy (Netherlands)

- Junkers Control CT100 (Belgium, Germany)

- Buderus Logamatic TC100 (Belgium)

- E.L.M. Touch (France)

- Worcester Wave (UK)

- Bosch Control CT100 (Other).


## Usage

First define the thermostat device:

```
define nefit_thermostat fhempy nefit <SERIAL_NUMBER>
```

Set the credential attributes:

```
attr nefit_thermostat access_key <ACCEESS_KEY>
```

```
attr nefit_thermostat password <PASSWORD>
```
