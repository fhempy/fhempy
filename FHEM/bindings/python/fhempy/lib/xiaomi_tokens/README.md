
# Xiaomi Tokens
This module retrieves all tokens from Xiaomi Cloud. Thanks for the micloud integration:

https://github.com/squachen/micloud


## Usage
```
define xiaomi_tokens PythonModule xiaomi_tokens
set xiaomi_tokens username USERNAME@MAIL.COM
set xiaomi_tokens password PASSWORD
set xiaomi_tokens get_tokens
```

Reload the page with F5 to display the newly created readings with tokens. Tokens are retrieved from de, cn and sg servers.

Username and password are saved encrypted in the readings. Even though they are encrypted, it's not recommended to post them on the internet.

You can create FHEM devices out of the xiaomi_tokens module by using
```
set xiaomi_tokens create_miio_device ...
set xiaomi_tokens create_gateway3_device ...
```

Those are created with the proper values (IP, Token).