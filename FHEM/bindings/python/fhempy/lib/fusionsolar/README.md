
# fusionsolar
Access data from your Huawei Fusion Solar solar system via Huawei REST API.

# Usage

1. Login to https://eu5.fusionsolar.huawei.com/
2. Click on System - Personal Settings
3. Select Modify Personal Info
4. Change Auto-Logout If No Activity Within to Unlimited
5. Click save
6. Go to FHEM and do
```
define my_solar fhempy fusionsolar USERNAME PASSWORD REGION
```

 - USERNAME: Fusionsolar username
 - PASSWORD: Fusionsolar password
 - REGION: Default eu5, copy it from the first part of the URL

# Attributes

 - interval: Update interval in seconds (default 300, minimum 60). FusionSolar refreshes its data every 5 minutes, so shorter intervals mostly fetch the same values again.

# Connection problems

If FusionSolar is not reachable (e.g. maintenance) or the session expired, the module logs in again automatically. The wait before the next login starts at 30 seconds and doubles after every failure up to 15 minutes, so the module never gives up but doesn't trigger the FusionSolar captcha with too many logins. The state shows e.g. `login failed, reconnect in 900s`.

If FusionSolar asks for a captcha (verification code) at login, it blocks logins from your IP for a longer time. The module then waits 1 hour, if the captcha is still required 2 hours, and shows `captcha required, reconnect in 3600s`.
