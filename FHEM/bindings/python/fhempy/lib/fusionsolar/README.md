
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
 - REGION: Default region01eu5, copy it from the first part of the URL