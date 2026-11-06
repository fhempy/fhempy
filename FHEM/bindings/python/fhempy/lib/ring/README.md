
# Ring doorbell / chime / cam
This module supports Ring products

## Usage
```
define rrring fhempy ring USERNAME@MAIL.COM RINGDEVICENAME
set rrring password PASSWORD
set rrring 2fa_code 2FACODE_FROM_MAIL
```

Password and token are saved encrypted with your FHEM unique id.

The module signs in the same way as the Ring app (OAuth v2 sign-in page with PKCE).
If your account uses 2-factor authentication, the state changes to `please set 2fa_code`
after `set password`. Enter the code Ring sent you with `set 2fa_code` within a few minutes.
If the login stopped working (e.g. `HTTP error with status code 406`), run `set password` again.

There is an optional parameter IDENTIFIER (just after RINGDEVICENAME) which allows you to specify the Auth identifier for Ring. By default a random string is created once and stored in the reading `identifier`, so there is normally no need to specify it.
