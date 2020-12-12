
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

Reload the page with F5 to display the newly created readings with tokens.

Username and password are NOT saved. They are just used once in memory to retrieve the tokens. Tokens are displayed in the readings.