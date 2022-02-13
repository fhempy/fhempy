
# fusionsolar
Access data from your Huawei Fusion Solar solar system.

# Usage

1. Login to https://eu5.fusionsolar.huawei.com/
2. Click on the plant in the list of solar plants
3. A new window opens with a "Kiosk" button in the upper right corner
4. Click on the kiosk button
5. Enter a name in the configuration window, copy the URL and click on save (click on save before you continue!!)
6. Go to FHEM and do
```
define my_solar fhempy fusionsolar KIOSK_URL
```

 - KIOSK_URL: Looks something like this https://region01eu5.fusionsolar.huawei.com/pvmswebsite/nologin/assets/build/index.html#/kiosk?kk=XXXXXXXXXX
