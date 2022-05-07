
# fusionsolar
Access data from your Huawei Fusion Solar solar system via Huawei REST API.

# Usage

1. Login to https://eu5.fusionsolar.huawei.com/
2. Click on System - Personal Settings
3. Select Modify Personal Info
4. Change Auto-Logout If No Activity Within to Unlimited
5. Click save
6. Open Cookies (in Chrome: Click on the lock symbol in the URL bar) and copy the content of the cookie bspsession to an empty text file
7. Go back to the Home screen and select the plant in the list of solar plants
8. Copy the station ID from the URL (NE=xxxxxxxx), including NE= and copy it to the text file
9. Go to FHEM and do
```
define my_solar fhempy fusionsolar SESSIONID STATIONID REGION
```

 - SESSIONID: The bspsession content, yes it's long
 - STATIONID: NE=xxxxxxxx (include NE=)
 - REGION: Default region01eu5, copy it from the first part of the URL