
# Ring doorbell / chime / cam
This module supports Ring products

## Usage
```
define rrring PythonModule ring USERNAME@MAIL.COM RINGDEVICENAME
set rrring password PASSWORD
set rrring 2fa_code 2FACODE_FROM_MAIL
```

Password and token are saved encrypted with your FHEM unique id.

There is an optional parameter IDENTIFIER (just after RINGDEVICENAME) which allows you to specify the Auth identifier for Ring. By default it is a random string and therefore there is normally no need to specify it.
