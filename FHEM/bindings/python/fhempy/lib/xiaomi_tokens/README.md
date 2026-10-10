# Xiaomi Tokens
This module retrieves all tokens from Xiaomi Cloud. The login is based on the Xiaomi Cloud Tokens Extractor:

https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor


## Usage
```
define xiaomi_tokens fhempy xiaomi_tokens
set xiaomi_tokens username USERNAME@MAIL.COM
set xiaomi_tokens password PASSWORD
set xiaomi_tokens get_tokens
```

Xiaomi might ask for additional verification during the login:
- Captcha: the reading `captcha` shows the image, enter the text with `set xiaomi_tokens captcha TEXT`.
- Email code (2FA): Xiaomi sends a code to the email address of your account, enter it with `set xiaomi_tokens verify_code CODE`.

Alternatively you can login without username/password by scanning a QR code with the Mi Home app:
```
set xiaomi_tokens qr_login
```
The reading `login_qr_code` shows the QR code.

Reload the page with F5 to display the newly created readings with tokens. Tokens are retrieved from all Xiaomi cloud servers, use the attribute `servers` (e.g. `de,cn,sg`) to check only some of them.

Username and password are saved encrypted in the readings. Even though they are encrypted, it's not recommended to post them on the internet.

You can create FHEM devices out of the xiaomi_tokens module by using
```
set xiaomi_tokens create_miio_device ...
set xiaomi_tokens create_gateway3_device ...
```

Those are created with the proper values (IP, Token).
