
# Ring doorbell / chime / cam
This module supports Ring products

## Usage
```
define rrring PythonModule ring USERNAME@MAIL.COM RINGDEVICENAME
set rrring password PASSWORD
set rrring 2fa_code 2FACODE_FROM_MAIL
```

Password and token are saved encrypted with your FHEM unique id.