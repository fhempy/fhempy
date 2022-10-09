# Changelog

<!--next-version-placeholder-->

## v0.1.502 (2022-10-09)
### Fix
* **tuya:** Update tinytuya==1.7.1 ([`d8e2c66`](https://github.com/dominikkarall/fhempy/commit/d8e2c66c3e8744171360a255dff10b10de526129))
* **fusionsolar:** Retry login if it fails ([`de70e9c`](https://github.com/dominikkarall/fhempy/commit/de70e9c26f00f8c954a30fbeb3ae2bfc1e1a90e8))
* **fhempy:** Disable events for the moment ([`5c6dee0`](https://github.com/dominikkarall/fhempy/commit/5c6dee08151f2b33e87fa14101915e542ecacc89))
* **google_weather:** Add further user agent ([`5c8ecaa`](https://github.com/dominikkarall/fhempy/commit/5c8ecaa4df6fb56c9e30bf17e63af45ea53e5fec))

## v0.1.501 (2022-10-05)
### Feature
* **skodaconnect:** New sensors for Enyaq iV ([#98](https://github.com/dominikkarall/fhempy/issues/98)) ([`a157ab9`](https://github.com/dominikkarall/fhempy/commit/a157ab9d24ebcd84eb4efcd5fdb02937a5b93dac))

## v0.1.500 (2022-10-05)
### Fix
* **kia_hyundai:** Check refresh token before update ([`041c732`](https://github.com/dominikkarall/fhempy/commit/041c732d5ee12977f91c3600592b33db825ad46a))

## v0.1.499 (2022-10-05)
### Feature
* **tuya:** Support led colours ([`852f522`](https://github.com/dominikkarall/fhempy/commit/852f522533e97c00421ffddfc36595906d48f3b2))

## v0.1.498 (2022-10-04)
### Fix
* **tuya:** Set tuya state reading to ready when finished initializing ([`79c247e`](https://github.com/dominikkarall/fhempy/commit/79c247e4a133e2f8d974f361c720eccb4804c882))

## v0.1.497 (2022-10-03)
### Fix
* **fhempy:** Disable readme help for the moment due to websocket issues ([`30eb51f`](https://github.com/dominikkarall/fhempy/commit/30eb51f92edb34924c2de62f34a7c51b9d5ba88a))
* **fhempy:** Add logging if sending to fhem needs to wait too long ([`36f12ec`](https://github.com/dominikkarall/fhempy/commit/36f12ec66e3972bdb122d8c6426c7ba514b2508a))
* **fhempy:** Reinit frames on error ([`ccbb284`](https://github.com/dominikkarall/fhempy/commit/ccbb284035bd03c384b5ab066ada4a914ec6ab66))

## v0.1.496 (2022-10-03)
### Fix
* **fhempy:** Fix websocket write_limit ([`3023385`](https://github.com/dominikkarall/fhempy/commit/302338574c0c2a6eba329c91df2d51b7e2bc1e2b))

## v0.1.495 (2022-10-02)
### Fix
* **fhempy:** Fix some websocket issues ([`587d0f0`](https://github.com/dominikkarall/fhempy/commit/587d0f0f78f7c4ba794a161eb0df19705cdbef75))

## v0.1.494 (2022-10-02)
### Fix
* **fusionsolar:** Fix to_grid values ([`12e57eb`](https://github.com/dominikkarall/fhempy/commit/12e57eb08afec8088197d44659974b65a778f12c))

## v0.1.493 (2022-10-02)
### Fix
* **tuya:** Fix non-str spec values ([`baa5977`](https://github.com/dominikkarall/fhempy/commit/baa59774279d1e54a1ef4c4e06a8e2993fde917b))

## v0.1.492 (2022-10-02)
### Feature
* **kia_hyundai:** Set state readings to online/error ([`dd5190d`](https://github.com/dominikkarall/fhempy/commit/dd5190d946d861dbd97514a07ced6b20b78a298f))

### Fix
* **kia_hyundai:** Always update readings ([`e221894`](https://github.com/dominikkarall/fhempy/commit/e2218944d2d6231fe35394b84a70e2272ca7133c))

## v0.1.491 (2022-10-02)
### Fix
* **tuya:** Fix issue with boolean specs ([`7b3910f`](https://github.com/dominikkarall/fhempy/commit/7b3910fe285a300e300bcdd2fdc942ed06ac9fdf))

## v0.1.490 (2022-10-01)
### Fix
* **gree_climate:** Add missing self.device = None ([`2a7657f`](https://github.com/dominikkarall/fhempy/commit/2a7657ff21d2d1f20ed943c726a708fc86e41f26))

## v0.1.489 (2022-10-01)
### Fix
* **gree_climate:** Retry connect if first connection attempt fails ([`1eee34a`](https://github.com/dominikkarall/fhempy/commit/1eee34af7fc6bfc06ef6f7c8c440b4afd35643f0))

## v0.1.488 (2022-10-01)
### Feature
* **kia_hyundai:** Update to latest kia_uvo code ([`638a7c8`](https://github.com/dominikkarall/fhempy/commit/638a7c808d6537e998deace600814e327fbd4a6f))
* **kia_hyundai:** Support update_data command ([`7b4876b`](https://github.com/dominikkarall/fhempy/commit/7b4876bf6f8466d2287b21819a3dda058e9e6a43))

### Fix
* **fusionsolar:** Better logging on data errors ([`adb5902`](https://github.com/dominikkarall/fhempy/commit/adb590267127e277a6932f01d56be129f56e7e78))
* **websitetests:** Fix reading response_status ([`a0371a8`](https://github.com/dominikkarall/fhempy/commit/a0371a854d12ddeea1b0b087f34fa5035dd2a021))

## v0.1.487 (2022-09-29)
### Fix
* **websitetests:** Support URLs with = ([`97a4cce`](https://github.com/dominikkarall/fhempy/commit/97a4cce3a3b0074d50699516c297a3d2033f76ac))
* **blue_connect:** Keep connection active ([`88f6f49`](https://github.com/dominikkarall/fhempy/commit/88f6f491be7d08aa78ad421949fc725931b2a6c1))

## v0.1.486 (2022-09-28)
### Feature
* **websitetests:** Small module to test speed of web responses ([`48e5c4e`](https://github.com/dominikkarall/fhempy/commit/48e5c4e8c3d741006b9a49a1e73aa7072f866c7a))

### Fix
* **websitetests:** Limit response reading to 5000 characters ([`f350798`](https://github.com/dominikkarall/fhempy/commit/f3507988b4b9776fffde807ef2609313ca79d8a1))

## v0.1.485 (2022-09-28)
### Fix
* **fhempy:** Fix "continue" response to FHEM ([`d63f0dd`](https://github.com/dominikkarall/fhempy/commit/d63f0dd1517d197ac56ead22007f2b439d304962))

## v0.1.484 (2022-09-28)
### Fix
* **tuya:** Fix translation for enum ([`31ddac2`](https://github.com/dominikkarall/fhempy/commit/31ddac209e2894c8b20809610337e697149d00a9))

## v0.1.483 (2022-09-27)
### Fix
* **tuya:** Fix translation for enums ([`348e176`](https://github.com/dominikkarall/fhempy/commit/348e176c67360efcda6855305901a668f1afe850))

## v0.1.482 (2022-09-27)
### Fix
* **googlecast:** Update youtube_dl/spotipy ([`6d94d69`](https://github.com/dominikkarall/fhempy/commit/6d94d697e86d2448c45606e096116af274500b67))
* **spotify:** Update spotipy lib ([`bbd9ae8`](https://github.com/dominikkarall/fhempy/commit/bbd9ae82c8366e37792cab4e9c432d05d990c304))

## v0.1.481 (2022-09-27)
### Feature
* **tuya:** Add translation for kettle state ([`eafac0c`](https://github.com/dominikkarall/fhempy/commit/eafac0c06c4ff3e9a17decd2f4c3b9c52edd1596))

### Fix
* **tuya:** Use online reading for online/offline state ([`dd75bf3`](https://github.com/dominikkarall/fhempy/commit/dd75bf33a4e9bb9986ffe6009cde25d3e0d974c4))

## v0.1.480 (2022-09-27)
### Fix
* **fhempy:** Support ws msgs up to 10MiB ([`87bfd3e`](https://github.com/dominikkarall/fhempy/commit/87bfd3e8baf6a6974ce6fe3caec617d7726877da))
* **blue_connect:** Keep BLE connection ([`7e89afd`](https://github.com/dominikkarall/fhempy/commit/7e89afd0f47132ed462e7e6d7c28b29b59106a92))

## v0.1.479 (2022-09-26)
### Fix
* **fhempy:** Make DevIo_IsOpen call more clear ([`2216284`](https://github.com/dominikkarall/fhempy/commit/2216284cfed0159cf991ebd06fab4d391e00b6ae))
* **fhempy:** Better connection closed handling ([`c59119f`](https://github.com/dominikkarall/fhempy/commit/c59119fec1dc26963898c93d2e9e7ee221b32c2e))

## v0.1.478 (2022-09-26)
### Fix
* **fhempy:** Fix asyncio warnings for WebSocketServerProtocol.handler() ([`cf11e97`](https://github.com/dominikkarall/fhempy/commit/cf11e97054c43d701ad9a864e834540ab6236ff7))

## v0.1.477 (2022-09-25)
### Feature
* **fhempy:** Add healthcheck possibility ([`11e2ef8`](https://github.com/dominikkarall/fhempy/commit/11e2ef8b700e5be56d0014bfb328c94948e3378f))

### Fix
* **tuya:** Do not rais exception on CancelledError ([`f9fe2f9`](https://github.com/dominikkarall/fhempy/commit/f9fe2f9a61c87d872c20a05254cc57f34489d937))
* **google_weather:** Use several user agent strings ([`7b0730c`](https://github.com/dominikkarall/fhempy/commit/7b0730c93ecff146a0df39d0a46c201e1303fef0))
* **fhempy:** Improve log message ([`47598df`](https://github.com/dominikkarall/fhempy/commit/47598df0563c069983c73b5543280df2610d9c4f))
* **blue_connect:** Try to connect 10 times every 10s on failure ([`2571ab1`](https://github.com/dominikkarall/fhempy/commit/2571ab175d6eb29814ebc4bbadbdab7aa1acd2b0))

## v0.1.476 (2022-09-24)
### Feature
* **meross:** Support thermostat ([`842ad75`](https://github.com/dominikkarall/fhempy/commit/842ad750590a47b3a518b4c7e3f8d939af79f60b))

## v0.1.475 (2022-09-24)
### Fix
* **fhempy:** Fix max_payload_size websocket issues, add state info on first define ([`896ed11`](https://github.com/dominikkarall/fhempy/commit/896ed11ed34b1d6aed8db3522f06a5684c4937e0))

## v0.1.474 (2022-09-24)
### Fix
* **tuya:** Fix values wrong format ([`8c44946`](https://github.com/dominikkarall/fhempy/commit/8c44946b1aafbf7ffb96183794a4d0a4d8d9082d))
* **fhempy:** Recommend Python 3.8 or higher ([`1d44b53`](https://github.com/dominikkarall/fhempy/commit/1d44b538e79a2f01cca0e5ec96f66cc9ebe18aeb))

## v0.1.473 (2022-09-21)
### Feature
* **tuya:** Support productid utzgmksz7zj66als ([`af599ff`](https://github.com/dominikkarall/fhempy/commit/af599ffa664085f34ce29aeb86195763f6d7e840))

### Fix
* **tuya:** Fix readings for local mapping ([`5f557cc`](https://github.com/dominikkarall/fhempy/commit/5f557cc3a453be89103707487cc2d667a459ace8))
* **zigbee2mqtt:** Start z2m after update ([`f6687aa`](https://github.com/dominikkarall/fhempy/commit/f6687aa7a566b748469d88d4e62fbbbc42a4ee55))
* **fhempy:** Better log when advertising fhempy on local network ([`bdff568`](https://github.com/dominikkarall/fhempy/commit/bdff5686eb9402e18c74aa733dba9fe7ee8021ed))

## v0.1.472 (2022-09-20)
### Fix
* **gfprobt:** Fix circular import ([`5b4670b`](https://github.com/dominikkarall/fhempy/commit/5b4670b7a06c1ff14f651eb0f1c142fceb3e6188))

## v0.1.471 (2022-09-20)
### Fix
* **blue_connect:** Do not round battery reading ([`30cf035`](https://github.com/dominikkarall/fhempy/commit/30cf03544c4b10060ac90a1db1c4f3da1ff217c1))

## v0.1.470 (2022-09-20)
### Fix
* **blue_connect:** Do not round battery reading ([`b7a5ccb`](https://github.com/dominikkarall/fhempy/commit/b7a5ccb3ef1d4043dea4d0c3f753a8ed713296d2))

## v0.1.469 (2022-09-20)
### Feature
* **blue_connect:** Support battery ([`f8d1360`](https://github.com/dominikkarall/fhempy/commit/f8d13603662a53ef6b19bf24fd0080c47c2a00ef))

### Fix
* **blue_connect:** Set readings 0 on errors ([`7d8d27c`](https://github.com/dominikkarall/fhempy/commit/7d8d27ccfd929b120e717b61176db9485f0ca496))

## v0.1.468 (2022-09-19)
### Feature
* **blue_connect:** Add raw data reading ([`2d6b32c`](https://github.com/dominikkarall/fhempy/commit/2d6b32cee3dcc735baf68b2f047c1ce4510b2389))

## v0.1.467 (2022-09-18)
### Fix
* **blue_connect:** Fix retry ([`14e29d8`](https://github.com/dominikkarall/fhempy/commit/14e29d8fccaf97b4ea55ae9ab9bcc349a324aadd))

## v0.1.466 (2022-09-18)
### Feature
* **esphome:** Update to 2022.8.3 ([`eb93ae9`](https://github.com/dominikkarall/fhempy/commit/eb93ae95cf9451fbb239f73ea399f5e70ec734f7))

## v0.1.465 (2022-09-18)
### Feature
* **blue_connect:** Add state reading and ph/orp_state reading ([`fd682b8`](https://github.com/dominikkarall/fhempy/commit/fd682b865d40ccba5073120e528b6e91990cf2b3))

## v0.1.464 (2022-09-18)
### Fix
* **blue_connect:** Fix blue connect ([`63a0356`](https://github.com/dominikkarall/fhempy/commit/63a0356e36b242dad06c52cfca7f95a982d4aae2))

## v0.1.463 (2022-09-16)
### Feature
* **blue_connect:** Initial version ([`fa0b3fd`](https://github.com/dominikkarall/fhempy/commit/fa0b3fd6a156bffab9a740d7016a5e167780c5e8))
* **fhempy:** Force version update ([`4ac7a31`](https://github.com/dominikkarall/fhempy/commit/4ac7a31dd5cf792d9ede472928b4c7f2a1d447a4))

### Fix
* **blue_connect:** Add retries ([`49a8833`](https://github.com/dominikkarall/fhempy/commit/49a88330c07754631c990d8b86c74f111629cdcc))

## v0.1.462 (2022-09-12)
### Fix
* **fhempy:** Fix docker installation? ([`31417aa`](https://github.com/dominikkarall/fhempy/commit/31417aa12d2dc4fa8ce71c069c0ca5064a14e433))

## v0.1.461 (2022-09-09)
### Fix
* **github_backup:** Only update file if sha1 sum changes ([`3cc7b7a`](https://github.com/dominikkarall/fhempy/commit/3cc7b7a2e9c68500ea556f5c51ea39aea134640c))
* **kia_hyundai:** Add pytz dependency ([`21eac89`](https://github.com/dominikkarall/fhempy/commit/21eac89b19f46af95e772b4925873cd78d813639))

## v0.1.460 (2022-09-09)
### Fix
* **kia_hyundai:** Fix name of dateutil ([`ad28c6b`](https://github.com/dominikkarall/fhempy/commit/ad28c6bd7195fe5c3c8a24fe0f62d954f933c166))

## v0.1.459 (2022-09-09)
### Fix
* **kia_hyundai:** Add dateutil ([`da3d112`](https://github.com/dominikkarall/fhempy/commit/da3d1125d4da5963024b32a5fc3fb8ded5f88171))

## v0.1.458 (2022-09-08)
### Feature
* **github_backup:** Improve commit message ([`dfb29ed`](https://github.com/dominikkarall/fhempy/commit/dfb29ed138ad4631e907c20c7a88af47c9ce1eb2))

### Fix
* **skodaconnect:** Update Base Lib ([#88](https://github.com/dominikkarall/fhempy/issues/88)) ([`b2d2c8f`](https://github.com/dominikkarall/fhempy/commit/b2d2c8f14676cd3ab12374ef6981cd57942faa16))

## v0.1.457 (2022-09-06)
### Fix
* **fhempy:** Fix memory leak ([`45f8909`](https://github.com/dominikkarall/fhempy/commit/45f89092b95a7335322897f8d832970a875d9646))

## v0.1.456 (2022-09-05)
### Fix
* **tuya:** Fix json loads ([`5037a89`](https://github.com/dominikkarall/fhempy/commit/5037a89b300e2220c2a01b398101f345838c8552))

## v0.1.455 (2022-09-05)
### Fix
* **tuya:** Fix translation again ([`754061d`](https://github.com/dominikkarall/fhempy/commit/754061dbd2ee2eba7c46eb4b0df13a38085077ed))

## v0.1.454 (2022-09-05)
### Feature
* **skodaconnect:** Update base lib ([`811efce`](https://github.com/dominikkarall/fhempy/commit/811efce3ff4e6c906b3b9de05c6beae4edd6ec55))

## v0.1.453 (2022-09-05)
### Fix
* **tuya:** Fix translation error for local devices ([`7fd5dcb`](https://github.com/dominikkarall/fhempy/commit/7fd5dcbca46f47f852dbeaae4122ad33356a527f))

## v0.1.452 (2022-09-05)
### Fix
* **tuya:** Fix set translation ([`6aac36d`](https://github.com/dominikkarall/fhempy/commit/6aac36d1fb1cea1a11d6bb5128e15dbcdaefa779))

## v0.1.451 (2022-09-04)
### Feature
* **tuya:** Support translation in mappings ([`2875c31`](https://github.com/dominikkarall/fhempy/commit/2875c31507712241f14e64af6da3d4aee499d85e))

## v0.1.450 (2022-09-04)
### Fix
* **fusionsolar:** Fix pv string current reading ([`1e94c42`](https://github.com/dominikkarall/fhempy/commit/1e94c428b7dcafdaea057d6a0f139530fecfc276))
* **github_backup:** Fix sha compare ([`96a7c07`](https://github.com/dominikkarall/fhempy/commit/96a7c072f0146bbe1bba3e3a859038a12734f10e))

## v0.1.449 (2022-09-03)
### Feature
* **tuya:** Add kettle support ([`92d5a09`](https://github.com/dominikkarall/fhempy/commit/92d5a09428946a43a957fd982d2ca1457973db87))

## v0.1.448 (2022-09-03)
### Feature
* **fusionsolar:** Add string voltage/current ([`f7d4b3d`](https://github.com/dominikkarall/fhempy/commit/f7d4b3da7703d460b45ec5403ddb8eb6b12dba8f))

## v0.1.447 (2022-09-02)
### Feature
* **fusionsolar:** Correct ratio values when battery is used ([`6d190ba`](https://github.com/dominikkarall/fhempy/commit/6d190bad0579d4382fe09f70d3064a0088b6630a))

### Fix
* **fhempy:** Support function_param also without function parameter in set_conf ([`2c5bb67`](https://github.com/dominikkarall/fhempy/commit/2c5bb670b97721fb9b1a3093334d8d5b0e5fa8a3))

## v0.1.446 (2022-09-01)
### Fix
* **meross:** Fix on/off ([`fe931dc`](https://github.com/dominikkarall/fhempy/commit/fe931dca53ae4a520d3e617cae53103c328c98ca))

## v0.1.445 (2022-08-31)
### Fix
* **meross:** Fix channel handling again ([`c48c59e`](https://github.com/dominikkarall/fhempy/commit/c48c59efb130598dc2cf29b35edfc09adb2e3cf9))

## v0.1.444 (2022-08-30)
### Fix
* **meross:** Fix channel support ([`a94020d`](https://github.com/dominikkarall/fhempy/commit/a94020db5358c84640297f6548dc02957ee705f9))

## v0.1.443 (2022-08-29)
### Feature
* **fhempy:** Report error when fhempy takes longer than 5s to send back answer to fhem ([`9825a67`](https://github.com/dominikkarall/fhempy/commit/9825a67608b33d2108295c23a7c026a748f8b1e8))

## v0.1.442 (2022-08-28)
### Feature
* **meross:** Support channels ([`7c89512`](https://github.com/dominikkarall/fhempy/commit/7c89512d10636da3f7e3f521120e31d6b6258828))

## v0.1.441 (2022-08-24)
### Fix
* **tuya:** Fix use API_KEY and API_SECRET reading ([`ad8db6c`](https://github.com/dominikkarall/fhempy/commit/ad8db6c5d34087c2ad10e3468f77f50b022ef5c6))

## v0.1.440 (2022-08-22)
### Feature
* **fhempy:** Support time format in set/attr ([`ecc84a3`](https://github.com/dominikkarall/fhempy/commit/ecc84a303d35afc1edcc636c071f8e6867106491))
* **github_backup:** New attr backup_time, support directories ([`2e26689`](https://github.com/dominikkarall/fhempy/commit/2e266895281081be544fe81ab5c8a2799e1d3d91))

## v0.1.439 (2022-08-21)
### Feature
* **github_backup:** Support binary files ([`c94bb7f`](https://github.com/dominikkarall/fhempy/commit/c94bb7fbd1ad1e1a6f046a67a038de917b92ab37))

## v0.1.438 (2022-08-21)
### Fix
* **github_backup:** Fix do_backup call ([`0a83c07`](https://github.com/dominikkarall/fhempy/commit/0a83c070aa99353543d17448978ce7923904e1c0))

## v0.1.437 (2022-08-21)
### Fix
* **github_backup:** Fix set backup_now ([`e28e7af`](https://github.com/dominikkarall/fhempy/commit/e28e7afb8523ba6533b20afd3eca9ab54c5719a2))

## v0.1.436 (2022-08-21)
### Feature
* **github_backup:** New github_backup module ([`6bff115`](https://github.com/dominikkarall/fhempy/commit/6bff115b9825aeecad6eab2af0ddf9eb0a192a83))

## v0.1.435 (2022-08-20)
### Feature
* **ddnssde:** Add ddnssde ([`2c706ab`](https://github.com/dominikkarall/fhempy/commit/2c706ab5ecd73db20f110e0b472dcfa76245aefd))

### Fix
* **fhempy:** Fix log level which caused delays ([`0b26f20`](https://github.com/dominikkarall/fhempy/commit/0b26f209e275e51834ffb7e55d6ea30e02635f2d))

## v0.1.434 (2022-08-20)
### Fix
* **object_detection:** Fix import ([`a815b68`](https://github.com/dominikkarall/fhempy/commit/a815b6854e6ebffe04d1c8017d24cdba28d5ec18))

## v0.1.433 (2022-08-20)
### Fix
* **object_detection:** Fix import ([`7fc674e`](https://github.com/dominikkarall/fhempy/commit/7fc674e55a44302d3060e9f85d24ebdc91903c62))

## v0.1.432 (2022-08-20)
### Fix
* **ddnssde:** Fix ip_check_interval attr ([`5ebca91`](https://github.com/dominikkarall/fhempy/commit/5ebca91b068b857a1d0da5f5a47fdc562c513e6b))

## v0.1.431 (2022-08-20)
### Fix
* **object_detection:** Update opencv lib ([`192f91d`](https://github.com/dominikkarall/fhempy/commit/192f91dd70f3396be52f3ad3627bc8b9187ff7f9))
* **object_detection:** Update tflite-runtime ([`b2f5880`](https://github.com/dominikkarall/fhempy/commit/b2f588005d9257a1252bdadcfdef9591105a9aa7))

## v0.1.430 (2022-08-20)
### Fix
* **geizhals:** Add missing dependency ([`1bab5a8`](https://github.com/dominikkarall/fhempy/commit/1bab5a8c0cc77d00545ccd5f70001d4bfd9a3999))

## v0.1.429 (2022-08-20)


## v0.1.428 (2022-08-20)


## v0.1.427 (2022-08-20)


## v0.1.426 (2022-08-20)


## v0.1.425 (2022-08-20)
### Feature
* **ddnssde:** Add ddnss.de IP updater ([`5ec7e04`](https://github.com/dominikkarall/fhempy/commit/5ec7e0413af4aae2bc8e777ff86a5c3cc2fe81f8))

## v0.1.424 (2022-08-13)
### Fix
* **fhempy:** Fix restart ([`4f7d452`](https://github.com/dominikkarall/fhempy/commit/4f7d45216fb967a69215d3b9ea20b0b9dcb62e69))

## v0.1.423 (2022-08-13)
### Fix
* **fhempy:** Stop sending msgs on shutdown ([`f1c9041`](https://github.com/dominikkarall/fhempy/commit/f1c90415e1af54b9dc07ed2ea303464f1abbf555))

## v0.1.422 (2022-08-13)
### Fix
* **fhempy:** Handle close frame ([`d8e5b44`](https://github.com/dominikkarall/fhempy/commit/d8e5b44e5a37dce52d1ae531bf8f289637e7a00b))

## v0.1.421 (2022-08-13)
### Fix
* **fhempy:** Fix long running set on define ([`24f99f8`](https://github.com/dominikkarall/fhempy/commit/24f99f8a21bc38e0dab396f816d40dc650a46b01))

## v0.1.420 (2022-08-13)
### Fix
* **fhempy:** Add more details to readme ([`402735e`](https://github.com/dominikkarall/fhempy/commit/402735ec9274ecfd756eeecfc225dc705b3b8342))

## v0.1.419 (2022-08-13)
### Fix
* **fhempy:** Logging seems to block fhempy ([`15872ee`](https://github.com/dominikkarall/fhempy/commit/15872eef3e5a3166d6d2c6982cab14cfc317a04e))

## v0.1.418 (2022-08-13)
### Feature
* **fhempy:** Add long running log again ([`69ab9bc`](https://github.com/dominikkarall/fhempy/commit/69ab9bcb4c02f7fc5566a5dbdb7779c1d423b0e1))

### Fix
* **fhempy:** Reduce timeout, fix hangup ([`f90b516`](https://github.com/dominikkarall/fhempy/commit/f90b5165d7157558024fbced8459b4e908fc7fae))

## v0.1.417 (2022-08-13)
### Fix
* **fhempy:** Fix hang on startup ([`d943ddd`](https://github.com/dominikkarall/fhempy/commit/d943ddd2ebf2fb542a06ba124a5ce409e841a17e))

## v0.1.416 (2022-08-13)
### Feature
* **fhempy:** Log error when fhempy takes over 100ms to reply to fhem ([`0649ec7`](https://github.com/dominikkarall/fhempy/commit/0649ec7c392da8b90dc5acecb8db864453fa4dd9))

## v0.1.415 (2022-08-13)
### Feature
* **fhempy:** Log error if fhem took longer than 200ms to handle cmd ([`2767776`](https://github.com/dominikkarall/fhempy/commit/27677769cb7372055ebdff5255771ca31203fad5))

### Fix
* **xiaomi_tokens:** Fix logging ([`2859f1f`](https://github.com/dominikkarall/fhempy/commit/2859f1f0ac0c966401e21d3b482333d3975301d6))

## v0.1.414 (2022-08-13)


## v0.1.413 (2022-08-13)
### Fix
* **fhempy:** Better error handling for fhempy connection ([`a1fb108`](https://github.com/dominikkarall/fhempy/commit/a1fb10858b348f57fc6748af8e25ffc3b6444b53))

## v0.1.412 (2022-08-13)
### Feature
* **fhempy:** Add fhem log entry on update ([`dc89f94`](https://github.com/dominikkarall/fhempy/commit/dc89f9428dec62ab6d49a9ef002fa25dc995d63f))

### Fix
* **fhempy:** Better error handling ([`9331279`](https://github.com/dominikkarall/fhempy/commit/933127998e0f1c1ca69ff0d647f18631e786fb2e))
* **fhempy:** Deactivate MOV for controls file ([`4bb248b`](https://github.com/dominikkarall/fhempy/commit/4bb248bac3e7956dbefa7667d9403f4d788d75ca))

## v0.1.411 (2022-08-12)
### Feature
* **fhempy:** Receive all fhem events in fhempy ([`0aad85a`](https://github.com/dominikkarall/fhempy/commit/0aad85a1dccb1efb514fb2925175f7ee60199e67))

### Fix
* **fhempy:** Skip non-utf8 messages ([`c1abfd1`](https://github.com/dominikkarall/fhempy/commit/c1abfd1662af378e15c70e753fdbaf4b79336e4b))
* **fhempy:** Fix continue in some cases and fix devStateIcon ([`5c98ef5`](https://github.com/dominikkarall/fhempy/commit/5c98ef5c987c5076debf5324bd26f9ba4bb1e310))
* **fhempy:** Set devio log level to 5 ([`f5d9492`](https://github.com/dominikkarall/fhempy/commit/f5d94928e67a54c68c6348509505feb1b34ee9f9))

## v0.1.410 (2022-08-12)
### Fix
* **xiaomi_tokens:** Fix newline from readings ([`4bba6f3`](https://github.com/dominikkarall/fhempy/commit/4bba6f3398d5b6e95e29c6be637c4b73aaa67ae9))

## v0.1.409 (2022-08-12)
### Fix
* **xiaomi_tokens:** Fix rstrip ([`9e5bc0d`](https://github.com/dominikkarall/fhempy/commit/9e5bc0dfc486b9815c5b1dd8c614c1d04f2d40a8))

## v0.1.408 (2022-08-12)
### Fix
* **fhempy:** Migrate to fhempyServer ([`710f79e`](https://github.com/dominikkarall/fhempy/commit/710f79e281b522eec6a1de3ffeaefc04f2bca429))
* **fhempy:** Migrate to fhempy ([`33ad82a`](https://github.com/dominikkarall/fhempy/commit/33ad82ae0c0f3f212af442d6075c2b05beb8ce8a))
* **xiaomi_tokens:** Remove newline from username, password ([`1e5ef64`](https://github.com/dominikkarall/fhempy/commit/1e5ef642e94df0d10e29fc118bbbc862b6332d97))

## v0.1.407 (2022-08-12)
### Fix
* **fhempy:** Log utf-8 decode error ([`5249cee`](https://github.com/dominikkarall/fhempy/commit/5249ceeb5b4fb966018be6815863cf918e4eedcd))

## v0.1.406 (2022-08-12)
### Fix
* **fhempy:** Fix sendBackError without id ([`c32c271`](https://github.com/dominikkarall/fhempy/commit/c32c271fdc63b4d9303a250af8c32f150f80e118))

## v0.1.405 (2022-08-11)
### Fix
* **fhempy:** Send back error on json error ([`7d951d1`](https://github.com/dominikkarall/fhempy/commit/7d951d1dc87f4d8a879ffd0d785dc1440367e81e))
* **fhempy:** Send binary data via websocket ([`912f15f`](https://github.com/dominikkarall/fhempy/commit/912f15f06d08c9ced432ae2a6760d65c0d27ea80))

## v0.1.404 (2022-08-11)
### Fix
* **fhempy:** Fix message handling ([`6c3a835`](https://github.com/dominikkarall/fhempy/commit/6c3a8351ac1c6269d0208f4ea27a9d81c687a363))

## v0.1.403 (2022-08-11)
### Feature
* **fhempy:** Support binary messages from fhem ([`63d8b92`](https://github.com/dominikkarall/fhempy/commit/63d8b92ecb6a0aa6eb08720eb6e20b9b43438176))

### Fix
* **esphome:** Update esphome lib ([`6cff272`](https://github.com/dominikkarall/fhempy/commit/6cff2724203a6ae50feaf909c59dce2dac7da3ad))
* **fhem_forum:** Fix state reading ([`6f42906`](https://github.com/dominikkarall/fhempy/commit/6f42906e7436303df50dd086d1cfb9e968b502aa))

## v0.1.402 (2022-08-10)
### Fix
* **fhempy:** Fix disconnected icon ([`05994b9`](https://github.com/dominikkarall/fhempy/commit/05994b970a69b032abf2b8a35e213f2fcc11eb8f))

## v0.1.401 (2022-08-10)
### Fix
* **fhempy:** Update available fhempy version every 12 hours ([`8af8092`](https://github.com/dominikkarall/fhempy/commit/8af8092ff0a76b39e3827b97a54223324967f441))

## v0.1.400 (2022-08-10)
### Fix
* **fhempy:** Always show update icon in BindingsIo device ([`cb322da`](https://github.com/dominikkarall/fhempy/commit/cb322da3014d80f3f17686d81594eee54eaa4621))

## v0.1.399 (2022-08-10)
### Feature
* **fhempy:** Add info about available update ([`23fd613`](https://github.com/dominikkarall/fhempy/commit/23fd613b9f6430b85c8371e1edbcdb4dd3f2f0f3))

## v0.1.398 (2022-08-10)
### Fix
* **fhempy:** Fix README for blocking code ([`81e332f`](https://github.com/dominikkarall/fhempy/commit/81e332fcad42a8c00f8ab2a270d4c65bca3b7a5b))
* **fhem_forum:** Fix state reading ([`e0abe40`](https://github.com/dominikkarall/fhempy/commit/e0abe40e32ffe4b842e6f83252f00846c9159e8c))

## v0.1.397 (2022-08-10)
### Feature
* **miio:** Update python-miio lib ([`b5b65ac`](https://github.com/dominikkarall/fhempy/commit/b5b65acab2ceabeb25b25eeab190021ccbfc7e0a))

## v0.1.396 (2022-08-10)
### Feature
* **geizhals:** Add alias attr, best store reading and store availability ([`874d5c9`](https://github.com/dominikkarall/fhempy/commit/874d5c9b6c437b2128d0131c0135e9457b3bd363))

### Fix
* **fhempy:** Change timeout to 60s on shutdown/restart ([`0b87dbf`](https://github.com/dominikkarall/fhempy/commit/0b87dbfef46fcdc5b44ab7f9f6e44ccdbb297ba0))
* **fhem_forum:** Fix keyword handling and state reading ([`a6af955`](https://github.com/dominikkarall/fhempy/commit/a6af955e48fbed5457f18ceed794526856be6e23))
* **fhem_forum:** Fix state ([`7371bf4`](https://github.com/dominikkarall/fhempy/commit/7371bf40b6860ac585d606aa1812c1babc99668d))

## v0.1.395 (2022-08-10)
### Feature
* **fhem_forum:** Check FHEM forum for updates ([`4e843e0`](https://github.com/dominikkarall/fhempy/commit/4e843e024fb8cd7ad6f14a48f4c58b0929b9b33a))

## v0.1.394 (2022-08-09)
### Fix
* **fhempy:** Fix restart/shutdown issues ([`8198930`](https://github.com/dominikkarall/fhempy/commit/8198930a92ca50c86db8c91e8e12a3466dd98447))
* **geizhals:** Change default update interval ([`e11770e`](https://github.com/dominikkarall/fhempy/commit/e11770e95aa05cb509db6604572ae8f9941360a6))
* **google_weather:** Add headers ([`5b0d423`](https://github.com/dominikkarall/fhempy/commit/5b0d4237cd37df7bbf71d963f5cd834273969d66))

## v0.1.393 (2022-08-08)
### Feature
* **geizhals:** Add link reading ([`fd9ee3a`](https://github.com/dominikkarall/fhempy/commit/fd9ee3a876fe624d2a6f8e14690b670521dd546c))

## v0.1.392 (2022-08-07)
### Fix
* **tuya:** Correct current, power values ([`229d549`](https://github.com/dominikkarall/fhempy/commit/229d54968dd365662ccde90bc81207715a638991))
* **warema:** Add README ([`f836930`](https://github.com/dominikkarall/fhempy/commit/f8369301590ee560fa25beeeeecdc3ad79aac107))

## v0.1.391 (2022-08-07)
### Fix
* **tuya:** Fix dp readings when locally not detected ([`e4b5f92`](https://github.com/dominikkarall/fhempy/commit/e4b5f928d6dc9e8f61bd6ebd35200016f51aa0fc))

## v0.1.390 (2022-08-06)
### Fix
* **tuya:** Add debug msgs ([`53732a9`](https://github.com/dominikkarall/fhempy/commit/53732a97581df0b4e55037d751ebc92677b5d236))

## v0.1.389 (2022-08-06)
### Feature
* **kia_hyundai:** Support commands ([`4fa92bf`](https://github.com/dominikkarall/fhempy/commit/4fa92bfc36fc030b24a8ec8d19ea9deae1611119))

## v0.1.388 (2022-08-06)
### Feature
* **kia_hyundai:** Initial release for Kia / Hyundai cars ([`08987cb`](https://github.com/dominikkarall/fhempy/commit/08987cbeedcf8ed235e952950a6f0d5cf13606eb))

## v0.1.387 (2022-08-06)
### Feature
* **tuya:** Support Json for category zndb devices ([`53209ff`](https://github.com/dominikkarall/fhempy/commit/53209ff361fabfe3d8b6dc4014753234cbbe0487))

## v0.1.386 (2022-08-05)
### Feature
* **tuya:** Split json into multiple readings ([`366d729`](https://github.com/dominikkarall/fhempy/commit/366d729267d27c9603bef1bbe1a929ef5cca9f97))

### Fix
* **fusionsolar:** Better error handling ([`03d67f3`](https://github.com/dominikkarall/fhempy/commit/03d67f3e0b191be42d8c08f7b2e3d949624bbb85))
* **fhempy:** Support string format for flatten_json ([`d7457a8`](https://github.com/dominikkarall/fhempy/commit/d7457a851d0374fc1fda76ece0fa775f7c3234f0))

## v0.1.385 (2022-08-04)
### Feature
* **geizhals:** Add geizhals module ([`dda5f09`](https://github.com/dominikkarall/fhempy/commit/dda5f0989f2adb395c1ac9b3be9157f2a4421512))

## v0.1.384 (2022-08-04)
### Feature
* **geizhals:** Retrieve best prices from geizhals ([`b6c935e`](https://github.com/dominikkarall/fhempy/commit/b6c935e75521d9432b18541aa9c2d55f86c19b6d))

### Fix
* **google_weather:** Fix replace command ([`311ee9c`](https://github.com/dominikkarall/fhempy/commit/311ee9c9adc10d481b89819be532d1b212c905ec))

## v0.1.383 (2022-08-04)
### Feature
* **google_weather:** Add hourly weather data ([`65101c3`](https://github.com/dominikkarall/fhempy/commit/65101c33101c5a8996d3ab07cbccd1728fff8580))

## v0.1.382 (2022-08-03)


## v0.1.381 (2022-08-03)
### Feature
* **google_weather:** Add google weather ([`6a45ff5`](https://github.com/dominikkarall/fhempy/commit/6a45ff5f23a2fc545075ee22186507d44e0cf3a6))

### Fix
* **zigbee2mqtt:** Fix restart ([`d872abd`](https://github.com/dominikkarall/fhempy/commit/d872abd0581c045a4beac6c5f11a4bcc1fcbf1bc))
* **gree_climate:** Update greeclimate lib ([`db874ed`](https://github.com/dominikkarall/fhempy/commit/db874ed9a002ecf6ba4906501a08fbf09ad4370c))

## v0.1.380 (2022-07-16)
### Fix
* **fhempy:** Handle defmod/modify properly ([`c0e29df`](https://github.com/dominikkarall/fhempy/commit/c0e29df6ac8cb38c8c12bfe1185414bb3d85daf4))

## v0.1.379 (2022-07-15)
### Fix
* **gree_climate:** Retry to establish connection on startup ([`4a8141c`](https://github.com/dominikkarall/fhempy/commit/4a8141c47d4a6829ac50e700df59d3ab358d3df3))

## v0.1.378 (2022-07-13)
### Fix
* **fusionsolar:** Fix login procedure ([`a2387c1`](https://github.com/dominikkarall/fhempy/commit/a2387c12f9ba53a5ac1b6d79b5785f41441aaf98))

## v0.1.377 (2022-07-13)
### Fix
* **fusionsolar:** Add debug output ([`ba2c97f`](https://github.com/dominikkarall/fhempy/commit/ba2c97f52e0fded216cfb2231175a54bce1fe7c5))

## v0.1.376 (2022-07-12)
### Fix
* **fhempy:** Fix ssdp ([`95febe2`](https://github.com/dominikkarall/fhempy/commit/95febe2d1b9f79d0ab8d267d77d8e683d7adec19))

## v0.1.375 (2022-07-12)
### Fix
* **fhempy:** Update cryptography, aiohttp, async-upnp-client ([`7d7f654`](https://github.com/dominikkarall/fhempy/commit/7d7f65438335d5efaee9a2cc1cd113486562bd5d))

## v0.1.374 (2022-07-12)
### Fix
* **dlna_dmr:** Fix manifest ([`98a7f03`](https://github.com/dominikkarall/fhempy/commit/98a7f036650546c7fc55303e568398569918d960))

## v0.1.373 (2022-07-12)
### Fix
* **wienerlinien:** Fix requirements ([`85679d4`](https://github.com/dominikkarall/fhempy/commit/85679d48a1c970f0824b7f0aaeaced057fc7a136))

## v0.1.372 (2022-07-12)
### Fix
* **fhempy:** Fix aiohttp bug ([`2cd64fd`](https://github.com/dominikkarall/fhempy/commit/2cd64fd25819b47a749d6accd6741d1e22584625))

## v0.1.371 (2022-07-12)
### Fix
* **fhempy:** Disable events because of utf-8 bug ([`3a3bf25`](https://github.com/dominikkarall/fhempy/commit/3a3bf25f2535ff2fadc490c7a917c40b9e11b94e))

## v0.1.370 (2022-07-10)
### Feature
* **fusionsolar:** BREAKING CHANGE, see README. Username/password support instead of sessionid. ([`0a3d94d`](https://github.com/dominikkarall/fhempy/commit/0a3d94de9fa15d854e28076684fbf033039f0c0c))

## v0.1.369 (2022-07-09)
### Feature
* **volvo_software_update:** New module which notifies about volvo software updates ([`aada589`](https://github.com/dominikkarall/fhempy/commit/aada58901979f5c79d2ddbc8640890cd21e6e957))

### Fix
* **fhempy:** Fix event handling ([`8649e04`](https://github.com/dominikkarall/fhempy/commit/8649e04cda8fde246a0ee4c187af1f74a4b3c79a))
* **tuya:** Prevent error when attr dp_xx is not available localy ([`30ebebf`](https://github.com/dominikkarall/fhempy/commit/30ebebff1af3aaede5a8ff01ad96642229c970a0))
* **fusionsolar:** Support new web api ([`31423a8`](https://github.com/dominikkarall/fhempy/commit/31423a8f1309eb4c46607c70e4608dbca13dab82))
* **googlecast:** Update pychromecast lib ([`d30c288`](https://github.com/dominikkarall/fhempy/commit/d30c288f020978b525ea2ef8d27f3d02b6afaa0c))

## v0.1.368 (2022-06-20)
### Fix
* **fhempy:** Fix ble disconnect failure ([`1142d94`](https://github.com/dominikkarall/fhempy/commit/1142d94de4a365449b531acdc71995045149fe35))
* **fhempy:** Fix naming ([`6b7ddc2`](https://github.com/dominikkarall/fhempy/commit/6b7ddc2dc71483d0b08bc3d9a38c354746ce4818))
* **fusionsolar:** Fix string energy ([`f015ac7`](https://github.com/dominikkarall/fhempy/commit/f015ac71d4b7c0908ecbaa74bc6f7ab29f020788))

## v0.1.367 (2022-06-17)
### Fix
* **fusionsolar:** Fix string_output_power ([`4f83d8a`](https://github.com/dominikkarall/fhempy/commit/4f83d8ab6b3a04820ce7dc75b10a11d23f0a743c))

## v0.1.366 (2022-06-16)
### Fix
* **fusionsolar:** Fix NoneType exception ([`9cc40c3`](https://github.com/dominikkarall/fhempy/commit/9cc40c3bc188b8a4deb1ed7c2193828b7f0a7264))

## v0.1.365 (2022-06-15)
### Fix
* **tuya:** Do not raise exception if decoding fails ([`1371ca4`](https://github.com/dominikkarall/fhempy/commit/1371ca4376c5365b940d94074363796286cf418e))

## v0.1.364 (2022-06-14)
### Fix
* **tuya:** Add logging if payload decoding fails ([`79953c5`](https://github.com/dominikkarall/fhempy/commit/79953c5de67e1f1e950336cbec6d32903af8da67))

## v0.1.363 (2022-06-13)
### Fix
* **fusionsolar:** Prevent token to expire ([`9629bfb`](https://github.com/dominikkarall/fhempy/commit/9629bfb16133595248c6b5d3df856483c546e67b))
* **gfprobt:** Do not send parallel commands ([`3f1e504`](https://github.com/dominikkarall/fhempy/commit/3f1e504cf6992337abb0886d4f19316dd42c2915))
* **gfprobt:** Fix adjust ([`54427b2`](https://github.com/dominikkarall/fhempy/commit/54427b2e3f9aade0ba6400b58cbeea48574d1c95))

## v0.1.362 (2022-06-10)
### Feature
* **fusionsolar:** Add string_output_power ([`84bdaa1`](https://github.com/dominikkarall/fhempy/commit/84bdaa155871bd199c21a46e87af5e690c803484))

## v0.1.361 (2022-06-10)
### Fix
* **fusionsolar:** Add idle call ([`987a88a`](https://github.com/dominikkarall/fhempy/commit/987a88ab4f91e68f96e745db2acebb0a59f3bc28))
* **fhempy:** Fix local restart ([`3842026`](https://github.com/dominikkarall/fhempy/commit/38420261e3176d6cc43b32f73c219833706efe50))

## v0.1.360 (2022-06-04)
### Fix
* **googlecast:** Update lib and fix protobuf ([`bf73a18`](https://github.com/dominikkarall/fhempy/commit/bf73a182363dc39bcafc9570ec0b3579f484c814))

## v0.1.359 (2022-06-04)
### Fix
* **tuya:** Improve state text when device couldn't be discovered ([`2db8add`](https://github.com/dominikkarall/fhempy/commit/2db8addc3bcd993f6294b8211c72a2b065a0eab4))
* **fusionsolar:** Fix division by zero exception ([`765982c`](https://github.com/dominikkarall/fhempy/commit/765982c9401c08aa1d400b23128888a3c4acaa19))

## v0.1.358 (2022-05-23)
### Fix
* **fhempy:** Downgrade libraries to working versions ([`8ba4662`](https://github.com/dominikkarall/fhempy/commit/8ba46629905c6233ef3a79ae204e0d7dc468fd8d))

## v0.1.357 (2022-05-19)
### Fix
* **fhempy:** Revert aiohttp version ([`905dfe0`](https://github.com/dominikkarall/fhempy/commit/905dfe01af0aeb3a7894aa945b855370e2486ec5))

## v0.1.356 (2022-05-19)
### Fix
* **fhempy:** Update libraries ([`20f40b8`](https://github.com/dominikkarall/fhempy/commit/20f40b86fbccc160f254cf2d184e301eccb8e8fe))
* **fhempy:** Cleanup imports ([`d66b01a`](https://github.com/dominikkarall/fhempy/commit/d66b01a6e0ff1d70feb6b34b12910066dd558a0b))

## v0.1.355 (2022-05-19)
### Fix
* **fhempy:** Update zeroconf to 0.38.6 ([`4f60df8`](https://github.com/dominikkarall/fhempy/commit/4f60df8a79f804b97016588aefb80d3575e7bb5f))

## v0.1.354 (2022-05-19)
### Fix
* **fhempy:** Deactivate events ([`40bd9a4`](https://github.com/dominikkarall/fhempy/commit/40bd9a44c42ea9081f9db00c8b0e785dd4fcb21d))

## v0.1.353 (2022-05-19)
### Fix
* **fhempy:** Revert event handling ([`f020c34`](https://github.com/dominikkarall/fhempy/commit/f020c34d1c790ce831bf50db86f1ddd950735d82))

## v0.1.352 (2022-05-19)
### Fix
* **fhempy:** Fix event handling (?) ([`ba5e9c4`](https://github.com/dominikkarall/fhempy/commit/ba5e9c42f3a28ded54d31ec6d2fb2e8a8291ecfe))

## v0.1.351 (2022-05-18)
### Feature
* **fusionsolar:** Support battery values ([`f0a67cd`](https://github.com/dominikkarall/fhempy/commit/f0a67cd9362c324cf73cf413f2fa4a9a3b15fe5f))

## v0.1.350 (2022-05-18)
### Fix
* **fusionsolar:** Fix if battery in use ([`ad7c12f`](https://github.com/dominikkarall/fhempy/commit/ad7c12f6970b92a49bab10999498ef11daed3847))

## v0.1.349 (2022-05-18)
### Fix
* **fusionsolar:** Fix region usage in define ([`d388160`](https://github.com/dominikkarall/fhempy/commit/d38816072464b140ef774f0d003820935c640b8a))

## v0.1.348 (2022-05-16)
### Fix
* **fhempy:** Deactivate events as long as encoding issues are not fixed ([`55353e9`](https://github.com/dominikkarall/fhempy/commit/55353e922902a655d4efda95b9897e467bf56689))
* **fhempy:** Rename PyBinding class to fhempy ([`259507d`](https://github.com/dominikkarall/fhempy/commit/259507d668c101778f58a03bd22ba95632e05652))

## v0.1.347 (2022-05-16)
### Fix
* **fhempy:** Fix for non string events ([`fdccd1f`](https://github.com/dominikkarall/fhempy/commit/fdccd1f41a17ae0e41904bcff7dc7a7ec7466923))

## v0.1.346 (2022-05-15)
### Fix
* **miio:** Set offline when no reply on status call ([`57c4908`](https://github.com/dominikkarall/fhempy/commit/57c49089e49119770b1ef673fcbbe30f2a98fef1))

## v0.1.345 (2022-05-15)
### Feature
* **fhempy:** Support FHEM events (register_event_listener) ([`1c4e38b`](https://github.com/dominikkarall/fhempy/commit/1c4e38bc830b5a6bd9b3c2e05bd55ae7d041ff93))

### Fix
* **fhempy:** Add SIGINT handling ([`c2ab429`](https://github.com/dominikkarall/fhempy/commit/c2ab42979241cce82cd250a72046023855330427))

## v0.1.344 (2022-05-14)
### Fix
* **esphome:** Fix long running set functions ([`48fbf28`](https://github.com/dominikkarall/fhempy/commit/48fbf28f7b0b7bc38137d4ad13ea6604064d9587))
* **gfprobt:** Fix loop on asyncio cancel ([`7fc9075`](https://github.com/dominikkarall/fhempy/commit/7fc9075e9cea31cd4609ad7b77446579e8c1b0dd))

## v0.1.343 (2022-05-14)
### Fix
* **zigbee2mqtt:** Fix function arguments ([`790b00a`](https://github.com/dominikkarall/fhempy/commit/790b00a646581eab4c1739814c2e6ee78fadca6b))

## v0.1.342 (2022-05-14)
### Fix
* **fhempy:** Use os._exit again ([`9c64c08`](https://github.com/dominikkarall/fhempy/commit/9c64c081f52edfe957cbcabec115021313a98c22))
* **zigbee2mqtt:** Some restart fixes, z2m takes about 15s to shutdown correctly ([`20d6761`](https://github.com/dominikkarall/fhempy/commit/20d676147c21a241f1beb9e28a853978d607b28b))

## v0.1.341 (2022-05-14)
### Fix
* **zigbee2mqtt:** Fix possible zombie process ([`bc8102b`](https://github.com/dominikkarall/fhempy/commit/bc8102b2768685494080a1329c83c54baca0b1ce))
* **esphome:** Fix possible zombie process ([`8140d62`](https://github.com/dominikkarall/fhempy/commit/8140d62cbb122e53f69770e9deffa64a1ec4cbd4))

## v0.1.340 (2022-05-14)
### Fix
* **zigbee2mqtt:** Wait longer for z2m to stop ([`7bab4d9`](https://github.com/dominikkarall/fhempy/commit/7bab4d97c208e18d637bb22b90c19e7ef1e2ea0f))
* **fhempy:** Use os._exit if undefine fails to ensure exit ([`c634917`](https://github.com/dominikkarall/fhempy/commit/c63491715c28d1ba0020e20bf961fc34b507e226))

## v0.1.339 (2022-05-14)
### Fix
* **gfprobt:** Disconnect on Undefine ([`8ab7a81`](https://github.com/dominikkarall/fhempy/commit/8ab7a81f3ff80ed55a0d699171e92666b4abeac9))

## v0.1.338 (2022-05-13)
### Fix
* **fhempy:** Fix Undefine calls when stopped ([`2f62033`](https://github.com/dominikkarall/fhempy/commit/2f620330e70c28d77137db840fd0570b0c56adf5))
* **eq3bt:** Fix Undefine when not yet connected ([`ebdbe92`](https://github.com/dominikkarall/fhempy/commit/ebdbe92dcbbb1f3d5e57a6c311e8ef6a25b31900))

## v0.1.337 (2022-05-13)
### Fix
* **eq3bt:** Disconnect on Undefine ([`bbd52d0`](https://github.com/dominikkarall/fhempy/commit/bbd52d0a3b91f0e0fe2088231e9a361fd152db86))

## v0.1.336 (2022-05-13)
### Fix
* **zigbee2mqtt:** Better stop process handling ([`46ac614`](https://github.com/dominikkarall/fhempy/commit/46ac6143c1c85cde01365eaa62ee1d34d5088ef3))
* **esphome:** Better stop process handling ([`8efa358`](https://github.com/dominikkarall/fhempy/commit/8efa3588f8565d1070054f439c4cfc17f0f14dfd))
* **zigbee2mqtt:** Code style improvement ([`39f6bca`](https://github.com/dominikkarall/fhempy/commit/39f6bcace4074195741973593e369c05737befbd))

## v0.1.335 (2022-05-10)
### Feature
* **fhempy:** Support peer restart from FHEM ([`ce7803a`](https://github.com/dominikkarall/fhempy/commit/ce7803a9672f460e6599cec899b0d1787f69dfea))

### Fix
* **spotify:** Update spotipy to 2.19.0 ([`77d8ee2`](https://github.com/dominikkarall/fhempy/commit/77d8ee2589e14b32132a7458bad745c78118a829))

## v0.1.334 (2022-05-10)
### Fix
* **fhempy:** Fix stash for release script ([`ef9fada`](https://github.com/dominikkarall/fhempy/commit/ef9fadad91908550ac7bac17d381266b67fa887e))
* **fhempy:** Add update info log ([`920d4c9`](https://github.com/dominikkarall/fhempy/commit/920d4c9fddd911a0fa0dc872d7bcd5b9ea61bb07))
* **fhempy:** Update websockets to 10.3 ([`b0313d0`](https://github.com/dominikkarall/fhempy/commit/b0313d03148f35e45858e8ffd7ee0a0c772dc4bc))
* **fhempy:** Close websockets on restart ([`729a65e`](https://github.com/dominikkarall/fhempy/commit/729a65e83f8d322ecaf05b2dbef1818fdfc96935))
* **zigbee2mqtt:** Stop task on restart ([`6fea8af`](https://github.com/dominikkarall/fhempy/commit/6fea8af00f58e2f83117ca1c8051ad06d155c4ad))

## v0.1.333 (2022-05-10)
### Fix
* **zigbee2mqtt:** Fix stop zigbee2mqtt process ([`ab44052`](https://github.com/dominikkarall/fhempy/commit/ab44052bf25e64fa8d84685c152d43aeb877080a))

## v0.1.332 (2022-05-10)
### Fix
* **fhempy:** Log exit code ([`7dee7c8`](https://github.com/dominikkarall/fhempy/commit/7dee7c8914a420aab8c4c6185d395859c572a6d8))
* **fhempy:** Asyncio improvements ([`7d2e005`](https://github.com/dominikkarall/fhempy/commit/7d2e00579b1b3d85ce7004381c0055b1f2ef02b4))
* **tuya:** Fix usage without api key/secret ([`4e716d7`](https://github.com/dominikkarall/fhempy/commit/4e716d7163b216a1a1555612626fd6c5ee456a1f))
* **fhempy:** Code style improvements ([`1c6744c`](https://github.com/dominikkarall/fhempy/commit/1c6744c3220852f45cf0246492c774640fc9aa33))
* **discover_upnp:** Code style improvements ([`b0eb47b`](https://github.com/dominikkarall/fhempy/commit/b0eb47bc0a301581cbc03652366a0654d446df04))
* **fhempy:** Import cleanup ([`427f826`](https://github.com/dominikkarall/fhempy/commit/427f8267ae8dcd4a12e376c82e59d33cb5e8b154))
* **zigbee2mqtt:** Code style improvements ([`560d061`](https://github.com/dominikkarall/fhempy/commit/560d06133996aa34bd1cc50b1531845e90cf11b5))

## v0.1.331 (2022-05-09)
### Fix
* **zigbee2mqtt:** Kill instead of terminate ([`dbeeb36`](https://github.com/dominikkarall/fhempy/commit/dbeeb36a77981fe360f70149c97f7b619c0b0ba5))
* **esphome:** Kill instead of terminate ([`0040297`](https://github.com/dominikkarall/fhempy/commit/0040297d934398a3027059c090cac0a31cc908e9))
* **discover_upnp:** Delete unused variable ([`e30f2c6`](https://github.com/dominikkarall/fhempy/commit/e30f2c692496cc4980f9bd0995654a14f72a2c11))

## v0.1.330 (2022-05-09)
### Fix
* **fhempy:** Better restart/shutdown handling ([`4e97c58`](https://github.com/dominikkarall/fhempy/commit/4e97c58b02573cdee0ee9dd11fee30667abb7ad8))
* **tuya:** Import only Cloud, deviceScan ([`3f92df2`](https://github.com/dominikkarall/fhempy/commit/3f92df2412409541f55a70e49d26b1fe0dbc5337))
* **tuya:** Remove unused attributes ([`1beab02`](https://github.com/dominikkarall/fhempy/commit/1beab02553dcee4c265cc49131e1afe93fe0c0b0))
* **miio:** Fix send_command, sort imports ([`737eeef`](https://github.com/dominikkarall/fhempy/commit/737eeefbbf37f9a263ea4527248834ef351cef3c))
* **tuya:** Sort imports ([`1a3acfd`](https://github.com/dominikkarall/fhempy/commit/1a3acfd020c853e08ad3f8a93915a7682c5b9844))

## v0.1.329 (2022-05-08)
### Fix
* **miio:** Fix tuple usage ([`d97751a`](https://github.com/dominikkarall/fhempy/commit/d97751ad8c7c0ca31fc2bce6f7991a14f4f3c6a3))
* **tuya:** Fix tests ([`dd9ce3c`](https://github.com/dominikkarall/fhempy/commit/dd9ce3cda1f98ed73c743051f2ea1abe72d62721))

## v0.1.328 (2022-05-08)
### Feature
* **fhempy:** Log version on startup ([`63ecc62`](https://github.com/dominikkarall/fhempy/commit/63ecc627966b3aaa8647f6eb06e2b6bf1dd51fda))

### Fix
* **fhempy:** Fix shutdown again ([`6e0e1f1`](https://github.com/dominikkarall/fhempy/commit/6e0e1f1a4cf13a30803087f2f337dfc3e46728a1))

## v0.1.327 (2022-05-08)
### Fix
* **fhempy:** Fix shutdown handler ([`d246ca8`](https://github.com/dominikkarall/fhempy/commit/d246ca8cdb7aa44c1a7e7c2b0f17e217b24836dc))

## v0.1.326 (2022-05-08)
### Fix
* **fhempy:** Handle SIGTERM for graceful shutdown ([`35dff0a`](https://github.com/dominikkarall/fhempy/commit/35dff0aac289f97fceb15ceff3f7b51469b2e778))
* **zigbee2mqtt:** Call stop_process on Undefine ([`e3626e5`](https://github.com/dominikkarall/fhempy/commit/e3626e518b171b0610dd0d95f5356a9ac72e7a89))
* **esphome:** Call stop_process on Undefine ([`8402760`](https://github.com/dominikkarall/fhempy/commit/84027609c91ff675634165f8c0a25511b32541b1))
* **esphome:** Set proc None when terminated ([`81f10b0`](https://github.com/dominikkarall/fhempy/commit/81f10b0f8c68a0b3ad424201574aa9d2b50c0920))
* **zigbee2mqtt:** Fix blocking calls ([`a980bf3`](https://github.com/dominikkarall/fhempy/commit/a980bf3000341e43ffd83dec9c8b1b4784f971dc))

## v0.1.325 (2022-05-08)
### Fix
* **tuya:** Always use cloud specs when APIKEY and APISECRET is provided ([`d9d3812`](https://github.com/dominikkarall/fhempy/commit/d9d381292fe731fccf4b04a11dcc06dfe0514d7c))

## v0.1.324 (2022-05-08)
### Fix
* **fusionsolar:** Update takes a bit longer, extend to full 5min + 30s ([`79cb26a`](https://github.com/dominikkarall/fhempy/commit/79cb26a08008f6b30c00598244e0117a39f2b4b6))

## v0.1.323 (2022-05-08)
### Fix
* **tuya:** Fix local found counter ([`a8b708c`](https://github.com/dominikkarall/fhempy/commit/a8b708cfa13d6266966ce27b70cdc98216594dc1))

## v0.1.322 (2022-05-08)
### Fix
* **wienerlinien:** Code style improvements ([`c5207f4`](https://github.com/dominikkarall/fhempy/commit/c5207f47970d689a7b4ed5c0ee9fa8356072f6fe))
* **tuya_cloud:** Code style improvements ([`46c90ca`](https://github.com/dominikkarall/fhempy/commit/46c90ca41b62a2bd24d46dff20a333bb3ced5f00))
* **esphome:** Code style improvements ([`f8a091b`](https://github.com/dominikkarall/fhempy/commit/f8a091be9dd6505c4416217309e1307246b81abc))
* **fusionnsolar:** Code style improvements ([`dd01e29`](https://github.com/dominikkarall/fhempy/commit/dd01e29c433ab4593536060a9d8f829cb452c6d2))
* **tuya:** Code style improvements ([`b014060`](https://github.com/dominikkarall/fhempy/commit/b01406066a0b460ee0d63a011755f96423263a06))
* **fusionsolar:** Fix update interval ([`a33dc00`](https://github.com/dominikkarall/fhempy/commit/a33dc005daf44920d921c4283a824feb859b6eff))

## v0.1.321 (2022-05-08)
### Feature
* **tuya:** Support wifi devices which are not online all the time (e.g. water leak sensor, smoke detector, ...) ([`035429c`](https://github.com/dominikkarall/fhempy/commit/035429ceab4508ba94c4e9e2253f2ba736e62bea))
* **fusionsolar:** Update on fusionsolar update (every full 5min) ([`b338277`](https://github.com/dominikkarall/fhempy/commit/b338277d1e42e93b681dd8e1344d72d13d97c032))

### Fix
* **fusionsolar:** Fix div/0 ([`57bbc51`](https://github.com/dominikkarall/fhempy/commit/57bbc51ad9e51637d70bbba57902aa73ddd3937f))
* **fusionsolar:** Delete unused file ([`45f7bb8`](https://github.com/dominikkarall/fhempy/commit/45f7bb8ad4d4ca2882d7c9b4cce0c13dd9a04ad9))

## v0.1.320 (2022-05-07)
### Fix
* **miio:** Fix tuple type ([`4282a99`](https://github.com/dominikkarall/fhempy/commit/4282a995425efc1940d4a27ca11cd1fd08dac692))

## v0.1.319 (2022-05-07)
### Fix
* **fhempy:** Wait max 10s for restart ([`896d80b`](https://github.com/dominikkarall/fhempy/commit/896d80bd065e4f3670e0b66df706bc64ccd2fb32))

## v0.1.318 (2022-05-07)
### Feature
* **fusionsolar:** Add daily_self_use_solar_ratio reading ([`4abd020`](https://github.com/dominikkarall/fhempy/commit/4abd02016a99e319afcb04ab0c99fe3668a255ff))

## v0.1.317 (2022-05-07)
### Fix
* **fusionsolar:** Fix daily_self_use_ratio ([`84ea1e0`](https://github.com/dominikkarall/fhempy/commit/84ea1e0ab36a2a66a5e6caabe86c9aff92ed71d4))

## v0.1.316 (2022-05-07)
### Fix
* **fusionsolar:** Small fixes ([`cdbd06c`](https://github.com/dominikkarall/fhempy/commit/cdbd06ced4a2bcfedd43dd70fce916a4cab30ea9))

## v0.1.315 (2022-05-07)
### Feature
* **fusionsolar:** Add further readings ([`f3432af`](https://github.com/dominikkarall/fhempy/commit/f3432af9b8bbfa9708747680b91adac1eaf6a0b7))

## v0.1.314 (2022-05-07)
### Fix
* **fusionsolar:** Fix define ([`f421b51`](https://github.com/dominikkarall/fhempy/commit/f421b51e741e7e042e4dd38906c515ad7fd56191))

## v0.1.313 (2022-05-07)
### Feature
* **fusionsolar:** BREAKING: no more kiosk mode, all values are taken from REST API. See README for details ([`221e88c`](https://github.com/dominikkarall/fhempy/commit/221e88c67bc6697c4a1f45144a321467b4ca7912))

## v0.1.312 (2022-05-07)
### Fix
* **fusionsolar:** Fix wrong default region ([`bea81bf`](https://github.com/dominikkarall/fhempy/commit/bea81bf0ea2f84871b34ee1af9aadad8321fc9a6))

## v0.1.311 (2022-05-07)
### Fix
* **fusionsolar:** Fix from/to_grid_power ([`fe7bea1`](https://github.com/dominikkarall/fhempy/commit/fe7bea111b286e6c3cf8287cbe09f51c9c8ae456))

## v0.1.310 (2022-05-07)
### Feature
* **fusionsolar:** Support from/to_grid, electrical_load, grid_power and inverter_output_power ([`3c73b83`](https://github.com/dominikkarall/fhempy/commit/3c73b8312ae71d9fa74e23d7d9299e40ece61951))

## v0.1.309 (2022-05-06)
### Fix
* **fhempy:** Fix task exception handling ([`81225c1`](https://github.com/dominikkarall/fhempy/commit/81225c12840754ea691b7d9624c1fd3446babd89))

## v0.1.308 (2022-05-06)
### Fix
* **fhempy:** Handle exceptions in asyncio tasks ([`6708650`](https://github.com/dominikkarall/fhempy/commit/670865014807e9aceb636b03f81106fca466ba88))
* **tuya:** Remove unused function ([`3b8b785`](https://github.com/dominikkarall/fhempy/commit/3b8b785d459a815bc9890227a572f554857b8a3a))

## v0.1.307 (2022-05-05)
### Fix
* **tuya:** Get info before connection setup ([`fd5edcc`](https://github.com/dominikkarall/fhempy/commit/fd5edcc20ff04ee7cf7c3f6523168cb7372b0453))

## v0.1.306 (2022-05-03)
### Fix
* **tuya:** Handle exception ([`0b3c77b`](https://github.com/dominikkarall/fhempy/commit/0b3c77b29caf58aa18257e763664237cac9a36f8))

## v0.1.305 (2022-05-02)
### Feature
* **tuya:** Try to support water leak sensor ([`b3229d6`](https://github.com/dominikkarall/fhempy/commit/b3229d6790cfcb73be963490d2f641c374bc02d0))

## v0.1.304 (2022-05-01)
### Fix
* **nespresso_ble:** Remove unused requirement ([`889e582`](https://github.com/dominikkarall/fhempy/commit/889e582813c225f481db4fbfc5110f263e57cbc3))

## v0.1.303 (2022-05-01)
### Fix
* **fhempy:** Remove Python 3.7 test ([`d1c2b7b`](https://github.com/dominikkarall/fhempy/commit/d1c2b7b2438c4429d05b4c329d8c8c3440f48ad8))

## v0.1.302 (2022-05-01)
### Fix
* **rct_power:** Fix commands ([`4efb800`](https://github.com/dominikkarall/fhempy/commit/4efb8002ab923878c761aabf65e95263c7a44d77))

## v0.1.301 (2022-05-01)
### Fix
* **rct_power:** Fix commands ([`5753a35`](https://github.com/dominikkarall/fhempy/commit/5753a35bc2f67bcb58af0ae6cf8fd0dde570bc97))
* **rct_power:** Fix commands ([#75](https://github.com/dominikkarall/fhempy/issues/75)) ([`4dbe2f7`](https://github.com/dominikkarall/fhempy/commit/4dbe2f765040f42e5056c0984b5b8175fb028c8c))

## v0.1.300 (2022-05-01)
### Fix
* **rct_power:** Fix commands ([#76](https://github.com/dominikkarall/fhempy/issues/76)) ([`bf88baa`](https://github.com/dominikkarall/fhempy/commit/bf88baaed7f13a63956baa3e68e7bf91e3e83c36))

## v0.1.299 (2022-05-01)
### Fix
* **tuya:** Optimize define runtime ([`2109d7a`](https://github.com/dominikkarall/fhempy/commit/2109d7a7273c1ba857b32ee50d5cf9b70b18a3fc))
* **gree_climate:** Fix missing off cmd ([`fdcb422`](https://github.com/dominikkarall/fhempy/commit/fdcb422e3c8e473596217ef5bd0656de7ec1521f))

## v0.1.298 (2022-05-01)
### Fix
* **tuya:** Update tuya cloud instructions ([`84dd50c`](https://github.com/dominikkarall/fhempy/commit/84dd50cce90cb990ac727459a5e263c74d26bd8b))
* **tuya_cloud:** Update README link ([`507ffb0`](https://github.com/dominikkarall/fhempy/commit/507ffb038daa1e033f2b80293a39dab40a5c8ddc))

## v0.1.297 (2022-04-29)
### Fix
* **gree_climate:** Fix usage ([`0023119`](https://github.com/dominikkarall/fhempy/commit/00231192441a53284e3789a9b540242c8753ee08))

## v0.1.296 (2022-04-29)
### Fix
* **gree_climate:** Fix set temperature ([`fcc825f`](https://github.com/dominikkarall/fhempy/commit/fcc825fe177f0bb35163d65473cb76ae32a7525d))
* **gree_climate:** Fix commands ([`1f2779a`](https://github.com/dominikkarall/fhempy/commit/1f2779a9e71954ddddfc53a75272398dcb5e91fd))
* **gree_climate:** Remove set cmds for scan device ([`45c2d2f`](https://github.com/dominikkarall/fhempy/commit/45c2d2fe1afa5953cb6d6eeb36c55e7cedb06240))

## v0.1.295 (2022-04-29)
### Fix
* **rct_power:** Remove slider ([#74](https://github.com/dominikkarall/fhempy/issues/74)) ([`e45006d`](https://github.com/dominikkarall/fhempy/commit/e45006d7d04fce3768a90830a83492e316ab758e))
* **gree_climate:** Fix function call on error ([`0bcedbe`](https://github.com/dominikkarall/fhempy/commit/0bcedbe75c8b0ab4f062edd2c2448b689826a4c9))

## v0.1.294 (2022-04-29)
### Feature
* **gree_climate:** Add to readme ([`7ed6b1e`](https://github.com/dominikkarall/fhempy/commit/7ed6b1eae89690f2576115c396eb4e8fb8ac70da))
* **gree_climate:** First release ([`c526e10`](https://github.com/dominikkarall/fhempy/commit/c526e10a6e38d07793ffc0d3584730c763528a1c))
* **rct_power:** Update help ([#73](https://github.com/dominikkarall/fhempy/issues/73)) ([`b67e0a6`](https://github.com/dominikkarall/fhempy/commit/b67e0a606a8abaacf19ac1c529ee23def8746fbd))

## v0.1.293 (2022-04-26)
### Fix
* **tuya:** Fix create device ([`6b4c524`](https://github.com/dominikkarall/fhempy/commit/6b4c5247dd052ba42f766268b92253c9d1d49561))

## v0.1.292 (2022-04-26)
### Fix
* **tuya:** Fix tests ([`fd7c390`](https://github.com/dominikkarall/fhempy/commit/fd7c390aece3c7477203c1e78d516a4680a7dbf4))

## v0.1.291 (2022-04-26)
### Feature
* **tuya:** Add info readings ([`f1817ad`](https://github.com/dominikkarall/fhempy/commit/f1817ada60d07a83f1274b38f240694298d929b4))

## v0.1.290 (2022-04-26)
### Fix
* **tuya:** Fix local scan ([`6a850d4`](https://github.com/dominikkarall/fhempy/commit/6a850d4ced3cb3bf573943e9269383ce930ce728))

## v0.1.289 (2022-04-26)
### Fix
* **gfprobt:** Deactivate not working adjust values ([`73c5aae`](https://github.com/dominikkarall/fhempy/commit/73c5aae511e5e28a4c250e0d45c074e6597ee92c))

## v0.1.288 (2022-04-26)
### Fix
* **tuya:** Fix local scan ([`eed15a2`](https://github.com/dominikkarall/fhempy/commit/eed15a2198e9c856a95dd052323438e031b401bc))

## v0.1.287 (2022-04-26)
### Fix
* **tuya:** Fix for existing mappings ([`1d5d301`](https://github.com/dominikkarall/fhempy/commit/1d5d301dd69d0cef8b7b84655d01dc325c161375))

## v0.1.286 (2022-04-26)
### Feature
* **tuya:** Support tuya local real-time updates ([`9104867`](https://github.com/dominikkarall/fhempy/commit/9104867f51edb1a22ec3d8d34ff0dda4fbabfaf6))

## v0.1.285 (2022-04-25)
### Feature
* **rct_power:** Further readings and commands ([#72](https://github.com/dominikkarall/fhempy/issues/72)) ([`85981f4`](https://github.com/dominikkarall/fhempy/commit/85981f430b18c7d2821861ce1af014a231c9002d))

### Fix
* **ring:** Change update order ([`75016f6`](https://github.com/dominikkarall/fhempy/commit/75016f6e263420eb9fb24e58bf529d638d2a05a7))
* **miio:** Support Tuple data type ([`3b8dce5`](https://github.com/dominikkarall/fhempy/commit/3b8dce51f65a6c0b9f47ea9397ec7ee81162ef65))
* **ring:** Show errors in state ([`32d2a4b`](https://github.com/dominikkarall/fhempy/commit/32d2a4b39de821895407157352e6cfb2a79c8ddf))

## v0.1.284 (2022-04-20)
### Feature
* **esphome:** Update to 2022.4.0 ([`59683c2`](https://github.com/dominikkarall/fhempy/commit/59683c2f7c0bc125334320ae0dfa8ae198cbafa7))

## v0.1.283 (2022-04-20)


## v0.1.282 (2022-04-20)


## v0.1.281 (2022-04-20)
### Fix
* **eq3bt:** Fix possible infinite loop ([`7c21c2a`](https://github.com/dominikkarall/fhempy/commit/7c21c2a49bb645a7071259799b22c4c85f96dae5))
* **discover_mdns:** Fix exception handling ([`f2bb640`](https://github.com/dominikkarall/fhempy/commit/f2bb6409005b3d7bac9ae6d2db05dbd3f9264ef3))
* **fhempy:** Fix exception handling ([`db7c74b`](https://github.com/dominikkarall/fhempy/commit/db7c74b9d9810d4ee3a9b9cdb0e2be4fb2318f59))
* **gfprobt:** Fix invalid type ([`93f2873`](https://github.com/dominikkarall/fhempy/commit/93f28736e577d69e489ce680904c0a596b7fe61f))

## v0.1.280 (2022-04-20)
### Feature
* **rct_power:** Update commands ([#71](https://github.com/dominikkarall/fhempy/issues/71)) ([`ee8ea0d`](https://github.com/dominikkarall/fhempy/commit/ee8ea0d5b8aa3622a9aec43f24090aef1fa48d27))
* **esphome:** Update to 2022.3.1 ([`3abba2f`](https://github.com/dominikkarall/fhempy/commit/3abba2f6b02c52a252b5705b6d0226a121c2e4cd))
* **gfprobt:** Prepare adjust ([`115fc60`](https://github.com/dominikkarall/fhempy/commit/115fc6060a78d3949dd2d5a022429b2dac0f1219))

### Fix
* **fhempy:** Code cleanup ([`9e123cf`](https://github.com/dominikkarall/fhempy/commit/9e123cfea795629f8e2c52a6e2e88a93bcb62c2b))
* **fhempy:** Code style fixes ([`23db77b`](https://github.com/dominikkarall/fhempy/commit/23db77bee65481d844c3fc6fcc66f8e43f1050c6))
* **helloworld:** Remove unused import ([`ebe9245`](https://github.com/dominikkarall/fhempy/commit/ebe92454e0658c8f420fa6f65c767a22486dc4cf))
* **gfprobt:** Prepare adjust ([`51cc4bb`](https://github.com/dominikkarall/fhempy/commit/51cc4bb5fd369d124a2a3c84ffe639b4a0bf5c8c))
* **nefit:** Fix Undefine ([`e9b0168`](https://github.com/dominikkarall/fhempy/commit/e9b016828cc5fb00254d538cc5a11fd2d9925c6d))

## v0.1.279 (2022-04-11)
### Fix
* **fhempy:** Cryptography 3.4.8 ([`0bf5665`](https://github.com/dominikkarall/fhempy/commit/0bf56652a74ad231c4c3b9cbb9b281f68971c44d))

## v0.1.278 (2022-04-10)


## v0.1.277 (2022-04-10)


## v0.1.276 (2022-04-10)
### Fix
* **ring:** Fix Undefine ([`56ceda2`](https://github.com/dominikkarall/fhempy/commit/56ceda2b38528f89bf63c649d7279e425ffa4b63))
* **ring:** Fix test ([`b637c09`](https://github.com/dominikkarall/fhempy/commit/b637c092e03f5b233f0b64c34d242c7d1729aa11))
* **fhempy:** Fix ssdp stop_search ([`5d998d6`](https://github.com/dominikkarall/fhempy/commit/5d998d65c39c7e262551255d88b67361e0ffb56e))

## v0.1.275 (2022-04-10)
### Feature
* **erelax_vaillant:** Use vaillant-netatmo-api ([`f138b6b`](https://github.com/dominikkarall/fhempy/commit/f138b6b1a9e852a70ba545a1afb5a11224c8842c))

## v0.1.274 (2022-04-10)
### Fix
* **fhempy:** Update cryptography ([`52afbf7`](https://github.com/dominikkarall/fhempy/commit/52afbf71510ad985d156d19941336319032c0fab))

## v0.1.273 (2022-04-10)
### Fix
* **ring:** Fix Undefine endless loop ([`e1ce34f`](https://github.com/dominikkarall/fhempy/commit/e1ce34fb1d20757ac4d4a4e4fe566ae0a20388fa))

## v0.1.272 (2022-04-10)
### Feature
* **xiaomi_gateway3:** Support ble smoke detector ([`3dee86f`](https://github.com/dominikkarall/fhempy/commit/3dee86f38fd2550fc0f30b88cccfbe8c79cfc832))
* **fhempy:** Support git+https requirements ([`7987489`](https://github.com/dominikkarall/fhempy/commit/7987489abbaf31cfc9b8bd2305609e4e460f39c7))

## v0.1.271 (2022-04-10)
### Fix
* **esphome:** Fix esphome start ([`e4c1697`](https://github.com/dominikkarall/fhempy/commit/e4c1697cc62aa4734c2ca5879a35207889e641e7))

## v0.1.270 (2022-03-09)
### Fix
* **fhempy:** Downgrade requests to fix errors ([`82a5eb5`](https://github.com/dominikkarall/fhempy/commit/82a5eb566601a1e18118914cf8c65fb5ab596027))

## v0.1.269 (2022-03-09)
### Fix
* **tuya_cloud:** Try to fix circular import ([`7187a88`](https://github.com/dominikkarall/fhempy/commit/7187a88bf401c531419cda3bbe2251f66ff783fa))

## v0.1.268 (2022-03-07)
### Fix
* **tuya_cloud:** Try to fix circular import ([`d5cf08f`](https://github.com/dominikkarall/fhempy/commit/d5cf08faeabee835432fec80c6eb2a4406caf8d3))

## v0.1.267 (2022-03-06)
### Fix
* **tuya_cloud:** Fix circular import ([`48b0d5d`](https://github.com/dominikkarall/fhempy/commit/48b0d5dfe7a48219af74d0379e1ce4d553b57523))

## v0.1.266 (2022-03-06)
### Feature
* **fhempy:** Add more info about peer ([`54c320d`](https://github.com/dominikkarall/fhempy/commit/54c320d050cb2ce200b39a405ac413350d28603c))

## v0.1.265 (2022-03-06)
### Fix
* **fhempy:** Fix restart ([`04ac131`](https://github.com/dominikkarall/fhempy/commit/04ac13107deda0eb044daba1dbf98ad2960b8dba))

## v0.1.264 (2022-03-05)
### Fix
* **fhempy:** Fix IODev missing when disconnected ([`9244dd3`](https://github.com/dominikkarall/fhempy/commit/9244dd366b137cb5270fe24eadf44b49b21b20a3))
* **fhempy:** Use fhempy instead of PythonModule ([`8d8abb4`](https://github.com/dominikkarall/fhempy/commit/8d8abb485286945156d60b77f6ee6f128ee0e46d))

## v0.1.263 (2022-03-05)
### Fix
* **fhempy:** Keep disconnected state for bindings ([`4f6621c`](https://github.com/dominikkarall/fhempy/commit/4f6621c2b38eeb5572bddb4cbf96549f4cbd8c8b))

## v0.1.262 (2022-03-05)
### Fix
* **fhempy:** Python reading font correction ([`3284f3c`](https://github.com/dominikkarall/fhempy/commit/3284f3c332bef010dd00dad409fe69c00e09a80e))

## v0.1.261 (2022-03-05)
### Fix
* **fhempy:** Fix startup ([`2145a4d`](https://github.com/dominikkarall/fhempy/commit/2145a4d5fc6fbc4731025625d1b081f389735842))

## v0.1.260 (2022-03-04)
### Fix
* **fhempy:** Fix sartup ([`5d23162`](https://github.com/dominikkarall/fhempy/commit/5d2316218912c8e51cbd970a0f3de3c13d85e255))

## v0.1.259 (2022-03-04)
### Fix
* **fhempy:** Fix reading ([`5bbba76`](https://github.com/dominikkarall/fhempy/commit/5bbba76743abe5ec6089fc603ed134001b4d8841))

## v0.1.258 (2022-03-04)
### Fix
* **fhempy:** Add python version check to perl code ([`2452f37`](https://github.com/dominikkarall/fhempy/commit/2452f37fa7a0312fb480d8b078dd06b22d6b1b02))

## v0.1.257 (2022-03-04)
### Fix
* **fhempy:** Fix installation errors ([`b3dfa34`](https://github.com/dominikkarall/fhempy/commit/b3dfa3446dceb2cce4d7be5a9c3c06d564f1b19e))

## v0.1.256 (2022-03-03)
### Feature
* **rct_power:** Support ext_power_reduction ([`3d72be9`](https://github.com/dominikkarall/fhempy/commit/3d72be98c9d6348413f32086aeea2c184b8516dc))

## v0.1.255 (2022-03-03)
### Fix
* **fhempy:** Fix python version error handling ([`f9c1d89`](https://github.com/dominikkarall/fhempy/commit/f9c1d899ac312d3e70a5c4d3dffa21124f91d407))

## v0.1.254 (2022-03-02)
### Fix
* **tuya_cloud:** Fix logging ([`f384975`](https://github.com/dominikkarall/fhempy/commit/f38497553e662633c139b7825fe3c047b0bf932f))

## v0.1.253 (2022-03-02)
### Feature
* **fhempy:** Support datetime for   readings ([`3a9cf74`](https://github.com/dominikkarall/fhempy/commit/3a9cf740b946d80bf9673a04d98c3ed21301bf03))

## v0.1.252 (2022-02-23)
### Fix
* **miio:** Fix error when no helptext available ([`e22c55c`](https://github.com/dominikkarall/fhempy/commit/e22c55cf8654791895f6b220b349f1044a9c008b))

## v0.1.251 (2022-02-22)
### Fix
* **ble_monitor:** Fix possible unregister error ([`264f1fb`](https://github.com/dominikkarall/fhempy/commit/264f1fb50f55fa0296d9aeca1fe45c385d952a11))

## v0.1.250 (2022-02-21)
### Feature
* **meross:** Support mod100 ([`6c0b7e2`](https://github.com/dominikkarall/fhempy/commit/6c0b7e2a94e29299d54104592d11acdad6c8fbcd))

## v0.1.249 (2022-02-21)
### Fix
* **zigbee2mqtt:** Fix restart ([`54545c2`](https://github.com/dominikkarall/fhempy/commit/54545c2b1935c7cc7f14ec9961188101fe540846))

## v0.1.248 (2022-02-20)
### Fix
* **fhempy:** Replace \n in help text ([`7a02515`](https://github.com/dominikkarall/fhempy/commit/7a02515a1f73b8a6e4aaca23baa05d08090b59a5))
* **miio:** Fixes for new library ([`edeab1f`](https://github.com/dominikkarall/fhempy/commit/edeab1f7ecc437fc017e474fb4304cf0f889d488))

## v0.1.247 (2022-02-20)
### Fix
* **miscale:** Fix missing method ([`dbb4c3a`](https://github.com/dominikkarall/fhempy/commit/dbb4c3a29b6faccf9466ed261e0a913bdef0f574))

## v0.1.246 (2022-02-19)
### Feature
* **rct_power:** Add min_soc_maint_charge ([`7695d8e`](https://github.com/dominikkarall/fhempy/commit/7695d8eb1129d0fe0ca505c62f9b28b79cdbf1f0))
* **ble_monitor:** Support encryption key attr ([`cdd1521`](https://github.com/dominikkarall/fhempy/commit/cdd1521c5fe0d6d23792c7b7283d2ecff0c1fdd9))

## v0.1.245 (2022-02-18)
### Fix
* **zigbee2mqtt:** Fix weblink ([`ca6c105`](https://github.com/dominikkarall/fhempy/commit/ca6c105ed6140a7d308a69c5f98cf29abd0996ec))

## v0.1.244 (2022-02-18)
### Feature
* **zigbee2mqtt:** First working release ([`8f9d26a`](https://github.com/dominikkarall/fhempy/commit/8f9d26a503966edef49950d62c2b26e3350fc531))

### Fix
* **seatconnect:** Fix Seatconnect Login ([#67](https://github.com/dominikkarall/fhempy/issues/67)) ([`d67cce0`](https://github.com/dominikkarall/fhempy/commit/d67cce057f73e6e91f731fc2196abc14d0e8feef))
* **zigbee2mqtt:** Fix restart ([`d36bea4`](https://github.com/dominikkarall/fhempy/commit/d36bea4249350ea493757406328602f1b8e7a400))

## v0.1.243 (2022-02-18)
### Feature
* **zigbee2mqtt:** First release ([`ac1cd73`](https://github.com/dominikkarall/fhempy/commit/ac1cd73555f2edf0b0d34baa68e77a545377aa42))
* **miio:** Update lib ([`828bcec`](https://github.com/dominikkarall/fhempy/commit/828bcec59e385d242cf1cf4c0c69c7e5dabcf44a))
* **zigbee2mqtt:** Prepare zigbee2mqtt ([`9810678`](https://github.com/dominikkarall/fhempy/commit/98106780b9699a7be17ba713b79e188402d94c55))

### Fix
* **ring:** Fix Undefine? ([`c6d9d6a`](https://github.com/dominikkarall/fhempy/commit/c6d9d6af60297eba29800ccb8ce1df5e6114b5b1))

## v0.1.242 (2022-02-16)
### Fix
* **xiaomi_gateway3:** Fix disable ([`16830d1`](https://github.com/dominikkarall/fhempy/commit/16830d1ae68a1da82cb1a7454d9bef6beb4c3947))

## v0.1.241 (2022-02-16)
### Fix
* **xiaomi_gateway3:** Fix disable ([`591612d`](https://github.com/dominikkarall/fhempy/commit/591612de340b4ed7e0162e441dddbc817dcb7086))

## v0.1.240 (2022-02-16)
### Fix
* **xiaomi_gateway3:** Support disable ([`1b2a59c`](https://github.com/dominikkarall/fhempy/commit/1b2a59c7488c7c3e0047e8a3b3a2433c94e81f16))

## v0.1.239 (2022-02-15)
### Feature
* **fhempy:** Add ble_monitor, miscale ([`819e678`](https://github.com/dominikkarall/fhempy/commit/819e6789a2d141287daa6f6a10b865013f27c5ce))
* **miscale:** Support miscale ([`b9dc4d6`](https://github.com/dominikkarall/fhempy/commit/b9dc4d698d9df2dc88e7fb888df3157ffd9d6509))

### Fix
* **miscale:** Working version ([`e30988a`](https://github.com/dominikkarall/fhempy/commit/e30988adc9e2e488617f93b2441bd9e3cfd38abe))
* **ble_monitor:** Working again ([`5399399`](https://github.com/dominikkarall/fhempy/commit/5399399b8ad45350d83a52dc74ef8343f6bbeba1))
* **miscale:** Fix usage ([`2492790`](https://github.com/dominikkarall/fhempy/commit/2492790f803f5455403048dd3cfa89e6a2deb1d5))
* **fhempy:** Fix readme processing ([`df9d48d`](https://github.com/dominikkarall/fhempy/commit/df9d48d1055562627c2492335ce28bba73abcad3))
* **ble_monitor:** Update readme ([`dc82d3d`](https://github.com/dominikkarall/fhempy/commit/dc82d3d9d9e88ec1286cdbb4ba1d4ad0ae6be025))
* **ble_monitor:** Remove unneeded function ([`206d62e`](https://github.com/dominikkarall/fhempy/commit/206d62ec888b15564750908b029ca52ac426cbc4))
* **ble_monitor:** Support more devs with same mac ([`2c18861`](https://github.com/dominikkarall/fhempy/commit/2c18861934fa83908bbefae0901922a98899ffe5))
* **ble_monitor:** Make it working ([`dec3186`](https://github.com/dominikkarall/fhempy/commit/dec31860d40b545cb3b6ad328c08e0344e858d44))
* **ble_monitor:** Code structure changes ([`aa6e14f`](https://github.com/dominikkarall/fhempy/commit/aa6e14f4b673d98b998df761678e3cfa995eb0da))

## v0.1.238 (2022-02-14)
### Feature
* **ble_monitor:** First working release ([`24eb78e`](https://github.com/dominikkarall/fhempy/commit/24eb78e3328bea123a1c17c75d404373ef526a9a))
* **rct_power:** Support max_power_ac ([`f4f6d8c`](https://github.com/dominikkarall/fhempy/commit/f4f6d8c89792ed3c4e8e2b84a0dc4d92f0a1081f))

### Fix
* **ble_monitor:** Fix codestyle ([`9c8e691`](https://github.com/dominikkarall/fhempy/commit/9c8e6919fbbe8e8aa0e811ca28d160e9ba4a664c))
* **fhempy:** Do not call set_attr on define ([`f32f12f`](https://github.com/dominikkarall/fhempy/commit/f32f12ff173b410492c4184b48085373046163e1))
* **fhempy:** Fix port parameter ([`1f55020`](https://github.com/dominikkarall/fhempy/commit/1f5502006678b2161fd6ee7393541bd5a3f91a88))
* **fhempy:** Fix quotes ([`934a344`](https://github.com/dominikkarall/fhempy/commit/934a344d5cfc10479799e73434bf6bf8440be466))

## v0.1.237 (2022-02-13)
### Feature
* **ble_monitor:** Prepare ble_monitor ([`c6098fa`](https://github.com/dominikkarall/fhempy/commit/c6098faf16fe140631c470a1e72d3def6eeae07d))

## v0.1.236 (2022-02-13)
### Fix
* **fusionsolar:** Fix usage ([`76e4858`](https://github.com/dominikkarall/fhempy/commit/76e485828b35179dd5bd8de11700c7e2e3e806c0))

## v0.1.235 (2022-02-13)
### Feature
* **fhempy:** Add fusionsolar ([`a449c5e`](https://github.com/dominikkarall/fhempy/commit/a449c5e22b632f8a486a9d17a7e5dc8c7707cda6))
* **rct_power:** Support max_(dis)charge_current ([`0612cae`](https://github.com/dominikkarall/fhempy/commit/0612cae475e10e54da7f428cd14f104fcc267e47))
* **fusionsolar:** Get data from fusionsolar kiosk ([`85f1a1f`](https://github.com/dominikkarall/fhempy/commit/85f1a1fc3dc98c21ecaca66a70ef5950531b8266))
* **fhempy:** No more BETA ([`bac69fc`](https://github.com/dominikkarall/fhempy/commit/bac69fc659dbcc5224d907d867bc5d7424eae278))

## v0.1.198 (2022-02-13)


## v0.1.197 (2022-02-13)
### Feature
* **fhempy:** Add fusionsolar ([`a449c5e`](https://github.com/dominikkarall/fhempy/commit/a449c5e22b632f8a486a9d17a7e5dc8c7707cda6))

## v0.1.196 (2022-02-13)
### Feature
* **rct_power:** Support disable/update_readings ([`f511879`](https://github.com/dominikkarall/fhempy/commit/f51187962b5357406e97fabe24e7203d85faaa2f))
* **rct_power:** Further set functions ([`27812d0`](https://github.com/dominikkarall/fhempy/commit/27812d066ee58689aab681b066180705f5805b5d))
* **rct_power:** Support display brightness ([`533954a`](https://github.com/dominikkarall/fhempy/commit/533954ac61b9fa84ce07a1edc692c712ff3d2a70))
* **rct_power:** Attr error_reading, default_... ([`584e849`](https://github.com/dominikkarall/fhempy/commit/584e8495ae323e4f71d2d4db9e4ac4af98bc000a))
* **rct_power:** Add format, add error reading ([`0772e76`](https://github.com/dominikkarall/fhempy/commit/0772e7693cefb66f84bc90b9a633b8cd11f22f56))
* **rct_power:** New attributes ([`0651dc5`](https://github.com/dominikkarall/fhempy/commit/0651dc5dbe48e3ecaf8454a20ad357ecac61be35))
* **rct_power:** Support RCT Power inverter ([`76f316f`](https://github.com/dominikkarall/fhempy/commit/76f316fd280a3209c44e0f6fc91a21bb8f206079))
* **tuya_cloud:** Add tuya open pulsar messaging ([`2c49000`](https://github.com/dominikkarall/fhempy/commit/2c4900090738a80113512877a3a65172246514cb))
* **xiaomi_gateway3:** Support BT smoke alarm ([`983fe78`](https://github.com/dominikkarall/fhempy/commit/983fe78877eefa9232091273276a127776bd143b))
* **xiaomi_gateway3:** Support 1371 sensor ([`3c04477`](https://github.com/dominikkarall/fhempy/commit/3c044779f1ccf3d7fafcd7fcdc238425169c90f1))
* **meross:** Support roller shutter ([`eba7e27`](https://github.com/dominikkarall/fhempy/commit/eba7e2744e80549dd2efd5c733f17222481527b1))
* **eq3bt:** Support max_retries attr ([`b483878`](https://github.com/dominikkarall/fhempy/commit/b483878b89e05fe78df9db4df4cbe2498468799c))
* **pyit600:** Additional attributes added ([#59](https://github.com/dominikkarall/fhempy/issues/59)) ([`1753761`](https://github.com/dominikkarall/fhempy/commit/1753761290a41ba11e8959e6010a879554e8b0c9))
* **nefit:** Support system pressure ([`c90669e`](https://github.com/dominikkarall/fhempy/commit/c90669e3e1a053691eca2356c22fac30bc7a1ce6))
* **nefit:** Support dayassunday set functions ([`0ed99f2`](https://github.com/dominikkarall/fhempy/commit/0ed99f2ddb49d03bf1112efa50684d01c6e2afea))
* **nefit:** Retrieve dayassunday ([`8462ba4`](https://github.com/dominikkarall/fhempy/commit/8462ba421fc30c793b178d4f7b0ea7509f794dbf))
* **nefit:** Add outdoor temperature ([`ecaadb1`](https://github.com/dominikkarall/fhempy/commit/ecaadb159dad75b96ea13d1149ca893b588af922))

### Fix
* **rct_power:** Use textfield for set *_soc_target ([`ba9a923`](https://github.com/dominikkarall/fhempy/commit/ba9a92370159b35c33f87778c977173a5915f941))
* **rct_power:** Fix set *_soc_target ([`f867b78`](https://github.com/dominikkarall/fhempy/commit/f867b7882ea37441e91ee0ace3760e3f74720946))
* **meross:** Remove stopped state ([`450fbf4`](https://github.com/dominikkarall/fhempy/commit/450fbf4ec7d412a08e86c8173ce0933212fdd945))
* **skodaconnect:** Fix login ([`d3a92df`](https://github.com/dominikkarall/fhempy/commit/d3a92df885c40d5a500bfc640cef191c5e2a6124))
* **rct_power:** Fix display_brightness ([`89c8d92`](https://github.com/dominikkarall/fhempy/commit/89c8d92b3ce3e1db89cd909d1a97fc3b6a918e1d))
* **rct_power:** Fix function call ([`995c6ba`](https://github.com/dominikkarall/fhempy/commit/995c6ba5d9ab78c906ff2c7d320e46ea122f1b73))
* **fhempy:** Fix naming ([`b9c9cf1`](https://github.com/dominikkarall/fhempy/commit/b9c9cf1fa3562fe24d8c4601a9520c565f1bb09c))
* **rct_power:** Support json/array format ([`c282ac9`](https://github.com/dominikkarall/fhempy/commit/c282ac979ee79e53a08593b169619b046b86f362))
* **rct_power:** Change interval to 10s, fix state ([`72dced8`](https://github.com/dominikkarall/fhempy/commit/72dced8eb70b4082a317254b9be6eac35d608c2e))
* **tuya_cloud:** Add pulsar activation error msg ([`faab929`](https://github.com/dominikkarall/fhempy/commit/faab92932949a2eea85414704397d50aa8270e4b))
* **skodaconnect:** Update Base Lib ([#65](https://github.com/dominikkarall/fhempy/issues/65)) ([`7ef4a13`](https://github.com/dominikkarall/fhempy/commit/7ef4a13358312ef14f764d5f81e754fc47732dcf))
* **xiaomi_gateway3:** Fix dict changed during iter ([`8c5bd74`](https://github.com/dominikkarall/fhempy/commit/8c5bd74e3262d60b9afbe3af472c1b3944c92d54))
* **fhempy:** Fix utf8 issues ([`36383c5`](https://github.com/dominikkarall/fhempy/commit/36383c5141a7ed48e386c73dfac9074bb1b3d28d))
* **xiaomi_gateway3:** Fix BT devices ([`81f8aea`](https://github.com/dominikkarall/fhempy/commit/81f8aea5ffc16f55a239a3579c15ca5b1fc9b547))
* **ring:** Fix circular import? ([`a061667`](https://github.com/dominikkarall/fhempy/commit/a061667c55ec1e58d57ef0bd2ed6452a2acf0c0c))
* **meross:** Fix stop ([`b22b7a0`](https://github.com/dominikkarall/fhempy/commit/b22b7a0d232b0312aeb8eb62974f0dfdcd020fe6))
* **helloworld:** Add README ([`7f12567`](https://github.com/dominikkarall/fhempy/commit/7f12567ab7a5e84adeab4dfb5395e76bdc38011f))
* **xiaomi_gateway3:** Fix BT devices ([`be7b30d`](https://github.com/dominikkarall/fhempy/commit/be7b30d6117c77b0c8e9d6fcfce995d7a619bfca))
* **fhempy:** Change fhempy_remote to _peer ([`570afc8`](https://github.com/dominikkarall/fhempy/commit/570afc8d469e2e498b1320928f359fa52628d2db))
* **xiaomi_gateway3:** Fix ble devices ([`3c100d9`](https://github.com/dominikkarall/fhempy/commit/3c100d990ae16ddd2af94508c89545dd735414a7))
* **fhempy:** Fix fhempy_log error msg ([`da0f71c`](https://github.com/dominikkarall/fhempy/commit/da0f71c9d1230c4cc83980711797f42a6d84a3ae))
* **nefit:** Change default interval to 900s ([`48a69e8`](https://github.com/dominikkarall/fhempy/commit/48a69e8cd819fe443a7e5ff2ef5e432e8972827f))
* **skodaconnect:** Update Base Lib ([#64](https://github.com/dominikkarall/fhempy/issues/64)) ([`c1eefd4`](https://github.com/dominikkarall/fhempy/commit/c1eefd4dd91c5563453b14469b2a41777208afda))
* **nefit:** Fix system_pressure ([`1804780`](https://github.com/dominikkarall/fhempy/commit/1804780e585ca796277346d57da87810f9ec1349))
* **skodaconnect:** Update manifest.json ([#60](https://github.com/dominikkarall/fhempy/issues/60)) ([`df00380`](https://github.com/dominikkarall/fhempy/commit/df0038006fece2eee2ff176255d1113a09037633))
* **nefit:** Update dayassunday readings asap ([`9f55182`](https://github.com/dominikkarall/fhempy/commit/9f55182cd8231bf397d824b43cfeff0b36ab6111))
* **nefit:** Fix again tomorrow/todayAsSunday ([`6449ad2`](https://github.com/dominikkarall/fhempy/commit/6449ad21485ce005e34d88853b2b71c44192d28e))
* **nefit:** Fix today/tomorrowAsSunday ([`ff11294`](https://github.com/dominikkarall/fhempy/commit/ff1129413f761ee9d9badff2d5080ac525c8e469))
* **fhempy:** Remove sentry as I'm not using it ([`0fefcf0`](https://github.com/dominikkarall/fhempy/commit/0fefcf0dfd67d94f20678cf50dee8f9847233b86))
* **nefit:** Fix retrieve dayassunday ([`c78e836`](https://github.com/dominikkarall/fhempy/commit/c78e836598aabf7289213200ce12aad3843e2423))
* **nefix:** Readme fixes ([`7f698e8`](https://github.com/dominikkarall/fhempy/commit/7f698e898a7281f3a789ac54284c44261c86fb9f))
* **fhempy:** Use markdown2 instead of markdown ([`f2403e6`](https://github.com/dominikkarall/fhempy/commit/f2403e6457e860afc4b69485e48caf90a0a8c24a))
* **nefit:** Fix umlaut issue ([`76710bf`](https://github.com/dominikkarall/fhempy/commit/76710bf279eef26303edff96f7cce3de968c5983))
* **nefit:** Fix consumption again ([`def458c`](https://github.com/dominikkarall/fhempy/commit/def458c970e5deae0e60b237a973e3cdcfb93338))
* **nefit:** Fix consumption ([`11ce422`](https://github.com/dominikkarall/fhempy/commit/11ce4222a7c9ddbf214eca26a5fdec6b03bea882))
* **nefit:** Fix some readings ([`e4613f9`](https://github.com/dominikkarall/fhempy/commit/e4613f909156015c190d2d39603f241e4d2769b3))
* **pyit600:** Usage description updated ([#58](https://github.com/dominikkarall/fhempy/issues/58)) ([`9ce8405`](https://github.com/dominikkarall/fhempy/commit/9ce84058d648878e06cb720d1abdfc505124d388))
* **nefit:** Fix reconnect, rename readings ([`0705e8d`](https://github.com/dominikkarall/fhempy/commit/0705e8d44ab84743cb99b05ca8252a5a2e0e31e4))
* **pyit600:** Minor fixes ([#56](https://github.com/dominikkarall/fhempy/issues/56)) ([`3bdbaff`](https://github.com/dominikkarall/fhempy/commit/3bdbaff9f374b4ab7b5fae250b76921b8ea2a98a))

## v0.1.234 (2022-02-13)
### Fix
* **rct_power:** Use textfield for set *_soc_target ([`ba9a923`](https://github.com/dominikkarall/fhempy/commit/ba9a92370159b35c33f87778c977173a5915f941))

## v0.1.233 (2022-02-13)
### Feature
* **rct_power:** Support disable/update_readings ([`f511879`](https://github.com/dominikkarall/fhempy/commit/f51187962b5357406e97fabe24e7203d85faaa2f))

## v0.1.232 (2022-02-12)
### Fix
* **rct_power:** Fix set *_soc_target ([`f867b78`](https://github.com/dominikkarall/fhempy/commit/f867b7882ea37441e91ee0ace3760e3f74720946))
* **meross:** Remove stopped state ([`450fbf4`](https://github.com/dominikkarall/fhempy/commit/450fbf4ec7d412a08e86c8173ce0933212fdd945))

## v0.1.231 (2022-02-12)
### Feature
* **rct_power:** Further set functions ([`27812d0`](https://github.com/dominikkarall/fhempy/commit/27812d066ee58689aab681b066180705f5805b5d))

## v0.1.230 (2022-02-12)
### Fix
* **skodaconnect:** Fix login ([`d3a92df`](https://github.com/dominikkarall/fhempy/commit/d3a92df885c40d5a500bfc640cef191c5e2a6124))

## v0.1.229 (2022-02-12)
### Fix
* **rct_power:** Fix display_brightness ([`89c8d92`](https://github.com/dominikkarall/fhempy/commit/89c8d92b3ce3e1db89cd909d1a97fc3b6a918e1d))

## v0.1.228 (2022-02-12)
### Fix
* **rct_power:** Fix function call ([`995c6ba`](https://github.com/dominikkarall/fhempy/commit/995c6ba5d9ab78c906ff2c7d320e46ea122f1b73))

## v0.1.227 (2022-02-12)
### Feature
* **rct_power:** Support display brightness ([`533954a`](https://github.com/dominikkarall/fhempy/commit/533954ac61b9fa84ce07a1edc692c712ff3d2a70))

## v0.1.226 (2022-02-11)
### Feature
* **rct_power:** Attr error_reading, default_... ([`584e849`](https://github.com/dominikkarall/fhempy/commit/584e8495ae323e4f71d2d4db9e4ac4af98bc000a))
* **rct_power:** Add format, add error reading ([`0772e76`](https://github.com/dominikkarall/fhempy/commit/0772e7693cefb66f84bc90b9a633b8cd11f22f56))

### Fix
* **fhempy:** Fix naming ([`b9c9cf1`](https://github.com/dominikkarall/fhempy/commit/b9c9cf1fa3562fe24d8c4601a9520c565f1bb09c))

## v0.1.225 (2022-02-11)
### Fix
* **rct_power:** Support json/array format ([`c282ac9`](https://github.com/dominikkarall/fhempy/commit/c282ac979ee79e53a08593b169619b046b86f362))

## v0.1.224 (2022-02-10)
### Feature
* **rct_power:** New attributes ([`0651dc5`](https://github.com/dominikkarall/fhempy/commit/0651dc5dbe48e3ecaf8454a20ad357ecac61be35))

## v0.1.223 (2022-02-10)
### Fix
* **rct_power:** Change interval to 10s, fix state ([`72dced8`](https://github.com/dominikkarall/fhempy/commit/72dced8eb70b4082a317254b9be6eac35d608c2e))

## v0.1.222 (2022-02-09)
### Feature
* **rct_power:** Support RCT Power inverter ([`76f316f`](https://github.com/dominikkarall/fhempy/commit/76f316fd280a3209c44e0f6fc91a21bb8f206079))

## v0.1.221 (2022-02-09)
### Fix
* **tuya_cloud:** Add pulsar activation error msg ([`faab929`](https://github.com/dominikkarall/fhempy/commit/faab92932949a2eea85414704397d50aa8270e4b))

## v0.1.220 (2022-02-08)
### Fix
* **skodaconnect:** Update Base Lib ([#65](https://github.com/dominikkarall/fhempy/issues/65)) ([`7ef4a13`](https://github.com/dominikkarall/fhempy/commit/7ef4a13358312ef14f764d5f81e754fc47732dcf))

## v0.1.219 (2022-02-08)
### Feature
* **tuya_cloud:** Add tuya open pulsar messaging ([`2c49000`](https://github.com/dominikkarall/fhempy/commit/2c4900090738a80113512877a3a65172246514cb))

### Fix
* **xiaomi_gateway3:** Fix dict changed during iter ([`8c5bd74`](https://github.com/dominikkarall/fhempy/commit/8c5bd74e3262d60b9afbe3af472c1b3944c92d54))
* **fhempy:** Fix utf8 issues ([`36383c5`](https://github.com/dominikkarall/fhempy/commit/36383c5141a7ed48e386c73dfac9074bb1b3d28d))

## v0.1.218 (2022-02-07)
### Fix
* **xiaomi_gateway3:** Fix BT devices ([`81f8aea`](https://github.com/dominikkarall/fhempy/commit/81f8aea5ffc16f55a239a3579c15ca5b1fc9b547))
* **ring:** Fix circular import? ([`a061667`](https://github.com/dominikkarall/fhempy/commit/a061667c55ec1e58d57ef0bd2ed6452a2acf0c0c))
* **meross:** Fix stop ([`b22b7a0`](https://github.com/dominikkarall/fhempy/commit/b22b7a0d232b0312aeb8eb62974f0dfdcd020fe6))
* **helloworld:** Add README ([`7f12567`](https://github.com/dominikkarall/fhempy/commit/7f12567ab7a5e84adeab4dfb5395e76bdc38011f))

## v0.1.217 (2022-02-06)
### Fix
* **xiaomi_gateway3:** Fix BT devices ([`be7b30d`](https://github.com/dominikkarall/fhempy/commit/be7b30d6117c77b0c8e9d6fcfce995d7a619bfca))

## v0.1.216 (2022-02-06)
### Feature
* **xiaomi_gateway3:** Support BT smoke alarm ([`983fe78`](https://github.com/dominikkarall/fhempy/commit/983fe78877eefa9232091273276a127776bd143b))

## v0.1.215 (2022-02-06)
### Feature
* **xiaomi_gateway3:** Support 1371 sensor ([`3c04477`](https://github.com/dominikkarall/fhempy/commit/3c044779f1ccf3d7fafcd7fcdc238425169c90f1))

### Fix
* **fhempy:** Change fhempy_remote to _peer ([`570afc8`](https://github.com/dominikkarall/fhempy/commit/570afc8d469e2e498b1320928f359fa52628d2db))

## v0.1.214 (2022-02-06)
### Feature
* **meross:** Support roller shutter ([`eba7e27`](https://github.com/dominikkarall/fhempy/commit/eba7e2744e80549dd2efd5c733f17222481527b1))

## v0.1.213 (2022-02-06)
### Fix
* **xiaomi_gateway3:** Fix ble devices ([`3c100d9`](https://github.com/dominikkarall/fhempy/commit/3c100d990ae16ddd2af94508c89545dd735414a7))
* **fhempy:** Fix fhempy_log error msg ([`da0f71c`](https://github.com/dominikkarall/fhempy/commit/da0f71c9d1230c4cc83980711797f42a6d84a3ae))

## v0.1.212 (2022-02-06)
### Feature
* **eq3bt:** Support max_retries attr ([`b483878`](https://github.com/dominikkarall/fhempy/commit/b483878b89e05fe78df9db4df4cbe2498468799c))

## v0.1.211 (2022-02-04)
### Fix
* **nefit:** Change default interval to 900s ([`48a69e8`](https://github.com/dominikkarall/fhempy/commit/48a69e8cd819fe443a7e5ff2ef5e432e8972827f))
* **skodaconnect:** Update Base Lib ([#64](https://github.com/dominikkarall/fhempy/issues/64)) ([`c1eefd4`](https://github.com/dominikkarall/fhempy/commit/c1eefd4dd91c5563453b14469b2a41777208afda))

## v0.1.210 (2022-02-01)
### Feature
* **pyit600:** Additional attributes added ([#59](https://github.com/dominikkarall/fhempy/issues/59)) ([`1753761`](https://github.com/dominikkarall/fhempy/commit/1753761290a41ba11e8959e6010a879554e8b0c9))

### Fix
* **nefit:** Fix system_pressure ([`1804780`](https://github.com/dominikkarall/fhempy/commit/1804780e585ca796277346d57da87810f9ec1349))
* **skodaconnect:** Update manifest.json ([#60](https://github.com/dominikkarall/fhempy/issues/60)) ([`df00380`](https://github.com/dominikkarall/fhempy/commit/df0038006fece2eee2ff176255d1113a09037633))

## v0.1.209 (2022-01-23)
### Feature
* **nefit:** Support system pressure ([`c90669e`](https://github.com/dominikkarall/fhempy/commit/c90669e3e1a053691eca2356c22fac30bc7a1ce6))

## v0.1.208 (2022-01-23)
### Fix
* **nefit:** Update dayassunday readings asap ([`9f55182`](https://github.com/dominikkarall/fhempy/commit/9f55182cd8231bf397d824b43cfeff0b36ab6111))

## v0.1.207 (2022-01-23)
### Fix
* **nefit:** Fix again tomorrow/todayAsSunday ([`6449ad2`](https://github.com/dominikkarall/fhempy/commit/6449ad21485ce005e34d88853b2b71c44192d28e))

## v0.1.206 (2022-01-23)
### Fix
* **nefit:** Fix today/tomorrowAsSunday ([`ff11294`](https://github.com/dominikkarall/fhempy/commit/ff1129413f761ee9d9badff2d5080ac525c8e469))

## v0.1.205 (2022-01-23)
### Feature
* **nefit:** Support dayassunday set functions ([`0ed99f2`](https://github.com/dominikkarall/fhempy/commit/0ed99f2ddb49d03bf1112efa50684d01c6e2afea))

### Fix
* **fhempy:** Remove sentry as I'm not using it ([`0fefcf0`](https://github.com/dominikkarall/fhempy/commit/0fefcf0dfd67d94f20678cf50dee8f9847233b86))

## v0.1.204 (2022-01-22)
### Fix
* **nefit:** Fix retrieve dayassunday ([`c78e836`](https://github.com/dominikkarall/fhempy/commit/c78e836598aabf7289213200ce12aad3843e2423))

## v0.1.203 (2022-01-22)
### Feature
* **nefit:** Retrieve dayassunday ([`8462ba4`](https://github.com/dominikkarall/fhempy/commit/8462ba421fc30c793b178d4f7b0ea7509f794dbf))

### Fix
* **nefix:** Readme fixes ([`7f698e8`](https://github.com/dominikkarall/fhempy/commit/7f698e898a7281f3a789ac54284c44261c86fb9f))

## v0.1.202 (2022-01-22)
### Fix
* **fhempy:** Use markdown2 instead of markdown ([`f2403e6`](https://github.com/dominikkarall/fhempy/commit/f2403e6457e860afc4b69485e48caf90a0a8c24a))

## v0.1.201 (2022-01-22)
### Fix
* **nefit:** Fix umlaut issue ([`76710bf`](https://github.com/dominikkarall/fhempy/commit/76710bf279eef26303edff96f7cce3de968c5983))

## v0.1.200 (2022-01-22)
### Fix
* **nefit:** Fix consumption again ([`def458c`](https://github.com/dominikkarall/fhempy/commit/def458c970e5deae0e60b237a973e3cdcfb93338))

## v0.1.199 (2022-01-22)
### Fix
* **nefit:** Fix consumption ([`11ce422`](https://github.com/dominikkarall/fhempy/commit/11ce4222a7c9ddbf214eca26a5fdec6b03bea882))

## v0.1.198 (2022-01-22)
### Fix
* **nefit:** Fix some readings ([`e4613f9`](https://github.com/dominikkarall/fhempy/commit/e4613f909156015c190d2d39603f241e4d2769b3))
* **pyit600:** Usage description updated ([#58](https://github.com/dominikkarall/fhempy/issues/58)) ([`9ce8405`](https://github.com/dominikkarall/fhempy/commit/9ce84058d648878e06cb720d1abdfc505124d388))

## v0.1.197 (2022-01-15)
### Fix
* **pyit600:** Minor fixes ([#56](https://github.com/dominikkarall/fhempy/issues/56)) ([`3bdbaff`](https://github.com/dominikkarall/fhempy/commit/3bdbaff9f374b4ab7b5fae250b76921b8ea2a98a))

## v0.1.196 (2022-01-15)
### Feature
* **nefit:** Add outdoor temperature ([`ecaadb1`](https://github.com/dominikkarall/fhempy/commit/ecaadb159dad75b96ea13d1149ca893b588af922))

### Fix
* **nefit:** Fix reconnect, rename readings ([`0705e8d`](https://github.com/dominikkarall/fhempy/commit/0705e8d44ab84743cb99b05ca8252a5a2e0e31e4))

## v0.1.195 (2022-01-08)
### Feature
* **nefit:** Support nefit devices ([`ea41aa8`](https://github.com/fhempy/fhempy/commit/ea41aa8d608e19a11c61fafae0c708f9fb7df140))

## v0.1.194 (2022-01-08)


## v0.1.193 (2022-01-07)


## v0.1.192 (2022-01-03)
### Fix
* **tuya_cloud:** Restart mqtt loop deactivated ([`3cbad93`](https://github.com/fhempy/fhempy/commit/3cbad9381002299d3b64f51887838e92dc9fb4fd))

## v0.1.191 (2022-01-03)
### Fix
* **xiaomi_tokens:** Fix for de server ([`63c6c4b`](https://github.com/fhempy/fhempy/commit/63c6c4b458f2432cef97dade4d490f2cc0be7369))

## v0.1.190 (2021-12-26)
### Fix
* **tuya_cloud:** Fix lib usage ([`9b2dccf`](https://github.com/fhempy/fhempy/commit/9b2dccfc4469b0f186d3097b2f4aa1a3898ff058))

## v0.1.189 (2021-12-26)
### Fix
* **tuya_cloud:** Update lib, python>3.7 required!! ([`ea69096`](https://github.com/fhempy/fhempy/commit/ea690962be90d0c8713b503008ea52d8d4fe338d))

## v0.1.188 (2021-12-19)
### Feature
* **esphome:** Attr port_dashboard ([`c52fa7a`](https://github.com/fhempy/fhempy/commit/c52fa7aa7f50bf195803c4b81435832c391c9d7c))

### Fix
* **fhempy:** Remove temporary for log ([`957a14b`](https://github.com/fhempy/fhempy/commit/957a14b92368af0b8a329bb2fc601eff98518a38))

## v0.1.187 (2021-12-05)
### Fix
* **fhempy:** Fix CoProcess error ([`397edde`](https://github.com/fhempy/fhempy/commit/397edde0b39d52b0175454c2fd071b5ce8b2e973))

## v0.1.186 (2021-12-05)
### Feature
* **fhempy:** Support "all" notification in ble ([`ea1f5eb`](https://github.com/fhempy/fhempy/commit/ea1f5ebb0d40f5b3efdde39e04d38fd1350a8302))

### Fix
* **mitemp2:** Try to fix mitemp2 ([`ba558c0`](https://github.com/fhempy/fhempy/commit/ba558c07a56841c998166709447902e6fb671fa7))

## v0.1.185 (2021-12-03)
### Fix
* **eq3bt:** WindowOpenTemp starts at 5 degrees ([`3ef7e36`](https://github.com/fhempy/fhempy/commit/3ef7e36bdfe2b90cd5f9780ac390decb5d0a3775))

## v0.1.184 (2021-12-01)
### Fix
* **eq3bt:** Fix windowOpenTime/Temp ([`47ad1d2`](https://github.com/fhempy/fhempy/commit/47ad1d2c24fb50dba7f1f1ed09041eb4375ac56e))

## v0.1.183 (2021-11-30)
### Fix
* **tuya_cloud:** Fix AuthType ([`777edc0`](https://github.com/fhempy/fhempy/commit/777edc0327b71e424864f9478e0fbc2564ac51f2))

## v0.1.182 (2021-11-30)
### Fix
* **tuya_cloud:** Support python 3.7 again ([`b54b5b8`](https://github.com/fhempy/fhempy/commit/b54b5b82683d177691df0a7c0c3bb85ab9670f38))
* **fhempy:** Clarify peer installation ([`9d9a5d3`](https://github.com/fhempy/fhempy/commit/9d9a5d3415afd500948f4043ae02847245998d8f))

## v0.1.181 (2021-11-29)
### Fix
* **tuya_cloud:** Remove update API calls ([`2aac25c`](https://github.com/fhempy/fhempy/commit/2aac25c2426850ee0fa3d419b5eff9e4474b150a))
* **googlecast:** Update lib to 10.1.1 ([`334d171`](https://github.com/fhempy/fhempy/commit/334d171f3ead33f6b108bd519d0e5d01a2577779))

## v0.1.180 (2021-11-28)
### Fix
* **esphome:** Fix esphome_installer device ([`7b0d925`](https://github.com/fhempy/fhempy/commit/7b0d92581d0700e295164e125a909687f97dfd2f))
* **fhempy:** Link to github releases ([`7e3f326`](https://github.com/fhempy/fhempy/commit/7e3f326b3f8cf34728510ada4d2bffc07b6408a4))

## v0.1.179 (2021-11-28)
### Fix
* **tuya_cloud:** Fix typo ([`e7b8b62`](https://github.com/fhempy/fhempy/commit/e7b8b62c1acf7cc65de83c8cd8688e4c0808fa05))
* **tuya_cloud:** Retrieve status every 900s ([`c085381`](https://github.com/fhempy/fhempy/commit/c085381fe00d1087feba2afd1a44dea88b0b5e3b))
* **tuya_cloud:** Better error handling ([`0d94229`](https://github.com/fhempy/fhempy/commit/0d94229f70039e7b650462101fd3940c8cb26e95))

## v0.1.178 (2021-11-27)
### Fix
* **tuya_cloud:** Update lib to 0.6.3 (python>=3.8) ([`d2448d7`](https://github.com/fhempy/fhempy/commit/d2448d764ece18b4387420216e86b83f15adb495))

## v0.1.177 (2021-11-26)
### Fix
* **esphome:** Fix checkIfDeviceExists ([`2b67d7d`](https://github.com/fhempy/fhempy/commit/2b67d7d6dbfc14e1e800dcdd957f5d7a0355bfbd))
* **fhempy:** Fix dbus dependency ([`09c5717`](https://github.com/fhempy/fhempy/commit/09c5717cee2fd8aa13c911ca5466d1a50dba7f6d))

## v0.1.176 (2021-11-26)
### Fix
* **esphome:** Fix attr sortby on restart ([`a605adf`](https://github.com/fhempy/fhempy/commit/a605adfe0c0704f3e04db94fbb4d59697a4bef3f))
* **tuya_cloud:** Change lib to 0.4.1 ([`8ef2e9f`](https://github.com/fhempy/fhempy/commit/8ef2e9f03c64bb0ef69ab6e14aaddd73806251b0))

## v0.1.175 (2021-11-21)
### Fix
* **googlecast:** Update lib and change discovery ([`13f02e1`](https://github.com/fhempy/fhempy/commit/13f02e1eeba09a4f6f61452727b5a4f3825c64fd))

## v0.1.174 (2021-11-15)


## v0.1.173 (2021-11-15)
### Fix
* **tuya_cloud:** Fix colour_data ([`d2fd1ac`](https://github.com/fhempy/fhempy/commit/d2fd1ac0b56540ff589c234489416e95f1973fc4))
* **fhempy:** Update zeroconf 0.36.12 ([`768df9e`](https://github.com/fhempy/fhempy/commit/768df9e8a27d0ac06b1f8e7ccd95ff01a7ec34f5))
* **googlecast:** Update lib to 9.4.0 ([`82a1d6b`](https://github.com/fhempy/fhempy/commit/82a1d6b8431343d4d5ed1a1c9dd8c07de2ac2e28))
* **tuya_cloud:** Fix pow() bug ([`275ef99`](https://github.com/fhempy/fhempy/commit/275ef996e953cf65224af85d606d517db07cc8b3))

## v0.1.172 (2021-11-06)
### Fix
* **googlecast:** Fix speak ([`5a37d57`](https://github.com/fhempy/fhempy/commit/5a37d57ac0ce598827598918dbe3c50d261f9cf7))
* **skodaconnect:** Update lib to 1.1.10 ([`eb19421`](https://github.com/fhempy/fhempy/commit/eb19421b9ddc7c17cddb84847503fa1f5f608fcb))

## v0.1.171 (2021-11-06)
### Fix
* **xiaomi_gateway3:** Fix z2m mode ([`14f3f5b`](https://github.com/fhempy/fhempy/commit/14f3f5b305e7a76bb61092819c5dc404f66e6206))

## v0.1.170 (2021-11-05)
### Fix
* **xiaomi_gateway3:** Fix connected state ([`08005c0`](https://github.com/fhempy/fhempy/commit/08005c0634846aa21e9b56b977b41d24497bc288))

## v0.1.169 (2021-11-05)
### Feature
* **xiaomi_gateway3:** Update to 1.6.0rc2 xgw3 lib ([`bcf7f8d`](https://github.com/fhempy/fhempy/commit/bcf7f8d9d303efadafc5f33c0166b5d38fa575c0))

### Fix
* **esphome:** Fix weblinks device ([`9e93ef0`](https://github.com/fhempy/fhempy/commit/9e93ef00a44e15845906196536651dd858fab87a))

## v0.1.168 (2021-10-30)
### Fix
* **tuya_cloud:** Fix python 3.7 ([`b28cf4e`](https://github.com/fhempy/fhempy/commit/b28cf4e0213e9ee802c8aec94b40d1840d92ba3f))

## v0.1.167 (2021-10-30)
### Fix
* **tuya_cloud:** Update tuya iot lib ([`3ef9f5b`](https://github.com/fhempy/fhempy/commit/3ef9f5bbddf53aa03d07044b881fedf069733f91))
* **esphome:** Fix create weblinks ([`e4ec22f`](https://github.com/fhempy/fhempy/commit/e4ec22f6597ee96307bc1ea5de6a4d2c22f67264))

## v0.1.166 (2021-10-28)
### Fix
* **ring:** Update test ([`cef1d64`](https://github.com/fhempy/fhempy/commit/cef1d643813884af75ff54e24296d56fe79aa422))
* **ring:** Correctly stop update thread ([`cec6b74`](https://github.com/fhempy/fhempy/commit/cec6b746886a8991cacb95a10ec361b6f0d7085b))
* **googlecast:** Do not stop zeroconf ([`720b007`](https://github.com/fhempy/fhempy/commit/720b007c81f3ff41da84485feedd7a0660e5fc5e))
* **fhempy:** Add sentry requirement ([`0df8c52`](https://github.com/fhempy/fhempy/commit/0df8c522e369b225878d656a291cf22714e66157))

## v0.1.165 (2021-10-28)
### Fix
* **xiaomi_gateway3:** Fix zigbee2mqtt ([`fd10b93`](https://github.com/fhempy/fhempy/commit/fd10b93e9719626add8604b913743a5bcba41694))

## v0.1.164 (2021-10-27)
### Fix
* **xiaomi_gateway3:** Fix pairing ([`26848db`](https://github.com/fhempy/fhempy/commit/26848db865253f70a95851fa44621adc0e783b51))

## v0.1.163 (2021-10-27)
### Feature
* **xiaomi_gateway3:** Support zigbee2mqtt ([`3829860`](https://github.com/fhempy/fhempy/commit/3829860d8cdf9ace4b181b3769579874d62eee43))
* **xiaomi_gateway3:** Support non xiaomi zigbee ([`be74c22`](https://github.com/fhempy/fhempy/commit/be74c22428b890bf30650f0031eba02bd7507bc9))

## v0.1.162 (2021-10-25)
### Fix
* **fhempy:** Wait max60s for fhem reply ([`1dbcf1e`](https://github.com/fhempy/fhempy/commit/1dbcf1e5e929815864f2791dc6407c3415b30688))

## v0.1.161 (2021-10-25)
### Fix
* **googlecast:** Update lib/zeroconf ([`cab72a7`](https://github.com/fhempy/fhempy/commit/cab72a71694f9754af29d8ccdb64050697717dea))
* **fhempy:** Fix timeout again ([`6f920cb`](https://github.com/fhempy/fhempy/commit/6f920cbc79fb1ebfe4394ae147fa908213555d2a))
* **fhempy:** Update zeroconf ([`650f7ad`](https://github.com/fhempy/fhempy/commit/650f7ad6176d0d89a54fa638b12da75e50619740))

## v0.1.160 (2021-10-25)
### Fix
* **tuya:** Remove error when offline ([`91cfa6c`](https://github.com/fhempy/fhempy/commit/91cfa6cf58df2dd789d9675c420849a7c1a04a35))

## v0.1.159 (2021-10-24)
### Fix
* **fhempy:** Remove perf sentry ([`cc5d4f8`](https://github.com/fhempy/fhempy/commit/cc5d4f8985ecd3c904f5c9bac78f50170f6da830))
* **googlecast:** Fix endless loop on undefine ([`655e3ad`](https://github.com/fhempy/fhempy/commit/655e3adc13a4d7d79036055a2595893f6b98ad60))

## v0.1.158 (2021-10-24)
### Fix
* **ring:** Ding poll in separate thread ([`7fc27a6`](https://github.com/fhempy/fhempy/commit/7fc27a683177ce84b2aaac7eac541c66b6bde574))

## v0.1.157 (2021-10-24)
### Fix
* **fhempy:** Change sentry sample rate ([`3a0d3e5`](https://github.com/fhempy/fhempy/commit/3a0d3e5b4d617cc73f4107801ad4237d4e596672))
* **googlecast:** Report token errors to user ([`a65c64e`](https://github.com/fhempy/fhempy/commit/a65c64ea956e415afa0a2e52dce7e293ba8b5d65))
* **fhempy:** Hopefully fixed a timeout bug ([`1c4f6be`](https://github.com/fhempy/fhempy/commit/1c4f6be11f7c8d06b57094bfffafb5ec9fda6ecc))

## v0.1.156 (2021-10-23)
### Feature
* **fhempy:** Add sentry logging ([`4d3cab6`](https://github.com/fhempy/fhempy/commit/4d3cab6a833d21fcb87136550e00b5bd96fffdb6))

### Fix
* **fhempy:** Iodev selection fix ([`495e41d`](https://github.com/fhempy/fhempy/commit/495e41da6c4b6054ffa8de5b0cde2ca2e297141c))

## v0.1.155 (2021-10-23)
### Fix
* **meross:** Fix typo ([`08f332e`](https://github.com/fhempy/fhempy/commit/08f332e8c2f08e70429b2f54b40988c37654c01f))

## v0.1.154 (2021-10-23)
### Feature
* **meross:** Support rgb,bri,ct ([`a23f34d`](https://github.com/fhempy/fhempy/commit/a23f34ddb496feba162f51542a6c1f66af26b62b))
* **fhempy:** Support iodev select in attr ([`3f64c63`](https://github.com/fhempy/fhempy/commit/3f64c633721cee69d9d4042e6a941ae6f97a8895))

## v0.1.153 (2021-10-23)
### Fix
* **fhempy:** Better logging ([`d35fff7`](https://github.com/fhempy/fhempy/commit/d35fff7c6bf35197ddb0e0323d10e9029dd0fab7))

## v0.1.152 (2021-10-22)
### Fix
* **meross:** Fix garage readings ([`b65e004`](https://github.com/fhempy/fhempy/commit/b65e004ad9942063cc6d24eefcec6e4292a1e7ea))

## v0.1.151 (2021-10-21)
### Fix
* **esphome:** Fix weblink creation (2) ([`3df3ec0`](https://github.com/fhempy/fhempy/commit/3df3ec013400939ce17a6ba1883ef8eff256a964))

## v0.1.150 (2021-10-21)
### Fix
* **meross:** Fix open/close ([`63e25bd`](https://github.com/fhempy/fhempy/commit/63e25bdda3adcb54ee75109601a52e0fee3219b4))
* **esphome:** Fix weblink creation ([`60ebbcf`](https://github.com/fhempy/fhempy/commit/60ebbcf2896802410dd5b1f8c2b6d96cef2bddae))

## v0.1.149 (2021-10-21)
### Feature
* **erelax_vaillant:** Add duration for temp ([`d96f897`](https://github.com/fhempy/fhempy/commit/d96f897a18b29bb03af3838869b710aa996968ae))
* **esphome:** Add install link ([`6a22557`](https://github.com/fhempy/fhempy/commit/6a225570b39d201f670061cbe96b288ad0fdd99b))
* **meross:** Support garage opener ([`dd4136e`](https://github.com/fhempy/fhempy/commit/dd4136e3ded61788242771ddd70fe37cfaff2e8e))

### Fix
* **fhempy:** Make installation easier on debian 11 ([`6857d47`](https://github.com/fhempy/fhempy/commit/6857d475dd67cba27fdf074949e87741fadcc4e2))

## v0.1.148 (2021-10-17)
### Fix
* **esphome:** Fix path again ([`d35b0af`](https://github.com/fhempy/fhempy/commit/d35b0af64b8a2603385f9bc499c40fd549d18c89))

## v0.1.147 (2021-10-16)
### Fix
* **esphome:** Revert path change ([`7452ebb`](https://github.com/fhempy/fhempy/commit/7452ebb20fa012bda4a6a52bc955e20cf7dd24b1))

## v0.1.146 (2021-10-16)
### Fix
* **googlecast:** Fix circular import ([`6d705de`](https://github.com/fhempy/fhempy/commit/6d705def909adef171a8d461d10ea5cbf9a44a8a))
* **esphome:** Update library ([`56af685`](https://github.com/fhempy/fhempy/commit/56af685dba0cf25c362a3dd320acc8ae795695e4))
* **esphome:** Set path for esphome ([`5b80c65`](https://github.com/fhempy/fhempy/commit/5b80c65b4ffcb3acbeca3dff2725f980b2cfa34d))

## v0.1.145 (2021-10-13)
### Fix
* **fhempy:** Fix circular imports ([`6feb2e9`](https://github.com/fhempy/fhempy/commit/6feb2e9641f0122402f6840030fc1b0a41d7b1ef))

## v0.1.144 (2021-10-13)
### Fix
* **tuya_cloud:** Change info to debug ([`55b5ed5`](https://github.com/fhempy/fhempy/commit/55b5ed5aea41c94fc97ab5ac6edd6692c98415bf))

## v0.1.143 (2021-10-13)
### Fix
* **fhempy:** Better logging ([`38337ea`](https://github.com/fhempy/fhempy/commit/38337ea15575c56cc3cb3d4edad2e6050e1413f3))
* **fhempy:** Fix fhempyServer module ([`c969a27`](https://github.com/fhempy/fhempy/commit/c969a279c2ee1ba0b60afac96091695d72d9a243))
* **fhempy:** Fix fhem help ([`220bf15`](https://github.com/fhempy/fhempy/commit/220bf1544dee7103dc40b5afdc6bd0f93d945ee0))

## v0.1.142 (2021-10-13)
### Fix
* **fhempy:** Revert websockets change ([`4c4bf7e`](https://github.com/fhempy/fhempy/commit/4c4bf7e27f286cf1f794a0b4c41f142b7de95612))

## v0.1.141 (2021-10-13)
### Fix
* **eq3bt:** Fix circular import ([`0ffe738`](https://github.com/fhempy/fhempy/commit/0ffe7383c645ceecfa7d4411437a8f009245e9a9))

## v0.1.140 (2021-10-13)
### Fix
* **fhempy:** Do not use legacy websockets ([`c5ea3c1`](https://github.com/fhempy/fhempy/commit/c5ea3c1e1969058a03f71314598491477c5f4b79))

## v0.1.139 (2021-10-13)
### Fix
* **xiaomi_gateway3:** Update readme ([`541d941`](https://github.com/fhempy/fhempy/commit/541d941f5f0a08b9c5e5f04e2bd3dba4e41e3a6f))
* **fhempy:** Reducing >100ms "blocking" ([`a4d2799`](https://github.com/fhempy/fhempy/commit/a4d27996c83ae197145b5ebd1dbcace3f90b2471))

## v0.1.138 (2021-10-13)
### Feature
* **fhempy:** Use readme as help in fhem ([`faf245f`](https://github.com/fhempy/fhempy/commit/faf245f403af6da5d752a2ebce248bb2d3d0c212))

### Fix
* **xiaomi_gateway3:** Fix circular import ([`d9402b9`](https://github.com/fhempy/fhempy/commit/d9402b9e4d3554ac15532351e15b684f081f42ca))

## v0.1.137 (2021-10-12)
### Fix
* **fhempy:** Fix no response ([`a2656a0`](https://github.com/fhempy/fhempy/commit/a2656a0e0c00260e299e0593751fd22f503d67bc))

## v0.1.136 (2021-10-11)
### Fix
* **fhempy:** Fix tests ([`8cd8c71`](https://github.com/fhempy/fhempy/commit/8cd8c7116eab1c0e53f55413c4e82bacb7eaa324))

## v0.1.135 (2021-10-11)
### Fix
* **fhempy:** Fix tests for 3.7 ([`c620d09`](https://github.com/fhempy/fhempy/commit/c620d0992acd3e94b309b9bda493e92775abf30f))

## v0.1.134 (2021-10-11)
### Fix
* **fhempy:** Fix version ([`ed0159d`](https://github.com/fhempy/fhempy/commit/ed0159da60a40da8077cee4cf77855965084062a))
* **fhempy:** Add 3.8,3.9 tests ([`d06989d`](https://github.com/fhempy/fhempy/commit/d06989d3bd9aa713cb8eea87c163aa9471be0ae0))
* **fhempy:** Update requirements ([`3dd10df`](https://github.com/fhempy/fhempy/commit/3dd10dfa1e86c88c3b68aa1b8a3d89f15aaf553b))
* **fhempy:** Fix tests ([`b1e68a8`](https://github.com/fhempy/fhempy/commit/b1e68a88ff25565a63c89b45a9a550fd45434d26))
* **fhempy:** Fix pythontype handling ([`8c43843`](https://github.com/fhempy/fhempy/commit/8c4384324501b03fdbeb712bacf0ca1fa773800f))
* **object_detection:** Update lib ([`8273a31`](https://github.com/fhempy/fhempy/commit/8273a314ed001c7b54ff324f3831be389bc09e1d))

## v0.1.45 (2021-10-11)
### Fix
* **fhempy:** Add 3.8,3.9 tests ([`d06989d`](https://github.com/fhempy/fhempy/commit/d06989d3bd9aa713cb8eea87c163aa9471be0ae0))

## v0.1.44 (2021-10-11)
### Feature
* **seatconnect:** Bugfixing ([#39](https://github.com/fhempy/fhempy/issues/39)) ([`a5996f5`](https://github.com/fhempy/fhempy/commit/a5996f557c12ce4a7390faee31d0cbaeb05dbe71))
* **fhempy:** Add new devices to room/group ([`c197110`](https://github.com/fhempy/fhempy/commit/c197110a26df50acea79ae9abdac7832ac0182f6))
* **seatconnect:** Integration of Timer Schedule for Climatisation ([#38](https://github.com/fhempy/fhempy/issues/38)) ([`f3a130d`](https://github.com/fhempy/fhempy/commit/f3a130d92948ce9eaa5cb65c61ce7e68c7049251))
* **xiaomi_gateway3:** Update xg3 library ([`62352da`](https://github.com/fhempy/fhempy/commit/62352da7581f1f338d34078ebfc2822fd38e217a))
* **meross:** Support meross on/off ([`d08c927`](https://github.com/fhempy/fhempy/commit/d08c927361771164d8dc7665e0687fdc3420e777))
* **fhempy:** Add gen_fhemdev_name fct ([`6cf9829`](https://github.com/fhempy/fhempy/commit/6cf9829124d6c3f759360b176be34510b319b7c7))
* **seatconnect:** First Version of seatconnect ([#35](https://github.com/fhempy/fhempy/issues/35)) ([`124f715`](https://github.com/fhempy/fhempy/commit/124f71588f3bd54e20118baf37029760809cdfe8))
* **skodaconnect:** Add honk and flash support ([`623c3d3`](https://github.com/fhempy/fhempy/commit/623c3d3bef608edfa0ed5c00f157e8f90fcc908d))
* **erelax_vaillant:** Add away, manual readings ([`2e49418`](https://github.com/fhempy/fhempy/commit/2e494188b5e5c84603e2994bf4cb977b33b4c586))
* **upnp:** Update upnp library ([`f2c5120`](https://github.com/fhempy/fhempy/commit/f2c512079c665e8dd84c1efa288b08873cc98fed))
* **googlecast:** Update libraries ([#25](https://github.com/fhempy/fhempy/issues/25)) ([`856eeac`](https://github.com/fhempy/fhempy/commit/856eeac940659974458b323c6aa2d266a576040d))
* **ring:** Update library to 0.7.1 ([#24](https://github.com/fhempy/fhempy/issues/24)) ([`9aa2360`](https://github.com/fhempy/fhempy/commit/9aa236079a81f483294be41e0a84a167b2ae5bed))
* **fhempy:** Update to asynczeroconf ([`7b319e3`](https://github.com/fhempy/fhempy/commit/7b319e347601634894c458c7ac2b3782b99dee5e))
* **tuya_cloud:** Support colorpicker ([`fbef95d`](https://github.com/fhempy/fhempy/commit/fbef95d49466342270833adb428b466312ef372c))
* **tuya_cloud:** Set state for some devices ([`de4f07a`](https://github.com/fhempy/fhempy/commit/de4f07a9d47c19c536464670081ef5f80f3789cf))
* **miflora:** Change conductivity to fertility ([`6d27f47`](https://github.com/fhempy/fhempy/commit/6d27f47f196c889c0c80cbaf0f5fcf2af0c2ae51))
* **tuya_cloud:** Use switch_led for state ([`a5f7e65`](https://github.com/fhempy/fhempy/commit/a5f7e659af1ba32ae9f15567f061122a6312c22c))
* **tuya_cloud:** Support json commands ([`fdc9170`](https://github.com/fhempy/fhempy/commit/fdc9170129fb0d45298eb9d3d323169fdba857a0))
* **tuya_cloud:** Support all tuya devices ([`ddceb85`](https://github.com/fhempy/fhempy/commit/ddceb855fe6758d5884346ea93a6e84a06625c34))
* **fhempy:** Use fhempy room instead of hidden ([`ae2ffdc`](https://github.com/fhempy/fhempy/commit/ae2ffdc9672e467d0ae68294acb6b79b559c8a04))
* **fhempy:** Support init_done ([`c807582`](https://github.com/fhempy/fhempy/commit/c80758235165e50f9256cc060db2930a5b97b738))
* **erelax_vaillant:** Support home/away ([`b29edde`](https://github.com/fhempy/fhempy/commit/b29eddeb16eb50c86f22eceb7cd8b2277e87f718))
* **erelax_vaillant:** Support erelax vaillant ([`0c7f12c`](https://github.com/fhempy/fhempy/commit/0c7f12c7f8709687cdf2d477b055c03bb3c6e38a))
* **tuya:** Support unknown tuya devices ([`d42d30d`](https://github.com/fhempy/fhempy/commit/d42d30d2f91b4266eabf13a8e0985a24dee10f32))
* **skodaconnect:** Change vehicle.update() to connection.update(), add UpdateInterval, add UpdateReading, add ForceUpdate, add missing set_ commands, ([`1de20c3`](https://github.com/fhempy/fhempy/commit/1de20c34fe61541d42a1628a05b6b526aa439698))
* **skodaconnect:** Add skoda connect support ([`ab507e8`](https://github.com/fhempy/fhempy/commit/ab507e872293014fedad786bf5d85c4e82eb36a4))
* **mitemp2:** Test version of mitemp2 ([`31e17a4`](https://github.com/fhempy/fhempy/commit/31e17a4e439ab92463659c20c0e494cd33f85947))
* **tuya:** Support miio lib 0.5.5.2 ([`88fb98b`](https://github.com/fhempy/fhempy/commit/88fb98bdd7e9f73bff231e64236832685e12f47b))
* **googlecast:** Update to pychromecast 9.1.1 ([`fdaab50`](https://github.com/fhempy/fhempy/commit/fdaab50f99006806464603a2ecfd2f4adf137967))
* **ring:** Update to latest ring_doorbell lib ([`a7295ca`](https://github.com/fhempy/fhempy/commit/a7295ca3fcfb3e6f62cdcc969556b79f8198f468))
* **tuya:** Update to latest tinytuya lib ([`0edc476`](https://github.com/fhempy/fhempy/commit/0edc476557bf54da6c7775b0101b68eb35894115))
* **xiaomi_gateway3:** Update to latest version ([`9643837`](https://github.com/fhempy/fhempy/commit/96438373925c4c583dfbe4a9d8433fbc98aa678a))

### Fix
* **fhempy:** Rename to fhempy ([`3ee719c`](https://github.com/fhempy/fhempy/commit/3ee719c336ba7ddb834ecd236e4e66961c6cb7d7))
* **fhempy:** Rename to fhempy ([`74442ea`](https://github.com/fhempy/fhempy/commit/74442ea9c4c03e748e4734df95ae6c4c93ef72ce))
* **fhempy:** Rename to fhempy ([`53c68c0`](https://github.com/fhempy/fhempy/commit/53c68c0f95b584ade1d6283a8208295f8e5038be))
* **fhempy:** Rename to fhempy ([`7aac6cb`](https://github.com/fhempy/fhempy/commit/7aac6cb07e8195835c5b28b5227caeaa8b7fa81d))
* **fhempy:** Rename to fhempy ([`058ba5f`](https://github.com/fhempy/fhempy/commit/058ba5f385c90a6ae79a27f575fcd90390af4448))
* **fhempy:** Rename to fhempy ([`11e8f99`](https://github.com/fhempy/fhempy/commit/11e8f99f033481a4bd44e58007831d9036d823f2))
* **miio:** Update miio lib ([`32cbc78`](https://github.com/fhempy/fhempy/commit/32cbc78d21326edc760425c32727ddea5f7a380b))
* **fhempy:** Update zeroconf lib ([`40eefeb`](https://github.com/fhempy/fhempy/commit/40eefebec873f5ebba506bbd0aa9bb47f73db44c))
* **tuya_cloud:** Better error handling ([`056ab5c`](https://github.com/fhempy/fhempy/commit/056ab5c4c5583f490c17b7d007b347f1d08ca2a4))
* **xiaomi_gateway3:** Fix attr usage ([`eb1f4b1`](https://github.com/fhempy/fhempy/commit/eb1f4b180944d28697fd49a0c4b7be5730d9e326))
* **fhempy:** Flake8 fixes ([`519658c`](https://github.com/fhempy/fhempy/commit/519658ccbad6ebc9c8eb27f4dc9025913f7fdb4f))
* **xiaomi_gateway3:** Small fixes ([`d96bbc8`](https://github.com/fhempy/fhempy/commit/d96bbc849c24fb275e8bc3e3f3b0095f81464ccc))
* **xiaomi_gateway3:** Fix gateway device ([`24f0b13`](https://github.com/fhempy/fhempy/commit/24f0b13aa29f557ec3ccee32e78c18fc03a619ef))
* **fhempy:** Better error handling ([`5910b6a`](https://github.com/fhempy/fhempy/commit/5910b6ae1fe3a6ea2e2cb97cdcf45ba782a25024))
* **fhempy:** Update requirements ([`f327a5a`](https://github.com/fhempy/fhempy/commit/f327a5a5e5abd3393c336743a376618d5136176a))
* **tuya_cloud:** Fix rgb readings ([`5257ff2`](https://github.com/fhempy/fhempy/commit/5257ff2428219e75767b4f756734d7dbf1982bbf))
* **meross:** Add usage ([`ccd7a4c`](https://github.com/fhempy/fhempy/commit/ccd7a4cd9b84573fbc472a024c0e1854fb509038))
* **fhempy:** Add exception handling ([`bcaaf97`](https://github.com/fhempy/fhempy/commit/bcaaf970f4b0f2e239bba52fe7c136f92c95218c))
* **tuya_cloud:** Handle stop() exceptions ([`8bb081a`](https://github.com/fhempy/fhempy/commit/8bb081aa46f55a98a3900fc062b77fdd8369c16f))
* **tuya_cloud:** Fix devnames with dashes ([`54e2f7c`](https://github.com/fhempy/fhempy/commit/54e2f7cb1de5f8bc844eb18f4332fbbbb8c7151d))
* **fhempy:** Handle zeroconf exceptions ([`eebf78f`](https://github.com/fhempy/fhempy/commit/eebf78f761909ded5228cb0e32e99a89bd7cbeab))
* **fhempy:** Add debug output ([`3b09a35`](https://github.com/fhempy/fhempy/commit/3b09a351db8851dfc5b34b684768d093e1a8ba45))
* **tuya_cloud:** Support devices with umlauts ([`df937dc`](https://github.com/fhempy/fhempy/commit/df937dc0c9298ac0dea0a795510ea14330b0b2d9))
* **discover_mdns:** Use async zeroconf ([`6ad6445`](https://github.com/fhempy/fhempy/commit/6ad6445e202e5cbe0a486b2701a775b6b32d599d))
* **fhempy:** Fix release script ([`de82f89`](https://github.com/fhempy/fhempy/commit/de82f891c300feda26bc35168119293a520991f6))
* **skodaconnect:** Update lib to 1.1.4 ([`192c4f3`](https://github.com/fhempy/fhempy/commit/192c4f3ac70b1b2ee33298f8d23d3aba7b025e79))
* **skodaconnect:** Update lib to 1.1.3 ([`ae47357`](https://github.com/fhempy/fhempy/commit/ae4735782c9d15a7a408de965b27bcdb422c1d23))
* **skodaconnect:** Update lib to 1.1.2 ([`a012022`](https://github.com/fhempy/fhempy/commit/a012022ae7ccb7c746df448d0b99975251fa25ce))
* **erelax_vaillant:** Set endtime 0 if not active ([`9103634`](https://github.com/fhempy/fhempy/commit/91036349b24ded901051833a79aecf920af23f0f))
* **erelax_vaillant:** Fix readings again ([`4fcb9d2`](https://github.com/fhempy/fhempy/commit/4fcb9d24c6deadbc1b622dc7dd9df4d26a6be645))
* **erelax_vaillant:** Fix away/manual readings ([`ab0cc0c`](https://github.com/fhempy/fhempy/commit/ab0cc0ca69a24b66dbef4ff7343f11297588425f))
* **erelax_vaillant:** Fix away/manual readings ([`31dfb46`](https://github.com/fhempy/fhempy/commit/31dfb464fc2a79121cbe0ea89a2e890954244f5c))
* **tuya_cloud:** Fix reading updates ([`572c088`](https://github.com/fhempy/fhempy/commit/572c0880747a8535f9092f87cc12ee91e0910f6c))
* **tuya_cloud:** Fix startup issues ([`a9c2e99`](https://github.com/fhempy/fhempy/commit/a9c2e99db2fd0730b95bb3a1dab5e8f853753ec1))
* **fhempy:** Fix github sec alert ([`6be1403`](https://github.com/fhempy/fhempy/commit/6be14039106babb653faa048336827e1719533bb))
* **fhempy:** Update aiohttp library ([`f00540a`](https://github.com/fhempy/fhempy/commit/f00540abbc6daf6c8b8ba81772c3bef6769499fd))
* **skodaconnect:** Update library to 1.0.52 ([`f14583e`](https://github.com/fhempy/fhempy/commit/f14583ef3b6beb5032064aeb016fe0966238cbe8))
* **dlna_dmr:** Fix get_local_ip ([`e12f602`](https://github.com/fhempy/fhempy/commit/e12f60233cb5bd703d091a47bc21a3261d926331))
* **tests:** Fix ring test ([`9098245`](https://github.com/fhempy/fhempy/commit/90982456484aec502ceeefe08c3a4be9e0ff9db4))
* **fhempy:** Fix zeroconf exception ([`7ad2e73`](https://github.com/fhempy/fhempy/commit/7ad2e73c4140fa99ccac5a9a28fcc094fa890a61))
* **fhempy:** Update requirements ([`02de53d`](https://github.com/fhempy/fhempy/commit/02de53de90b910c9a00a16267961869e5848ee41))
* **fhempy:** Better error handling ([`e4f2ba2`](https://github.com/fhempy/fhempy/commit/e4f2ba2a2d1c46b9bc767119ff4f4519e61ce724))
* **fhempy:** Rename to fhempy ([`38121ce`](https://github.com/fhempy/fhempy/commit/38121ce24260cf4dfd8291901c760008d6ee48e8))
* **esphome:** Fix deprecation warning ([`49af229`](https://github.com/fhempy/fhempy/commit/49af2290a0527370857292c23bc51b9a9a522b2f))
* **fhempy:** Fix NO RESPONSE msgs ([`3413202`](https://github.com/fhempy/fhempy/commit/341320259b85f2d545c62cf898c060025181db5a))
* **fhempy:** Fix log ([`d3d11c4`](https://github.com/fhempy/fhempy/commit/d3d11c440c107fa21a871e331c7834add1e820ad))
* **skodaconnect:** Update library ([`dc2035b`](https://github.com/fhempy/fhempy/commit/dc2035bb80810343eae441279ce52d1d1eddbbea))
* **tuya_cloud:** Update tuya lib ([`8059a68`](https://github.com/fhempy/fhempy/commit/8059a68023c693e0035bd163cdb6a393a53a63d4))
* **tuya_cloud:** Fix colour_data again ([`fd37524`](https://github.com/fhempy/fhempy/commit/fd37524f94bc30667b75849b1933e223d92df361))
* **tuya_cloud:** Fix again colour_data ([`82998c7`](https://github.com/fhempy/fhempy/commit/82998c757357c9c9aee4fbc0b7c83ac8d9170cfb))
* **tuya_cloud:** Handle exception on mqtt stop ([`de40876`](https://github.com/fhempy/fhempy/commit/de4087678f95429e9c86bf4ee3cd767f6836a326))
* **tuya_cloud:** Fix colour_data ([`c87c985`](https://github.com/fhempy/fhempy/commit/c87c9857c67b164cca75f87f5ff2b28fc284b5ac))
* **fhempy:** Add use Color ([`89c8264`](https://github.com/fhempy/fhempy/commit/89c8264adab1a2d788d73c0e1caaa438aa7af850))
* **tuya_cloud:** Fix colour_data ([`b46189c`](https://github.com/fhempy/fhempy/commit/b46189c60d0f0e58797b2dd0e8024ddfd97a66f8))
* **mitemp:** Latest mitemp lib not working ([`9e2dcfc`](https://github.com/fhempy/fhempy/commit/9e2dcfc092d9102248bc8b4ef28c340505d5fc46))
* **tuya_cloud:** Fix reset_reading ([`48410ec`](https://github.com/fhempy/fhempy/commit/48410ecfbe89b1c0310e83c4676c9407900551ad))
* **mitemp:** Update library ([`6919917`](https://github.com/fhempy/fhempy/commit/691991759cbc9909ede6aa44b23c030d9350d234))
* **fhempy:** Fix room for fhempy log ([`9662148`](https://github.com/fhempy/fhempy/commit/966214849c577e085dd3e796bb4ba71a7367a721))
* **tuya_cloud:** Fix set_json ([`246584f`](https://github.com/fhempy/fhempy/commit/246584fc1fd7adc6d4743e6dc9be9c43c8a28498))
* **skodaconnect:** Fix climater with new library ([`bdc8058`](https://github.com/fhempy/fhempy/commit/bdc8058c2d759454e6919b16d04aa36238de1d2e))
* **skodaconnect:** Fix climatisation ([`1870427`](https://github.com/fhempy/fhempy/commit/18704278f393203e487899b79ca6fe2b7b065745))
* **skodaconnect:** Fix climatisation ([`527214f`](https://github.com/fhempy/fhempy/commit/527214fa5be15a7ba52b726472f1900b43262f61))
* **xiaomi_gateway3:** Fix reading updates ([`d8a7ff0`](https://github.com/fhempy/fhempy/commit/d8a7ff04545b8411c0692df3f5d42cf44f14bec8))
* **tuya_cloud:** Fix reading updates ([`54a1259`](https://github.com/fhempy/fhempy/commit/54a12595ec52bb6bb13a6619a77e26d16b161654))
* **skodaconnect:** Fix update readings ([#21](https://github.com/fhempy/fhempy/issues/21)) ([`cd0aef9`](https://github.com/fhempy/fhempy/commit/cd0aef9dec0350570b9b6667e356db53216e631e))
* **tuya_cloud:** Fix switch ([`d1d1e03`](https://github.com/fhempy/fhempy/commit/d1d1e03f629985175a0bae88f797f5cc49ab1b0d))
* **tuya_cloud:** Fix default code for state ([`deedac5`](https://github.com/fhempy/fhempy/commit/deedac5f4853c92d3d79b6848b89542134dfdaf0))
* **tuya_cloud:** Fix tuya lib version ([`9cb101e`](https://github.com/fhempy/fhempy/commit/9cb101e9ba9812e5060039eebb105e4f95855385))
* **skodaconnect:** Fix typo auxiliary ([`9455fc2`](https://github.com/fhempy/fhempy/commit/9455fc2b8fd66c329f4eb3e30b67e9fabd31cee6))
* **skodaconnect:** Fix update_interval/_readings ([`8ee0686`](https://github.com/fhempy/fhempy/commit/8ee0686595e22337b0f5bf8c17720ec09a3a33a8))
* **fhempy:** Fix zeroconf ([`bf048e3`](https://github.com/fhempy/fhempy/commit/bf048e322a58949eef11f305ecf09435b24ebda9))
* **skodaconnect:** Climatisation fix ([`8f2bc7d`](https://github.com/fhempy/fhempy/commit/8f2bc7da3d0767897d31269a5fba91e2c3854f0c))
* **tests:** Fix update test ([`b170df1`](https://github.com/fhempy/fhempy/commit/b170df1cfb06185c83aad5aa8a8c05aa183d89c9))
* **fhempy:** Log successfull update ([`2a3e37f`](https://github.com/fhempy/fhempy/commit/2a3e37f75db9b7277344e8fe0e255f31f1a59f9f))
* **fhempy:** Fix shutdown after update ([`3d7d556`](https://github.com/fhempy/fhempy/commit/3d7d5569ee5416e08ed793791a55b5d3e15531d8))
* **tuya_cloud:** One more fix ([`4a8dc19`](https://github.com/fhempy/fhempy/commit/4a8dc199c0fbb5ea99105e7ee47e0c83a0acbc96))
* **tuya_cloud:** Some fixes ([`357ddf1`](https://github.com/fhempy/fhempy/commit/357ddf1299a123e28c3b18571b64ced5da2aeac4))
* **tuya_cloud:** Fix readings for unsupported devs ([`8dea541`](https://github.com/fhempy/fhempy/commit/8dea541efce093b80eb187a051d00fc1051f55a0))
* **tuya_cloud:** Handle unsupported devices ([`0c224bd`](https://github.com/fhempy/fhempy/commit/0c224bd5d05825c6da004890574640442df6566c))
* **tuya_cloud:** Fix autocreation of new devices ([`80607f2`](https://github.com/fhempy/fhempy/commit/80607f2c566e6cf548e3eee786cc00df516e50ec))
* **xiaomi_gateway3:** Fix temp symbol ([`b033d42`](https://github.com/fhempy/fhempy/commit/b033d421c0634375fda99512b91e99b5dcb9e27c))
* **tuya:** Fix attributes ([`1bd998e`](https://github.com/fhempy/fhempy/commit/1bd998e478ff6e278b889169baeb89d0493031cb))
* **tuya:** Create unknown devices ([`3a57f5b`](https://github.com/fhempy/fhempy/commit/3a57f5bb5bbd3697ad19e8d58a0cff5da9267ad2))
* **ring:** Fix ring auth ([`ebc454d`](https://github.com/fhempy/fhempy/commit/ebc454d5302b3f9356b9d54efab6d76f833c5d35))
* **miflora:** Fix deadlocks ([`21810f8`](https://github.com/fhempy/fhempy/commit/21810f8f6680186b329db31e5a6de8fc0010b0aa))
* **BindingsIo:** Fix possible 100% cpu bug ([`947a90e`](https://github.com/fhempy/fhempy/commit/947a90e472034186656128676ba7d16f728950b3))
* **spotify:** Change auth url ([`63319ba`](https://github.com/fhempy/fhempy/commit/63319bad78301caae4b0273745e459969fcf308f))
* **googlecast:** Fix spotify play ([`08ea929`](https://github.com/fhempy/fhempy/commit/08ea929003d6966c587aed433f6fefbe70e13cdf))
* **spotify:** Fix deprecation warning ([`a852b75`](https://github.com/fhempy/fhempy/commit/a852b75cd13a06ae90ad8b004225fb04014b0b45))
* **spotify_connect_player:** Fix deprecation warn ([`e9bc04b`](https://github.com/fhempy/fhempy/commit/e9bc04bc61cf439b12e6ad4b5101ca57f1bab2e6))
* **googlecast:** Fix spotify, add speak_lang attr ([`6a81f15`](https://github.com/fhempy/fhempy/commit/6a81f15dbce5d2b57489b1c0cffec88fe5653c53))
* **ring:** Fix update_health_data ([`747a129`](https://github.com/fhempy/fhempy/commit/747a12996a9b2552256fe0492086150c94586e5d))
* **fhempy:** Fix possible crash on reconnect ([`d68d60b`](https://github.com/fhempy/fhempy/commit/d68d60bcf9f52c145ad6be221fb6a7fe7388ee03))
* **ring:** Fix battery/volume updates ([`936cc49`](https://github.com/fhempy/fhempy/commit/936cc495c86040d13fc34e11668daf6d32967aa1))
* **ring:** Revert ring_doorbell lib to 0.6.2 ([`71b9511`](https://github.com/fhempy/fhempy/commit/71b9511e47751eb93e2365f0861918aabfe738cd))
* **fhempy:** Update cryptography ([`b154eb6`](https://github.com/fhempy/fhempy/commit/b154eb6b592cb672dbaabefc45b37e11ef304bce))
* **fhempy:** Fix cryptography installation ([`a7b4b6e`](https://github.com/fhempy/fhempy/commit/a7b4b6e5a5357f6b409656f4f79d99ce1b6154a3))
* **xiaomi_tokens:** Fix create miio device ([`f8e4352`](https://github.com/fhempy/fhempy/commit/f8e43525f62f00939f60d0ee30349246203682db))
* **xiaomi_tokens:** Fix device creation ([`ebbc3bb`](https://github.com/fhempy/fhempy/commit/ebbc3bb61f20fba4ff8d1eadd1af61017abe956e))
* **xiaomi_tokens:** Make readings country specific ([`efe1b7a`](https://github.com/fhempy/fhempy/commit/efe1b7a4f37d3530b2f92a906e45f202d67e6d21))
* **fhempy:** Raise error if pkg install fails ([`8b15dcd`](https://github.com/fhempy/fhempy/commit/8b15dcd19180451b45f3de4aa420938334f951d2))
* **xiaomi_gateway3:** Sort imports ([`89c14bc`](https://github.com/fhempy/fhempy/commit/89c14bc1477a91be51c86a80666f12e94430cb04))
* **googlecast:** Remove spotify_token dependency ([`ab8f872`](https://github.com/fhempy/fhempy/commit/ab8f8726158eb7037a62e98517a61b2760fbc47f))
* **xiaomi_gateway3:** Fix motion sensor reset ([`37222fc`](https://github.com/fhempy/fhempy/commit/37222fcd1d52c09cb97ba5943d939436c40d56a8))
* **fhempy:** Change logfile name to fhempy ([`2dc88df`](https://github.com/fhempy/fhempy/commit/2dc88df1177c69990926d5e55852656ee365f666))
* **xiaomi_gateway3:** Remove added_device reading ([`700e361`](https://github.com/fhempy/fhempy/commit/700e361417c9fc4ea634874b2f447396657c85fc))
* **fhempy:** Change log name to fhempy ([`ce8fac5`](https://github.com/fhempy/fhempy/commit/ce8fac5e3faa8fa8db360d787dc481288ba045f0))

## v0.1.133 (2021-10-11)
### Fix
* **fhempy:** Rename to fhempy ([`3ee719c`](https://github.com/fhempy/fhempy/commit/3ee719c336ba7ddb834ecd236e4e66961c6cb7d7))
* **fhempy:** Rename to fhempy ([`74442ea`](https://github.com/fhempy/fhempy/commit/74442ea9c4c03e748e4734df95ae6c4c93ef72ce))

## v0.1.132 (2021-10-11)
### Fix
* **fhempy:** Rename to fhempy ([`53c68c0`](https://github.com/fhempy/fhempy/commit/53c68c0f95b584ade1d6283a8208295f8e5038be))
* **fhempy:** Rename to fhempy ([`7aac6cb`](https://github.com/fhempy/fhempy/commit/7aac6cb07e8195835c5b28b5227caeaa8b7fa81d))
* **fhempy:** Rename to fhempy ([`058ba5f`](https://github.com/fhempy/fhempy/commit/058ba5f385c90a6ae79a27f575fcd90390af4448))
* **fhempy:** Rename to fhempy ([`11e8f99`](https://github.com/fhempy/fhempy/commit/11e8f99f033481a4bd44e58007831d9036d823f2))
* **miio:** Update miio lib ([`32cbc78`](https://github.com/fhempy/fhempy/commit/32cbc78d21326edc760425c32727ddea5f7a380b))
* **fhempy:** Update zeroconf lib ([`40eefeb`](https://github.com/fhempy/fhempy/commit/40eefebec873f5ebba506bbd0aa9bb47f73db44c))

## v0.1.131 (2021-10-10)
### Feature
* **seatconnect:** Bugfixing ([#39](https://github.com/fhempy/fhempy/issues/39)) ([`a5996f5`](https://github.com/fhempy/fhempy/commit/a5996f557c12ce4a7390faee31d0cbaeb05dbe71))
* **fhempy:** Add new devices to room/group ([`c197110`](https://github.com/fhempy/fhempy/commit/c197110a26df50acea79ae9abdac7832ac0182f6))

### Fix
* **tuya_cloud:** Better error handling ([`056ab5c`](https://github.com/fhempy/fhempy/commit/056ab5c4c5583f490c17b7d007b347f1d08ca2a4))
* **xiaomi_gateway3:** Fix attr usage ([`eb1f4b1`](https://github.com/fhempy/fhempy/commit/eb1f4b180944d28697fd49a0c4b7be5730d9e326))
* **fhempy:** Flake8 fixes ([`519658c`](https://github.com/fhempy/fhempy/commit/519658ccbad6ebc9c8eb27f4dc9025913f7fdb4f))

## v0.1.130 (2021-10-08)
### Feature
* **seatconnect:** Integration of Timer Schedule for Climatisation ([#38](https://github.com/fhempy/fhempy/issues/38)) ([`f3a130d`](https://github.com/fhempy/fhempy/commit/f3a130d92948ce9eaa5cb65c61ce7e68c7049251))

## v0.1.129 (2021-10-08)
### Fix
* **xiaomi_gateway3:** Small fixes ([`d96bbc8`](https://github.com/fhempy/fhempy/commit/d96bbc849c24fb275e8bc3e3f3b0095f81464ccc))

## v0.1.128 (2021-10-07)
### Fix
* **xiaomi_gateway3:** Fix gateway device ([`24f0b13`](https://github.com/fhempy/fhempy/commit/24f0b13aa29f557ec3ccee32e78c18fc03a619ef))

## v0.1.127 (2021-10-07)
### Feature
* **xiaomi_gateway3:** Update xg3 library ([`62352da`](https://github.com/fhempy/fhempy/commit/62352da7581f1f338d34078ebfc2822fd38e217a))

### Fix
* **fhempy:** Better error handling ([`5910b6a`](https://github.com/fhempy/fhempy/commit/5910b6ae1fe3a6ea2e2cb97cdcf45ba782a25024))

## v0.1.126 (2021-09-30)
### Fix
* **fhempy:** Update requirements ([`f327a5a`](https://github.com/fhempy/fhempy/commit/f327a5a5e5abd3393c336743a376618d5136176a))

## v0.1.125 (2021-09-30)
### Fix
* **tuya_cloud:** Fix rgb readings ([`5257ff2`](https://github.com/fhempy/fhempy/commit/5257ff2428219e75767b4f756734d7dbf1982bbf))
* **meross:** Add usage ([`ccd7a4c`](https://github.com/fhempy/fhempy/commit/ccd7a4cd9b84573fbc472a024c0e1854fb509038))

## v0.1.124 (2021-09-29)
### Feature
* **meross:** Support meross on/off ([`d08c927`](https://github.com/fhempy/fhempy/commit/d08c927361771164d8dc7665e0687fdc3420e777))
* **fhempy:** Add gen_fhemdev_name fct ([`6cf9829`](https://github.com/fhempy/fhempy/commit/6cf9829124d6c3f759360b176be34510b319b7c7))

### Fix
* **fhempy:** Add exception handling ([`bcaaf97`](https://github.com/fhempy/fhempy/commit/bcaaf970f4b0f2e239bba52fe7c136f92c95218c))
* **tuya_cloud:** Handle stop() exceptions ([`8bb081a`](https://github.com/fhempy/fhempy/commit/8bb081aa46f55a98a3900fc062b77fdd8369c16f))

## v0.1.123 (2021-09-28)
### Fix
* **tuya_cloud:** Fix devnames with dashes ([`54e2f7c`](https://github.com/fhempy/fhempy/commit/54e2f7cb1de5f8bc844eb18f4332fbbbb8c7151d))

## v0.1.122 (2021-09-28)
### Feature
* **seatconnect:** First Version of seatconnect ([#35](https://github.com/fhempy/fhempy/issues/35)) ([`124f715`](https://github.com/fhempy/fhempy/commit/124f71588f3bd54e20118baf37029760809cdfe8))

## v0.1.121 (2021-09-28)


## v0.1.120 (2021-09-22)
### Fix
* **fhempy:** Handle zeroconf exceptions ([`eebf78f`](https://github.com/fhempy/fhempy/commit/eebf78f761909ded5228cb0e32e99a89bd7cbeab))

## v0.1.119 (2021-09-20)
### Fix
* **fhempy:** Add debug output ([`3b09a35`](https://github.com/fhempy/fhempy/commit/3b09a351db8851dfc5b34b684768d093e1a8ba45))

## v0.1.118 (2021-09-19)
### Fix
* **tuya_cloud:** Support devices with umlauts ([`df937dc`](https://github.com/fhempy/fhempy/commit/df937dc0c9298ac0dea0a795510ea14330b0b2d9))
* **discover_mdns:** Use async zeroconf ([`6ad6445`](https://github.com/fhempy/fhempy/commit/6ad6445e202e5cbe0a486b2701a775b6b32d599d))

## v0.1.117 (2021-09-08)
### Fix
* **fhempy:** Fix release script ([`de82f89`](https://github.com/fhempy/fhempy/commit/de82f891c300feda26bc35168119293a520991f6))

## v0.1.116 (2021-09-07)
### Feature
* **skodaconnect:** Add honk and flash support ([`623c3d3`](https://github.com/fhempy/fhempy/commit/623c3d3bef608edfa0ed5c00f157e8f90fcc908d))

### Fix
* **skodaconnect:** Update lib to 1.1.4 ([`192c4f3`](https://github.com/fhempy/fhempy/commit/192c4f3ac70b1b2ee33298f8d23d3aba7b025e79))
* **skodaconnect:** Update lib to 1.1.3 ([`ae47357`](https://github.com/fhempy/fhempy/commit/ae4735782c9d15a7a408de965b27bcdb422c1d23))

## v0.1.115 (2021-09-05)
### Fix
* **skodaconnect:** Update lib to 1.1.2 ([`a012022`](https://github.com/fhempy/fhempy/commit/a012022ae7ccb7c746df448d0b99975251fa25ce))

## v0.1.114 (2021-09-05)
### Fix
* **erelax_vaillant:** Set endtime 0 if not active ([`9103634`](https://github.com/fhempy/fhempy/commit/91036349b24ded901051833a79aecf920af23f0f))

## v0.1.113 (2021-09-05)
### Fix
* **erelax_vaillant:** Fix readings again ([`4fcb9d2`](https://github.com/fhempy/fhempy/commit/4fcb9d24c6deadbc1b622dc7dd9df4d26a6be645))

## v0.1.112 (2021-09-05)
### Fix
* **erelax_vaillant:** Fix away/manual readings ([`ab0cc0c`](https://github.com/fhempy/fhempy/commit/ab0cc0ca69a24b66dbef4ff7343f11297588425f))

## v0.1.111 (2021-09-05)
### Fix
* **erelax_vaillant:** Fix away/manual readings ([`31dfb46`](https://github.com/fhempy/fhempy/commit/31dfb464fc2a79121cbe0ea89a2e890954244f5c))

## v0.1.110 (2021-09-05)
### Feature
* **erelax_vaillant:** Add away, manual readings ([`2e49418`](https://github.com/fhempy/fhempy/commit/2e494188b5e5c84603e2994bf4cb977b33b4c586))

## v0.1.109 (2021-08-31)
### Fix
* **tuya_cloud:** Fix reading updates ([`572c088`](https://github.com/fhempy/fhempy/commit/572c0880747a8535f9092f87cc12ee91e0910f6c))

## v0.1.108 (2021-08-30)
### Fix
* **tuya_cloud:** Fix startup issues ([`a9c2e99`](https://github.com/fhempy/fhempy/commit/a9c2e99db2fd0730b95bb3a1dab5e8f853753ec1))
* **fhempy:** Fix github sec alert ([`6be1403`](https://github.com/fhempy/fhempy/commit/6be14039106babb653faa048336827e1719533bb))

## v0.1.107 (2021-08-30)
### Fix
* **fhempy:** Update aiohttp library ([`f00540a`](https://github.com/fhempy/fhempy/commit/f00540abbc6daf6c8b8ba81772c3bef6769499fd))
* **skodaconnect:** Update library to 1.0.52 ([`f14583e`](https://github.com/fhempy/fhempy/commit/f14583ef3b6beb5032064aeb016fe0966238cbe8))
* **dlna_dmr:** Fix get_local_ip ([`e12f602`](https://github.com/fhempy/fhempy/commit/e12f60233cb5bd703d091a47bc21a3261d926331))

## v0.1.106 (2021-08-29)
### Fix
* **tests:** Fix ring test ([`9098245`](https://github.com/fhempy/fhempy/commit/90982456484aec502ceeefe08c3a4be9e0ff9db4))

## v0.1.105 (2021-08-29)
### Feature
* **upnp:** Update upnp library ([`f2c5120`](https://github.com/fhempy/fhempy/commit/f2c512079c665e8dd84c1efa288b08873cc98fed))

### Fix
* **fhempy:** Fix zeroconf exception ([`7ad2e73`](https://github.com/fhempy/fhempy/commit/7ad2e73c4140fa99ccac5a9a28fcc094fa890a61))

## v0.1.104 (2021-08-28)
### Feature
* **googlecast:** Update libraries ([#25](https://github.com/fhempy/fhempy/issues/25)) ([`856eeac`](https://github.com/fhempy/fhempy/commit/856eeac940659974458b323c6aa2d266a576040d))
* **ring:** Update library to 0.7.1 ([#24](https://github.com/fhempy/fhempy/issues/24)) ([`9aa2360`](https://github.com/fhempy/fhempy/commit/9aa236079a81f483294be41e0a84a167b2ae5bed))

## v0.1.103 (2021-08-28)
### Fix
* **fhempy:** Update requirements ([`02de53d`](https://github.com/fhempy/fhempy/commit/02de53de90b910c9a00a16267961869e5848ee41))

## v0.1.102 (2021-08-28)
### Feature
* **fhempy:** Update to asynczeroconf ([`7b319e3`](https://github.com/fhempy/fhempy/commit/7b319e347601634894c458c7ac2b3782b99dee5e))

### Fix
* **fhempy:** Better error handling ([`e4f2ba2`](https://github.com/fhempy/fhempy/commit/e4f2ba2a2d1c46b9bc767119ff4f4519e61ce724))
* **fhempy:** Rename to fhempy ([`38121ce`](https://github.com/fhempy/fhempy/commit/38121ce24260cf4dfd8291901c760008d6ee48e8))

## v0.1.101 (2021-08-27)
### Fix
* **esphome:** Fix deprecation warning ([`49af229`](https://github.com/fhempy/fhempy/commit/49af2290a0527370857292c23bc51b9a9a522b2f))
* **fhempy:** Fix NO RESPONSE msgs ([`3413202`](https://github.com/fhempy/fhempy/commit/341320259b85f2d545c62cf898c060025181db5a))
* **fhempy:** Fix log ([`d3d11c4`](https://github.com/fhempy/fhempy/commit/d3d11c440c107fa21a871e331c7834add1e820ad))

## v0.1.100 (2021-08-27)
### Fix
* **skodaconnect:** Update library ([`dc2035b`](https://github.com/fhempy/fhempy/commit/dc2035bb80810343eae441279ce52d1d1eddbbea))
* **tuya_cloud:** Update tuya lib ([`8059a68`](https://github.com/fhempy/fhempy/commit/8059a68023c693e0035bd163cdb6a393a53a63d4))

## v0.1.99 (2021-08-27)
### Fix
* **tuya_cloud:** Fix colour_data again ([`fd37524`](https://github.com/fhempy/fhempy/commit/fd37524f94bc30667b75849b1933e223d92df361))

## v0.1.98 (2021-08-27)
### Fix
* **tuya_cloud:** Fix again colour_data ([`82998c7`](https://github.com/fhempy/fhempy/commit/82998c757357c9c9aee4fbc0b7c83ac8d9170cfb))

## v0.1.97 (2021-08-26)
### Fix
* **tuya_cloud:** Handle exception on mqtt stop ([`de40876`](https://github.com/fhempy/fhempy/commit/de4087678f95429e9c86bf4ee3cd767f6836a326))
* **tuya_cloud:** Fix colour_data ([`c87c985`](https://github.com/fhempy/fhempy/commit/c87c9857c67b164cca75f87f5ff2b28fc284b5ac))
* **fhempy:** Add use Color ([`89c8264`](https://github.com/fhempy/fhempy/commit/89c8264adab1a2d788d73c0e1caaa438aa7af850))

## v0.1.96 (2021-08-26)
### Fix
* **tuya_cloud:** Fix colour_data ([`b46189c`](https://github.com/fhempy/fhempy/commit/b46189c60d0f0e58797b2dd0e8024ddfd97a66f8))

## v0.1.95 (2021-08-26)
### Feature
* **tuya_cloud:** Support colorpicker ([`fbef95d`](https://github.com/fhempy/fhempy/commit/fbef95d49466342270833adb428b466312ef372c))

## v0.1.94 (2021-08-25)
### Fix
* **mitemp:** Latest mitemp lib not working ([`9e2dcfc`](https://github.com/fhempy/fhempy/commit/9e2dcfc092d9102248bc8b4ef28c340505d5fc46))

## v0.1.93 (2021-08-25)
### Fix
* **tuya_cloud:** Fix reset_reading ([`48410ec`](https://github.com/fhempy/fhempy/commit/48410ecfbe89b1c0310e83c4676c9407900551ad))
* **mitemp:** Update library ([`6919917`](https://github.com/fhempy/fhempy/commit/691991759cbc9909ede6aa44b23c030d9350d234))

## v0.1.92 (2021-08-25)
### Feature
* **tuya_cloud:** Set state for some devices ([`de4f07a`](https://github.com/fhempy/fhempy/commit/de4f07a9d47c19c536464670081ef5f80f3789cf))
* **miflora:** Change conductivity to fertility ([`6d27f47`](https://github.com/fhempy/fhempy/commit/6d27f47f196c889c0c80cbaf0f5fcf2af0c2ae51))
* **tuya_cloud:** Use switch_led for state ([`a5f7e65`](https://github.com/fhempy/fhempy/commit/a5f7e659af1ba32ae9f15567f061122a6312c22c))

### Fix
* **fhempy:** Fix room for fhempy log ([`9662148`](https://github.com/fhempy/fhempy/commit/966214849c577e085dd3e796bb4ba71a7367a721))

## v0.1.91 (2021-08-24)
### Fix
* **tuya_cloud:** Fix set_json ([`246584f`](https://github.com/fhempy/fhempy/commit/246584fc1fd7adc6d4743e6dc9be9c43c8a28498))
* **skodaconnect:** Fix climater with new library ([`bdc8058`](https://github.com/fhempy/fhempy/commit/bdc8058c2d759454e6919b16d04aa36238de1d2e))

## v0.1.90 (2021-08-23)


## v0.1.89 (2021-08-23)
### Feature
* **tuya_cloud:** Support json commands ([`fdc9170`](https://github.com/fhempy/fhempy/commit/fdc9170129fb0d45298eb9d3d323169fdba857a0))

### Fix
* **skodaconnect:** Fix climatisation ([`1870427`](https://github.com/fhempy/fhempy/commit/18704278f393203e487899b79ca6fe2b7b065745))

## v0.1.88 (2021-08-22)
### Fix
* **skodaconnect:** Fix climatisation ([`527214f`](https://github.com/fhempy/fhempy/commit/527214fa5be15a7ba52b726472f1900b43262f61))

## v0.1.87 (2021-08-17)
### Fix
* **xiaomi_gateway3:** Fix reading updates ([`d8a7ff0`](https://github.com/fhempy/fhempy/commit/d8a7ff04545b8411c0692df3f5d42cf44f14bec8))

## v0.1.86 (2021-08-16)
### Fix
* **tuya_cloud:** Fix reading updates ([`54a1259`](https://github.com/fhempy/fhempy/commit/54a12595ec52bb6bb13a6619a77e26d16b161654))

## v0.1.85 (2021-08-16)
### Fix
* **skodaconnect:** Fix update readings ([#21](https://github.com/fhempy/fhempy/issues/21)) ([`cd0aef9`](https://github.com/fhempy/fhempy/commit/cd0aef9dec0350570b9b6667e356db53216e631e))

## v0.1.84 (2021-08-15)
### Fix
* **tuya_cloud:** Fix switch ([`d1d1e03`](https://github.com/fhempy/fhempy/commit/d1d1e03f629985175a0bae88f797f5cc49ab1b0d))

## v0.1.83 (2021-08-13)
### Fix
* **tuya_cloud:** Fix default code for state ([`deedac5`](https://github.com/fhempy/fhempy/commit/deedac5f4853c92d3d79b6848b89542134dfdaf0))

## v0.1.82 (2021-08-08)
### Fix
* **tuya_cloud:** Fix tuya lib version ([`9cb101e`](https://github.com/fhempy/fhempy/commit/9cb101e9ba9812e5060039eebb105e4f95855385))

## v0.1.81 (2021-08-07)
### Fix
* **skodaconnect:** Fix typo auxiliary ([`9455fc2`](https://github.com/fhempy/fhempy/commit/9455fc2b8fd66c329f4eb3e30b67e9fabd31cee6))

## v0.1.80 (2021-08-07)
### Fix
* **skodaconnect:** Fix update_interval/_readings ([`8ee0686`](https://github.com/fhempy/fhempy/commit/8ee0686595e22337b0f5bf8c17720ec09a3a33a8))

## v0.1.79 (2021-08-06)
### Fix
* **fhempy:** Fix zeroconf ([`bf048e3`](https://github.com/fhempy/fhempy/commit/bf048e322a58949eef11f305ecf09435b24ebda9))

## v0.1.78 (2021-08-06)
### Fix
* **skodaconnect:** Climatisation fix ([`8f2bc7d`](https://github.com/fhempy/fhempy/commit/8f2bc7da3d0767897d31269a5fba91e2c3854f0c))

## v0.1.77 (2021-08-02)
### Fix
* **tests:** Fix update test ([`b170df1`](https://github.com/fhempy/fhempy/commit/b170df1cfb06185c83aad5aa8a8c05aa183d89c9))
* **fhempy:** Log successfull update ([`2a3e37f`](https://github.com/fhempy/fhempy/commit/2a3e37f75db9b7277344e8fe0e255f31f1a59f9f))

## v0.1.76 (2021-08-02)
### Fix
* **fhempy:** Fix shutdown after update ([`3d7d556`](https://github.com/fhempy/fhempy/commit/3d7d5569ee5416e08ed793791a55b5d3e15531d8))

## v0.1.75 (2021-08-02)
### Fix
* **tuya_cloud:** One more fix ([`4a8dc19`](https://github.com/fhempy/fhempy/commit/4a8dc199c0fbb5ea99105e7ee47e0c83a0acbc96))

## v0.1.74 (2021-08-02)
### Fix
* **tuya_cloud:** Some fixes ([`357ddf1`](https://github.com/fhempy/fhempy/commit/357ddf1299a123e28c3b18571b64ced5da2aeac4))

## v0.1.73 (2021-08-02)
### Fix
* **tuya_cloud:** Fix readings for unsupported devs ([`8dea541`](https://github.com/fhempy/fhempy/commit/8dea541efce093b80eb187a051d00fc1051f55a0))

## v0.1.72 (2021-08-01)
### Fix
* **tuya_cloud:** Handle unsupported devices ([`0c224bd`](https://github.com/fhempy/fhempy/commit/0c224bd5d05825c6da004890574640442df6566c))

## v0.1.71 (2021-07-31)
### Fix
* **tuya_cloud:** Fix autocreation of new devices ([`80607f2`](https://github.com/fhempy/fhempy/commit/80607f2c566e6cf548e3eee786cc00df516e50ec))
* **xiaomi_gateway3:** Fix temp symbol ([`b033d42`](https://github.com/fhempy/fhempy/commit/b033d421c0634375fda99512b91e99b5dcb9e27c))

## v0.1.70 (2021-07-30)
### Feature
* **tuya_cloud:** Support all tuya devices ([`ddceb85`](https://github.com/fhempy/fhempy/commit/ddceb855fe6758d5884346ea93a6e84a06625c34))
* **fhempy:** Use fhempy room instead of hidden ([`ae2ffdc`](https://github.com/fhempy/fhempy/commit/ae2ffdc9672e467d0ae68294acb6b79b559c8a04))
* **fhempy:** Support init_done ([`c807582`](https://github.com/fhempy/fhempy/commit/c80758235165e50f9256cc060db2930a5b97b738))
* **erelax_vaillant:** Support home/away ([`b29edde`](https://github.com/fhempy/fhempy/commit/b29eddeb16eb50c86f22eceb7cd8b2277e87f718))

### Fix
* **tuya:** Fix attributes ([`1bd998e`](https://github.com/fhempy/fhempy/commit/1bd998e478ff6e278b889169baeb89d0493031cb))

## v0.1.69 (2021-07-27)
### Feature
* **erelax_vaillant:** Support erelax vaillant ([`0c7f12c`](https://github.com/fhempy/fhempy/commit/0c7f12c7f8709687cdf2d477b055c03bb3c6e38a))

## v0.1.68 (2021-07-13)
### Feature
* **tuya:** Support unknown tuya devices ([`d42d30d`](https://github.com/fhempy/fhempy/commit/d42d30d2f91b4266eabf13a8e0985a24dee10f32))

## v0.1.67 (2021-07-13)
### Fix
* **tuya:** Create unknown devices ([`3a57f5b`](https://github.com/fhempy/fhempy/commit/3a57f5bb5bbd3697ad19e8d58a0cff5da9267ad2))
* **ring:** Fix ring auth ([`ebc454d`](https://github.com/fhempy/fhempy/commit/ebc454d5302b3f9356b9d54efab6d76f833c5d35))

## v0.1.66 (2021-07-04)


## v0.1.65 (2021-06-25)
### Feature
* **skodaconnect:** Change vehicle.update() to connection.update(), add UpdateInterval, add UpdateReading, add ForceUpdate, add missing set_ commands, ([`1de20c3`](https://github.com/fhempy/fhempy/commit/1de20c34fe61541d42a1628a05b6b526aa439698))

## v0.1.64 (2021-06-23)
### Feature
* **skodaconnect:** Add skoda connect support ([`ab507e8`](https://github.com/fhempy/fhempy/commit/ab507e872293014fedad786bf5d85c4e82eb36a4))

## v0.1.63 (2021-06-01)


## v0.1.62 (2021-06-01)


## v0.1.61 (2021-05-23)
### Fix
* **miflora:** Fix deadlocks ([`21810f8`](https://github.com/fhempy/fhempy/commit/21810f8f6680186b329db31e5a6de8fc0010b0aa))
* **BindingsIo:** Fix possible 100% cpu bug ([`947a90e`](https://github.com/fhempy/fhempy/commit/947a90e472034186656128676ba7d16f728950b3))

## v0.1.60 (2021-05-04)
### Feature
* **mitemp2:** Test version of mitemp2 ([`31e17a4`](https://github.com/fhempy/fhempy/commit/31e17a4e439ab92463659c20c0e494cd33f85947))

### Fix
* **spotify:** Change auth url ([`63319ba`](https://github.com/fhempy/fhempy/commit/63319bad78301caae4b0273745e459969fcf308f))
* **googlecast:** Fix spotify play ([`08ea929`](https://github.com/fhempy/fhempy/commit/08ea929003d6966c587aed433f6fefbe70e13cdf))
* **spotify:** Fix deprecation warning ([`a852b75`](https://github.com/fhempy/fhempy/commit/a852b75cd13a06ae90ad8b004225fb04014b0b45))
* **spotify_connect_player:** Fix deprecation warn ([`e9bc04b`](https://github.com/fhempy/fhempy/commit/e9bc04bc61cf439b12e6ad4b5101ca57f1bab2e6))
* **googlecast:** Fix spotify, add speak_lang attr ([`6a81f15`](https://github.com/fhempy/fhempy/commit/6a81f15dbce5d2b57489b1c0cffec88fe5653c53))

## v0.1.59 (2021-04-18)
### Fix
* **ring:** Fix update_health_data ([`747a129`](https://github.com/fhempy/fhempy/commit/747a12996a9b2552256fe0492086150c94586e5d))

## v0.1.58 (2021-04-18)
### Feature
* **tuya:** Support miio lib 0.5.5.2 ([`88fb98b`](https://github.com/fhempy/fhempy/commit/88fb98bdd7e9f73bff231e64236832685e12f47b))

## v0.1.57 (2021-03-09)
### Fix
* **fhempy:** Fix possible crash on reconnect ([`d68d60b`](https://github.com/fhempy/fhempy/commit/d68d60bcf9f52c145ad6be221fb6a7fe7388ee03))
* **ring:** Fix battery/volume updates ([`936cc49`](https://github.com/fhempy/fhempy/commit/936cc495c86040d13fc34e11668daf6d32967aa1))

## v0.1.56 (2021-03-08)
### Feature
* **googlecast:** Update to pychromecast 9.1.1 ([`fdaab50`](https://github.com/fhempy/fhempy/commit/fdaab50f99006806464603a2ecfd2f4adf137967))

### Fix
* **ring:** Revert ring_doorbell lib to 0.6.2 ([`71b9511`](https://github.com/fhempy/fhempy/commit/71b9511e47751eb93e2365f0861918aabfe738cd))

## v0.1.55 (2021-03-01)


## v0.1.54 (2021-03-01)


## v0.1.53 (2021-03-01)


## v0.1.52 (2021-03-01)
### Feature
* **ring:** Update to latest ring_doorbell lib ([`a7295ca`](https://github.com/fhempy/fhempy/commit/a7295ca3fcfb3e6f62cdcc969556b79f8198f468))
* **tuya:** Update to latest tinytuya lib ([`0edc476`](https://github.com/fhempy/fhempy/commit/0edc476557bf54da6c7775b0101b68eb35894115))

## v0.1.51 (2021-02-17)
### Fix
* **fhempy:** Update cryptography ([`b154eb6`](https://github.com/fhempy/fhempy/commit/b154eb6b592cb672dbaabefc45b37e11ef304bce))

## v0.1.50 (2021-02-17)
### Fix
* **fhempy:** Fix cryptography installation ([`a7b4b6e`](https://github.com/fhempy/fhempy/commit/a7b4b6e5a5357f6b409656f4f79d99ce1b6154a3))

## v0.1.49 (2021-02-14)
### Feature
* **xiaomi_gateway3:** Update to latest version ([`9643837`](https://github.com/fhempy/fhempy/commit/96438373925c4c583dfbe4a9d8433fbc98aa678a))

### Fix
* **xiaomi_tokens:** Fix create miio device ([`f8e4352`](https://github.com/fhempy/fhempy/commit/f8e43525f62f00939f60d0ee30349246203682db))

## v0.1.48 (2021-02-02)
### Fix
* **xiaomi_tokens:** Fix device creation ([`ebbc3bb`](https://github.com/fhempy/fhempy/commit/ebbc3bb61f20fba4ff8d1eadd1af61017abe956e))

## v0.1.47 (2021-02-01)
### Fix
* **xiaomi_tokens:** Make readings country specific ([`efe1b7a`](https://github.com/fhempy/fhempy/commit/efe1b7a4f37d3530b2f92a906e45f202d67e6d21))

## v0.1.46 (2021-02-01)
### Fix
* **fhempy:** Raise error if pkg install fails ([`8b15dcd`](https://github.com/fhempy/fhempy/commit/8b15dcd19180451b45f3de4aa420938334f951d2))

## v0.1.45 (2021-01-31)
### Fix
* **xiaomi_gateway3:** Sort imports ([`89c14bc`](https://github.com/fhempy/fhempy/commit/89c14bc1477a91be51c86a80666f12e94430cb04))
* **googlecast:** Remove spotify_token dependency ([`ab8f872`](https://github.com/fhempy/fhempy/commit/ab8f8726158eb7037a62e98517a61b2760fbc47f))
* **xiaomi_gateway3:** Fix motion sensor reset ([`37222fc`](https://github.com/fhempy/fhempy/commit/37222fcd1d52c09cb97ba5943d939436c40d56a8))

## v0.1.44 (2021-01-30)
### Fix
* **fhempy:** Change logfile name to fhempy ([`2dc88df`](https://github.com/fhempy/fhempy/commit/2dc88df1177c69990926d5e55852656ee365f666))
* **xiaomi_gateway3:** Remove added_device reading ([`700e361`](https://github.com/fhempy/fhempy/commit/700e361417c9fc4ea634874b2f447396657c85fc))
* **fhempy:** Change log name to fhempy ([`ce8fac5`](https://github.com/fhempy/fhempy/commit/ce8fac5e3faa8fa8db360d787dc481288ba045f0))

## v0.1.43 (2021-01-30)


## v0.1.42 (2021-01-30)
### Feature
* **eq3bt:** Support wndOpnTime/Temp, eco/cmftTemp ([`107805f`](https://github.com/fhempy/fhempy/commit/107805fd5d85fde76a49e2fabe1994943d27a169))

## v0.1.41 (2021-01-30)


## v0.1.40 (2021-01-30)
### Feature
* **xiaomi_gateway3:** Support sensor_wleak.aq1 ([`bc8cf61`](https://github.com/fhempy/fhempy/commit/bc8cf6183bb4568b5f47b98e07669e3e8cda4f4e))

### Fix
* **fhempy:** Fix update ([`6f381c1`](https://github.com/fhempy/fhempy/commit/6f381c1be050f3ee26d4cbd236b2e2da447c581f))
* **object_detection:** Fix image detection ([`cc5c8de`](https://github.com/fhempy/fhempy/commit/cc5c8defa3457d5a60d812c062623654ed3b0e9e))
* **esphome:** Fix restart ([`be47a72`](https://github.com/fhempy/fhempy/commit/be47a7221fc1814c091992393652c4c767a8b203))

## v0.1.39 (2021-01-29)
### Feature
* **xiaomi_gateway3:** Support motion sensor ([`478db7a`](https://github.com/fhempy/fhempy/commit/478db7ad578ae6fef5a18066b2a4058fe561f745))
* **tuya:** Support another heating device ([`8843138`](https://github.com/fhempy/fhempy/commit/884313823231407a2155518cc01d04930246313c))

## v0.1.38 (2021-01-28)
### Fix
* **eq3bt:** Fix set temperatureOffset ([`429afcd`](https://github.com/fhempy/fhempy/commit/429afcd4f61f17b248dce60161d7418ec5770a54))

## v0.1.37 (2021-01-28)
### Fix
* **xiaomi_gateway3:** Add missing imports ([`b54aa4a`](https://github.com/fhempy/fhempy/commit/b54aa4a2529f1c7c23c3bfbb457c05790dcc0014))
* **fhempy:** Set IODev after CommandDefine ([`b1a1299`](https://github.com/fhempy/fhempy/commit/b1a12993b76cebe3949f510add7a7e1857b91869))

### Documentation
* Remove useless stuff ([`7401907`](https://github.com/fhempy/fhempy/commit/74019075190fb53b2cc7fdf6e4721360a698974e))

## v0.1.31 (2021-01-27)
### Feature
* **tuya:** Add keep_connected attr ([`b2c1ca4`](https://github.com/fhempy/fhempy/commit/b2c1ca47cf1b7adda9eb86731f21e0f755cf3dcd))

## v0.1.30 (2021-01-27)
### Fix
* **xiaomi_gateway3:** Remove unused imports ([`1758909`](https://github.com/fhempy/fhem_pythonbinding/commit/175890932f4efeeedba79ae6b2d1dfe81839abcc))

## v0.1.29 (2021-01-27)
### Fix
* **xiaomi_gateway3:** Add import time ([`7ef7a9e`](https://github.com/fhempy/fhem_pythonbinding/commit/7ef7a9ecabb2e8f765f6e1223bcaaaed365c6644))
* **xiaomi_gateway3:** Set last_update on update ([`146487d`](https://github.com/fhempy/fhem_pythonbinding/commit/146487daf69f9ed5219043c444fdfbac9f90021c))

## v0.1.28 (2021-01-27)
### Feature
* New reading pairing on/off ([`ee42b9c`](https://github.com/fhempy/fhem_pythonbinding/commit/ee42b9c1dc822993ee882e94be056b311f87bd8e))

## v0.1.27 (2021-01-27)
### Fix
* Pychromecast min version ([`8a58a53`](https://github.com/fhempy/fhem_pythonbinding/commit/8a58a5374c25ffcaf1f3c9a9f37b5ebb83272d96))
