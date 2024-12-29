# CHANGELOG


## v0.1.745 (2024-12-29)

### Bug Fixes

- **tuya_smartlife**: Update lib to 0.2.1
  ([`be6f26f`](https://github.com/fhempy/fhempy/commit/be6f26fd790abc57aeee83985a01356c68cc5772))


## v0.1.744 (2024-12-29)

### Chores

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#477](https://github.com/fhempy/fhempy/pull/477),
  [`3c09521`](https://github.com/fhempy/fhempy/commit/3c095214cae72b582565d0c3b7c90a02dd48c14d))

- **deps**: Bump shogo82148/actions-setup-perl from 1.31.3 to 1.31.4
  ([#467](https://github.com/fhempy/fhempy/pull/467),
  [`3eeceb2`](https://github.com/fhempy/fhempy/commit/3eeceb205935649fda212f2e4a188fe94a7a06c8))

- **deps-dev**: Bump pytest-asyncio from 0.23.6 to 0.25.0
  ([#472](https://github.com/fhempy/fhempy/pull/472),
  [`df02781`](https://github.com/fhempy/fhempy/commit/df02781664afbd18d217a3a26580d4ccb7a0da34))

### Features

- **esphome**: Update to 2024.12.2
  ([`e8cf875`](https://github.com/fhempy/fhempy/commit/e8cf87594ab39e88336de20af84182d84a2a1f63))

- **esphome**: Update to 2024.12.2
  ([`fbdcef1`](https://github.com/fhempy/fhempy/commit/fbdcef10a2a5676d3a12fd0a50d1432038f05e5b))


## v0.1.743 (2024-11-12)

### Bug Fixes

- **huawei_modbus**: Add 60s sleep before reconnect
  ([`1890639`](https://github.com/fhempy/fhempy/commit/18906394cfc8f38487f0b1b6d6383baa26a11df9))

- **tuya_smartlife**: Fix for TypeError: 'DeviceFunction' object is not subscriptable'
  ([#465](https://github.com/fhempy/fhempy/pull/465),
  [`65c5fae`](https://github.com/fhempy/fhempy/commit/65c5faebae40c329f2b6723d9f6beaac2c54acc5))

- **zigbee2mqtt**: Fix nodejs installations with nvm
  ([`4c1858a`](https://github.com/fhempy/fhempy/commit/4c1858aee136cda810274609059d12d1f78f2e3f))

- **zigbee2mqtt**: Revert last commits
  ([`38e3558`](https://github.com/fhempy/fhempy/commit/38e35584c21a71eef9791b0770c16a48b1ec29ce))

- **zigbee2mqtt**: Support nvm installations
  ([`2f3d17a`](https://github.com/fhempy/fhempy/commit/2f3d17a5eac0d8500942a3c68a1cf536d29e16a8))

### Chores

- **deps**: Bump certifi from 2024.2.2 to 2024.7.4
  ([#438](https://github.com/fhempy/fhempy/pull/438),
  [`c34bdb6`](https://github.com/fhempy/fhempy/commit/c34bdb6dd268a7e355692bb9600952bd283bc3c7))

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#444](https://github.com/fhempy/fhempy/pull/444),
  [`c953566`](https://github.com/fhempy/fhempy/commit/c95356630e2a448a2c72e89ba42bf708f042999a))

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#462](https://github.com/fhempy/fhempy/pull/462),
  [`f30049d`](https://github.com/fhempy/fhempy/commit/f30049dabfd590e5bc2dbca5a72a91a0b6489e2c))

Bumps
  [python-semantic-release/python-semantic-release](https://github.com/python-semantic-release/python-semantic-release)
  from 9.8.5 to 9.12.0. - [Release
  notes](https://github.com/python-semantic-release/python-semantic-release/releases) -
  [Changelog](https://github.com/python-semantic-release/python-semantic-release/blob/master/CHANGELOG.md)
  -
  [Commits](https://github.com/python-semantic-release/python-semantic-release/compare/v9.8.5...v9.12.0)

--- updated-dependencies: - dependency-name: python-semantic-release/python-semantic-release
  dependency-type: direct:production

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump requests from 2.31.0 to 2.32.2 ([#443](https://github.com/fhempy/fhempy/pull/443),
  [`fd1c86e`](https://github.com/fhempy/fhempy/commit/fd1c86eaa39e77dac92d04c8ca2f1a870b9632c6))

- **deps**: Bump shogo82148/actions-setup-perl from 1.29.0 to 1.30.0
  ([#436](https://github.com/fhempy/fhempy/pull/436),
  [`a990dd2`](https://github.com/fhempy/fhempy/commit/a990dd2ea5d16cb038cb4f94f6d7c4f63699474a))

- **deps**: Bump shogo82148/actions-setup-perl from 1.30.0 to 1.31.3
  ([#457](https://github.com/fhempy/fhempy/pull/457),
  [`d4d078c`](https://github.com/fhempy/fhempy/commit/d4d078cb35f0dcebfecac236a8050bc591353a32))

- **deps**: Bump urllib3 from 2.2.1 to 2.2.2 ([#437](https://github.com/fhempy/fhempy/pull/437),
  [`9195575`](https://github.com/fhempy/fhempy/commit/9195575e8f957efae1d5948682cbf5cd12ae121d))

- **deps**: Bump zipp from 3.18.1 to 3.19.1 ([#440](https://github.com/fhempy/fhempy/pull/440),
  [`ec35a43`](https://github.com/fhempy/fhempy/commit/ec35a43044b39f797a575d1792dc22190dc776ba))

- **deps-dev**: Bump btsocket from 0.2.0 to 0.3.0
  ([#447](https://github.com/fhempy/fhempy/pull/447),
  [`e8eeab2`](https://github.com/fhempy/fhempy/commit/e8eeab2b5cc6661d8f0f0a4ce88f9e9e5febfb62))

- **deps-dev**: Bump goodwe from 0.4.0 to 0.4.8 ([#450](https://github.com/fhempy/fhempy/pull/450),
  [`238b382`](https://github.com/fhempy/fhempy/commit/238b382543267e4d80881e183f86a8e106df92be))

- **deps-dev**: Bump pytest from 8.1.1 to 8.2.2 ([#442](https://github.com/fhempy/fhempy/pull/442),
  [`43c9f27`](https://github.com/fhempy/fhempy/commit/43c9f27fd8ca4372aaaef4de8664c9ed65ab28e7))

- **deps-dev**: Bump setuptools from 69.5.1 to 70.0.0
  ([#441](https://github.com/fhempy/fhempy/pull/441),
  [`b64f2d0`](https://github.com/fhempy/fhempy/commit/b64f2d0377d00f0d13b208279d246b553d77650c))

- **deps-dev**: Bump tox from 4.14.2 to 4.15.1 ([#435](https://github.com/fhempy/fhempy/pull/435),
  [`25dccd1`](https://github.com/fhempy/fhempy/commit/25dccd1dd017428be357f76e332732186d151146))

- **deps-dev**: Bump tqdm from 4.66.2 to 4.66.3 ([#420](https://github.com/fhempy/fhempy/pull/420),
  [`1031c0c`](https://github.com/fhempy/fhempy/commit/1031c0c714bc974b0feffe8077218ce041e6cd4c))

### Features

- **pyit600**: Reading for current_humidity added
  ([#458](https://github.com/fhempy/fhempy/pull/458),
  [`ae91811`](https://github.com/fhempy/fhempy/commit/ae918117784d995c4cd46b131746545cb898a910))

* Add reading current humidity

* Update README.md

Add SQ610RF to supported devices


## v0.1.742 (2024-05-09)

### Bug Fixes

- **ring**: Update ring_doorbell to 0.8.11 ([#428](https://github.com/fhempy/fhempy/pull/428),
  [`394910c`](https://github.com/fhempy/fhempy/commit/394910ca7d9cb3acc3b46f4b5b48f9bac75dd798))

Update ring_doorbell to 0.8.11

### Chores

- **deps-dev**: Bump esphome from 2024.3.2 to 2024.4.2
  ([#418](https://github.com/fhempy/fhempy/pull/418),
  [`666d2d3`](https://github.com/fhempy/fhempy/commit/666d2d3eba41643a8ea6f459e4c5f23bd30fc815))

- **deps-dev**: Bump goodwe from 0.3.1 to 0.4.0 ([#424](https://github.com/fhempy/fhempy/pull/424),
  [`1c390bb`](https://github.com/fhempy/fhempy/commit/1c390bb3c58650fc0bb2ace79ab30e4d0c993c4f))


## v0.1.741 (2024-05-04)

### Bug Fixes

- **volvo**: Fixing broken Volvo integration ([#422](https://github.com/fhempy/fhempy/pull/422),
  [`4336a52`](https://github.com/fhempy/fhempy/commit/4336a52cc560835f36a3b9f082399f13bd9909a6))

* bugfix: added support for Volvo API v2

feat: adding more car information

* fix: fixing commands invocation for volvo API v2

### Chores

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#416](https://github.com/fhempy/fhempy/pull/416),
  [`f2ff9d3`](https://github.com/fhempy/fhempy/commit/f2ff9d37c3adfc1943fc73b86be068a116187019))

- **deps-dev**: Bump bluetooth-auto-recovery from 1.4.0 to 1.4.1
  ([#410](https://github.com/fhempy/fhempy/pull/410),
  [`835ec0f`](https://github.com/fhempy/fhempy/commit/835ec0fa5cac54a09402ccce79329635562b43f6))

- **deps-dev**: Bump bluetooth-auto-recovery from 1.4.1 to 1.4.2
  ([#411](https://github.com/fhempy/fhempy/pull/411),
  [`ab92f18`](https://github.com/fhempy/fhempy/commit/ab92f188fe151c5263d48139d77a38c1873f630b))

- **deps-dev**: Bump gitpython from 3.1.41 to 3.1.43
  ([#415](https://github.com/fhempy/fhempy/pull/415),
  [`8e0bb34`](https://github.com/fhempy/fhempy/commit/8e0bb34c1efeca720763a7d4056e26c48526dafe))

- **deps-dev**: Bump meross-iot from 0.4.6.2 to 0.4.7.1
  ([#413](https://github.com/fhempy/fhempy/pull/413),
  [`232c0e1`](https://github.com/fhempy/fhempy/commit/232c0e184ea768045eaffe6a6a84035eb8c0c809))

- **deps-dev**: Bump playwright from 1.42.0 to 1.43.0
  ([#409](https://github.com/fhempy/fhempy/pull/409),
  [`5aa5a0d`](https://github.com/fhempy/fhempy/commit/5aa5a0db45cce14b1a302866b9931af65215c39f))

- **deps-dev**: Bump setuptools from 69.2.0 to 69.5.1
  ([#408](https://github.com/fhempy/fhempy/pull/408),
  [`fbcf8d6`](https://github.com/fhempy/fhempy/commit/fbcf8d6348fb3b46b8535f01fc4e4e440dea4283))


## v0.1.740 (2024-04-20)

### Bug Fixes

- **github_backup**: Fix SVG location
  ([`31e861c`](https://github.com/fhempy/fhempy/commit/31e861c61f88e9259076137bb75c81201e2a8d47))


## v0.1.739 (2024-04-20)

### Bug Fixes

- **github_backup**: Fix backup of files
  ([`7918a3e`](https://github.com/fhempy/fhempy/commit/7918a3eb0aa6128e592a87ec97bd3cb1c93091b4))

### Chores

- Add recommendation for python 3.11
  ([`541735f`](https://github.com/fhempy/fhempy/commit/541735f646b12ff5824d10878c948a8725af4d62))

- **deps**: Bump aiohttp from 3.9.3 to 3.9.5 ([#406](https://github.com/fhempy/fhempy/pull/406),
  [`57d2017`](https://github.com/fhempy/fhempy/commit/57d201727503ca11b2c6ebbf11e9e72d45c04d7d))

- **deps**: Bump idna from 3.6 to 3.7 ([#402](https://github.com/fhempy/fhempy/pull/402),
  [`cd11e8c`](https://github.com/fhempy/fhempy/commit/cd11e8c10aa4c590d7631b1bcbe3e1d7220c6fe9))

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#403](https://github.com/fhempy/fhempy/pull/403),
  [`63831fb`](https://github.com/fhempy/fhempy/commit/63831fbf2df9d76b95babe1c91267046cfb97190))

- **deps-dev**: Bump luma-led-matrix from 1.7.0 to 1.7.1
  ([#400](https://github.com/fhempy/fhempy/pull/400),
  [`dc9d88e`](https://github.com/fhempy/fhempy/commit/dc9d88e24952bc034a25951a3c4f513966faabb5))

- **deps-dev**: Bump lxml from 5.1.0 to 5.2.1 ([#395](https://github.com/fhempy/fhempy/pull/395),
  [`d3d8a52`](https://github.com/fhempy/fhempy/commit/d3d8a529ce1b9d7095aa328ef906cc2841e2a135))


## v0.1.738 (2024-04-14)

### Bug Fixes

- **tibber**: Fix tibber version
  ([`2eb9729`](https://github.com/fhempy/fhempy/commit/2eb9729886fde1294935a2078c624d60e2778da7))


## v0.1.737 (2024-04-12)

### Bug Fixes

- **prusalink**: Fix connection with httpx
  ([`b1f311d`](https://github.com/fhempy/fhempy/commit/b1f311d7d9114792cb47d243f95b75e07813fe5f))

- **prusalink**: Remove state value
  ([`e3e4238`](https://github.com/fhempy/fhempy/commit/e3e4238020853056811dc150fffeb116319eb16c))

### Chores

- Fix httpx dependency
  ([`6006efa`](https://github.com/fhempy/fhempy/commit/6006efaa05343cdd7e56c1b7d08720e2a62314ff))

- **deps-dev**: Bump bluetooth-auto-recovery from 1.3.0 to 1.4.0
  ([#401](https://github.com/fhempy/fhempy/pull/401),
  [`59883b4`](https://github.com/fhempy/fhempy/commit/59883b4f240e1be84f48da344887b929d5631cdb))


## v0.1.736 (2024-04-09)

### Bug Fixes

- **piclock**: Fix text_size return value
  ([`2c8646d`](https://github.com/fhempy/fhempy/commit/2c8646d29bb2a3e408da0479c0d5760b964db3cc))


## v0.1.735 (2024-04-09)

### Bug Fixes

- **piclock**: Fix textsize => textlength
  ([`ffd4bff`](https://github.com/fhempy/fhempy/commit/ffd4bff18ffe25ca228228c903806a23df99259e))

### Chores

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#396](https://github.com/fhempy/fhempy/pull/396),
  [`a3373c6`](https://github.com/fhempy/fhempy/commit/a3373c679045a2917f48a2b7905d81cd1230da29))

- **deps-dev**: Bump esphome from 2024.3.1 to 2024.3.2
  ([#394](https://github.com/fhempy/fhempy/pull/394),
  [`a890c43`](https://github.com/fhempy/fhempy/commit/a890c43217289e290909220af0be94d96d8867e0))

- **deps-dev**: Bump tox from 4.14.1 to 4.14.2 ([#397](https://github.com/fhempy/fhempy/pull/397),
  [`5ec54d2`](https://github.com/fhempy/fhempy/commit/5ec54d24eb82f14923f343201beb6f9f75392b20))


## v0.1.734 (2024-04-08)

### Bug Fixes

- **tibber**: Fix integration ([#399](https://github.com/fhempy/fhempy/pull/399),
  [`7eb60c2`](https://github.com/fhempy/fhempy/commit/7eb60c2c5e5743200fd076a247f263123e9ca342))


## v0.1.733 (2024-04-07)

### Bug Fixes

- **homekit**: Update values before update_readings
  ([`2175e96`](https://github.com/fhempy/fhempy/commit/2175e96879f1b963a3ec63a264e7e3c9595484b1))


## v0.1.732 (2024-04-06)

### Bug Fixes

- **esphome**: Fix startup in certain conditions
  ([`4cdd9ac`](https://github.com/fhempy/fhempy/commit/4cdd9acce5e7250e2a3a133ec748d1a992083dc5))


## v0.1.731 (2024-04-06)

### Bug Fixes

- **alphaess**: Fixed usage info in readme and FHEM info
  ([#388](https://github.com/fhempy/fhempy/pull/388),
  [`be634ec`](https://github.com/fhempy/fhempy/commit/be634ec7f86e77d5130f0a128e43e737789a5716))

- **fhempy**: Update dependencies in toml
  ([`761928d`](https://github.com/fhempy/fhempy/commit/761928daf81c6a95ad9f83b09bbde68ffd8a4597))

### Chores

- Add infos on how to add tuya readings from datapoints
  ([#384](https://github.com/fhempy/fhempy/pull/384),
  [`bf8f182`](https://github.com/fhempy/fhempy/commit/bf8f182d68209f58d26a8a73d1127eeb295c89ca))

* Add infos on how to add tuya readings from datapoints

* typo/formatting

* typo / add fhem command

* add more info for tuya

- Fix dependencies
  ([`4dd4023`](https://github.com/fhempy/fhempy/commit/4dd4023f752509a0c7bbd5a47967cbbb2627f2ba))

- Fix tibber test
  ([`7aa3511`](https://github.com/fhempy/fhempy/commit/7aa3511176bc1b12d537b9f35f084008a0923329))

- Remove pybluez from deps, as it wasn't released yet
  ([`2a4d295`](https://github.com/fhempy/fhempy/commit/2a4d295426bb12e3af5bcb1e8937c2e5442efb27))

- **deps**: Update async-upnp-client requirement from 0.38.1 to 0.38.3
  ([#389](https://github.com/fhempy/fhempy/pull/389),
  [`2c49d43`](https://github.com/fhempy/fhempy/commit/2c49d43d96b38c92a083096e9bfb500e16ae7617))

- **deps**: Update packaging requirement from 23.2 to 24.0
  ([#390](https://github.com/fhempy/fhempy/pull/390),
  [`9f81340`](https://github.com/fhempy/fhempy/commit/9f8134010aeb6513d9913d6218cc4ef6fe512b31))

- **deps-dev**: Bump pillow from 10.2.0 to 10.3.0
  ([#393](https://github.com/fhempy/fhempy/pull/393),
  [`c904492`](https://github.com/fhempy/fhempy/commit/c904492766490eb0a9224a9c65b4318cba4237a6))

- **deps-dev**: Update esphome requirement from ==2024.2.2 to ==2024.3.1
  ([#385](https://github.com/fhempy/fhempy/pull/385),
  [`a0f89c1`](https://github.com/fhempy/fhempy/commit/a0f89c10a9f6237e2bd2b0234515f48733888e16))

- **deps-dev**: Update pyprusalink requirement from ==2.0.1 to ==2.1.1
  ([#386](https://github.com/fhempy/fhempy/pull/386),
  [`7dc6bdd`](https://github.com/fhempy/fhempy/commit/7dc6bddc21b16c7f42797721ac568223dab3c0c3))

- **deps-dev**: Update pytest-env requirement from 1.1.0 to 1.1.3
  ([#387](https://github.com/fhempy/fhempy/pull/387),
  [`0f57879`](https://github.com/fhempy/fhempy/commit/0f578799e6644822e2e94b846f4f5a4cc27a7019))

- **deps-dev**: Update requests-mock requirement from 1.11.0 to 1.12.1
  ([#391](https://github.com/fhempy/fhempy/pull/391),
  [`209038d`](https://github.com/fhempy/fhempy/commit/209038de1a0862e8ff4c78be50b202b051d7837c))

### Features

- **homekit**: Update readings every "interval" seconds, support bool and string set
  ([`7e20713`](https://github.com/fhempy/fhempy/commit/7e20713980408ddad7040a843c543293fd7ebe49))


## v0.1.730 (2024-04-01)

### Chores

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#382](https://github.com/fhempy/fhempy/pull/382),
  [`05b3884`](https://github.com/fhempy/fhempy/commit/05b38845468ab1fe7d0c4c6b6d424965dc849094))

- **deps-dev**: Update hyundai-kia-connect-api requirement from ==3.17.5 to ==3.19.1
  ([#381](https://github.com/fhempy/fhempy/pull/381),
  [`80d5ad1`](https://github.com/fhempy/fhempy/commit/80d5ad18b02f8345f50cebbcde5dc02a224de81b))

- **deps-dev**: Update pytest-mock requirement from 3.12.0 to 3.14.0
  ([#379](https://github.com/fhempy/fhempy/pull/379),
  [`e01570d`](https://github.com/fhempy/fhempy/commit/e01570d30fbb6bd6fbd055b789f7cbe6ea31dbd4))

- **deps-dev**: Update setuptools requirement from ==69.1.1 to ==69.2.0
  ([#380](https://github.com/fhempy/fhempy/pull/380),
  [`fc43440`](https://github.com/fhempy/fhempy/commit/fc4344002a8bfb4f5918e05732aa931adbcf4d76))

### Features

- **alphaesscloud**: Support Alpha Ess inverter cloud API
  ([#383](https://github.com/fhempy/fhempy/pull/383),
  [`013ba36`](https://github.com/fhempy/fhempy/commit/013ba361a0ce70e7dd87a9179bf30c441e430190))


## v0.1.729 (2024-03-31)

### Bug Fixes

- **energie_gv_at**: Fix retry on error
  ([`9b2121c`](https://github.com/fhempy/fhempy/commit/9b2121c4fd6b9c068a3871af1f673556e3c2e5b2))

### Chores

- **deps**: Bump python-semantic-release/python-semantic-release from 9.1.1 to 9.3.1
  ([#375](https://github.com/fhempy/fhempy/pull/375),
  [`7629d81`](https://github.com/fhempy/fhempy/commit/7629d81af2a11d85e3988f5af4b718e7294f9aa3))

- **deps**: Update importlib-metadata requirement from 7.0.1 to 7.1.0
  ([#373](https://github.com/fhempy/fhempy/pull/373),
  [`685e9e9`](https://github.com/fhempy/fhempy/commit/685e9e985785a867b25817a158a186074d09e784))

- **deps**: Update markdown2 requirement from 2.4.12 to 2.4.13
  ([#369](https://github.com/fhempy/fhempy/pull/369),
  [`5f57433`](https://github.com/fhempy/fhempy/commit/5f57433eecd16e0c1a3f6580c275a94943917c98))

- **deps-dev**: Update pytest requirement from 8.0.2 to 8.1.1
  ([#367](https://github.com/fhempy/fhempy/pull/367),
  [`1809032`](https://github.com/fhempy/fhempy/commit/1809032292072a51e2ffd8c4354cc7ae0052edaa))

### Features

- **huawei_modbus**: Add reconnect functionality
  ([`b2bbc3a`](https://github.com/fhempy/fhempy/commit/b2bbc3af0676538678f84dcbb05c97a0382c5c51))


## v0.1.728 (2024-03-20)


## v0.1.727 (2024-03-16)

### Bug Fixes

- **github_backup**: Fix helptext
  ([`e6fc0d0`](https://github.com/fhempy/fhempy/commit/e6fc0d049626f3324789123ad8ce70216e594323))

- **piclock**: Add installation details
  ([`65ea1ba`](https://github.com/fhempy/fhempy/commit/65ea1bac80ab55fbdd705a5f70a4b1e04fdc5d78))

### Chores

- **deps-dev**: Update playwright requirement from ==1.41.2 to ==1.42.0
  ([#364](https://github.com/fhempy/fhempy/pull/364),
  [`27d8532`](https://github.com/fhempy/fhempy/commit/27d8532d3bf885cd41f38ed708fda5f2ad961e85))

- **deps-dev**: Update python-dateutil requirement from ==2.8.2 to ==2.9.0.post0
  ([#363](https://github.com/fhempy/fhempy/pull/363),
  [`90c6886`](https://github.com/fhempy/fhempy/commit/90c68864f256ae34e1be34cdbebcec1b0a44fb1d))

- **deps-dev**: Update setuptools requirement from ==69.0.3 to ==69.1.1
  ([#362](https://github.com/fhempy/fhempy/pull/362),
  [`43f3097`](https://github.com/fhempy/fhempy/commit/43f309752797abeb84d11ae8ba857186af54487d))


## v0.1.726 (2024-03-09)

### Features

- **github_backup**: Backup SVG*.gplot files
  ([`0215ea1`](https://github.com/fhempy/fhempy/commit/0215ea1642b1dd0a3f8d2b3a79e4779d369fbdfc))

- **huawei_modbus**: Support interval attribute
  ([`66b4799`](https://github.com/fhempy/fhempy/commit/66b479994b4f6d71eac9846a9dad7d84ff8fa082))


## v0.1.725 (2024-03-07)

### Bug Fixes

- **esphome**: Update library
  ([`2458be6`](https://github.com/fhempy/fhempy/commit/2458be69c2aeee0abe24f9336d48423d6a0db110))

- **esphome**: Update library
  ([`f48c017`](https://github.com/fhempy/fhempy/commit/f48c0176c9df72d9540bab393277e1f807af6d69))

- **fhempy**: Downgrade cryptography
  ([`ba5f542`](https://github.com/fhempy/fhempy/commit/ba5f542c55f4164d8fbde605bf8144afcc659ee5))

- **fhempy**: Fix cryptography dependency
  ([`0fa5770`](https://github.com/fhempy/fhempy/commit/0fa5770e9353e003232b87718d49245b15032eb0))

- **fhempy**: Prevent adding 127.0.1.1 peer
  ([`dedb8df`](https://github.com/fhempy/fhempy/commit/dedb8df6277edd653f660b5bf08d643e91100219))

- **fhempy**: Update zeroconf
  ([`b8181c1`](https://github.com/fhempy/fhempy/commit/b8181c1fa71ff92928ef9d4746b99b764decf60f))

### Chores

- **deps-dev**: Update goodwe requirement from ==0.3.0 to ==0.3.1
  ([#357](https://github.com/fhempy/fhempy/pull/357),
  [`a4b8b32`](https://github.com/fhempy/fhempy/commit/a4b8b32e08e1d58a23aed4898b4dfcb1278b3450))

- **deps-dev**: Update hyundai-kia-connect-api requirement from ==3.17.3 to ==3.17.5
  ([#358](https://github.com/fhempy/fhempy/pull/358),
  [`7fcf6e4`](https://github.com/fhempy/fhempy/commit/7fcf6e4c52f8291488be381b2c273cf41ac78c97))

- **deps-dev**: Update tox requirement from 4.12.1 to 4.14.1
  ([#361](https://github.com/fhempy/fhempy/pull/361),
  [`397a418`](https://github.com/fhempy/fhempy/commit/397a41818e85e87358d23e327aeb894e1430848b))

### Features

- **fhempy**: Inform about pairing process
  ([`1486dad`](https://github.com/fhempy/fhempy/commit/1486dada37c83e49870223499248cf38e3646d5a))


## v0.1.724 (2024-03-01)

### Chores

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#348](https://github.com/fhempy/fhempy/pull/348),
  [`e32c637`](https://github.com/fhempy/fhempy/commit/e32c637adbfff3ae831b43371e0cae0e9405bf0f))

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#351](https://github.com/fhempy/fhempy/pull/351),
  [`35bfd52`](https://github.com/fhempy/fhempy/commit/35bfd52b62204654e6a0ee857d13a235d798d7d3))

- **deps**: Bump shogo82148/actions-setup-perl from 1.28.0 to 1.29.0
  ([#349](https://github.com/fhempy/fhempy/pull/349),
  [`a06a8b6`](https://github.com/fhempy/fhempy/commit/a06a8b6c7a876435c55c19b6e3b5f7f4fc7fed68))

- **deps-dev**: Update cryptography requirement from ==42.0.2 to ==42.0.5
  ([#354](https://github.com/fhempy/fhempy/pull/354),
  [`38a81e3`](https://github.com/fhempy/fhempy/commit/38a81e37c607e2bbf96137e45b157536048caa26))

- **deps-dev**: Update meross-iot requirement from ==0.4.6.0 to ==0.4.6.2
  ([#346](https://github.com/fhempy/fhempy/pull/346),
  [`620cf69`](https://github.com/fhempy/fhempy/commit/620cf69b4851a3ab3d2235d8b84c97966f802d53))

- **deps-dev**: Update playwright requirement from ==1.41.1 to ==1.41.2
  ([#345](https://github.com/fhempy/fhempy/pull/345),
  [`c48c60c`](https://github.com/fhempy/fhempy/commit/c48c60c4a98ec136be8306ab56e0320863734cc6))

- **deps-dev**: Update pytest requirement from 8.0.0 to 8.0.2
  ([#352](https://github.com/fhempy/fhempy/pull/352),
  [`e3a06c8`](https://github.com/fhempy/fhempy/commit/e3a06c8e41471cf991f2e2f88ec2f8e3b639c807))

- **deps-dev**: Update pytest-mock requirement from 3.11.1 to 3.12.0
  ([#347](https://github.com/fhempy/fhempy/pull/347),
  [`2a7a11e`](https://github.com/fhempy/fhempy/commit/2a7a11e5fdb2197d0c0264ab06fd304339812449))

- **deps-dev**: Update pytz requirement from ==2023.3.post1 to ==2024.1
  ([#353](https://github.com/fhempy/fhempy/pull/353),
  [`53249a6`](https://github.com/fhempy/fhempy/commit/53249a6715ea058ff326746417902628a54a4703))

### Features

- **meross**: Add power, voltage, current readings
  ([`5456fe8`](https://github.com/fhempy/fhempy/commit/5456fe8a581cd7688234385d7851d4a269501e03))


## v0.1.723 (2024-02-17)

### Bug Fixes

- **fhempy**: Add bluetoothctl exit in case of pairing failed
  ([`5ddba8e`](https://github.com/fhempy/fhempy/commit/5ddba8e1294784bd504945fc03a28c72f93675de))

- **fhempy**: Properly handle expect timeout
  ([`b8a1689`](https://github.com/fhempy/fhempy/commit/b8a16899d87d61cb6ed861cd6be4a2920e16b283))

- **fhempy**: Set connection reading to pairing during pairing process
  ([`f10d7cd`](https://github.com/fhempy/fhempy/commit/f10d7cdc32813f3e041bd7cfc0c2da3c40e6a3e7))

- **tuya_smartlife**: Fix save token call
  ([`af37fbd`](https://github.com/fhempy/fhempy/commit/af37fbd43ddc62697c0122dba3b7c55fefb81a81))


## v0.1.722 (2024-02-16)

### Bug Fixes

- **eq3bt**: Fix schedule iteration error
  ([`e826fdf`](https://github.com/fhempy/fhempy/commit/e826fdf26915e41845abcb791483a8d516349758))

- **fhempy**: Add connection_paired reading for bluetooth connections
  ([`2d99f0c`](https://github.com/fhempy/fhempy/commit/2d99f0cc70fdeeb00c25118ebca16fe172f0d090))

- **tuya_smartlife**: Add cryptography dependency
  ([`07add41`](https://github.com/fhempy/fhempy/commit/07add41deeae0fa29390b66cde6b9d020465b75b))

### Chores

- **deps**: Bump fhem/fhem-controls-actions from V2.2.1 to 2.3.0
  ([#336](https://github.com/fhempy/fhempy/pull/336),
  [`ce93812`](https://github.com/fhempy/fhempy/commit/ce9381213d98f6c3d3694ec333c8829af9f48a47))

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#335](https://github.com/fhempy/fhempy/pull/335),
  [`a8faebf`](https://github.com/fhempy/fhempy/commit/a8faebf53fb6f934bd7a3f9a3c765c3f91830990))

- **deps-dev**: Update cryptography requirement from ==41.0.7 to ==42.0.2
  ([#328](https://github.com/fhempy/fhempy/pull/328),
  [`a7d31f8`](https://github.com/fhempy/fhempy/commit/a7d31f8a12f7b625f81d007bced42c855fac57a7))

- **deps-dev**: Update goodwe requirement from ==0.2.33 to ==0.3.0
  ([#329](https://github.com/fhempy/fhempy/pull/329),
  [`4fc42b0`](https://github.com/fhempy/fhempy/commit/4fc42b03673644f1e9fc88ce541d691a491f184a))

- **deps-dev**: Update hyundai-kia-connect-api requirement from ==3.13.2 to ==3.17.3
  ([#342](https://github.com/fhempy/fhempy/pull/342),
  [`2eaba7a`](https://github.com/fhempy/fhempy/commit/2eaba7a9662bb8c82f11ac16008ce33f7c9fa67d))

- **deps-dev**: Update pytest requirement from ^7.4.2 to >=7.4.2,<9.0.0
  ([#320](https://github.com/fhempy/fhempy/pull/320),
  [`129d8db`](https://github.com/fhempy/fhempy/commit/129d8db49b8e5e67f070fda8939dcb6cc35785f4))

- **deps-dev**: Update skodaconnect requirement from ==1.3.9 to ==1.3.10
  ([#343](https://github.com/fhempy/fhempy/pull/343),
  [`be9d2d7`](https://github.com/fhempy/fhempy/commit/be9d2d7b8775cf9057aed41c2415debac612422b))

- **deps-dev**: Update tox requirement from 4.11.3 to 4.12.1
  ([#341](https://github.com/fhempy/fhempy/pull/341),
  [`bd7d8dc`](https://github.com/fhempy/fhempy/commit/bd7d8dc3aa692c3f7d434d1a033ac1502b53ed01))


## v0.1.721 (2024-02-14)

### Bug Fixes

- **fhempy**: Fix bluetooth passkey handling
  ([`0a98d7e`](https://github.com/fhempy/fhempy/commit/0a98d7e3042bb01d4f43fd371571bacd08f0d516))


## v0.1.720 (2024-02-14)

### Bug Fixes

- **bt_presence**: Fix readme ([#332](https://github.com/fhempy/fhempy/pull/332),
  [`7e0149a`](https://github.com/fhempy/fhempy/commit/7e0149a28f52eadcdecaf3d40ab68addbff37cb1))

- **fhempy**: Add check for "devices Paired"
  ([`243436b`](https://github.com/fhempy/fhempy/commit/243436b5d4d75fa9f0afa6148f300fd61d73f79c))

- **fhempy**: Fix peer installation
  ([`45d06ae`](https://github.com/fhempy/fhempy/commit/45d06ae518508fa1ee6776aa0867701d822a526a))

### Chores

- Code style fixes
  ([`3a452e0`](https://github.com/fhempy/fhempy/commit/3a452e08d6f4ebbdc5188f86d9e2e448f1b67011))


## v0.1.719 (2024-02-08)

### Bug Fixes

- **fhempy**: Disable pairing
  ([`72b3b93`](https://github.com/fhempy/fhempy/commit/72b3b9322e2977dfb5f8eb0fefe5a8987afd5621))

- **fhempy**: Fix pairing procedure
  ([`0a55dfe`](https://github.com/fhempy/fhempy/commit/0a55dfe280a1a7df7703c9520a5d7a58a3b2eb77))


## v0.1.718 (2024-02-05)

### Bug Fixes

- **esphome**: Try to run esphome from PATH first
  ([`c982c75`](https://github.com/fhempy/fhempy/commit/c982c753df3947f17ce097c6cc90c771b92d335b))

### Chores

- Set dev dependencies to specific version
  ([`26a86fb`](https://github.com/fhempy/fhempy/commit/26a86fb6d46730edd81f15302d56e041d1a76b34))

- **deps**: Bump shogo82148/actions-setup-perl from 1.27.0 to 1.28.0
  ([#326](https://github.com/fhempy/fhempy/pull/326),
  [`d8f38fb`](https://github.com/fhempy/fhempy/commit/d8f38fb116c6a012bc107986219d589932a1d67c))

- **deps**: Update aiohttp requirement from 3.9.1 to 3.9.3
  ([#324](https://github.com/fhempy/fhempy/pull/324),
  [`386fa80`](https://github.com/fhempy/fhempy/commit/386fa80c67b1c8ee8da5de106caa2b5f49c22e93))

- **deps**: Update async-upnp-client requirement from 0.38.0 to 0.38.1
  ([#319](https://github.com/fhempy/fhempy/pull/319),
  [`1284e7e`](https://github.com/fhempy/fhempy/commit/1284e7e8c4f2805bf6d8f8534131879d7f1cd742))

- **deps-dev**: Update hyundai-kia-connect-api requirement from ==3.12.0 to ==3.13.2
  ([#321](https://github.com/fhempy/fhempy/pull/321),
  [`ee477e9`](https://github.com/fhempy/fhempy/commit/ee477e913612ae8f51ad22f68efd1a55762f5c86))

- **deps-dev**: Update playwright requirement from ==1.41.0 to ==1.41.1
  ([#317](https://github.com/fhempy/fhempy/pull/317),
  [`7e3a6b8`](https://github.com/fhempy/fhempy/commit/7e3a6b83a614e7512acf2c3ec05a9be74c90fe93))

- **deps-dev**: Update pytest-env requirement from 1.0.1 to 1.1.0
  ([#322](https://github.com/fhempy/fhempy/pull/322),
  [`c9bd78e`](https://github.com/fhempy/fhempy/commit/c9bd78ee610bf6aba7c8ff3eabd5e5d14341c3da))

### Features

- Tuya SmartLife integration ([#327](https://github.com/fhempy/fhempy/pull/327),
  [`7325034`](https://github.com/fhempy/fhempy/commit/73250347a78a730f3af1e949139f0ae150b06228))

This integration is based on the SmartLife SDK from Tuya. You need to have all your devices in the
  SmartLife app to use it.


## v0.1.717 (2024-01-28)

### Bug Fixes

- **esphome**: Update esphome ([#315](https://github.com/fhempy/fhempy/pull/315),
  [`220fd97`](https://github.com/fhempy/fhempy/commit/220fd9724d68c8004946efe39adf5d40d120f67c))

### Chores

- **deps**: Bump importlib-metadata from 7.0.0 to 7.0.1
  ([#312](https://github.com/fhempy/fhempy/pull/312),
  [`e1aeb92`](https://github.com/fhempy/fhempy/commit/e1aeb92c34fa6afe75a9263cdf18b91c113f8917))


## v0.1.716 (2024-01-24)

### Bug Fixes

- **fhempy**: Fix return value if no addr available
  ([`5ee0c62`](https://github.com/fhempy/fhempy/commit/5ee0c620450ab68c38ee87bef454651e8fb8ef86))

- **fhempy**: Set state to "connected (no notifications)" if only notifications fail to subscribe
  ([`b81b67a`](https://github.com/fhempy/fhempy/commit/b81b67ad18328589b2f6f6067ed2806ea1c666d8))


## v0.1.715 (2024-01-24)

### Bug Fixes

- **eq3bt**: Fix notification lock
  ([`0bf270c`](https://github.com/fhempy/fhempy/commit/0bf270c40a8fbba064410ad28c4b8890eb731efa))


## v0.1.714 (2024-01-21)

### Features

- **github_restore**: Restore your github backup with this module
  ([`c179425`](https://github.com/fhempy/fhempy/commit/c1794255bbf5a748b3a4ae7ce2f592c13f17fbc7))


## v0.1.713 (2024-01-21)

### Bug Fixes

- **fhempy**: Do bluetooth checks for pairing and conf only when required
  ([`cb8d956`](https://github.com/fhempy/fhempy/commit/cb8d9567e96a3572f02da20a37b6d62ad9b71716))

- **fhempy**: Fix -b argument for bind
  ([`23d2a74`](https://github.com/fhempy/fhempy/commit/23d2a7408492c9cdf88fb6dd1437a71486b84433))


## v0.1.712 (2024-01-21)

### Bug Fixes

- **eq3bt**: Fix if rfkill is not working ([#311](https://github.com/fhempy/fhempy/pull/311),
  [`002ff8b`](https://github.com/fhempy/fhempy/commit/002ff8ba67e7545d5975746c9c08912fba5e05c5))


## v0.1.711 (2024-01-21)

### Bug Fixes

- **eq3bt**: Add notification lock and fix pin usage
  ([#311](https://github.com/fhempy/fhempy/pull/311),
  [`a8072ba`](https://github.com/fhempy/fhempy/commit/a8072ba86105670c91e01c54029a7626d9408b62))

### Chores

- **deps-dev**: Update esphome requirement from ==2023.12.6 to ==2023.12.7
  ([#309](https://github.com/fhempy/fhempy/pull/309),
  [`f2a1123`](https://github.com/fhempy/fhempy/commit/f2a1123b5071abfb584fa94e2f14b87e09a2e8b7))

### Features

- **eq3bt**: Add pairing pin to define
  ([`1b9d8ec`](https://github.com/fhempy/fhempy/commit/1b9d8ec37bf7a6f89fb02319935328436e95c4ed))


## v0.1.710 (2024-01-20)

### Bug Fixes

- **eq3bt**: Fix bt connection
  ([`15d430f`](https://github.com/fhempy/fhempy/commit/15d430f8b0ea57ccaf95efc2760530be296bde25))

- **piclock**: Fix brightness on startup
  ([`ed6a92c`](https://github.com/fhempy/fhempy/commit/ed6a92c68da2a65a502d148e336680212b17c45c))


## v0.1.709 (2024-01-20)

### Bug Fixes

- **fhempy**: Fix lock
  ([`8a1b0e2`](https://github.com/fhempy/fhempy/commit/8a1b0e2871c5fd519aee0ed2767e8d677a848c76))


## v0.1.708 (2024-01-20)

### Bug Fixes

- **fhempy**: Do not run bluetoothctl in parallel
  ([`33fb4d0`](https://github.com/fhempy/fhempy/commit/33fb4d040b5d9e2ad5ef8181da2f774041ab573a))


## v0.1.707 (2024-01-20)

### Bug Fixes

- **fhempy**: Add missing import
  ([`1bac858`](https://github.com/fhempy/fhempy/commit/1bac85833982b7f9e39e51d0e4f57bb32a361e2d))


## v0.1.706 (2024-01-20)

### Bug Fixes

- **fhempy**: Use getpass instead of os
  ([`5c8e4fc`](https://github.com/fhempy/fhempy/commit/5c8e4fc0310acf872f72b213a5d444eee1016ad7))


## v0.1.705 (2024-01-20)

### Bug Fixes

- **fhempy**: Add aiofiles, pexpect for bluetooth pairing
  ([`017c7dc`](https://github.com/fhempy/fhempy/commit/017c7dcfe70399b69a1c761e11974f4769ebf6f2))

### Features

- **eq3bt**: Add pairing functionality with PIN
  ([`9a41859`](https://github.com/fhempy/fhempy/commit/9a418598aa24b6238b4ab0b71b220b6c37b07a14))

- **fhempy**: Add bluetooth pairing function
  ([`978a375`](https://github.com/fhempy/fhempy/commit/978a3751f8ab4d09ec7bffb2a8ef922b3d600399))


## v0.1.704 (2024-01-19)

### Bug Fixes

- **piclock**: Add piclock dependencies
  ([`50516ac`](https://github.com/fhempy/fhempy/commit/50516acc4d517a82acb0f9e3ff79e908b20654b7))

### Chores

- Do not run rpi tests
  ([`f4c7865`](https://github.com/fhempy/fhempy/commit/f4c7865c151180570490d84965faf995eb9895e7))

- Fix rpi.gpio dependency
  ([`69cf7c6`](https://github.com/fhempy/fhempy/commit/69cf7c62b9c836c2ebea21cd4a00498327781cb5))

- Try to fix luma dependency
  ([`b109fb2`](https://github.com/fhempy/fhempy/commit/b109fb2fad4377189fb70adc7ef44d37b25cad47))

### Features

- **piclock**: Create MAX7219 based clock with this module
  ([`b8b4126`](https://github.com/fhempy/fhempy/commit/b8b41264eb966557fc80a63a34f735c3fdcd2835))


## v0.1.703 (2024-01-19)

### Bug Fixes

- **fhempy**: Fix bind parameter ([#295](https://github.com/fhempy/fhempy/pull/295),
  [`cb8b525`](https://github.com/fhempy/fhempy/commit/cb8b525f348b2ff6bb300bdb9845934c69c4e98b))

### Chores

- **deps-dev**: Update playwright requirement from ==1.40.0 to ==1.41.0
  ([#307](https://github.com/fhempy/fhempy/pull/307),
  [`fd21751`](https://github.com/fhempy/fhempy/commit/fd21751f1c8cb1a9ddc8828d68b425575bf9709a))


## v0.1.702 (2024-01-18)

### Bug Fixes

- **skodaconnect**: Support target temperature in 0.5 steps
  ([#308](https://github.com/fhempy/fhempy/pull/308),
  [`11d1c68`](https://github.com/fhempy/fhempy/commit/11d1c6847513d688443bb845f227ef2a3d623e80))

### Chores

- **deps-dev**: Update beautifulsoup4 requirement from ==4.12.2 to ==4.12.3
  ([#306](https://github.com/fhempy/fhempy/pull/306),
  [`e40306b`](https://github.com/fhempy/fhempy/commit/e40306b3b501e88c40b03fed9e7060c97f63eb55))

- **deps-dev**: Update esphome requirement from ==2023.12.5 to ==2023.12.6
  ([#304](https://github.com/fhempy/fhempy/pull/304),
  [`9ef45ca`](https://github.com/fhempy/fhempy/commit/9ef45cad1ff005e8829f693fa35d742abf005fde))

- **deps-dev**: Update pychromecast requirement from ==13.0.8 to ==13.1.0
  ([#305](https://github.com/fhempy/fhempy/pull/305),
  [`dc3e116`](https://github.com/fhempy/fhempy/commit/dc3e1165fe0c436790c3532baa572a24f1e28cd9))


## v0.1.701 (2024-01-17)

### Features

- **fhempy**: Specify bind ip address with -b parameter
  ([`09945e9`](https://github.com/fhempy/fhempy/commit/09945e9ada051c0498734d037673a4c3bc395c2a))


## v0.1.700 (2024-01-14)

### Bug Fixes

- **goodwe**: Fix get_enum_name function
  ([`9d57083`](https://github.com/fhempy/fhempy/commit/9d570839586d808a4cc0bbcaeb426e010a18abed))

### Features

- **goodwe**: Add operation_mode reading
  ([`112681c`](https://github.com/fhempy/fhempy/commit/112681c736fd629f8fba912421c2156f66b1786b))

- **tibber**: Add hourly price entries for today and tomorrow
  ([`61ba9f7`](https://github.com/fhempy/fhempy/commit/61ba9f7a5aae33cfb8e167abb210d12045b0c572))


## v0.1.699 (2024-01-13)

### Chores

- **deps**: Update pycryptodomex requirement from 3.19.1 to 3.20.0
  ([#301](https://github.com/fhempy/fhempy/pull/301),
  [`10fc2fb`](https://github.com/fhempy/fhempy/commit/10fc2fb5fc7114fe917a38da8c30f88c1bb76dc4))

- **deps-dev**: Update bluetooth-auto-recovery requirement from ==1.2.3 to ==1.3.0
  ([#302](https://github.com/fhempy/fhempy/pull/302),
  [`33c47b8`](https://github.com/fhempy/fhempy/commit/33c47b8d511bfe201543acfc216a1102fd92cd06))

- **deps-dev**: Update gitpython requirement from ==3.1.40 to ==3.1.41
  ([#300](https://github.com/fhempy/fhempy/pull/300),
  [`f3de32d`](https://github.com/fhempy/fhempy/commit/f3de32d59cb25ab92384e6418b60cb16e49eefca))

### Features

- **goodwe**: Support set_operation_mode
  ([`f68dbd5`](https://github.com/fhempy/fhempy/commit/f68dbd57aa54a76df297e297cad29d0472a76879))


## v0.1.698 (2024-01-10)

### Bug Fixes

- **fhempy**: Fix gen_fhempdev_name ([#298](https://github.com/fhempy/fhempy/pull/298),
  [`98a7b08`](https://github.com/fhempy/fhempy/commit/98a7b08af7e29d18b83984b03378eb8b902830d4))

fhem device name cannot contain `:`

- **homekit**: Save pairing_data as json ([#297](https://github.com/fhempy/fhempy/pull/297),
  [`16f88ee`](https://github.com/fhempy/fhempy/commit/16f88eeac4bac95b60ff65e186f5f7ed93fdc898))

### Chores

- Update DEVELOPMENT.md ([#296](https://github.com/fhempy/fhempy/pull/296),
  [`c67040a`](https://github.com/fhempy/fhempy/commit/c67040aae6650865b7a79fffe37cfa51b6e09970))

- **deps-dev**: Update lxml requirement from ==5.0.1 to ==5.1.0
  ([#294](https://github.com/fhempy/fhempy/pull/294),
  [`e20809d`](https://github.com/fhempy/fhempy/commit/e20809d5595569b3def9aebb38ca166e38a2afca))


## v0.1.697 (2024-01-08)

### Bug Fixes

- **homekit**: Fix await ([#292](https://github.com/fhempy/fhempy/pull/292),
  [`c108fcb`](https://github.com/fhempy/fhempy/commit/c108fcb95d9f05116cb8dc8a86ced852f26c4146))

### Chores

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#288](https://github.com/fhempy/fhempy/pull/288),
  [`cc0162f`](https://github.com/fhempy/fhempy/commit/cc0162fafcfab692ee56611812cd49eeded181d9))

- **deps-dev**: Update hyundai-kia-connect-api requirement from ==3.11.4 to ==3.12.0
  ([#290](https://github.com/fhempy/fhempy/pull/290),
  [`d7cec1b`](https://github.com/fhempy/fhempy/commit/d7cec1b066439cb6db599f9175136247b9d671e8))

- **deps-dev**: Update lxml requirement from ==5.0.0 to ==5.0.1
  ([#289](https://github.com/fhempy/fhempy/pull/289),
  [`d404eb5`](https://github.com/fhempy/fhempy/commit/d404eb56eea83a4d0e616babfb91be2b36ceb9d0))


## v0.1.696 (2024-01-07)

### Bug Fixes

- **github_backup**: Add coordinator_backup.json for z2m
  ([`8f880ac`](https://github.com/fhempy/fhempy/commit/8f880acdf2481afa70fc511b222167923982d4c4))

- **github_backup**: Add further z2m files
  ([`458e85e`](https://github.com/fhempy/fhempy/commit/458e85e2b3b13f255cafdbc0cc81b414b9d27f2c))


## v0.1.695 (2024-01-05)

### Chores

- Add issue msg
  ([`e1cdcec`](https://github.com/fhempy/fhempy/commit/e1cdcec852aa8699e3cb7be70417243c65fcfe47))

- **deps**: Bump shogo82148/actions-setup-perl from 1.26.0 to 1.27.0
  ([#284](https://github.com/fhempy/fhempy/pull/284),
  [`2f684c5`](https://github.com/fhempy/fhempy/commit/2f684c5021e86deb5e3209edc5ccf5991401006f))

- **deps**: Update pycryptodomex requirement from 3.19.0 to 3.19.1
  ([#281](https://github.com/fhempy/fhempy/pull/281),
  [`161d21e`](https://github.com/fhempy/fhempy/commit/161d21e82aa0f5be13e67f8d769030870d0b78b3))

- **deps-dev**: Update hyundai-kia-connect-api requirement from ==3.11.2 to ==3.11.3
  ([#279](https://github.com/fhempy/fhempy/pull/279),
  [`c754505`](https://github.com/fhempy/fhempy/commit/c7545059613100764bd762b49255e7f6711f7352))

- **deps-dev**: Update hyundai-kia-connect-api requirement from ==3.11.3 to ==3.11.4
  ([#280](https://github.com/fhempy/fhempy/pull/280),
  [`0eb0b32`](https://github.com/fhempy/fhempy/commit/0eb0b32e5851d4ea6fbf092a9d2a5b7b54b7b677))

- **deps-dev**: Update lxml requirement from ==4.9.4 to ==5.0.0
  ([#283](https://github.com/fhempy/fhempy/pull/283),
  [`6073ca6`](https://github.com/fhempy/fhempy/commit/6073ca6ac65a16288094734b1f9666bf0827ed31))

- **deps-dev**: Update mytoyota requirement from ==1.0.0 to ==1.1.0
  ([#286](https://github.com/fhempy/fhempy/pull/286),
  [`4fda236`](https://github.com/fhempy/fhempy/commit/4fda23617f2a9cf6f03af8190f6b3a5cf077d5bc))

- **deps-dev**: Update opencv-python-headless requirement from ==4.8.1.78 to ==4.9.0.80
  ([#282](https://github.com/fhempy/fhempy/pull/282),
  [`1f9ae51`](https://github.com/fhempy/fhempy/commit/1f9ae5143c0d53aa9a9ae55fef16a52130806f0b))

- **deps-dev**: Update pyprusalink requirement from ==2.0.0 to ==2.0.1
  ([#276](https://github.com/fhempy/fhempy/pull/276),
  [`5174c25`](https://github.com/fhempy/fhempy/commit/5174c25e6fd84258e01b9aa3e5f638503ebc3f92))

- **deps-dev**: Update xmodem requirement from ==0.4.6 to ==0.4.7
  ([#277](https://github.com/fhempy/fhempy/pull/277),
  [`3bdbfbf`](https://github.com/fhempy/fhempy/commit/3bdbfbfe649212f0542400f7115f95a8b5660138))


## v0.1.694 (2023-12-27)

### Bug Fixes

- **meross**: Fix meross login
  ([`fb7be37`](https://github.com/fhempy/fhempy/commit/fb7be3707d582da6ebc72411a6f1819228bb0893))

- **tibber**: Fix testcase
  ([`ffbe1cf`](https://github.com/fhempy/fhempy/commit/ffbe1cf768a11fa3acad6d3c404a2eb4bdd137ea))

### Chores

- **deps**: Update importlib-metadata requirement from 7.0.0 to 7.0.1
  ([#271](https://github.com/fhempy/fhempy/pull/271),
  [`d8d9840`](https://github.com/fhempy/fhempy/commit/d8d9840bfd1e0e555345bfc02a802c5298635ca2))

Updates the requirements on [importlib-metadata](https://github.com/python/importlib_metadata) to
  permit the latest version. - [Release
  notes](https://github.com/python/importlib_metadata/releases) -
  [Changelog](https://github.com/python/importlib_metadata/blob/main/NEWS.rst) -
  [Commits](https://github.com/python/importlib_metadata/compare/v7.0.0...v7.0.1)

--- updated-dependencies: - dependency-name: importlib-metadata dependency-type: direct:production

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump aioblescan from 0.2.12 to 0.2.14
  ([#263](https://github.com/fhempy/fhempy/pull/263),
  [`5bf225c`](https://github.com/fhempy/fhempy/commit/5bf225c9e8a75880b9b965b59e6de9afdf64002b))

* chore(deps-dev): bump aioblescan from 0.2.12 to 0.2.14

Bumps [aioblescan](https://github.com/frawau/aioblescan) from 0.2.12 to 0.2.14. - [Release
  notes](https://github.com/frawau/aioblescan/releases) -
  [Commits](https://github.com/frawau/aioblescan/compare/0.2.12...0.2.14)

--- updated-dependencies: - dependency-name: aioblescan dependency-type: direct:development

update-type: version-update:semver-patch

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps-dev**: Bump bluetooth-auto-recovery from 1.0.3 to 1.2.3
  ([#265](https://github.com/fhempy/fhempy/pull/265),
  [`caec13d`](https://github.com/fhempy/fhempy/commit/caec13dd1f32389ded8f24397efc218df6b70de2))

* chore(deps-dev): bump bluetooth-auto-recovery from 1.0.3 to 1.2.3

Bumps [bluetooth-auto-recovery](https://github.com/bluetooth-devices/bluetooth-auto-recovery) from
  1.0.3 to 1.2.3. - [Release
  notes](https://github.com/bluetooth-devices/bluetooth-auto-recovery/releases) -
  [Changelog](https://github.com/Bluetooth-Devices/bluetooth-auto-recovery/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/bluetooth-devices/bluetooth-auto-recovery/compare/v1.0.3...v1.2.3)

--- updated-dependencies: - dependency-name: bluetooth-auto-recovery dependency-type:
  direct:development

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps-dev**: Bump hyundai-kia-connect-api from 3.3.12 to 3.11.2
  ([#262](https://github.com/fhempy/fhempy/pull/262),
  [`4edb9dd`](https://github.com/fhempy/fhempy/commit/4edb9dd0f8792f9728858470e385989718b74eb0))

* chore(deps-dev): bump hyundai-kia-connect-api from 3.3.12 to 3.11.2

Bumps [hyundai-kia-connect-api](https://github.com/fuatakgun/hyundai_kia_connect_api) from 3.3.12 to
  3.11.2. - [Release notes](https://github.com/fuatakgun/hyundai_kia_connect_api/releases) -
  [Commits](https://github.com/fuatakgun/hyundai_kia_connect_api/compare/v3.3.12...v3.11.2)

--- updated-dependencies: - dependency-name: hyundai-kia-connect-api dependency-type:
  direct:development

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps-dev**: Bump micloud from 0.5 to 0.6 ([#264](https://github.com/fhempy/fhempy/pull/264),
  [`1724bed`](https://github.com/fhempy/fhempy/commit/1724bedbbe713015e36d94f6c05c067f1804734d))

* chore(deps-dev): bump micloud from 0.5 to 0.6

Bumps [micloud](https://github.com/squachen/micloud) from 0.5 to 0.6. - [Release
  notes](https://github.com/squachen/micloud/releases) -
  [Commits](https://github.com/squachen/micloud/compare/v_0.5...v_0.6)

--- updated-dependencies: - dependency-name: micloud dependency-type: direct:development

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps-dev**: Update bleak requirement from ==0.19.5 to ==0.20.2
  ([#272](https://github.com/fhempy/fhempy/pull/272),
  [`50a7819`](https://github.com/fhempy/fhempy/commit/50a7819b8c4e45d0645497a1177e70018bcb79e2))

* chore(deps-dev): update bleak requirement from ==0.19.5 to ==0.20.2

Updates the requirements on [bleak](https://github.com/hbldh/bleak) to permit the latest version. -
  [Release notes](https://github.com/hbldh/bleak/releases) -
  [Changelog](https://github.com/hbldh/bleak/blob/develop/CHANGELOG.rst) -
  [Commits](https://github.com/hbldh/bleak/compare/v0.19.5...v0.20.2)

--- updated-dependencies: - dependency-name: bleak dependency-type: direct:development

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps-dev**: Update bleparser requirement from ==2.0.0 to ==3.7.1
  ([#269](https://github.com/fhempy/fhempy/pull/269),
  [`eadb9b6`](https://github.com/fhempy/fhempy/commit/eadb9b62dd346c471c85b1c5ab0f7f4d398d225c))

* chore(deps-dev): update bleparser requirement from ==2.0.0 to ==3.7.1

Updates the requirements on [bleparser](https://github.com/Ernst79/bleparser) to permit the latest
  version. - [Release notes](https://github.com/Ernst79/bleparser/releases) -
  [Commits](https://github.com/Ernst79/bleparser/compare/2.0.0...3.7.1)

--- updated-dependencies: - dependency-name: bleparser dependency-type: direct:development

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps-dev**: Update greeclimate requirement from ==1.2.1 to ==1.4.1
  ([#270](https://github.com/fhempy/fhempy/pull/270),
  [`cfc79bb`](https://github.com/fhempy/fhempy/commit/cfc79bbf1c6b34512f17bb7b4aec4b1eb79cb0a7))

* chore(deps-dev): update greeclimate requirement from ==1.2.1 to ==1.4.1

Updates the requirements on [greeclimate](https://github.com/cmroche/greeclimate) to permit the
  latest version. - [Release notes](https://github.com/cmroche/greeclimate/releases) -
  [Changelog](https://github.com/cmroche/greeclimate/blob/master/CHANGELOG.md) -
  [Commits](https://github.com/cmroche/greeclimate/compare/v1.2.1...v1.4.1)

--- updated-dependencies: - dependency-name: greeclimate dependency-type: direct:development

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps-dev**: Update ring-doorbell requirement from ==0.8.4 to ==0.8.5
  ([#273](https://github.com/fhempy/fhempy/pull/273),
  [`332845e`](https://github.com/fhempy/fhempy/commit/332845e439d8149f5aff0c1f1b0005bac9d5b018))

* chore(deps-dev): update ring-doorbell requirement

Updates the requirements on [ring-doorbell](https://github.com/tchellomello/python-ring-doorbell) to
  permit the latest version. - [Release
  notes](https://github.com/tchellomello/python-ring-doorbell/releases) -
  [Changelog](https://github.com/tchellomello/python-ring-doorbell/blob/master/CHANGELOG.rst) -
  [Commits](https://github.com/tchellomello/python-ring-doorbell/compare/0.8.4...0.8.5)

--- updated-dependencies: - dependency-name: ring-doorbell dependency-type: direct:development

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>


## v0.1.693 (2023-12-25)

### Bug Fixes

- **tibber**: Fix realtime data
  ([`7644815`](https://github.com/fhempy/fhempy/commit/764481545404240c9b5d8b519b922917bd7d0cfb))

### Chores

- Fix version detection
  ([`b5e1c3e`](https://github.com/fhempy/fhempy/commit/b5e1c3e91cdaa550aed21493ee100d05176ee8eb))

- Remove dependency sync with lock file
  ([`9af3f32`](https://github.com/fhempy/fhempy/commit/9af3f3289294fc321e0595fb3aac66736b9ceec8))

- Remove lock file to prevent dependency locking
  ([`051eaf3`](https://github.com/fhempy/fhempy/commit/051eaf34f816627dfaa0a6ab950c85424792027e))

- Update dependencies
  ([`4e0d4a8`](https://github.com/fhempy/fhempy/commit/4e0d4a86aff5c4db98b53d378190fdb1daeaae55))


## v0.1.692 (2023-12-25)

### Chores

- Add ifaddr zeroconf dependency
  ([`7b0322a`](https://github.com/fhempy/fhempy/commit/7b0322a262d65241d0a26d40896863588cab9421))

- Update zeroconf and websockets
  ([`6beb29c`](https://github.com/fhempy/fhempy/commit/6beb29c00a885e7892e8bd31d9a17c904d4de707))


## v0.1.691 (2023-12-25)

### Bug Fixes

- **tibber**: Fix testcase
  ([`395e8ca`](https://github.com/fhempy/fhempy/commit/395e8caa601b0d93f2bd81b394238bb24e8a1322))

- **tibber**: Fix testcase
  ([`5b70aa5`](https://github.com/fhempy/fhempy/commit/5b70aa5c8fa92c2be443155119f3f9d2f95a1d7c))

### Chores

- Add python scripts to manage dependencies
  ([`7a3eb5a`](https://github.com/fhempy/fhempy/commit/7a3eb5a374d6735681fb730ed5bdff17682ff6a3))

- Always run tests
  ([`6ffd391`](https://github.com/fhempy/fhempy/commit/6ffd39166436b5de3bde38ee9dea1fd1d029af33))

- Another test for dependency updates
  ([`cf1f5be`](https://github.com/fhempy/fhempy/commit/cf1f5be022e811f633cec20a7d38bae8f67cdaea))

- Another test to update dependencies
  ([`1caea02`](https://github.com/fhempy/fhempy/commit/1caea02a9ca8a82d66018d246377ff18c0869917))

- Another try to push changes
  ([`d244716`](https://github.com/fhempy/fhempy/commit/d244716aab10e0d72a536a53a816a7170207e93e))

- Another workflow test
  ([`7a9b99b`](https://github.com/fhempy/fhempy/commit/7a9b99b1921cb9be4325b1f6dce5f55d23cc2369))

- Change permissions
  ([`0b08d86`](https://github.com/fhempy/fhempy/commit/0b08d8672b52679fa9faa878b1125b0d104ac7ce))

- Dep update fixes
  ([`b5f8363`](https://github.com/fhempy/fhempy/commit/b5f8363ccacd7c2efbbf1ee7d8b00dec81172caa))

- Do not run for pyproject.*
  ([`39a9aef`](https://github.com/fhempy/fhempy/commit/39a9aeff6b77b7c0bf17f43dc23ed323a6ff151c))

- Do tests after update manifest
  ([`a2c9a79`](https://github.com/fhempy/fhempy/commit/a2c9a79e959c4d0307b4dac94f4c994d2f607976))

- Fix checkout
  ([`ee7fd17`](https://github.com/fhempy/fhempy/commit/ee7fd1791038e9cb2dd9a5dd36466dfc8f1e684f))

- Fix dep updates
  ([`fa66b26`](https://github.com/fhempy/fhempy/commit/fa66b268497078de5eff9edaeef17a50f7c8cc8d))

- Fix loop
  ([`a30ab5d`](https://github.com/fhempy/fhempy/commit/a30ab5d1c2d06e1dc33aca4ea94c2618da207f63))

- Fix permission error
  ([`b8450b4`](https://github.com/fhempy/fhempy/commit/b8450b4487dc6f230423f2ad3a319687211a4ca4))

- Fix permissions
  ([`5400128`](https://github.com/fhempy/fhempy/commit/540012857e21d20a30980d95a835403e4e83e6b5))

- Fix permissions
  ([`3b0d59a`](https://github.com/fhempy/fhempy/commit/3b0d59a7e6c56fda70d7a428d81ba0923579af58))

- Further workflow changes
  ([`3d8e3cd`](https://github.com/fhempy/fhempy/commit/3d8e3cda5ad9981a40b5fac3b477211f283f22dd))

- Next try
  ([`5f96cd5`](https://github.com/fhempy/fhempy/commit/5f96cd592e966fbdd8a7a62029e09aca3e4bca31))

- Prevent duplicate checks
  ([`3385cb5`](https://github.com/fhempy/fhempy/commit/3385cb553212512cd9dae242fc01dc6685e2a148))

- Remove dep update
  ([`4f9171b`](https://github.com/fhempy/fhempy/commit/4f9171b00c3e51e2b53ad5734591af8e8293cf0d))

- Remove dependency update from tests.yml
  ([`c452ba7`](https://github.com/fhempy/fhempy/commit/c452ba7f9c86f46829c196343fd4bc55671bfcd6))

- Remove pycryptodome dependency as pycryptodomeex is used
  ([`d390692`](https://github.com/fhempy/fhempy/commit/d390692ea076e93de3b1955f272b5ff03133c9ee))

- Restructure for dep updates
  ([`ea97544`](https://github.com/fhempy/fhempy/commit/ea975448d06413f5cb601dd6b42c700ae2cd03eb))

- Run on manifest.json push
  ([`2d070eb`](https://github.com/fhempy/fhempy/commit/2d070ebc715ecf334c6eec8e33255bc5eaebd1b7))

- Run tests on every branch
  ([`072d092`](https://github.com/fhempy/fhempy/commit/072d09224712b46b924af1b44faaaaf49d8e6b24))

- Some yml updates
  ([`a80a31e`](https://github.com/fhempy/fhempy/commit/a80a31ebf0f508944b970f576e363a2eef8ff50a))

- Test pyproject2manifest on PRs
  ([`38ba28b`](https://github.com/fhempy/fhempy/commit/38ba28b55ca9dc53ef3a6a37c56f56bb3f9afc9d))

- Test update deps on PR
  ([`1ad66a4`](https://github.com/fhempy/fhempy/commit/1ad66a49e3da7393ada7a38e217a2f8be8ec6dff))

- Try reuseable workflow
  ([`ab3895f`](https://github.com/fhempy/fhempy/commit/ab3895f0a2e9bb5d95e749dcf512ba67a9bb1508))

- Update depencies
  ([`9336e19`](https://github.com/fhempy/fhempy/commit/9336e199a4870d0646e59e121f6ccbe6ef6ba3f7))

- Update dependencies
  ([`a3f8090`](https://github.com/fhempy/fhempy/commit/a3f80907097991cf24f7359ec88ec229d787f38b))

- Update manifest dependencies
  ([`d075bf5`](https://github.com/fhempy/fhempy/commit/d075bf5cb54333abda898082126d304a4bbe4ebd))

- Update meross-iot
  ([`5e31948`](https://github.com/fhempy/fhempy/commit/5e319481e712e015630e6ab154dc4983308d415e))

- Update mitemp-bt
  ([`ac82ea2`](https://github.com/fhempy/fhempy/commit/ac82ea2538411eefc930abc3be9f6faeec26d965))

- Update readme to include firmware pairing process
  ([#230](https://github.com/fhempy/fhempy/pull/230),
  [`445b5d8`](https://github.com/fhempy/fhempy/commit/445b5d8563a5a8d82b3d2353426b2c78cdb03097))

- **deps**: Bump importlib-metadata from 6.1.0 to 7.0.0
  ([#261](https://github.com/fhempy/fhempy/pull/261),
  [`67f517a`](https://github.com/fhempy/fhempy/commit/67f517a53b3f98029ea0b6507a5f2afd3e953447))

Bumps [importlib-metadata](https://github.com/python/importlib_metadata) from 6.1.0 to 7.0.0. -
  [Release notes](https://github.com/python/importlib_metadata/releases) -
  [Changelog](https://github.com/python/importlib_metadata/blob/main/NEWS.rst) -
  [Commits](https://github.com/python/importlib_metadata/compare/v6.1.0...v7.0.0)

--- updated-dependencies: - dependency-name: importlib-metadata dependency-type: direct:production

update-type: version-update:semver-major

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump pycryptodomex from 3.18.0 to 3.19.0
  ([#193](https://github.com/fhempy/fhempy/pull/193),
  [`22077f7`](https://github.com/fhempy/fhempy/commit/22077f75c45f54499c5c49d76884abc607caaad0))

* chore(deps): bump pycryptodomex from 3.18.0 to 3.19.0

Bumps [pycryptodomex](https://github.com/Legrandin/pycryptodome) from 3.18.0 to 3.19.0. - [Release
  notes](https://github.com/Legrandin/pycryptodome/releases) -
  [Changelog](https://github.com/Legrandin/pycryptodome/blob/master/Changelog.rst) -
  [Commits](https://github.com/Legrandin/pycryptodome/compare/v3.18.0...v3.19.0)

--- updated-dependencies: - dependency-name: pycryptodomex dependency-type: direct:production

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#266](https://github.com/fhempy/fhempy/pull/266),
  [`ea016f0`](https://github.com/fhempy/fhempy/commit/ea016f0bb26b9a091a6014b2f36f9f9c9fa2b40f))

Bumps
  [python-semantic-release/python-semantic-release](https://github.com/python-semantic-release/python-semantic-release)
  from 8.5.1 to 8.7.0. - [Release
  notes](https://github.com/python-semantic-release/python-semantic-release/releases) -
  [Changelog](https://github.com/python-semantic-release/python-semantic-release/blob/master/CHANGELOG.md)
  -
  [Commits](https://github.com/python-semantic-release/python-semantic-release/compare/v8.5.1...v8.7.0)

--- updated-dependencies: - dependency-name: python-semantic-release/python-semantic-release
  dependency-type: direct:production

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump shogo82148/actions-setup-perl from 1.25.0 to 1.26.0
  ([#268](https://github.com/fhempy/fhempy/pull/268),
  [`629ff46`](https://github.com/fhempy/fhempy/commit/629ff463553a47c3f2501cf6e553026934eb2973))

--- updated-dependencies: - dependency-name: shogo82148/actions-setup-perl dependency-type:
  direct:production

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump asyncio-mqtt from 0.16.1 to 0.16.2
  ([#258](https://github.com/fhempy/fhempy/pull/258),
  [`04d25db`](https://github.com/fhempy/fhempy/commit/04d25db1c38095a4ef822c841cda0e8b0da4e2f6))

* chore(deps-dev): bump asyncio-mqtt from 0.16.1 to 0.16.2

Bumps [asyncio-mqtt](https://github.com/sbtinstruments/asyncio-mqtt) from 0.16.1 to 0.16.2. -
  [Release notes](https://github.com/sbtinstruments/asyncio-mqtt/releases) -
  [Changelog](https://github.com/sbtinstruments/aiomqtt/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/sbtinstruments/asyncio-mqtt/commits)

--- updated-dependencies: - dependency-name: asyncio-mqtt dependency-type: direct:development

update-type: version-update:semver-patch

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps-dev**: Bump bluetooth-adapters from 0.15.2 to 0.16.2
  ([#260](https://github.com/fhempy/fhempy/pull/260),
  [`ab28f88`](https://github.com/fhempy/fhempy/commit/ab28f88e8b437b98188a41ce465390653d25d4c1))

* chore(deps-dev): bump bluetooth-adapters from 0.15.2 to 0.16.2

Bumps [bluetooth-adapters](https://github.com/bluetooth-devices/bluetooth-adapters) from 0.15.2 to
  0.16.2. - [Release notes](https://github.com/bluetooth-devices/bluetooth-adapters/releases) -
  [Changelog](https://github.com/Bluetooth-Devices/bluetooth-adapters/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/bluetooth-devices/bluetooth-adapters/compare/v0.15.2...v0.16.2)

--- updated-dependencies: - dependency-name: bluetooth-adapters dependency-type: direct:development

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps-dev**: Bump goodwe from 0.2.27 to 0.2.33
  ([#267](https://github.com/fhempy/fhempy/pull/267),
  [`5ab6663`](https://github.com/fhempy/fhempy/commit/5ab66631ab878fb6e7c779ed1095c2e24bcee3a7))

* chore(deps-dev): bump goodwe from 0.2.27 to 0.2.33

Bumps [goodwe](https://github.com/marcelblijleven/goodwe) from 0.2.27 to 0.2.33. - [Release
  notes](https://github.com/marcelblijleven/goodwe/releases) -
  [Commits](https://github.com/marcelblijleven/goodwe/compare/v0.2.27...v0.2.33)

--- updated-dependencies: - dependency-name: goodwe dependency-type: direct:development

update-type: version-update:semver-patch

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps-dev**: Bump meross-iot from 0.4.5.7 to 0.4.6.0
  ([#255](https://github.com/fhempy/fhempy/pull/255),
  [`7dad408`](https://github.com/fhempy/fhempy/commit/7dad408fa443050e4244d892a8256f82160b5f9a))

- **deps-dev**: Bump mitemp-bt from 0.0.3 to 0.0.5
  ([#254](https://github.com/fhempy/fhempy/pull/254),
  [`630dc87`](https://github.com/fhempy/fhempy/commit/630dc8771106a3a82a79af60ff20c9881f73716d))

- **deps-dev**: Bump pychromecast from 13.0.7 to 13.0.8
  ([#259](https://github.com/fhempy/fhempy/pull/259),
  [`ed6c319`](https://github.com/fhempy/fhempy/commit/ed6c319150db498fb8e2935a9e3b83d0dfa3ddf3))

* chore(deps-dev): bump pychromecast from 13.0.7 to 13.0.8

Bumps [pychromecast](https://github.com/balloob/pychromecast) from 13.0.7 to 13.0.8. - [Release
  notes](https://github.com/balloob/pychromecast/releases) -
  [Commits](https://github.com/balloob/pychromecast/compare/13.0.7...13.0.8)

--- updated-dependencies: - dependency-name: pychromecast dependency-type: direct:development

update-type: version-update:semver-patch

...

Signed-off-by: dependabot[bot] <support@github.com>

* action: auto update manifest.json

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

- **deps-dev**: Bump pytest-asyncio from 0.21.1 to 0.23.2
  ([#249](https://github.com/fhempy/fhempy/pull/249),
  [`5c6c7d8`](https://github.com/fhempy/fhempy/commit/5c6c7d8808fef1dfa7400520254f96b8f2325eec))

### Features

- **tibber**: Add tibber module ([#222](https://github.com/fhempy/fhempy/pull/222),
  [`7d89477`](https://github.com/fhempy/fhempy/commit/7d89477237d98fd479059b6e7290733fbfdf4f39))


## v0.1.690 (2023-12-19)

### Chores

- Cleanup manifest files
  ([`ca31810`](https://github.com/fhempy/fhempy/commit/ca3181052f6ca27f2a301d6b298134459f5781ff))

- Cleanup manifest files
  ([`5926ded`](https://github.com/fhempy/fhempy/commit/5926ded39aeea0ebe6e4dfd98b5319971002d204))

- Cleanup manifest files
  ([`068640e`](https://github.com/fhempy/fhempy/commit/068640e552b5bc4d973f3cd5adea5266b38cdd06))

- Remove schedule time from dependabot
  ([`aa09be4`](https://github.com/fhempy/fhempy/commit/aa09be45e155e58e6978854233f311571d7caeca))

- Resolve dependencies
  ([`4e44df7`](https://github.com/fhempy/fhempy/commit/4e44df73158a7ce6b3e74af70dafded0157ccf0b))

- Run dependabot daily
  ([`0d6bc27`](https://github.com/fhempy/fhempy/commit/0d6bc27ba5037600fb03e296b1b48cc1b2cf74d3))

- Try to handle libraries with dependabot
  ([`f6c379d`](https://github.com/fhempy/fhempy/commit/f6c379d0889931b30d6e91fbd99fd8250befe06d))

- Update dependencies lock file
  ([`1af3235`](https://github.com/fhempy/fhempy/commit/1af32354c17894ad37391ec4ef2f4fcf9e8cbe09))

- Update manifest files
  ([`fb7ab3e`](https://github.com/fhempy/fhempy/commit/fb7ab3e435e0e497ee9f3b4ae92749ca914d467c))

- Update spotipy
  ([`a90ac1e`](https://github.com/fhempy/fhempy/commit/a90ac1e56348e412c6fcc7a2f16aff14a0eb16a6))

- Update spotipy and paho-mqtt
  ([`4bea873`](https://github.com/fhempy/fhempy/commit/4bea8734df5d8eadf56f8fb20c483e69b237b3ab))

- **deps**: Bump aiohttp from 3.9.0 to 3.9.1 ([#250](https://github.com/fhempy/fhempy/pull/250),
  [`c0f5bce`](https://github.com/fhempy/fhempy/commit/c0f5bcefb6e9a92e23766e01684d9b5be9c4f34f))

Bumps [aiohttp](https://github.com/aio-libs/aiohttp) from 3.9.0 to 3.9.1. - [Release
  notes](https://github.com/aio-libs/aiohttp/releases) -
  [Changelog](https://github.com/aio-libs/aiohttp/blob/master/CHANGES.rst) -
  [Commits](https://github.com/aio-libs/aiohttp/compare/v3.9.0...v3.9.1)

--- updated-dependencies: - dependency-name: aiohttp dependency-type: direct:production

update-type: version-update:semver-patch

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump async-upnp-client from 0.31.2 to 0.38.0
  ([#256](https://github.com/fhempy/fhempy/pull/256),
  [`16d63fe`](https://github.com/fhempy/fhempy/commit/16d63fee9d09a89a134a7b94cdd24b2e83ebd3d1))

Bumps [async-upnp-client](https://github.com/StevenLooman/async_upnp_client) from 0.31.2 to 0.38.0.
  - [Changelog](https://github.com/StevenLooman/async_upnp_client/blob/development/CHANGES.rst) -
  [Commits](https://github.com/StevenLooman/async_upnp_client/compare/0.31.2...0.38.0)

--- updated-dependencies: - dependency-name: async-upnp-client dependency-type: direct:production

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump markdown2 from 2.4.10 to 2.4.12 ([#251](https://github.com/fhempy/fhempy/pull/251),
  [`ede5e10`](https://github.com/fhempy/fhempy/commit/ede5e104fbbd52276b6ecb2a930e13b10356853f))

Bumps [markdown2](https://github.com/trentm/python-markdown2) from 2.4.10 to 2.4.12. -
  [Changelog](https://github.com/trentm/python-markdown2/blob/master/CHANGES.md) -
  [Commits](https://github.com/trentm/python-markdown2/compare/2.4.10...2.4.12)

--- updated-dependencies: - dependency-name: markdown2 dependency-type: direct:production

update-type: version-update:semver-patch

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#252](https://github.com/fhempy/fhempy/pull/252),
  [`c3fc8d9`](https://github.com/fhempy/fhempy/commit/c3fc8d9eae54e42ca8fa5372febb756fe2b75355))

Bumps
  [python-semantic-release/python-semantic-release](https://github.com/python-semantic-release/python-semantic-release)
  from 8.3.0 to 8.5.1. - [Release
  notes](https://github.com/python-semantic-release/python-semantic-release/releases) -
  [Changelog](https://github.com/python-semantic-release/python-semantic-release/blob/master/CHANGELOG.md)
  -
  [Commits](https://github.com/python-semantic-release/python-semantic-release/compare/v8.3.0...v8.5.1)

--- updated-dependencies: - dependency-name: python-semantic-release/python-semantic-release
  dependency-type: direct:production

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>


## v0.1.689 (2023-12-17)

### Bug Fixes

- **fhempy**: Check for venv activate command
  ([`3539c66`](https://github.com/fhempy/fhempy/commit/3539c66094954b8e00433d76526e3c1066e57b2d))

- **skodaconnect**: Update lib
  ([`79eca38`](https://github.com/fhempy/fhempy/commit/79eca38c3567c2e816642190c01e5850454b9353))

### Chores

- Inform about venv requirement
  ([`e7c18d2`](https://github.com/fhempy/fhempy/commit/e7c18d287cb2901370e155ef08e2de1db5df7a0d))

- Missing new line
  ([`43fee61`](https://github.com/fhempy/fhempy/commit/43fee610b83e22c3caa403cb9f4e6d59083e6117))


## v0.1.688 (2023-12-17)


## v0.1.687 (2023-12-17)

### Chores

- Add gh-actions and test some module manifest.json files
  ([`4f6e6a6`](https://github.com/fhempy/fhempy/commit/4f6e6a691b0d08e7965017c6673917f6f30ebe5e))

- **deps**: Bump actions/checkout from 3 to 4 ([#243](https://github.com/fhempy/fhempy/pull/243),
  [`dc167a2`](https://github.com/fhempy/fhempy/commit/dc167a201e5425b00f3e291c1dfa9fcc6019c621))

- **deps**: Bump actions/setup-python from 4 to 5
  ([#244](https://github.com/fhempy/fhempy/pull/244),
  [`9a26482`](https://github.com/fhempy/fhempy/commit/9a2648223c65b0f0db36c6d34fdb8821f5356ed9))

- **deps**: Bump actions/stale from 3 to 9 ([#238](https://github.com/fhempy/fhempy/pull/238),
  [`b09ad38`](https://github.com/fhempy/fhempy/commit/b09ad38cfb1d8e7ab44b7831524fe0ed6739db06))

- **deps**: Bump fhem/fhem-controls-actions from 2.2.0 to 2.2.1
  ([#242](https://github.com/fhempy/fhempy/pull/242),
  [`af9a2c1`](https://github.com/fhempy/fhempy/commit/af9a2c17d041c0c99a62875af4ba828d9414d5a9))

- **deps**: Bump shogo82148/actions-setup-perl from 1.18.0 to 1.25.0
  ([#240](https://github.com/fhempy/fhempy/pull/240),
  [`4aac589`](https://github.com/fhempy/fhempy/commit/4aac5897bd197a23a2304a21581e8fc044b56c45))

- **deps**: Bump websockets from 11.0.3 to 12.0 ([#247](https://github.com/fhempy/fhempy/pull/247),
  [`23d0f0a`](https://github.com/fhempy/fhempy/commit/23d0f0a09d29936fa0eeb06b6d5438728df64001))

Bumps [websockets](https://github.com/python-websockets/websockets) from 11.0.3 to 12.0. - [Release
  notes](https://github.com/python-websockets/websockets/releases) -
  [Commits](https://github.com/python-websockets/websockets/compare/11.0.3...12.0)

--- updated-dependencies: - dependency-name: websockets dependency-type: direct:production

update-type: version-update:semver-major

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump zeroconf from 0.129.0 to 0.130.0
  ([#245](https://github.com/fhempy/fhempy/pull/245),
  [`809890e`](https://github.com/fhempy/fhempy/commit/809890ea59196047843291be1c1c785e655af6ad))

Bumps [zeroconf](https://github.com/python-zeroconf/python-zeroconf) from 0.129.0 to 0.130.0. -
  [Release notes](https://github.com/python-zeroconf/python-zeroconf/releases) -
  [Changelog](https://github.com/python-zeroconf/python-zeroconf/blob/master/CHANGELOG.md) -
  [Commits](https://github.com/python-zeroconf/python-zeroconf/compare/0.129.0...0.130.0)

--- updated-dependencies: - dependency-name: zeroconf dependency-type: direct:production

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump zeroconf from 0.64.1 to 0.129.0 ([#237](https://github.com/fhempy/fhempy/pull/237),
  [`d0d052e`](https://github.com/fhempy/fhempy/commit/d0d052e22a57019d8e251d3848dec90b9f4bac5e))

Bumps [zeroconf](https://github.com/python-zeroconf/python-zeroconf) from 0.64.1 to 0.129.0. -
  [Release notes](https://github.com/python-zeroconf/python-zeroconf/releases) -
  [Changelog](https://github.com/python-zeroconf/python-zeroconf/blob/master/CHANGELOG.md) -
  [Commits](https://github.com/python-zeroconf/python-zeroconf/compare/0.64.1...0.129.0)

--- updated-dependencies: - dependency-name: zeroconf dependency-type: direct:production

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump pytest from 7.4.2 to 7.4.3 ([#239](https://github.com/fhempy/fhempy/pull/239),
  [`6a08efb`](https://github.com/fhempy/fhempy/commit/6a08efbd464c06bc1392d97cceff52a9be947dd0))

- **deps-dev**: Bump pytest-env from 1.0.1 to 1.1.3
  ([#246](https://github.com/fhempy/fhempy/pull/246),
  [`24ba5fe`](https://github.com/fhempy/fhempy/commit/24ba5fefab1e0fe95d261d4e962d657af87ac72c))

- **deps-dev**: Bump tox from 4.11.3 to 4.11.4 ([#241](https://github.com/fhempy/fhempy/pull/241),
  [`d21ec28`](https://github.com/fhempy/fhempy/commit/d21ec2833129c5102ae8cc7002c90fd18080997b))


## v0.1.686 (2023-12-16)

### Bug Fixes

- **prusalink**: Requires python 3.10 or higher
  ([`3082abd`](https://github.com/fhempy/fhempy/commit/3082abdeed0590c2ee9e4939b7ebf05f811a5c57))

### Chores

- Test only with python 3.10 and 3.11
  ([`e5a5fad`](https://github.com/fhempy/fhempy/commit/e5a5fad9cd49b12a19404d24a06e6c42538c1559))

- **deps**: Bump aiohttp from 3.8.6 to 3.9.0 ([#236](https://github.com/fhempy/fhempy/pull/236),
  [`1a18d6a`](https://github.com/fhempy/fhempy/commit/1a18d6a81a0189457269a9752f9ec0bf4042d893))

Bumps [aiohttp](https://github.com/aio-libs/aiohttp) from 3.8.6 to 3.9.0. - [Release
  notes](https://github.com/aio-libs/aiohttp/releases) -
  [Changelog](https://github.com/aio-libs/aiohttp/blob/master/CHANGES.rst) -
  [Commits](https://github.com/aio-libs/aiohttp/compare/v3.8.6...v3.9.0)

--- updated-dependencies: - dependency-name: aiohttp dependency-type: direct:production

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump urllib3 from 2.0.6 to 2.0.7 ([#208](https://github.com/fhempy/fhempy/pull/208),
  [`6376ba5`](https://github.com/fhempy/fhempy/commit/6376ba537d19bbb02b28a4b52bb5b4d5f1454eb1))

Bumps [urllib3](https://github.com/urllib3/urllib3) from 2.0.6 to 2.0.7. - [Release
  notes](https://github.com/urllib3/urllib3/releases) -
  [Changelog](https://github.com/urllib3/urllib3/blob/main/CHANGES.rst) -
  [Commits](https://github.com/urllib3/urllib3/compare/2.0.6...2.0.7)

--- updated-dependencies: - dependency-name: urllib3 dependency-type: indirect

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Features

- **prusalink**: Support prusa 3d printer via prusalink
  ([`6dcea09`](https://github.com/fhempy/fhempy/commit/6dcea093848823f4e1163ad93168bee7cca786db))


## v0.1.685 (2023-12-16)

### Bug Fixes

- **bt_presence**: Update bt_proximity
  ([`8a34a11`](https://github.com/fhempy/fhempy/commit/8a34a11677e1cdf7dcda3833575faf9ed782764a))

- **bt_presence**: Use pybluez from git
  ([`7639626`](https://github.com/fhempy/fhempy/commit/7639626c3b92f194a4f23a99acca7a1a8db96a05))

- **bt_presence**: Use pybluez2 instead of pybluez
  ([`8f5717d`](https://github.com/fhempy/fhempy/commit/8f5717da66b6fc9a5e396791f7622296d9114829))

- **fhempy**: Add check if venv creation was successful
  ([`dd065e5`](https://github.com/fhempy/fhempy/commit/dd065e58bd90c64deff57a73ef8945c7de404eb4))

- **fhempy**: Add venv creation
  ([`f296a39`](https://github.com/fhempy/fhempy/commit/f296a396cef7d67a350f5f0a0901eb4545f6cb27))

- **fhempy**: Do not create venv in container environment
  ([#218](https://github.com/fhempy/fhempy/pull/218),
  [`98ebf9e`](https://github.com/fhempy/fhempy/commit/98ebf9ec5ca9698667d294caeb466b061978e0e1))

- **fhempy**: Do venv check only for non-container envs
  ([#218](https://github.com/fhempy/fhempy/pull/218),
  [`526b92a`](https://github.com/fhempy/fhempy/commit/526b92a339d89c43419deef5432b39aa7ab774b4))

- **fhempy**: Fix Line52 in fhempy ([#234](https://github.com/fhempy/fhempy/pull/234),
  [`24e47a8`](https://github.com/fhempy/fhempy/commit/24e47a84ff9e0610656bdea53c2270482de32b02))

* Modify default poll intervall to 300 seconds

* - Fix Line52 in fhempy - Update BaseLib Ring

- **fhempy**: Install fhempy in venv
  ([`2f05060`](https://github.com/fhempy/fhempy/commit/2f05060c022b12101badc9227cc240e16896656c))

- **object_detection**: Update libs
  ([`d6618b8`](https://github.com/fhempy/fhempy/commit/d6618b8546a116e8322b0d710e99674adaa32f2d))


## v0.1.684 (2023-12-12)

### Bug Fixes

- **fhempy**: Do not report error if .fhempy dir exists already
  ([`4c7c901`](https://github.com/fhempy/fhempy/commit/4c7c9018d331294ca36836ec8a7dd78272af9d6a))

- **googlecast**: Add six dependency
  ([`aa79813`](https://github.com/fhempy/fhempy/commit/aa79813e5011a3366c166a1dfd5f6d54f8612edf))

- **miio**: Add six dependency
  ([`aef754b`](https://github.com/fhempy/fhempy/commit/aef754b9688ebaba40e836d624772ed07a4f4388))


## v0.1.683 (2023-12-12)

### Bug Fixes

- **fhempy**: Create venv for fhempy installations to support bookworm
  ([#218](https://github.com/fhempy/fhempy/pull/218),
  [`9d5f9b7`](https://github.com/fhempy/fhempy/commit/9d5f9b758afdf05bd69621718b845dd7a7e4225a))

### Features

- **fhempy**: Add error log if another fhempy instance is running already
  ([`4a42883`](https://github.com/fhempy/fhempy/commit/4a42883c7ccf4b764417765b3a8c1bac6c12f9cc))


## v0.1.682 (2023-12-05)

### Bug Fixes

- **esphome**: Update lib to 2023.11.6
  ([`b20339a`](https://github.com/fhempy/fhempy/commit/b20339a0ff8d2e570b032cc04595f88a574c32bf))

- **ring**: Fix tests
  ([`0e7272f`](https://github.com/fhempy/fhempy/commit/0e7272fb299aaaabf9faf06135ca3a56bd7f1ec6))

- **xiaomi_gateway3**: Update python-miio to 0.5.12
  ([`9b2782f`](https://github.com/fhempy/fhempy/commit/9b2782f7631f7b6883d4b1eb9c3b447d03fbf994))

- **xiaomi_gateway3**: Update python-miio to 0.5.12
  ([`fcec43d`](https://github.com/fhempy/fhempy/commit/fcec43d085a57d83cc101e650990f568400b79b3))


## v0.1.681 (2023-11-18)

### Bug Fixes

- **fhempy**: Add missing packaging dep
  ([`4ca2884`](https://github.com/fhempy/fhempy/commit/4ca2884936070fcc866800743d5ba2e9198a21f9))

- **meross**: Add setuptools requirement
  ([`587fef9`](https://github.com/fhempy/fhempy/commit/587fef9757113f2eecd67858320d549e27eb457f))

- **miflora**: Add setuptools requirement
  ([`20999c9`](https://github.com/fhempy/fhempy/commit/20999c9b7e3efbdd5c28b819bac737ba3ef39c73))


## v0.1.680 (2023-11-18)

### Bug Fixes

- **fhempy**: Remove deprecated pkg_resources
  ([`a766fb7`](https://github.com/fhempy/fhempy/commit/a766fb7489dd26fbe7fc78db85eb8e90c6e4ad3c))

- **fusionsolar**: Try to fix local time issue ([#215](https://github.com/fhempy/fhempy/pull/215),
  [`668e440`](https://github.com/fhempy/fhempy/commit/668e4407dfb9a75a63f50d8cfa7f49e3857bd555))

- **fusionsolar**: Try to fix local time issue ([#219](https://github.com/fhempy/fhempy/pull/219),
  [`0b9d387`](https://github.com/fhempy/fhempy/commit/0b9d387c4bca526c58c33e527bf148078c582697))

### Chores

- Remove fhempy.sh
  ([`4d81501`](https://github.com/fhempy/fhempy/commit/4d815019ae60d3fafb3cfacf0702d0a1feef2a40))


## v0.1.679 (2023-11-18)

### Chores

- Fix python-semantic-release 8.3.0
  ([`7c321e1`](https://github.com/fhempy/fhempy/commit/7c321e1719ec93b6871666e6fee78ddedce9ecdc))

- Use python-semantic-release 8.3.0
  ([`43d098c`](https://github.com/fhempy/fhempy/commit/43d098ce11cf1815ab05efee459b6a2bb93f0069))


## v0.1.678 (2023-11-18)

### Features

- **pyit600**: Reading for hvac_action added ([#224](https://github.com/fhempy/fhempy/pull/224),
  [`d35d303`](https://github.com/fhempy/fhempy/commit/d35d3031aa789f590d949fa8c023f28b1d382af6))

* minor fixes

* usage description updated

* retry after connection timeout added

* fix: missing break added

* additional attributes added

* reading for hvac_action added


## v0.1.677 (2023-11-17)

### Bug Fixes

- **skodaconnect**: Modify default poll intervall to 300 seconds
  ([#221](https://github.com/fhempy/fhempy/pull/221),
  [`629940c`](https://github.com/fhempy/fhempy/commit/629940c5da5e1b17b9666bc86f85a1666c4db14e))

### Features

- **rct_power**: Adding options for manual grid loading
  ([#223](https://github.com/fhempy/fhempy/pull/223),
  [`58bdec5`](https://github.com/fhempy/fhempy/commit/58bdec560e5c064d66e71c98463e8f1dc9ec0568))

https://github.com/weltenwort/home-assistant-rct-power-integration/discussions/277


## v0.1.676 (2023-11-12)

### Bug Fixes

- **fusionsolar**: Fix multiregion account again
  ([`25eef13`](https://github.com/fhempy/fhempy/commit/25eef13ca3712b3406e531589082de2339effcb2))


## v0.1.675 (2023-11-12)

### Bug Fixes

- **fusionsolar**: Fix multiregion accounts
  ([`256e464`](https://github.com/fhempy/fhempy/commit/256e464d135f88f7304a1f80e52a338b0b99cd09))


## v0.1.674 (2023-11-11)

### Bug Fixes

- **huawei_modbus**: Add Python 3.10 or higher requirement
  ([`04b72c9`](https://github.com/fhempy/fhempy/commit/04b72c9ddb8300ef0f7bd9961e6c15e550a8cb0f))

### Features

- **fusionsolar**: Support multiregion accounts
  ([`293b209`](https://github.com/fhempy/fhempy/commit/293b2091d3bc58e9d102d32cc6b85e4dcb112177))


## v0.1.673 (2023-11-10)

### Bug Fixes

- **huawei_modbus**: Moved import to ensure event loop running
  ([`ada2d4f`](https://github.com/fhempy/fhempy/commit/ada2d4f10af2ebdf6632e0e8998c60f56d47a724))


## v0.1.672 (2023-11-10)

### Chores

- Add quick & dirty development instructions
  ([`f3e7d18`](https://github.com/fhempy/fhempy/commit/f3e7d18d3b180283c27273df9d61daaf4403243b))

- Update fhem-controls-actions
  ([`4fd76af`](https://github.com/fhempy/fhempy/commit/4fd76afd760f9ca007122ec8c5b1d997e120933b))

### Features

- **huawei_modbus**: Add Huawei ModBus module
  ([`28abee1`](https://github.com/fhempy/fhempy/commit/28abee157e7a09fa4389a83b314f5df3c46168ac))


## v0.1.671 (2023-11-10)

### Bug Fixes

- **fhempy**: Add dev dependencies, min version python 3.8
  ([`fcde943`](https://github.com/fhempy/fhempy/commit/fcde9432ae87377dab1fcfdd67ab3a21b7078e2e))

- **fhempy**: Use poetry for tox
  ([`c579343`](https://github.com/fhempy/fhempy/commit/c579343200c340afb7f98b33f28d41451971d63b))

- **ring**: Ring Doorbell - Update BaseLib ([#213](https://github.com/fhempy/fhempy/pull/213),
  [`c59b3e4`](https://github.com/fhempy/fhempy/commit/c59b3e4485c2cd19e19ef12ce6afbf8920fe59fa))

* Update BaseLibs SkodaConnect and Ring

* Ring Doorbell - Update BaseLib

* Important Update in BaseLib. Versions <1.3.8 not working anymore

* Ring Update to latest BaseLib

---------

Co-authored-by: Dominik <dominik.karall@gmail.com>

- **skodaconnect**: Update base lib ([#217](https://github.com/fhempy/fhempy/pull/217),
  [`2de2114`](https://github.com/fhempy/fhempy/commit/2de211469867eceaf10d357e94657dbc96d1257b))

Bump skodaconnect to 1.3.8

This Version is needed: "Updated User-Agent in order to get code on par with recent Android and IOS
  apps.

Outdated User-Agent from older app version seems to be blocked now at token endpoints. This change
  is confirmed working with Enyaq owners."

### Chores

- Install poetry
  ([`96b8610`](https://github.com/fhempy/fhempy/commit/96b861069e9a4b9bf4805aede5ab5a8e677974ff))


## v0.1.670 (2023-10-08)

### Bug Fixes

- **googlecast**: Try to fix spotify playback ([#196](https://github.com/fhempy/fhempy/pull/196),
  [`30eea09`](https://github.com/fhempy/fhempy/commit/30eea09b1a64a2b31db4aca164423c720d6b8672))

### Continuous Integration

- Move release.sh functionality to github actions
  ([`2661fa1`](https://github.com/fhempy/fhempy/commit/2661fa10f7afcbcaaca13110906cb6a19dcee371))


## v0.1.669 (2023-10-08)

### Chores

- Fix versioning
  ([`a99193e`](https://github.com/fhempy/fhempy/commit/a99193e35e8cda66edd174ebb9070962758e58c6))


## v0.1.668 (2023-10-08)

### Chores

- Update release.yml
  ([`9704eee`](https://github.com/fhempy/fhempy/commit/9704eee16a68e2e19f6bb281e6b340bd13126154))


## v0.1.667 (2023-10-08)


## v0.1.666 (2023-10-08)

### Bug Fixes

- **googlecast**: Update libraries ([#202](https://github.com/fhempy/fhempy/pull/202),
  [`db5b444`](https://github.com/fhempy/fhempy/commit/db5b4449bb44eced89a45542262391f8298bccd9))

### Chores

- Add semantic_release with poetry
  ([`3068664`](https://github.com/fhempy/fhempy/commit/30686640aac50274d30c85c920e846e12770ac7f))

- Auto update controls
  ([`e72edde`](https://github.com/fhempy/fhempy/commit/e72edde61dfee0298d8e43945e71008a0430f7dd))

- Auto update controls
  ([`0fdc06c`](https://github.com/fhempy/fhempy/commit/0fdc06c8a2d2b152e2be1a1accca22b16e8f54c2))

- Fix build with pyproject.toml
  ([`a16f7ee`](https://github.com/fhempy/fhempy/commit/a16f7ee9667e852498266e4fa4ac1289401587f4))

- Fix semantic_release build
  ([`8e54690`](https://github.com/fhempy/fhempy/commit/8e5469067c1f063e9a34b0319f2ac4048d66aaa0))

- Test gh actions release
  ([`37698a9`](https://github.com/fhempy/fhempy/commit/37698a984d7c810c68e424f69802753f3ff0aad8))

- Try to fix build
  ([`62b069c`](https://github.com/fhempy/fhempy/commit/62b069cd4e843c6219b2cab6ace23af7c79dd459))

- Try to fix checkout permissions
  ([`d04c963`](https://github.com/fhempy/fhempy/commit/d04c96310d0b5aeb56e28f63cb010c695ae81d50))

- Try to fix commit
  ([`ac8c329`](https://github.com/fhempy/fhempy/commit/ac8c329d1be5b3d7e2449a439a495bfcceb78f19))

- Try to fix perl setup
  ([`957a9cf`](https://github.com/fhempy/fhempy/commit/957a9cfbf3be71ac11d700668297e45a28b97f36))

- Try to use pyproject.toml
  ([`5abc23a`](https://github.com/fhempy/fhempy/commit/5abc23a472d0282194999a6b0ae92ffd1b926e5d))

- Update release.yml
  ([`e0bb41e`](https://github.com/fhempy/fhempy/commit/e0bb41e91ed469781deefd150a93278291bce422))

- Update release.yml
  ([`951ef9a`](https://github.com/fhempy/fhempy/commit/951ef9a819401335d86b305c5f8054ead64b7054))

- Update release.yml
  ([`799bbd7`](https://github.com/fhempy/fhempy/commit/799bbd7ae7cdf0c08f5f02667e907d0f0c0a008b))

- Update release.yml
  ([`d906c87`](https://github.com/fhempy/fhempy/commit/d906c8729c93ac98af7e16685babc64a6fb489c0))

- Update release.yml
  ([`c15db54`](https://github.com/fhempy/fhempy/commit/c15db5433ea31fdb741c981c230dd7e0f62a79f9))

- Update release.yml
  ([`a692907`](https://github.com/fhempy/fhempy/commit/a692907dd49fe65574d190e9fffe1b3553c098a3))

- Update release.yml
  ([`7b56ab4`](https://github.com/fhempy/fhempy/commit/7b56ab498a57a806d06526bbeac4779202b24bdb))

- Update release.yml
  ([`15b861b`](https://github.com/fhempy/fhempy/commit/15b861bb128e94e88c19a67b1ad95a6f8a3116a4))

- Use poetry
  ([`a0e2385`](https://github.com/fhempy/fhempy/commit/a0e238573bf1c44dd59532ef8485f295827eb3ed))

- Use poetry
  ([`9fdbbef`](https://github.com/fhempy/fhempy/commit/9fdbbef1d84e5ab43a9512afda8205827eb5746a))


## v0.1.665 (2023-09-09)

### Bug Fixes

- **object_detection**: Support python 3.10
  ([`62e0183`](https://github.com/fhempy/fhempy/commit/62e0183694dbe68f57ee082ee8cf6fc5c9c6c306))


## v0.1.664 (2023-09-09)

### Bug Fixes

- **skodaconnect**: Fix possible installation issues
  ([`fb360d3`](https://github.com/fhempy/fhempy/commit/fb360d3d2be591d51b9cd79c9ee29acca9bb8ed0))


## v0.1.663 (2023-09-09)

### Bug Fixes

- **homekit**: Update aiohomekit lib
  ([`fb5c4fc`](https://github.com/fhempy/fhempy/commit/fb5c4fccd88ea1cc48a7913bad46b454083aead0))

- **skodaconnect**: Fix installation dependency
  ([`b78ec37`](https://github.com/fhempy/fhempy/commit/b78ec375a41244ad70f88bdf69857a08179fbaab))

### Chores

- Add test for python 3.10
  ([`ab8e2a0`](https://github.com/fhempy/fhempy/commit/ab8e2a01ac86343a4b5f31a02160bd3fd64b2ebf))


## v0.1.662 (2023-09-09)

### Bug Fixes

- **seatconnect**: Update seatconnect lib ([#190](https://github.com/fhempy/fhempy/pull/190),
  [`d2ae3ef`](https://github.com/fhempy/fhempy/commit/d2ae3ef34cc36119027ac1847e43715c28bb07e4))


## v0.1.661 (2023-08-16)

### Chores

- **deps**: Bump aiohttp[speedups] from 3.8.4 to 3.8.5
  ([#175](https://github.com/fhempy/fhempy/pull/175),
  [`43e684c`](https://github.com/fhempy/fhempy/commit/43e684c3ceff1c6caa220608406419a0933753c5))

Bumps [aiohttp[speedups]](https://github.com/aio-libs/aiohttp) from 3.8.4 to 3.8.5. - [Release
  notes](https://github.com/aio-libs/aiohttp/releases) -
  [Changelog](https://github.com/aio-libs/aiohttp/blob/v3.8.5/CHANGES.rst) -
  [Commits](https://github.com/aio-libs/aiohttp/compare/v3.8.4...v3.8.5)

--- updated-dependencies: - dependency-name: aiohttp[speedups] dependency-type: direct:production

update-type: version-update:semver-patch

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump markdown2 from 2.4.8 to 2.4.10 ([#177](https://github.com/fhempy/fhempy/pull/177),
  [`884e47a`](https://github.com/fhempy/fhempy/commit/884e47a59bfdc0378835411aae91b13b0ffe9694))

Bumps [markdown2](https://github.com/trentm/python-markdown2) from 2.4.8 to 2.4.10. -
  [Changelog](https://github.com/trentm/python-markdown2/blob/master/CHANGES.md) -
  [Commits](https://github.com/trentm/python-markdown2/compare/2.4.8...2.4.10)

--- updated-dependencies: - dependency-name: markdown2 dependency-type: direct:production

update-type: version-update:semver-patch

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Features

- **skodaconnect**: Add some features ([#180](https://github.com/fhempy/fhempy/pull/180),
  [`4662110`](https://github.com/fhempy/fhempy/commit/46621102f7bd0b13bad19f99e33a24bb05b5562c))

- added setting for EV Cars - added "connected" state - added int-cast to charge_limit


## v0.1.660 (2023-07-10)

### Bug Fixes

- **fhempy**: Add async upnp client to requirements
  ([`bbb68f5`](https://github.com/fhempy/fhempy/commit/bbb68f5f8dcc33eed0e2f5f3af16a67cc6eea097))


## v0.1.659 (2023-07-10)

### Bug Fixes

- **kia_hyundai**: Update base lib to 3.3.12
  ([`8f4b732`](https://github.com/fhempy/fhempy/commit/8f4b73289750ac647b570b45c40d6bc8ac2603fb))

- **seatconnect**: Update base lib to 1.1.7 ([#168](https://github.com/fhempy/fhempy/pull/168),
  [`72acd0d`](https://github.com/fhempy/fhempy/commit/72acd0d5f316b9a577ec13b7ca0e3a751388661d))

- **skodaconnect**: Update base lib to 1.3.6
  ([`34460fc`](https://github.com/fhempy/fhempy/commit/34460fc55cf2e32d75f675ecf931ac39fcbdbec5))

- **tuya**: Fix energy calculation
  ([`aa9a52b`](https://github.com/fhempy/fhempy/commit/aa9a52b818937e075e9cc0c32c65414c105dccfc))


## v0.1.658 (2023-06-17)

### Bug Fixes

- **tuya**: Fix localkey attr on create_device ([#162](https://github.com/fhempy/fhempy/pull/162),
  [`b45555d`](https://github.com/fhempy/fhempy/commit/b45555d6d74c44dd98b52868f38ee5bf75ec66b4))


## v0.1.657 (2023-06-17)

### Bug Fixes

- **fhempy**: Add pyOpenSSL for cryptography
  ([`9494bc4`](https://github.com/fhempy/fhempy/commit/9494bc49844311ae5c488ee16c61c048b94f9cf1))

- **fhempy**: Add pyOpenSSL for cryptography
  ([`1dc4a78`](https://github.com/fhempy/fhempy/commit/1dc4a78d76082b199502fc08548ccf140a1da69e))

- **homekit**: Do set call async
  ([`b5fd2eb`](https://github.com/fhempy/fhempy/commit/b5fd2ebbc51f3864703397b3e0c7bb11211108e5))

- **homekit**: Do set call async
  ([`9e0821e`](https://github.com/fhempy/fhempy/commit/9e0821ed4df01608abb5826a909de05ab98a0a7f))


## v0.1.656 (2023-06-11)

### Bug Fixes

- **fhempy**: Fix cryptography imports
  ([`3eddf85`](https://github.com/fhempy/fhempy/commit/3eddf853ef9571b0ebee49250ffd8e826f20ce7b))


## v0.1.655 (2023-06-11)

### Bug Fixes

- **homekit**: Fix cryptography version
  ([`2d66139`](https://github.com/fhempy/fhempy/commit/2d661398dc99d035a91b5e2738b56df21cfa8c69))


## v0.1.654 (2023-06-11)

### Chores

- Update controls
  ([`83b0ae1`](https://github.com/fhempy/fhempy/commit/83b0ae1454cea1ae16bb76dd3111d1f543476d70))

### Features

- **fhempy**: Update zeroconf
  ([`509cddd`](https://github.com/fhempy/fhempy/commit/509cdddd865d56a150d62dfd12d2101b94fd4c77))


## v0.1.653 (2023-06-11)

### Features

- **homekit**: Initial version of homekit support (very basic!)
  ([`4171521`](https://github.com/fhempy/fhempy/commit/4171521e34b6b712e1330e7e41abda3cbbe9de99))


## v0.1.652 (2023-06-05)

### Bug Fixes

- **tuya**: Fix localkey attr on create
  ([`e697616`](https://github.com/fhempy/fhempy/commit/e697616aae47973b3655da1ed74e05d73c5b2160))

- **tuya**: Fix localkey attr on create
  ([`e8d620a`](https://github.com/fhempy/fhempy/commit/e8d620af06119ed421a7c42453eb35ee6ff458ae))


## v0.1.651 (2023-05-27)

### Bug Fixes

- **seatconnect**: Use cryptography 3.3.2
  ([`3e7f943`](https://github.com/fhempy/fhempy/commit/3e7f94300cec1bb78eec5bdf0078957c4b7c5d41))

- **skodaconnect**: Update baselib and use cryptography 3.3.2
  ([`43be1b2`](https://github.com/fhempy/fhempy/commit/43be1b2eff7b00cb378f460cedef315ce7e21ab1))

### Chores

- Update controls
  ([`07f4df4`](https://github.com/fhempy/fhempy/commit/07f4df4aa310d9144f1582240fccc664ae81c07f))


## v0.1.650 (2023-05-27)

### Chores

- **deps**: Bump pycryptodomex from 3.17 to 3.18.0
  ([#157](https://github.com/fhempy/fhempy/pull/157),
  [`1b642cb`](https://github.com/fhempy/fhempy/commit/1b642cb6f127c50bf85824a11519f332f0525564))

Bumps [pycryptodomex](https://github.com/Legrandin/pycryptodome) from 3.17 to 3.18.0. - [Release
  notes](https://github.com/Legrandin/pycryptodome/releases) -
  [Changelog](https://github.com/Legrandin/pycryptodome/blob/master/Changelog.rst) -
  [Commits](https://github.com/Legrandin/pycryptodome/compare/v3.17.0...v3.18.0)

--- updated-dependencies: - dependency-name: pycryptodomex dependency-type: direct:production

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump requests from 2.28.2 to 2.31.0 ([#158](https://github.com/fhempy/fhempy/pull/158),
  [`7d73a7d`](https://github.com/fhempy/fhempy/commit/7d73a7d09351b484f89efd988fd3cee789d7d7fa))

Bumps [requests](https://github.com/psf/requests) from 2.28.2 to 2.31.0. - [Release
  notes](https://github.com/psf/requests/releases) -
  [Changelog](https://github.com/psf/requests/blob/main/HISTORY.md) -
  [Commits](https://github.com/psf/requests/compare/v2.28.2...v2.31.0)

--- updated-dependencies: - dependency-name: requests dependency-type: direct:production

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump websockets from 10.4 to 11.0.3 ([#154](https://github.com/fhempy/fhempy/pull/154),
  [`3f0acee`](https://github.com/fhempy/fhempy/commit/3f0acee4bacacc16d72b79735e48a1dc82bbf9a4))

Bumps [websockets](https://github.com/aaugustin/websockets) from 10.4 to 11.0.3. - [Release
  notes](https://github.com/aaugustin/websockets/releases) -
  [Commits](https://github.com/aaugustin/websockets/compare/10.4...11.0.3)

--- updated-dependencies: - dependency-name: websockets dependency-type: direct:production

update-type: version-update:semver-major

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>


## v0.1.649 (2023-05-27)

### Bug Fixes

- **tuya**: Support locakeys with special characters. localkey is used from attr instead of define
  ([#156](https://github.com/fhempy/fhempy/pull/156),
  [`a0dad2b`](https://github.com/fhempy/fhempy/commit/a0dad2b3d09e78f746fab56f69e4ded593c68415))

### Features

- **esphome**: Update esphome to 2023.5.4
  ([`5e6a585`](https://github.com/fhempy/fhempy/commit/5e6a58516cb726c9e88b99e413b88481483ea462))

- **ikos**: New module for ikos hotels
  ([`6b0f38c`](https://github.com/fhempy/fhempy/commit/6b0f38c87305c67b9c2c4a196db694084d38b492))


## v0.1.648 (2023-04-20)

### Bug Fixes

- **fhempy**: Fix special characters in readings and device names
  ([`6ed1f18`](https://github.com/fhempy/fhempy/commit/6ed1f181579e6565df0d27afbc69adad53d460aa))

- **fhempy**: Fix special characters in readings and device names
  ([`e81d6d0`](https://github.com/fhempy/fhempy/commit/e81d6d009b37f7a9dfd18eadbe70fc2b88f707f3))

### Features

- **geizhals**: Add image and get store from offer 0
  ([`6b04f0c`](https://github.com/fhempy/fhempy/commit/6b04f0c8a364b4fad63e3131f80f0b72bfbce1d4))

- **geizhals**: Add image and get store from offer 0
  ([`0397ef4`](https://github.com/fhempy/fhempy/commit/0397ef4b35a8c2b3c53df0074cd986e73e53fcdd))


## v0.1.647 (2023-04-16)

### Bug Fixes

- **tuya**: Update aiotinytuya 1.12.3
  ([`46f8fa9`](https://github.com/fhempy/fhempy/commit/46f8fa960a518d493f82cb02651f1702c6b71396))


## v0.1.646 (2023-04-11)

### Features

- **mqtt_ha_discovery**: Mqtt HomeAssistant discovery support
  ([`34e04cf`](https://github.com/fhempy/fhempy/commit/34e04cf6c80d59a47360b0283f0ebc2058f1b0db))


## v0.1.645 (2023-04-09)

### Bug Fixes

- **kia_hyundai**: Fix login with lib update to 3.1.8
  ([`8e630af`](https://github.com/fhempy/fhempy/commit/8e630afceddf48d4620ccfe6fdb6b41ccb3901f0))


## v0.1.644 (2023-04-08)

### Bug Fixes

- **skodaconnect**: Minor improvements in BaseLib
  ([#140](https://github.com/fhempy/fhempy/pull/140),
  [`9033dbd`](https://github.com/fhempy/fhempy/commit/9033dbdb4ad9e2e7fd2a2f9483b2eff5377e2c3b))

- **tuya_cloud**: Add values in exception log
  ([`0d16830`](https://github.com/fhempy/fhempy/commit/0d16830b90a6c126f97cd0d2e21ce6563ffce67a))

### Features

- **esphome**: Update esphome to 2023.3.2
  ([`a4f81b2`](https://github.com/fhempy/fhempy/commit/a4f81b2f6b751d8191541878026a6ce3d6b6ae20))


## v0.1.643 (2023-03-25)

### Bug Fixes

- **zigbee2mqtt**: Fix z2m version reading again
  ([`e64b707`](https://github.com/fhempy/fhempy/commit/e64b7077b39335dab640cfe30d1972008d1705f7))


## v0.1.642 (2023-03-25)

### Bug Fixes

- **zigbee2mqtt**: Fix startup
  ([`4444db7`](https://github.com/fhempy/fhempy/commit/4444db7d4c4d1206b9e3df42d44b56f0d1c0838b))


## v0.1.641 (2023-03-25)

### Features

- **zigbee2mqtt**: Add z2m_version reading
  ([`ed09190`](https://github.com/fhempy/fhempy/commit/ed091906442f7de603a04632615d704598c83c5f))


## v0.1.640 (2023-03-25)

### Bug Fixes

- **wienernetze_smartmeter**: Clear cookies on login
  ([#136](https://github.com/fhempy/fhempy/pull/136),
  [`5567821`](https://github.com/fhempy/fhempy/commit/5567821ea4615c947f29dd2300decb1028ba9a34))


## v0.1.639 (2023-03-23)

### Bug Fixes

- **wienernetze_smartmeter**: Add more log output
  ([#136](https://github.com/fhempy/fhempy/pull/136),
  [`17f77a5`](https://github.com/fhempy/fhempy/commit/17f77a53c3415eddfa0aaf93ebe1352f07167dfe))


## v0.1.638 (2023-03-23)

### Bug Fixes

- **fhempy**: Handle github api rate limits on latest release check
  ([`564f7a1`](https://github.com/fhempy/fhempy/commit/564f7a1720d6fb36537e74bbf2953e093411fc4d))

### Chores

- Test manifest dependencies
  ([`c1ad29b`](https://github.com/fhempy/fhempy/commit/c1ad29b2b360f0afc7f8dee66fa933fe4e654662))

- Test manifest dependencies
  ([`48e7221`](https://github.com/fhempy/fhempy/commit/48e72218bd9914d8710a85e427bb6c6d94531231))

### Features

- **esphome**: Update lib to 2023.3.1
  ([`f3e9ecb`](https://github.com/fhempy/fhempy/commit/f3e9ecb7b9a8cc070c31a6d641f01b8ced6c18cd))

- **fhem_forum**: Support private messages
  ([`78eeb03`](https://github.com/fhempy/fhempy/commit/78eeb03b12ff3e47724355887f069da40349f7ad))


## v0.1.637 (2023-03-21)

### Chores

- **deps**: Bump importlib-metadata from 4.8.1 to 6.1.0
  ([#138](https://github.com/fhempy/fhempy/pull/138),
  [`ad9babe`](https://github.com/fhempy/fhempy/commit/ad9babe769213b56f732ffd497096b8374a41359))

- **deps**: Bump markdown2 from 2.4.2 to 2.4.8 ([#133](https://github.com/fhempy/fhempy/pull/133),
  [`592c4b2`](https://github.com/fhempy/fhempy/commit/592c4b229482fc6fc085a99e2d1514f06ac556a5))

Bumps [markdown2](https://github.com/trentm/python-markdown2) from 2.4.2 to 2.4.8. - [Release
  notes](https://github.com/trentm/python-markdown2/releases) -
  [Changelog](https://github.com/trentm/python-markdown2/blob/master/CHANGES.md) -
  [Commits](https://github.com/trentm/python-markdown2/compare/2.4.2...2.4.8)

--- updated-dependencies: - dependency-name: markdown2 dependency-type: direct:production

update-type: version-update:semver-patch

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump pycryptodomex from 3.16.0 to 3.17
  ([#135](https://github.com/fhempy/fhempy/pull/135),
  [`4e5aba1`](https://github.com/fhempy/fhempy/commit/4e5aba183dc20887d726df7ac0ff5350d5755b1b))

Bumps [pycryptodomex](https://github.com/Legrandin/pycryptodome) from 3.16.0 to 3.17. - [Release
  notes](https://github.com/Legrandin/pycryptodome/releases) -
  [Changelog](https://github.com/Legrandin/pycryptodome/blob/master/Changelog.rst) -
  [Commits](https://github.com/Legrandin/pycryptodome/compare/v3.16.0...v3.17.0)

--- updated-dependencies: - dependency-name: pycryptodomex dependency-type: direct:production

update-type: version-update:semver-minor

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump requests from 2.26.0 to 2.28.2 ([#131](https://github.com/fhempy/fhempy/pull/131),
  [`aa913d3`](https://github.com/fhempy/fhempy/commit/aa913d3987e4b00991e51843fb4ba85d93610ff0))


## v0.1.636 (2023-03-21)

### Bug Fixes

- **volvo_software_update**: Fix update headers
  ([`d024d99`](https://github.com/fhempy/fhempy/commit/d024d994868fa5d8699746ee238079ee2e826415))


## v0.1.635 (2023-03-20)

### Bug Fixes

- **fhempy**: Fix perl syntax
  ([`09b4377`](https://github.com/fhempy/fhempy/commit/09b4377ebfacabf11f9747c1197b95835868c452))


## v0.1.634 (2023-03-20)

### Bug Fixes

- **fhempy**: Run received commands for max 300ms within fhem
  ([`18a26a2`](https://github.com/fhempy/fhempy/commit/18a26a2832d6039fe1d5719008acdb74bd62ecbb))


## v0.1.633 (2023-03-19)

### Bug Fixes

- **fhem_forum**: Support new forum software
  ([`2cb1134`](https://github.com/fhempy/fhempy/commit/2cb1134df4fb9d3796ead7344ddd64a206ee9637))


## v0.1.632 (2023-03-19)

### Bug Fixes

- **volvo_software_update**: Support new volvo urls, please update your url!
  ([`7b13a5e`](https://github.com/fhempy/fhempy/commit/7b13a5e966598e8b6b8a05e368791e424da76881))

- **wienernetze_smartmeter**: Add exception handling
  ([#136](https://github.com/fhempy/fhempy/pull/136),
  [`af66eb2`](https://github.com/fhempy/fhempy/commit/af66eb2fc5e5fcec40a7dab3224c64724ebbfda4))

### Features

- **aktionsfinder**: Support multiple arguments as search items
  ([`6e20578`](https://github.com/fhempy/fhempy/commit/6e20578d6222af26e3bb1c61aa4ae84928f02d7c))


## v0.1.631 (2023-03-18)

### Bug Fixes

- **fhempy**: Remove () in dev and reading names
  ([`19aadef`](https://github.com/fhempy/fhempy/commit/19aadefc5841063a929a34de83ee79a213ef61e7))


## v0.1.630 (2023-03-12)

### Bug Fixes

- **goodwe**: Fix reading names
  ([`0c466ca`](https://github.com/fhempy/fhempy/commit/0c466ca8d758bb6db595393cd5910bff35e91f16))


## v0.1.629 (2023-03-12)

### Chores

- Create .github/dependabot.yml
  ([`cdfa87b`](https://github.com/fhempy/fhempy/commit/cdfa87bb81eede1b17d05dfa1c98976e484e81b9))

- Update dependabot.yml
  ([`d8692e0`](https://github.com/fhempy/fhempy/commit/d8692e083b7bf3085d09665b4628b39fa5c18453))

### Features

- **goodwe**: New module for goodwe inverters
  ([`04a98f2`](https://github.com/fhempy/fhempy/commit/04a98f2d031387f477755d5bdc909f1212b3ba25))


## v0.1.628 (2023-03-11)

### Features

- **aktionsfinder**: New module aktionsfinder
  ([`4edcad3`](https://github.com/fhempy/fhempy/commit/4edcad3f30ec4e48027c6d97e0b2f6cbf777f6d9))

- **arp_presence**: Add icon
  ([`33f29c4`](https://github.com/fhempy/fhempy/commit/33f29c4a0b528edddcb95138a2465ca9ca332b65))

- **blue_connect**: Add icon
  ([`3ad3964`](https://github.com/fhempy/fhempy/commit/3ad396497972983244404d09d30e2e1a6f08e886))


## v0.1.627 (2023-03-11)

### Bug Fixes

- **kia_hyundai**: Fix dateutil requirement
  ([`c5dc94c`](https://github.com/fhempy/fhempy/commit/c5dc94c31b8d09efe84d8188be9c5497cbf9de10))


## v0.1.626 (2023-03-11)


## v0.1.625 (2023-03-11)

### Bug Fixes

- **kia_hyundai**: Add further dependencies which are missing in the base library
  ([`6f6134b`](https://github.com/fhempy/fhempy/commit/6f6134b8275d541755b6adecb2017eccf255dfef))


## v0.1.624 (2023-03-11)

### Bug Fixes

- **kia_hyundai**: Add missing pytz requirement
  ([`d5be5bf`](https://github.com/fhempy/fhempy/commit/d5be5bf255adf6fdd561068b2c17fb476dd8fef0))


## v0.1.623 (2023-03-11)

### Bug Fixes

- **kia_hyundai**: Use library instead of own code
  ([`51aa0b4`](https://github.com/fhempy/fhempy/commit/51aa0b47ff1ca814c89b70955ac20ccf89e25e31))

- **tuya**: Fix testcase by using aiotinytuya
  ([`148e2bb`](https://github.com/fhempy/fhempy/commit/148e2bbb481093addeafd768c7e6aef73a5be4f6))


## v0.1.622 (2023-03-11)

### Bug Fixes

- **tuya**: Use aiotinytuya
  ([`264f2db`](https://github.com/fhempy/fhempy/commit/264f2db8d7cfb1e4a1104789907c074c4727f00e))


## v0.1.621 (2023-03-11)

### Features

- **tuya**: Update to latest tinytuya release (1.11.0)
  ([`1740bf0`](https://github.com/fhempy/fhempy/commit/1740bf0ef90638ea63ca67709d89e4a89636c3d1))


## v0.1.620 (2023-03-10)

### Bug Fixes

- **wienernetze_smartmeter**: Fix login via logwien
  ([`99e0872`](https://github.com/fhempy/fhempy/commit/99e087231ab6db0672ea7cfcbb92359317fc32e4))


## v0.1.619 (2023-03-07)

### Bug Fixes

- **tuya**: Allow float values
  ([`1484727`](https://github.com/fhempy/fhempy/commit/148472771da6472610f2bb76dbfbea1e70c77d2e))


## v0.1.618 (2023-03-07)

### Bug Fixes

- **tuya**: Revert last change
  ([`bd66d41`](https://github.com/fhempy/fhempy/commit/bd66d414009c1c55556230476aed168f0da6f55a))


## v0.1.617 (2023-03-07)

### Bug Fixes

- **erelax_vaillant**: Use vaillant-netatmo-api library
  ([`bc61d49`](https://github.com/fhempy/fhempy/commit/bc61d49278f2c370ad1a8533e2caa1f34c00e49e))

- **tuya**: Retry connect on failure
  ([`a370795`](https://github.com/fhempy/fhempy/commit/a370795822976227b5b5b821a83c77738c77a291))


## v0.1.616 (2023-03-03)

### Bug Fixes

- **google_weather**: Update get images
  ([`91db97d`](https://github.com/fhempy/fhempy/commit/91db97d7060db5df6e31a4ac442da0947fd78ca3))


## v0.1.615 (2023-03-03)

### Bug Fixes

- **fhempy**: Update aiohttp to support Python 3.11
  ([`9a5975a`](https://github.com/fhempy/fhempy/commit/9a5975a4c69fc61717fbf29fb9e18b434b83d9f5))


## v0.1.614 (2023-03-03)

### Bug Fixes

- **tuya**: Colour_data = A, colour_data_v2 = B for rgb bulbs
  ([`022e2f1`](https://github.com/fhempy/fhempy/commit/022e2f1ccb9a1ad0148cfa38d8950d9c285911a8))


## v0.1.613 (2023-03-01)

### Bug Fixes

- **wienernetze_smartmeter**: Fix login ([#120](https://github.com/fhempy/fhempy/pull/120),
  [`542e308`](https://github.com/fhempy/fhempy/commit/542e308d4e8f23d856db59ac830235a827cd73af))


## v0.1.612 (2023-02-27)

### Bug Fixes

- **volvo**: Add domain in reading name
  ([`fb8f93c`](https://github.com/fhempy/fhempy/commit/fb8f93c6135b13813f6d3ccf4144739c58dd1074))


## v0.1.611 (2023-02-27)

### Bug Fixes

- **energie_gv_at**: Set label to 0 if no data received for that label
  ([`d88dc5d`](https://github.com/fhempy/fhempy/commit/d88dc5d6c0f1c7c2500acacf4bd23fe3b9d7afd7))

- **volvo**: Remove sunRoofOpen as currently not working, handle exceptions on update_readings
  ([`e8d8e45`](https://github.com/fhempy/fhempy/commit/e8d8e45d3564d9288fa24b171099c0510a928e1f))

### Features

- **fhempy**: Add set_icon method
  ([`42b4260`](https://github.com/fhempy/fhempy/commit/42b4260cf74dd7b0ef68d7353244fd9e06abf9b4))

- **tuya**: Support reset_energy
  ([`fb5f25f`](https://github.com/fhempy/fhempy/commit/fb5f25f36f0364cd4881d386b6b8ecc234dbee86))

- **tuya_cloud**: Support reset_energy
  ([`0a0b12c`](https://github.com/fhempy/fhempy/commit/0a0b12c90c2228f35d8c6d65df467c63a2b3f90e))


## v0.1.610 (2023-02-26)

### Bug Fixes

- **wienernetze_smartmeter**: Fix imports ([#120](https://github.com/fhempy/fhempy/pull/120),
  [`f1b2c80`](https://github.com/fhempy/fhempy/commit/f1b2c80317c298ac25fa2b1e5b7888fb993c3000))


## v0.1.609 (2023-02-26)

### Bug Fixes

- **tuya_cloud**: Fix wrong scale for some product ids
  ([`e1008d3`](https://github.com/fhempy/fhempy/commit/e1008d3e30de58290a1f9c69501fe3a4587ec3bf))


## v0.1.608 (2023-02-26)

### Bug Fixes

- **mitemp2**: Fix wrong number of arguments
  ([`b3f4066`](https://github.com/fhempy/fhempy/commit/b3f4066613e9cd2c4cd13f2cb75768134071ea2c))

- **wienernetze_smartmeter**: Update wiener netze api
  ([#120](https://github.com/fhempy/fhempy/pull/120),
  [`2f917c1`](https://github.com/fhempy/fhempy/commit/2f917c1ef286e85962f71d71cdfd10e560ffd051))


## v0.1.607 (2023-02-25)

### Bug Fixes

- **tuya**: Fix cur_power for prodid wifvoilfrqeo6hvu
  ([`b10a374`](https://github.com/fhempy/fhempy/commit/b10a374b63b8d837c993cfbbfb2432d8a2930b3e))

### Features

- **energie_gv_at**: Add more details about the current source of electricity
  ([`66ea3db`](https://github.com/fhempy/fhempy/commit/66ea3db36992876efa6879ba10c7a105d054470c))

- **volvo**: Initial release of volvo new api module
  ([`a69bd1b`](https://github.com/fhempy/fhempy/commit/a69bd1b42d399a66ccf5ad33a344a874f905aacc))

- **wienernetze_smartmeter**: Testing wiener netze smartmeter
  ([`c8cb33d`](https://github.com/fhempy/fhempy/commit/c8cb33dc342083afe8e985596f92ce56f6ed3728))


## v0.1.606 (2023-02-22)

### Features

- **tuya_cloud**: Add energy reading
  ([`1ad2090`](https://github.com/fhempy/fhempy/commit/1ad2090c455fb47903007b61f32bdf4d20e6d336))


## v0.1.605 (2023-02-22)

### Bug Fixes

- **tuya**: Fix energy formula
  ([`f2d25b7`](https://github.com/fhempy/fhempy/commit/f2d25b79d228967915693af4972deafda21ee887))


## v0.1.604 (2023-02-22)

### Features

- **tuya**: Add energy reading
  ([`7231691`](https://github.com/fhempy/fhempy/commit/72316919794aec137e9243ba4808a49667e99c9f))


## v0.1.603 (2023-02-20)

### Bug Fixes

- **fhempy**: Fix disable for modules without attributes
  ([`f85134d`](https://github.com/fhempy/fhempy/commit/f85134db71dd53d188fa9d3f3ceb8ae8e1598c23))


## v0.1.602 (2023-02-20)

### Bug Fixes

- **fhempy**: Fix disable ([#118](https://github.com/fhempy/fhempy/pull/118),
  [`fed397a`](https://github.com/fhempy/fhempy/commit/fed397afc36ef41e54907fdadc1deecc45299501))


## v0.1.601 (2023-02-20)

### Features

- **fhempy**: Activate disable attr for all fhempy modules
  ([#118](https://github.com/fhempy/fhempy/pull/118),
  [`0072cb6`](https://github.com/fhempy/fhempy/commit/0072cb6999b9727b60812e6c2393ea67d7c0d7e7))


## v0.1.600 (2023-02-20)

### Bug Fixes

- **spotify_connect_player**: Fix define
  ([`80df09c`](https://github.com/fhempy/fhempy/commit/80df09c1086cdb011801fd9cb8768dedd2ca074a))

### Features

- **fhempy**: Support disable attr for all fhempy devices
  ([`196ee60`](https://github.com/fhempy/fhempy/commit/196ee602d395310222f845d849a60c87a125b8f0))


## v0.1.599 (2023-02-19)

### Bug Fixes

- **fhempy**: Fix tests
  ([`e312537`](https://github.com/fhempy/fhempy/commit/e31253790b800197b656f6a721af48989a89723e))

- **fhempy**: Use set ? cache only when connected
  ([`1c59259`](https://github.com/fhempy/fhempy/commit/1c59259d4147e95cbec9dc0473ea261c8f7833bd))

### Features

- **tuya**: Add productid keym9qkuywghyrvs ([#128](https://github.com/fhempy/fhempy/pull/128),
  [`b5d9ec6`](https://github.com/fhempy/fhempy/commit/b5d9ec676e85fcb16c52a0e18dbfa68d2a6ba8bd))


## v0.1.598 (2023-02-17)

### Bug Fixes

- **fhempy**: Fix attr handling
  ([`58bf90d`](https://github.com/fhempy/fhempy/commit/58bf90d95a9146383385e680fa09954a1ebd5b51))

- **fhempy**: Fix attr handling 2
  ([`322cecb`](https://github.com/fhempy/fhempy/commit/322cecb2f6ea63701add23ddfe87f3b5a3a093a6))


## v0.1.597 (2023-02-17)

### Bug Fixes

- **fhempy**: Fix set error
  ([`d651009`](https://github.com/fhempy/fhempy/commit/d6510097548d04454c1efa8336ad7b5f2375a863))


## v0.1.596 (2023-02-17)

### Bug Fixes

- **fhempy**: Cleanup websocket message handling
  ([`8421824`](https://github.com/fhempy/fhempy/commit/84218242e3ca1c47a579a1c604256b7163b89899))

- **fhempy**: Use DevIo_SimpleRead
  ([`2fcc386`](https://github.com/fhempy/fhempy/commit/2fcc386484e96337646598874104a63f750c81c3))

### Features

- **fhempy**: Support set ? cache in BindingsIo
  ([`0615960`](https://github.com/fhempy/fhempy/commit/061596046f72d0ceb61e6f677913630f4104c164))


## v0.1.595 (2023-02-08)

### Bug Fixes

- **fhempy**: Fix deep recursion
  ([`685c12e`](https://github.com/fhempy/fhempy/commit/685c12e84bc0eef454c9cd9b1088667d25fd19da))


## v0.1.594 (2023-02-08)

### Bug Fixes

- **fhempy**: Do not drop messags on high load
  ([`30b43dd`](https://github.com/fhempy/fhempy/commit/30b43ddc069d159a785943d11dd3eb3bde595e0d))

- **fhempy**: Increase fhem timeout to 180s
  ([`919b5c3`](https://github.com/fhempy/fhempy/commit/919b5c3429c59bb3364c07d79c06dddd186936d7))

- **fhempy**: Support Python 3.9 and higher
  ([`1a672c5`](https://github.com/fhempy/fhempy/commit/1a672c582fc8e1651f832e933f3f6c37bb427c23))

- **tuya_cloud**: Do not update readings if they didn't change - reduce load on fhem
  ([`7bd27bb`](https://github.com/fhempy/fhempy/commit/7bd27bb252b3bc220096e3e4e777048f5386cf6c))


## v0.1.593 (2023-02-05)

### Bug Fixes

- **fhempy**: Revert readingsBulkUpdate lock
  ([`dada627`](https://github.com/fhempy/fhempy/commit/dada6278574018b4b19890859978149c218b701b))


## v0.1.592 (2023-02-04)

### Bug Fixes

- **fhempy**: Revert ping/pong support
  ([`ff5a3b3`](https://github.com/fhempy/fhempy/commit/ff5a3b33d37635c94a24c9db05508ad652228631))


## v0.1.591 (2023-02-04)

### Bug Fixes

- **fhempy**: Fix websocket ping/pong
  ([`5ab09fc`](https://github.com/fhempy/fhempy/commit/5ab09fc28bacde1277d9f25459f41cf817d41434))


## v0.1.590 (2023-02-04)

### Bug Fixes

- **fhempy**: Do not mix different readingsBulkUpdates, increase fhem timeout to 180s
  ([`b0d377e`](https://github.com/fhempy/fhempy/commit/b0d377ed80f26ea069d53d856343cc53e79568b6))

- **fhempy**: Support websocket ping/pong
  ([`814c009`](https://github.com/fhempy/fhempy/commit/814c009a06e1a42b80fbbc15c4f380fc471ae193))


## v0.1.589 (2023-02-03)

### Bug Fixes

- **tuya**: Set DEVICEID for offline devices
  ([`4bc9951`](https://github.com/fhempy/fhempy/commit/4bc9951faf0a24e867f484f1d61add681bdc64b0))

### Chores

- Always update controls first
  ([`25e86d3`](https://github.com/fhempy/fhempy/commit/25e86d3d54501ff871287b7cdf17379a6b0c44c1))


## v0.1.588 (2023-02-02)

### Bug Fixes

- **fhempy**: Fix checkIfDeviceExists, log error when fhem takes longer than 5s, ensure BeginUpdate
  call before EndUpdate
  ([`40119f9`](https://github.com/fhempy/fhempy/commit/40119f97e0643898e115827450b2bd968a23d47b))

- **fhempy**: Fix NO RESPONSE in some situations
  ([`9b05dba`](https://github.com/fhempy/fhempy/commit/9b05dba39fc7442de602a94bef0612283ab17e93))

- **fhempy**: Update websockets library
  ([`fc18898`](https://github.com/fhempy/fhempy/commit/fc18898fb559a97779d476b6f0f0e9aeaeb89220))

- **tuya_cloud**: Fix undefine
  ([`cc06489`](https://github.com/fhempy/fhempy/commit/cc06489669512bfdc32d24ab264043a038414f86))

### Features

- **fhempy**: Enable readme again
  ([`761dc85`](https://github.com/fhempy/fhempy/commit/761dc853a23e1c8a7fd6f7806838d30d74db7a50))

- **fhempy**: Log error when fhempy took longer than 1s to reply to fhem
  ([`af15f07`](https://github.com/fhempy/fhempy/commit/af15f073bc51c63cb2a5fe72fcb52933b19abdce))


## v0.1.587 (2023-02-01)

### Bug Fixes

- **fhempy**: Always handle messages on the receiver queue
  ([`bbeb97c`](https://github.com/fhempy/fhempy/commit/bbeb97c467c9d7a5f2046044081567540bd71fa4))


## v0.1.586 (2023-02-01)

### Bug Fixes

- **blue_connect**: Remove rssi as it is covered within core ble
  ([`a30591f`](https://github.com/fhempy/fhempy/commit/a30591f1bf5708f9f2acf7a6323e6737a845343d))

### Features

- **fhempy**: Set rssi reading for all ble devices
  ([`faa743a`](https://github.com/fhempy/fhempy/commit/faa743a81875a39886723b36d61e75618fac0834))


## v0.1.585 (2023-01-31)

### Bug Fixes

- **fhempy**: Add devicename to log output
  ([`c928e23`](https://github.com/fhempy/fhempy/commit/c928e23a1962a157359391583de5448b16563c69))

- **fhempy**: Update devStateIcon for all users
  ([`b438bcc`](https://github.com/fhempy/fhempy/commit/b438bccf2f4d3c6cf2725544aaacd125b545d7a7))


## v0.1.584 (2023-01-31)

### Bug Fixes

- **fhempy**: Change init_done response to int
  ([`c0a1b9b`](https://github.com/fhempy/fhempy/commit/c0a1b9bcd86469f67929ffb638129e7e371464fa))


## v0.1.583 (2023-01-31)

### Bug Fixes

- **fhempy**: Update attr_ver
  ([`83ac51d`](https://github.com/fhempy/fhempy/commit/83ac51de976afbae6b88aefb2f9cb70560df1e2c))


## v0.1.582 (2023-01-31)

### Bug Fixes

- **fhempy**: Do not skip messages older than 10s
  ([`afc3961`](https://github.com/fhempy/fhempy/commit/afc39612a91a370fe670591e6eb83a8da6144414))

- **fhempy**: Fix restart button
  ([`253fb16`](https://github.com/fhempy/fhempy/commit/253fb16b9e3c63538e35761c3656465e5214a59e))

- **tuya_cloud**: Fix warning when searching for DEVICEID
  ([`4e8f80e`](https://github.com/fhempy/fhempy/commit/4e8f80eb0f8b62aa3ffc6986e16bf7be7637f8e5))


## v0.1.581 (2023-01-31)

### Bug Fixes

- **fhempy**: Add logging if readingsBeginUpdate call is missing
  ([`fd893dd`](https://github.com/fhempy/fhempy/commit/fd893dd6ce81428b703fd41e14be4dade3df3115))


## v0.1.580 (2023-01-29)

### Bug Fixes

- **fhempy**: Change PYTHONTYPE to FHEMPYTYPE
  ([`b8d464e`](https://github.com/fhempy/fhempy/commit/b8d464e90fab9a0718c63e0c2b948f424f307048))

- **fhempy**: Handle WARNINGS in log message
  ([`2d19476`](https://github.com/fhempy/fhempy/commit/2d194760ce40905b01293dbb7b978f3cfc69cda7))

- **fhempy**: Update text for hard restart
  ([`22fe106`](https://github.com/fhempy/fhempy/commit/22fe106d93e89e5343d533ceaeccc7c959376950))

### Features

- **tuya_cloud**: Create only devices which do not exist as tuya or tuya_cloud device
  ([`299f393`](https://github.com/fhempy/fhempy/commit/299f393a65d176b3ca26396fc7084a5fc6803d63))


## v0.1.579 (2023-01-29)

### Features

- **fhempy**: Add restart button
  ([`13c93d1`](https://github.com/fhempy/fhempy/commit/13c93d1d8d5c16218618d3daf180e861f68b75d1))


## v0.1.578 (2023-01-26)

### Features

- **fhempy**: Support debug with verbose 5
  ([`6d96d9b`](https://github.com/fhempy/fhempy/commit/6d96d9b71a6eba1914b0faef3a5098cd2b9554ef))


## v0.1.577 (2023-01-26)


## v0.1.576 (2023-01-26)

### Bug Fixes

- **fhempy**: Debug log cleanup
  ([`7a54c9d`](https://github.com/fhempy/fhempy/commit/7a54c9d04a12c6531fb92b8eb53da88f7724e5ba))

### Features

- **fhempy**: Update devStateIcon
  ([`69ba9e1`](https://github.com/fhempy/fhempy/commit/69ba9e1e521eca19bd5853e24f1953a20c4bb748))

- **fhempy**: Update devStateIcon
  ([`457d60b`](https://github.com/fhempy/fhempy/commit/457d60bfbd3196b2d1629f29cdcdd05300a875e7))


## v0.1.575 (2023-01-24)

### Bug Fixes

- **tuya**: Try to reconnect every 15s
  ([`8f13ab2`](https://github.com/fhempy/fhempy/commit/8f13ab2b12639afc844ea594ade19653cb603cc1))


## v0.1.574 (2023-01-24)


## v0.1.573 (2023-01-24)

### Bug Fixes

- **tuya**: Proper import of fhempy tinytuya
  ([`d9eb64b`](https://github.com/fhempy/fhempy/commit/d9eb64bbe783d23a34b78bc0850b3b731cd6a766))


## v0.1.572 (2023-01-24)

### Bug Fixes

- **eq3bt**: Fix set comfort
  ([`c4c0d57`](https://github.com/fhempy/fhempy/commit/c4c0d576c8d9578a1865ec721fbc9a1c3c09a97f))


## v0.1.571 (2023-01-23)

### Features

- **tuya**: Support logging in tt core
  ([`495a85a`](https://github.com/fhempy/fhempy/commit/495a85a24ff07d674ab1735799846c3532ff347d))


## v0.1.570 (2023-01-23)

### Bug Fixes

- **tuya**: Fix update loops
  ([`28b66c8`](https://github.com/fhempy/fhempy/commit/28b66c8076981c9af2251e4d7e19c4cf77dfc97f))


## v0.1.569 (2023-01-23)

### Bug Fixes

- **fhempy**: Use services property as get_services is deprecated
  ([`6930105`](https://github.com/fhempy/fhempy/commit/6930105cb48097ae7decd040cbe5debc22e666bf))

### Features

- **esphome**: Update to 2022.12.5
  ([`9007f0e`](https://github.com/fhempy/fhempy/commit/9007f0e606c9f6a73da82675acca2bad4eea26be))


## v0.1.568 (2023-01-23)

### Bug Fixes

- **fhempy**: Fix unknown bluetooth manufacturer error
  ([`376aaa1`](https://github.com/fhempy/fhempy/commit/376aaa14dca71fef5e29844916b8ab6aa319cb69))


## v0.1.567 (2023-01-21)

### Bug Fixes

- **tuya**: Fix factor 10 for productid 37mnhia3pojleqfh
  ([`4e9f479`](https://github.com/fhempy/fhempy/commit/4e9f479d9c254a587450f81e93fd0038cf88a5f9))

- **tuya_cloud**: Create device with tuya_cloud_DEVICEID
  ([`39b8bf0`](https://github.com/fhempy/fhempy/commit/39b8bf050271e477d7431c7d49ed36dd0cfc893d))


## v0.1.566 (2023-01-20)

### Bug Fixes

- **tuya**: Do not poll device on scan
  ([`7540c16`](https://github.com/fhempy/fhempy/commit/7540c16b96255e1f0eebd68a37ceaa3fc216f8e7))


## v0.1.565 (2023-01-20)

### Bug Fixes

- **tuya**: Fix another possible high load bug
  ([`735f0f0`](https://github.com/fhempy/fhempy/commit/735f0f0ff0ec06dfbf8f65faea084bad6af0e893))


## v0.1.564 (2023-01-20)

### Bug Fixes

- **tuya**: Possible high load fix
  ([`f177628`](https://github.com/fhempy/fhempy/commit/f177628924616669e159d47f7482b2961fb32aa3))

### Features

- **esphome**: Update esphome library
  ([`5ba11a9`](https://github.com/fhempy/fhempy/commit/5ba11a9f2621b7623e49373f527a77a73ae761aa))


## v0.1.563 (2023-01-19)

### Bug Fixes

- **tuya**: Do not run update_readings in parallel
  ([`43a588e`](https://github.com/fhempy/fhempy/commit/43a588ef989f50f9b46526c8d4a1bfe50d57b793))


## v0.1.562 (2023-01-19)

### Features

- **tuya**: Show error message in state reading on getdevices error
  ([`f1ebfb2`](https://github.com/fhempy/fhempy/commit/f1ebfb2007e0c59aba768908b44eb7303de831b6))


## v0.1.561 (2023-01-17)

### Bug Fixes

- **blue_connect**: Write gatt event when not connected - lib automatically reconnects
  ([`29b71c0`](https://github.com/fhempy/fhempy/commit/29b71c0714bcfdecce42a126488ecd64952b2a4c))

- **mitemp2**: Notifications are enabled in ble lib
  ([`75918bf`](https://github.com/fhempy/fhempy/commit/75918bfa09ec8c40be88c3fefa5b92b2ac558040))

### Features

- **blue_connect**: Support blue_connect restart
  ([`1d6cb45`](https://github.com/fhempy/fhempy/commit/1d6cb458451a5cdfbae03349b2a012a23f640f27))


## v0.1.560 (2023-01-17)

### Bug Fixes

- **fhempy**: Bluetooth fixes
  ([`68db2d6`](https://github.com/fhempy/fhempy/commit/68db2d6e1bbfda46f3287a84cb457537cb224e6e))

- **fhempy**: Disable asyncio debug
  ([`b08559b`](https://github.com/fhempy/fhempy/commit/b08559bc64382b26e91bd5aef984e0c78f2b8d2d))

- **skodaconnect**: Skoda Connect Update BaseLib ([#121](https://github.com/fhempy/fhempy/pull/121),
  [`08a363f`](https://github.com/fhempy/fhempy/commit/08a363f989cf4cb399455c96cbd104633155b5cc))


## v0.1.559 (2023-01-16)

### Bug Fixes

- **fhempy**: Services not working, use get_services()
  ([`fbea26f`](https://github.com/fhempy/fhempy/commit/fbea26f3d15b7bdc5384b9c84fa18d3c75bfc2fa))


## v0.1.558 (2023-01-16)

### Bug Fixes

- **fhempy**: Fix ble notification subscription
  ([`a3fc5e5`](https://github.com/fhempy/fhempy/commit/a3fc5e5f412a9cbd232ff70601ecbeb76b9d7660))


## v0.1.557 (2023-01-16)

### Bug Fixes

- **eq3bt**: Add exception instead of error logging
  ([`7a6c2bc`](https://github.com/fhempy/fhempy/commit/7a6c2bca20bae055b96fa8deaeff41dd37035375))

- **eq3bt**: Handle timeout
  ([`c18783e`](https://github.com/fhempy/fhempy/commit/c18783e52f7c23a161e1f09ff4a415681e764171))

- **fhempy**: Fix bluetooth reconnect
  ([`5a6b6bc`](https://github.com/fhempy/fhempy/commit/5a6b6bc94c998ac1ce8a027fe5d6622d5d0288e7))

- **fhempy**: Increase timeout
  ([`6c9166b`](https://github.com/fhempy/fhempy/commit/6c9166b81a956d2c88f55c84abf1cae46230ea2a))


## v0.1.556 (2023-01-15)


## v0.1.555 (2023-01-15)

### Bug Fixes

- **ble_reset**: Add missing import
  ([`c5f3c55`](https://github.com/fhempy/fhempy/commit/c5f3c55ccd0dab6cc6afbce5ff505ec619fa54e7))

- **ble_reset**: New ble reset based on bluetooth-auto-recovery lib
  ([`0fed3e7`](https://github.com/fhempy/fhempy/commit/0fed3e74c247a43136f99fa03d9404752de3b2d7))

- **blue_connect**: Bluetoothle core fixes for reconnects
  ([`0cce921`](https://github.com/fhempy/fhempy/commit/0cce921a725dc0f9fca6a2c86beef9bc8d26342e))

- **blue_connect**: Connect only when not connected
  ([`5f2d39e`](https://github.com/fhempy/fhempy/commit/5f2d39e6db366c0eb771fb3f586b8e2656b62376))

- **blue_connect**: Stop loop when cancelled
  ([`380d9aa`](https://github.com/fhempy/fhempy/commit/380d9aa739a85d35a4cfbfeb61f555aa404c2ba7))

- **discover_ble**: Update bleak library
  ([`3e46df8`](https://github.com/fhempy/fhempy/commit/3e46df892a52c9abfc8d8b70debe05732d747ddf))

- **eq3bt**: Add await for disconnect
  ([`80edfcc`](https://github.com/fhempy/fhempy/commit/80edfccc9b7ef49aa9f29178661b64cfaeeced67))

- **eq3bt**: Bleak fixes
  ([`56365a3`](https://github.com/fhempy/fhempy/commit/56365a3fe7f555a63faaa889bc4c5852aca82604))

- **eq3bt**: Fix arguments
  ([`fe7d56c`](https://github.com/fhempy/fhempy/commit/fe7d56cdf259c5ee43d99a15786c943ff812b0f8))

- **eq3bt**: Fix circular import
  ([`f1240b2`](https://github.com/fhempy/fhempy/commit/f1240b2bc28526c78ce99560cd6b8c059b62d114))

- **eq3bt**: Fix notification callback argument
  ([`c35c354`](https://github.com/fhempy/fhempy/commit/c35c354b25552f90b20ef65b41b081e4aad62bc5))

- **eq3bt**: Remove presence reading, stop loop on cancel
  ([`5a3b1a1`](https://github.com/fhempy/fhempy/commit/5a3b1a12f2643d9e74e9b8a7824255737b48dc2e))

- **eq3bt**: Use bleak library
  ([`6de3ef2`](https://github.com/fhempy/fhempy/commit/6de3ef29648d839e369fb0b2ec40dfef29964b53))

- **eq3bt**: Use uuid instead of handle
  ([`97947c2`](https://github.com/fhempy/fhempy/commit/97947c2b1e6285a83d1f8f4aa766268dbcbf13d2))

- **eq3bt**: Wait a few seconds after each thermostat query, fix friday schedule query
  ([`fe0d183`](https://github.com/fhempy/fhempy/commit/fe0d18372c0cc596534c068e45b917e3625ad123))

- **fhempy**: Add bluetooth libs to modules instead of fhempy installation requirement
  ([`a0d321e`](https://github.com/fhempy/fhempy/commit/a0d321edd045109eb50f0ecabaafd48055be37fb))

- **fhempy**: Ble disconnect only when connected
  ([`598b4f8`](https://github.com/fhempy/fhempy/commit/598b4f8e17f71ee66847e534bbedcc873e91adc7))

- **fhempy**: Fix BluetoothLE update_adapters
  ([`e6b91f8`](https://github.com/fhempy/fhempy/commit/e6b91f8f5af1d3308aaa9cf85ddc8d35e4beb217))

- **fhempy**: Remove old bluepy library
  ([`6f8b046`](https://github.com/fhempy/fhempy/commit/6f8b0469d1b59ce83aba4901c757763909f50f7f))

- **gfprobt**: Fix circular import
  ([`c09a74c`](https://github.com/fhempy/fhempy/commit/c09a74c4eec0e32154467e48a20f856fc8356be0))

- **gfprobt**: Use bleak library
  ([`407eec6`](https://github.com/fhempy/fhempy/commit/407eec69cd5be79d0c3b0fc52cf3f766d89d4e8a))

- **mitemp2**: Fix circular import
  ([`3828bad`](https://github.com/fhempy/fhempy/commit/3828badb3af7c2bc18eefb57cbc703bf396fe090))

- **mitemp2**: Setup notify before write
  ([`5cb7ba1`](https://github.com/fhempy/fhempy/commit/5cb7ba10148dcc663875266176131b9d588a5ae2))

- **mitemp2**: Use bleak library
  ([`3ff7d74`](https://github.com/fhempy/fhempy/commit/3ff7d7478ecb78f6c67952045203ce91fad28d63))

### Features

- **fhempy**: Add restart icon and change colour of update icon if update available
  ([`ed8342d`](https://github.com/fhempy/fhempy/commit/ed8342dc4e742e94026f0c9055957c3663a1e244))


## v0.1.554 (2023-01-13)

### Bug Fixes

- **fhempy**: Fix bluetoothle core
  ([`5db91b5`](https://github.com/fhempy/fhempy/commit/5db91b53ebf85713c744253eebd3e5e11be28189))


## v0.1.553 (2023-01-13)


## v0.1.552 (2023-01-12)

### Bug Fixes

- **blue_connect**: Fix register_disconnect_listener
  ([`21d01fc`](https://github.com/fhempy/fhempy/commit/21d01fcb24e355e2eaab56e4b89f3fa5e1d3bd5b))


## v0.1.551 (2023-01-12)

### Bug Fixes

- **blue_connect**: Use fhempy bluetoothle core
  ([`2c31854`](https://github.com/fhempy/fhempy/commit/2c31854f4bab7bedfbc6b4a84789fc9511525406))

### Features

- **fhempy**: Add bleak bluetooth support
  ([`109d88f`](https://github.com/fhempy/fhempy/commit/109d88f767c61d29944d62ba137ef9c6c3bb4652))


## v0.1.550 (2023-01-10)

### Bug Fixes

- **blue_connect**: Disconnect on Undefine, wait 30s if device couldn't be discovered
  ([`26ae0fe`](https://github.com/fhempy/fhempy/commit/26ae0fef29cbbd56e1c185a931905b67cd8c6155))

- **blue_connect**: Fix max ph value
  ([`88d2333`](https://github.com/fhempy/fhempy/commit/88d23335e99e44618abbee30efbd1277bd601dac))

- **blue_connect**: Set variable to None on disconnect, change exception logging
  ([`6e1957d`](https://github.com/fhempy/fhempy/commit/6e1957d5ffd85b9fe7aae797809ec36b4b8ab7d4))

### Features

- **blue_connect**: Add connection reading
  ([`b3eddac`](https://github.com/fhempy/fhempy/commit/b3eddac38715039bdd972e35493beab5b5b2f713))


## v0.1.549 (2023-01-10)

### Bug Fixes

- **blue_connect**: Fix bleak connection
  ([`92beb09`](https://github.com/fhempy/fhempy/commit/92beb09a0d1afa9edd83014ec772d34052a830f4))

- **blue_connect**: Fix Undefine if no task started yet
  ([`8ef8f5d`](https://github.com/fhempy/fhempy/commit/8ef8f5dcc2058a73ffe3c85451172cad269d9e0e))

- **tuya**: Fix master_switch error in log
  ([`c245438`](https://github.com/fhempy/fhempy/commit/c245438c58d37a62db9632cf9fecaa5631c26357))


## v0.1.548 (2023-01-10)

### Bug Fixes

- **blue_connect**: Testing use of bleak instead of bluepy
  ([`0a6d93d`](https://github.com/fhempy/fhempy/commit/0a6d93dbc0f965b92cfb275f9a64bc6fdd8ff2e5))


## v0.1.547 (2023-01-08)

### Features

- **tuya**: Change to colour mode when changing colour data
  ([`5c64e4d`](https://github.com/fhempy/fhempy/commit/5c64e4d0fd9254b7178097b6460528e15c7d50bf))


## v0.1.546 (2023-01-08)

### Features

- **tuya**: Add generic master switch detection
  ([`65c4023`](https://github.com/fhempy/fhempy/commit/65c40239d381277e46bc417bdbc3f5f85f848e62))


## v0.1.545 (2023-01-07)

### Bug Fixes

- **tuya**: Fix RGB colour_data_v2
  ([`c991e09`](https://github.com/fhempy/fhempy/commit/c991e0940ce8213ebac3b803d243dc0174e90257))


## v0.1.544 (2023-01-07)

### Bug Fixes

- **meross**: Fix http api calls by meross-iot lib upgrade
  ([`f17047d`](https://github.com/fhempy/fhempy/commit/f17047d7fd8e40f478c503df3cd4b43e3d579a78))


## v0.1.543 (2023-01-06)

### Bug Fixes

- **fhempy**: Increase timeouts for function handling as fhem answers sometimes take more time on
  high load
  ([`e3693a2`](https://github.com/fhempy/fhempy/commit/e3693a297cf05d5c7783c80c887193478bae0eb5))


## v0.1.542 (2023-01-06)

### Bug Fixes

- **skodaconnect**: Update BaseLib to 1.3.2 ([#115](https://github.com/fhempy/fhempy/pull/115),
  [`dbbb549`](https://github.com/fhempy/fhempy/commit/dbbb549d81dd876f1dead23fac0b2619cf03e6e6))

* Update BaseLib to 1.3.0 (New token handling URLs)

* Update BaseLib to 1.3.2, Modify skodaconnect.py to work with BaseLib > 1.3.0

### Features

- **tuya**: Add error handling if getdevices returns error from tuya cloud
  ([`175d35a`](https://github.com/fhempy/fhempy/commit/175d35a7f6bd97400c2d5c7bf51c4fc0f8142dfe))


## v0.1.541 (2023-01-05)

### Bug Fixes

- **fhempy**: Fix device rename
  ([`4f1f5ea`](https://github.com/fhempy/fhempy/commit/4f1f5ea1979fd9810c3364696768dd627e35b238))


## v0.1.540 (2023-01-04)

### Bug Fixes

- **skodaconnect**: Update BaseLib to 1.3.0 (New token handling URLs)
  ([#111](https://github.com/fhempy/fhempy/pull/111),
  [`8d4f53e`](https://github.com/fhempy/fhempy/commit/8d4f53e8a78f45669833a1db4c27f737b753ec8a))


## v0.1.539 (2023-01-04)

### Bug Fixes

- **fhempy**: Create fhempy_log only on first setup
  ([`309ce46`](https://github.com/fhempy/fhempy/commit/309ce46ef504f592d483c8ff625522f18f381141))


## v0.1.538 (2023-01-02)

### Bug Fixes

- **fhempy**: Fix fhempy_log
  ([`b5125ab`](https://github.com/fhempy/fhempy/commit/b5125abfcd4ecff0609d15453cbb335f6500afc2))


## v0.1.537 (2023-01-02)

### Bug Fixes

- **fhempy**: Fix fhempy_log creation
  ([`b3d3f76`](https://github.com/fhempy/fhempy/commit/b3d3f766f0409e6441288a295229559bd965bf32))


## v0.1.536 (2023-01-02)

### Bug Fixes

- **blue_connect**: Remove unknown_handle_18 reading
  ([`729aac3`](https://github.com/fhempy/fhempy/commit/729aac323d986f532acaaf764bc8ec5ecd04afb6))

- **fhempy**: Create fhempy_log only if it doesn't exist
  ([`781adc1`](https://github.com/fhempy/fhempy/commit/781adc195159dbce5750053ef1c93603c2807246))

- **fhempy**: Use get_fhempy_root()
  ([`11bb24a`](https://github.com/fhempy/fhempy/commit/11bb24a23a28039f3a70f7221c53c6edc599890b))

- **gree_climate**: Fix discovery loop creating too many open udp sockets
  ([`edba7e9`](https://github.com/fhempy/fhempy/commit/edba7e962219eb155ccef3c6e1569563b565d416))

- **tuya**: Fix incorrect scaled values
  ([`ac3c4a3`](https://github.com/fhempy/fhempy/commit/ac3c4a37491e876c78b09ee38e3d7fa98dfe1362))

### Features

- **fhempy**: Add get_fhempy_root()
  ([`410fa8e`](https://github.com/fhempy/fhempy/commit/410fa8e6ddf0e5824095530c49bd4c6fcb687664))

- **fhempy**: Add restart info in state reading
  ([`bf3b54d`](https://github.com/fhempy/fhempy/commit/bf3b54dc422692022a350255fcd260692dcccc4f))

- **tuya**: Support colour_data reading
  ([`d7e3241`](https://github.com/fhempy/fhempy/commit/d7e3241b9bbd9f91fbc0c24d8e4b36324c152dc9))


## v0.1.535 (2022-12-20)

### Bug Fixes

- **tuya**: Fix device IAYz2WK1th0cMLmL
  ([`500fcd1`](https://github.com/fhempy/fhempy/commit/500fcd175d602024ed9504870fef5d546a244b69))


## v0.1.534 (2022-12-18)

### Bug Fixes

- **tuya**: Connect to cloud only if no tuya attr available
  ([`b624b1e`](https://github.com/fhempy/fhempy/commit/b624b1e43add88c0ab9f085207eae28a265898d5))


## v0.1.533 (2022-12-18)

### Bug Fixes

- **tuya**: Fix thermostat productid IAYz2WK1th0cMLmL values
  ([`21cca36`](https://github.com/fhempy/fhempy/commit/21cca36d3bd41113780eeef27ecbd6d1ef3c4100))


## v0.1.532 (2022-12-17)

### Bug Fixes

- **tuya**: Fix value scaling
  ([`fb32943`](https://github.com/fhempy/fhempy/commit/fb329431728c5830c3fcf84ae97829861638e4ec))


## v0.1.531 (2022-12-17)

### Bug Fixes

- **fhempy**: Create fhempy_log device
  ([`82e63b7`](https://github.com/fhempy/fhempy/commit/82e63b710de1045f822204d6a9fa8d8485cf717f))

- **tuya**: Fix step/scale usage for integer values
  ([`170181b`](https://github.com/fhempy/fhempy/commit/170181b10aa3bde9da015263da0fc404fa98fd81))


## v0.1.530 (2022-12-17)

### Bug Fixes

- **tuya**: Fix cur_voltage scale
  ([`8220acb`](https://github.com/fhempy/fhempy/commit/8220acb1abcd8a6de2d961f2b7d685e03cf25482))


## v0.1.529 (2022-12-17)

### Bug Fixes

- **fhempy**: Expand Container Check for Kubernetes
  ([#108](https://github.com/fhempy/fhempy/pull/108),
  [`529f46c`](https://github.com/fhempy/fhempy/commit/529f46c956a0b6459271856e799511139714bbff))

- **fhempy**: Release readingsBeginUpdate lock after 120s if no readingsEndUpdate received
  ([`3607d18`](https://github.com/fhempy/fhempy/commit/3607d18ececf487cf32c60882edd1b84000c4b66))

- **fhempy**: Support kubernetes
  ([`e7be7ac`](https://github.com/fhempy/fhempy/commit/e7be7ac30b00e17a1796515e564e636f2a731bb2))


## v0.1.528 (2022-12-17)

### Features

- **tuya**: Support v3.4 devices, fix "no reading updates"
  ([`cc1414b`](https://github.com/fhempy/fhempy/commit/cc1414b6b039e597ed659d7cb4a3e4e12bcbed56))


## v0.1.527 (2022-12-11)

### Bug Fixes

- **fhempy**: Replace cryptography with pycryptodome
  ([`a4965a3`](https://github.com/fhempy/fhempy/commit/a4965a31877c4417007f13ab7bf8fed0a66cabaa))


## v0.1.526 (2022-12-05)

### Bug Fixes

- **blue_connect**: Change salt to salinity
  ([`4880b33`](https://github.com/fhempy/fhempy/commit/4880b338ff1396d0c6b499e2e69ede0bd24827fc))

- **energie_gv_at**: Fix update interval
  ([`c02acd9`](https://github.com/fhempy/fhempy/commit/c02acd9422a6391fcd7d5ba22991270293a909ce))

### Chores

- Add energie_gv_at
  ([`72e7a37`](https://github.com/fhempy/fhempy/commit/72e7a379aad97c6a467979c085486c083c319748))

### Features

- **blue_connect**: Support salt and conductivity
  ([`3e78ef7`](https://github.com/fhempy/fhempy/commit/3e78ef781555ae083f783b9ba23ec4489c3bf132))


## v0.1.525 (2022-12-04)

### Features

- **energie_gv_at**: Add module to retrieve hours for energy saving
  ([`0ab3689`](https://github.com/fhempy/fhempy/commit/0ab3689750842dc7834739cb72c83df9f073d9fe))


## v0.1.524 (2022-11-26)

### Bug Fixes

- **github_backup**: Handle upload error
  ([`d5d3a86`](https://github.com/fhempy/fhempy/commit/d5d3a8631dbb350603e4288fbac5dda66a06b98f))


## v0.1.523 (2022-11-26)

### Bug Fixes

- **fusionsolar**: Use pycryptodome, re-login on error
  ([`1427342`](https://github.com/fhempy/fhempy/commit/1427342f2c547c411276e5821a7a37feadfea8df))

### Chores

- Fetch all commits ([#107](https://github.com/fhempy/fhempy/pull/107),
  [`e968bcf`](https://github.com/fhempy/fhempy/commit/e968bcf6092b8dce0943f2e6d78f7a5c53865fca))

* Update fhem_test.yml

fetch all commits

* action: auto update controls

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>


## v0.1.522 (2022-11-21)

### Bug Fixes

- **fusionsolar**: Fix region
  ([`f1a49f0`](https://github.com/fhempy/fhempy/commit/f1a49f0b9ddaeb3e120962cc0469159548e508b2))

### Features

- **fusionsolar**: Add more signals data, fix empty battery error
  ([`07df9c1`](https://github.com/fhempy/fhempy/commit/07df9c10af8f7ce468a9c0016c2a04963386dbbd))


## v0.1.521 (2022-11-21)

### Bug Fixes

- **tuya**: Add connection check loop
  ([`32942f4`](https://github.com/fhempy/fhempy/commit/32942f4dc3e2e022d8876e6c5d7898bf861a92d8))


## v0.1.520 (2022-11-20)

### Bug Fixes

- **blue_connect**: Handle broken pipe
  ([`256acae`](https://github.com/fhempy/fhempy/commit/256acae7159666f7ae031a63e11a2e4404e4cb6a))

- **fhempy**: Downgrade cryptography due to installation errors with newer version
  ([`7f2f14c`](https://github.com/fhempy/fhempy/commit/7f2f14c7a75feb8b73231dd496c43afcb21e3594))


## v0.1.519 (2022-11-20)

### Chores

- **deps**: Bump cryptography from 37.0.4 to 38.0.3
  ([#104](https://github.com/fhempy/fhempy/pull/104),
  [`e6ffd8e`](https://github.com/fhempy/fhempy/commit/e6ffd8efc14419f7782393565a13532e8411cc4f))

Bumps [cryptography](https://github.com/pyca/cryptography) from 37.0.4 to 38.0.3. - [Release
  notes](https://github.com/pyca/cryptography/releases) -
  [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst) -
  [Commits](https://github.com/pyca/cryptography/compare/37.0.4...38.0.3)

--- updated-dependencies: - dependency-name: cryptography dependency-type: direct:production

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Features

- **meross**: Add state per channel
  ([`ad734d8`](https://github.com/fhempy/fhempy/commit/ad734d8b78b155469b8437eaf5f89a065cf57471))


## v0.1.518 (2022-11-19)

### Bug Fixes

- **fusionsolar**: Finally support v3 auth
  ([`af63a3c`](https://github.com/fhempy/fhempy/commit/af63a3cde738aa49be5d599bcefb0c234734cd0f))


## v0.1.517 (2022-11-19)

### Bug Fixes

- **fusionsolar**: Try again to fix v3 auth
  ([`8e27c6c`](https://github.com/fhempy/fhempy/commit/8e27c6c6e6a9d3ad4bd19d194bc4f436ea63edf2))


## v0.1.516 (2022-11-19)

### Bug Fixes

- **fusionsolar**: Fix region usage
  ([`a90746a`](https://github.com/fhempy/fhempy/commit/a90746ad3d12d02ad3b6c6e1174ef03a00f5b414))


## v0.1.515 (2022-11-19)

### Bug Fixes

- **volvo_software_update**: Fix headers to prevent blocking
  ([`09a7bdf`](https://github.com/fhempy/fhempy/commit/09a7bdf40053dac3b0273602f895bd0b0f9e9c4a))


## v0.1.514 (2022-11-19)


## v0.1.513 (2022-11-19)

### Bug Fixes

- **fusionsolar**: Retry login max 10 times
  ([`4f7c619`](https://github.com/fhempy/fhempy/commit/4f7c61980ed1ba16dd21a28fbdc801dff5312efa))

- **fusionsolar**: Retry login max 10 times
  ([`66076e4`](https://github.com/fhempy/fhempy/commit/66076e4c656f231d282340ce3fdc629e05ec067e))


## v0.1.510 (2022-11-19)

### Bug Fixes

- **fhempy**: Fix DefineFn and some other fixes by @side79
  ([#100](https://github.com/fhempy/fhempy/pull/100),
  [`f896ea4`](https://github.com/fhempy/fhempy/commit/f896ea438888ec32f1198f13a65d328c31161431))

* fix define function

- BindingsIo_Define - remove protypes from BindingsIo_Initialize - Store Fn References as coderefs

* Add workflow for testing fhem module use perl with multi threading support

* added some ignores .gitignore

* update setup-fhem

* add plan to test

don't run tests parallel, because we need fhemweb with port binding

run update controls in separate job

* Create .gitattributes

Set Line endings to crlf for perlModule files.

* changed lineendings

* declare variable from main program

* changed search for existing devspec to devspec2array fn

add variable from main program

* avoid duplicate defines of same device small search improvement

* action: auto update controls

Signed-off-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

* added check for bindingtype

added tests

* Added support for "Python" as Bindingtype

* add python binary to FHEM modules updater controls file

Co-authored-by: github-actions <41898282+github-actions[bot]@users.noreply.github.com>

Co-authored-by: Dominik <dominik.karall@gmail.com>

- **fusionsolar**: Try to implement v3 authentication
  ([`ddb7283`](https://github.com/fhempy/fhempy/commit/ddb72838fe4ece4d5b98e93b5debad87096a2948))


## v0.1.509 (2022-11-12)

### Bug Fixes

- **fhempy**: Fix ble stop_helper
  ([`5e48356`](https://github.com/fhempy/fhempy/commit/5e483568919f90425a14be65b0423a4eafcd3969))

- **fhempy**: Fix innerHTML error
  ([`23c95b8`](https://github.com/fhempy/fhempy/commit/23c95b87bb5c739f6793e15e47f3bf33f09e146c))

### Chores

- Update controls
  ([`1c96321`](https://github.com/fhempy/fhempy/commit/1c963216231324cc2c1d189af828170123e57daa))


## v0.1.508 (2022-10-16)

### Chores

- Update controls
  ([`56e3239`](https://github.com/fhempy/fhempy/commit/56e3239764a424716b50432ee389db62126c1eed))

### Features

- **blue_connect**: Reconnect on BrokenPipeError
  ([`533d218`](https://github.com/fhempy/fhempy/commit/533d21803699f17d257471f89b8e04901e0704c0))

- **fhempy**: Support stop BLE helper to reconnect
  ([`5edf2da`](https://github.com/fhempy/fhempy/commit/5edf2dab63d8ddbe5123d760504e86f928c7aeaf))

- **fusionsolar**: Retry get request if it fails
  ([`975e787`](https://github.com/fhempy/fhempy/commit/975e7872b601a0e4e25bbf04bfab57d3e62d4d48))

- **websitetests**: Add websitetests
  ([`6482aca`](https://github.com/fhempy/fhempy/commit/6482acac6a62d873da1bbc122a47d70b0a33d130))


## v0.1.507 (2022-10-14)

### Bug Fixes

- **ddnss**: Fix connection issues
  ([`bca55e3`](https://github.com/fhempy/fhempy/commit/bca55e372654085c2c91e55d39f8f934ad915238))

### Chores

- Update controls
  ([`d34311f`](https://github.com/fhempy/fhempy/commit/d34311f0807dc0961c9dad09a6d4f48a6cbde28a))

### Features

- **arp_presence**: Add update command
  ([`48ef150`](https://github.com/fhempy/fhempy/commit/48ef150eff0d5fa339788e45de8cbf5f918d5517))

- **websitetests**: Add simple response check
  ([`84ecf90`](https://github.com/fhempy/fhempy/commit/84ecf90fe248a093cb11731dba9f8ced108d530a))


## v0.1.506 (2022-10-11)

### Bug Fixes

- **esphome**: Remove insaller link, it's part of esphome dashboard now
  ([`7657c38`](https://github.com/fhempy/fhempy/commit/7657c3814271a1b30166a96cedce4328910e4385))

- **fhempy**: Fix description
  ([`57cc650`](https://github.com/fhempy/fhempy/commit/57cc65063900db746152f0b4fa0d38b19b8c3abe))

- **fusionsolar**: Fix issues when some values are not reported by fusionsolar api
  ([`9018cb9`](https://github.com/fhempy/fhempy/commit/9018cb937ce2738f1cbc9a33e253764e01282948))

- **kia_hyundai**: Retry login every 2min if it fails
  ([`e5a1005`](https://github.com/fhempy/fhempy/commit/e5a10059707386fbccf223ebfcdaf22b5c7b9ca8))

### Chores

- Update controls
  ([`f81fb9f`](https://github.com/fhempy/fhempy/commit/f81fb9f97e6a09994e7e3fa124fee8c7e3e8a852))

### Features

- **arp_presence**: Check presene based on arp table, works also for iOS devices
  ([`7608dcd`](https://github.com/fhempy/fhempy/commit/7608dcd16bcc46d877973a05176bee5b655ac609))


## v0.1.505 (2022-10-10)

### Bug Fixes

- **tuya**: Fix colour_data
  ([`2dc4f07`](https://github.com/fhempy/fhempy/commit/2dc4f075adbec7fb6eafb25293920d15f0779246))

- **tuya**: Set state on startup only if there is no state reading
  ([`68c7f65`](https://github.com/fhempy/fhempy/commit/68c7f65c2201e85b07b6c8fc594681679304e206))

### Chores

- Update controls
  ([`b246252`](https://github.com/fhempy/fhempy/commit/b246252a19c3600b058336133be4610f9d64d830))


## v0.1.504 (2022-10-09)

### Bug Fixes

- **zigbee2mqtt**: Fix update
  ([`7c4bb66`](https://github.com/fhempy/fhempy/commit/7c4bb663aefc102d911ab1cfdbd535a565a6aadb))

### Chores

- Update controls
  ([`005194e`](https://github.com/fhempy/fhempy/commit/005194e592e3275ce6f242bb39a20e9fcd127cd6))


## v0.1.503 (2022-10-09)

### Bug Fixes

- **esphome**: Update esphome==2022.9.4
  ([`ed2e4d0`](https://github.com/fhempy/fhempy/commit/ed2e4d08bc7ed2b774dc72793c97d3da8bc56211))

- **tuya**: Add dp_ attributes even if they are not detected
  ([`fe295dc`](https://github.com/fhempy/fhempy/commit/fe295dc74c34312244626e621fd73e8171a49e62))

### Chores

- Update controls
  ([`495cbc5`](https://github.com/fhempy/fhempy/commit/495cbc5f43a58bf689a44f3cb00dffcad87b05be))


## v0.1.502 (2022-10-09)

### Bug Fixes

- **fhempy**: Disable events for the moment
  ([`5c6dee0`](https://github.com/fhempy/fhempy/commit/5c6dee08151f2b33e87fa14101915e542ecacc89))

- **fusionsolar**: Retry login if it fails
  ([`de70e9c`](https://github.com/fhempy/fhempy/commit/de70e9c26f00f8c954a30fbeb3ae2bfc1e1a90e8))

- **google_weather**: Add further user agent
  ([`5c8ecaa`](https://github.com/fhempy/fhempy/commit/5c8ecaa4df6fb56c9e30bf17e63af45ea53e5fec))

- **tuya**: Update tinytuya==1.7.1
  ([`d8e2c66`](https://github.com/fhempy/fhempy/commit/d8e2c66c3e8744171360a255dff10b10de526129))

### Chores

- Update controls
  ([`5a745a3`](https://github.com/fhempy/fhempy/commit/5a745a34abb2988a81c92a4d0713c57a5a665897))


## v0.1.501 (2022-10-05)

### Chores

- Update controls
  ([`69baa35`](https://github.com/fhempy/fhempy/commit/69baa35c879489f1e8a8ca27d07024b447199e67))

### Features

- **skodaconnect**: New sensors for Enyaq iV ([#98](https://github.com/fhempy/fhempy/pull/98),
  [`a157ab9`](https://github.com/fhempy/fhempy/commit/a157ab9d24ebcd84eb4efcd5fdb02937a5b93dac))


## v0.1.500 (2022-10-05)

### Bug Fixes

- **kia_hyundai**: Check refresh token before update
  ([`041c732`](https://github.com/fhempy/fhempy/commit/041c732d5ee12977f91c3600592b33db825ad46a))

### Chores

- Update controls
  ([`1e52036`](https://github.com/fhempy/fhempy/commit/1e52036c92d7c5203cc6233159eba9442ebfd07f))


## v0.1.499 (2022-10-05)

### Chores

- Update controls
  ([`72ec615`](https://github.com/fhempy/fhempy/commit/72ec615ca74c6a24b510696857a072f4be82afb2))

### Features

- **tuya**: Support led colours
  ([`852f522`](https://github.com/fhempy/fhempy/commit/852f522533e97c00421ffddfc36595906d48f3b2))


## v0.1.498 (2022-10-04)

### Bug Fixes

- **tuya**: Set tuya state reading to ready when finished initializing
  ([`79c247e`](https://github.com/fhempy/fhempy/commit/79c247e4a133e2f8d974f361c720eccb4804c882))

### Chores

- Update controls
  ([`bd00cda`](https://github.com/fhempy/fhempy/commit/bd00cdaeaf8aa02b6a617b1d7789e2c3bb1220b2))


## v0.1.497 (2022-10-03)

### Bug Fixes

- **fhempy**: Add logging if sending to fhem needs to wait too long
  ([`36f12ec`](https://github.com/fhempy/fhempy/commit/36f12ec66e3972bdb122d8c6426c7ba514b2508a))

- **fhempy**: Disable readme help for the moment due to websocket issues
  ([`30eb51f`](https://github.com/fhempy/fhempy/commit/30eb51f92edb34924c2de62f34a7c51b9d5ba88a))

- **fhempy**: Reinit frames on error
  ([`ccbb284`](https://github.com/fhempy/fhempy/commit/ccbb284035bd03c384b5ab066ada4a914ec6ab66))

### Chores

- Update controls
  ([`1b4c1f0`](https://github.com/fhempy/fhempy/commit/1b4c1f06e1b5e520317641f5404839993355b07c))


## v0.1.496 (2022-10-03)

### Bug Fixes

- **fhempy**: Fix websocket write_limit
  ([`3023385`](https://github.com/fhempy/fhempy/commit/302338574c0c2a6eba329c91df2d51b7e2bc1e2b))

### Chores

- Update controls
  ([`144855a`](https://github.com/fhempy/fhempy/commit/144855a198b2e6c4435e96b210088b7e832f630e))


## v0.1.495 (2022-10-02)

### Bug Fixes

- **fhempy**: Fix some websocket issues
  ([`587d0f0`](https://github.com/fhempy/fhempy/commit/587d0f0f78f7c4ba794a161eb0df19705cdbef75))

### Chores

- Update controls
  ([`b5d17cb`](https://github.com/fhempy/fhempy/commit/b5d17cb35c2ebbe69e919f93c7157c24fe236f49))


## v0.1.494 (2022-10-02)

### Bug Fixes

- **fusionsolar**: Fix to_grid values
  ([`12e57eb`](https://github.com/fhempy/fhempy/commit/12e57eb08afec8088197d44659974b65a778f12c))

### Chores

- Update controls
  ([`79064a9`](https://github.com/fhempy/fhempy/commit/79064a924163180ed1e57f8fc7490eaf626a9ba4))


## v0.1.493 (2022-10-02)

### Bug Fixes

- **tuya**: Fix non-str spec values
  ([`baa5977`](https://github.com/fhempy/fhempy/commit/baa59774279d1e54a1ef4c4e06a8e2993fde917b))

### Chores

- Update controls
  ([`29cf186`](https://github.com/fhempy/fhempy/commit/29cf186222100293e5f91a8d25b6a8259a142c6e))


## v0.1.492 (2022-10-02)

### Bug Fixes

- **kia_hyundai**: Always update readings
  ([`e221894`](https://github.com/fhempy/fhempy/commit/e2218944d2d6231fe35394b84a70e2272ca7133c))

### Chores

- Update controls
  ([`303b57f`](https://github.com/fhempy/fhempy/commit/303b57f7ddd99d22f5cf6df5683af0cf1faa85d3))

### Features

- **kia_hyundai**: Set state readings to online/error
  ([`dd5190d`](https://github.com/fhempy/fhempy/commit/dd5190d946d861dbd97514a07ced6b20b78a298f))


## v0.1.491 (2022-10-02)

### Bug Fixes

- **tuya**: Fix issue with boolean specs
  ([`7b3910f`](https://github.com/fhempy/fhempy/commit/7b3910fe285a300e300bcdd2fdc942ed06ac9fdf))

### Chores

- Update controls
  ([`e2b5a23`](https://github.com/fhempy/fhempy/commit/e2b5a23161d7d204bd9aaf8dde53220ae7574818))


## v0.1.490 (2022-10-01)

### Bug Fixes

- **gree_climate**: Add missing self.device = None
  ([`2a7657f`](https://github.com/fhempy/fhempy/commit/2a7657ff21d2d1f20ed943c726a708fc86e41f26))

### Chores

- Update controls
  ([`d0763bf`](https://github.com/fhempy/fhempy/commit/d0763bf92011f5bccff51544775b167041c80573))


## v0.1.489 (2022-10-01)

### Bug Fixes

- **gree_climate**: Retry connect if first connection attempt fails
  ([`1eee34a`](https://github.com/fhempy/fhempy/commit/1eee34af7fc6bfc06ef6f7c8c440b4afd35643f0))

### Chores

- Update controls
  ([`f6f0b51`](https://github.com/fhempy/fhempy/commit/f6f0b5163fb618da30d79e5481ecb9db734f6b8f))


## v0.1.488 (2022-10-01)

### Bug Fixes

- **fusionsolar**: Better logging on data errors
  ([`adb5902`](https://github.com/fhempy/fhempy/commit/adb590267127e277a6932f01d56be129f56e7e78))

- **websitetests**: Fix reading response_status
  ([`a0371a8`](https://github.com/fhempy/fhempy/commit/a0371a854d12ddeea1b0b087f34fa5035dd2a021))

### Chores

- Update controls
  ([`a3ec896`](https://github.com/fhempy/fhempy/commit/a3ec896ec7ecaed1191ea68215ee442c3f526cc2))

### Features

- **kia_hyundai**: Support update_data command
  ([`7b4876b`](https://github.com/fhempy/fhempy/commit/7b4876bf6f8466d2287b21819a3dda058e9e6a43))

- **kia_hyundai**: Update to latest kia_uvo code
  ([`638a7c8`](https://github.com/fhempy/fhempy/commit/638a7c808d6537e998deace600814e327fbd4a6f))


## v0.1.487 (2022-09-29)

### Bug Fixes

- **blue_connect**: Keep connection active
  ([`88f6f49`](https://github.com/fhempy/fhempy/commit/88f6f491be7d08aa78ad421949fc725931b2a6c1))

- **websitetests**: Support URLs with =
  ([`97a4cce`](https://github.com/fhempy/fhempy/commit/97a4cce3a3b0074d50699516c297a3d2033f76ac))

### Chores

- Update controls
  ([`5021c5f`](https://github.com/fhempy/fhempy/commit/5021c5f8ca691d240de8e948c024b1fffaca2cd1))


## v0.1.486 (2022-09-28)

### Bug Fixes

- **websitetests**: Limit response reading to 5000 characters
  ([`f350798`](https://github.com/fhempy/fhempy/commit/f3507988b4b9776fffde807ef2609313ca79d8a1))

### Chores

- Update controls
  ([`0d90f3f`](https://github.com/fhempy/fhempy/commit/0d90f3f412d98fb9fbb4c6d956dbe6fdc0b42fef))

### Features

- **websitetests**: Small module to test speed of web responses
  ([`48e5c4e`](https://github.com/fhempy/fhempy/commit/48e5c4e8c3d741006b9a49a1e73aa7072f866c7a))


## v0.1.485 (2022-09-28)

### Bug Fixes

- **fhempy**: Fix "continue" response to FHEM
  ([`d63f0dd`](https://github.com/fhempy/fhempy/commit/d63f0dd1517d197ac56ead22007f2b439d304962))

### Chores

- Update controls
  ([`e202dbe`](https://github.com/fhempy/fhempy/commit/e202dbed437b7a9229a80aa2e360a14319b2a839))


## v0.1.484 (2022-09-28)

### Bug Fixes

- **tuya**: Fix translation for enum
  ([`31ddac2`](https://github.com/fhempy/fhempy/commit/31ddac209e2894c8b20809610337e697149d00a9))

### Chores

- Update controls
  ([`a1b08ab`](https://github.com/fhempy/fhempy/commit/a1b08aba7a458fcd83d770ce8b553d25614b65e9))


## v0.1.483 (2022-09-27)

### Bug Fixes

- **tuya**: Fix translation for enums
  ([`348e176`](https://github.com/fhempy/fhempy/commit/348e176c67360efcda6855305901a668f1afe850))

### Chores

- Update controls
  ([`08e68f1`](https://github.com/fhempy/fhempy/commit/08e68f1c2a14f068058dd168d2c9bb0bf22d45c5))


## v0.1.482 (2022-09-27)

### Bug Fixes

- **googlecast**: Update youtube_dl/spotipy
  ([`6d94d69`](https://github.com/fhempy/fhempy/commit/6d94d697e86d2448c45606e096116af274500b67))

- **spotify**: Update spotipy lib
  ([`bbd9ae8`](https://github.com/fhempy/fhempy/commit/bbd9ae82c8366e37792cab4e9c432d05d990c304))

### Chores

- Add comment
  ([`ecb6074`](https://github.com/fhempy/fhempy/commit/ecb60748433d00bc5a937feae362301d805385c3))

- Update controls
  ([`f4f7cc5`](https://github.com/fhempy/fhempy/commit/f4f7cc5c2f8c8ac49b427d9bba4a0e739d0874a7))


## v0.1.481 (2022-09-27)

### Bug Fixes

- **tuya**: Use online reading for online/offline state
  ([`dd75bf3`](https://github.com/fhempy/fhempy/commit/dd75bf33a4e9bb9986ffe6009cde25d3e0d974c4))

### Chores

- Update controls
  ([`f4ea7ba`](https://github.com/fhempy/fhempy/commit/f4ea7baa6c0d974fd5a8a759fd5243870efcdfe6))

### Features

- **tuya**: Add translation for kettle state
  ([`eafac0c`](https://github.com/fhempy/fhempy/commit/eafac0c06c4ff3e9a17decd2f4c3b9c52edd1596))


## v0.1.480 (2022-09-27)

### Bug Fixes

- **blue_connect**: Keep BLE connection
  ([`7e89afd`](https://github.com/fhempy/fhempy/commit/7e89afd0f47132ed462e7e6d7c28b29b59106a92))

- **fhempy**: Support ws msgs up to 10MiB
  ([`87bfd3e`](https://github.com/fhempy/fhempy/commit/87bfd3e8baf6a6974ce6fe3caec617d7726877da))

### Chores

- Remove space at end of line
  ([`a3d9ec3`](https://github.com/fhempy/fhempy/commit/a3d9ec39d54f3ad89c73d6c1e6322b853625b320))

- Update controls
  ([`9bbeb67`](https://github.com/fhempy/fhempy/commit/9bbeb67e377bc4b5edf5d5c3e4d4d8f442b76737))


## v0.1.479 (2022-09-26)

### Bug Fixes

- **fhempy**: Better connection closed handling
  ([`c59119f`](https://github.com/fhempy/fhempy/commit/c59119fec1dc26963898c93d2e9e7ee221b32c2e))

- **fhempy**: Make DevIo_IsOpen call more clear
  ([`2216284`](https://github.com/fhempy/fhempy/commit/2216284cfed0159cf991ebd06fab4d391e00b6ae))

### Chores

- Update controls
  ([`cc5bbc9`](https://github.com/fhempy/fhempy/commit/cc5bbc97dd6df61e9b27b78918d02ae8e557814a))


## v0.1.478 (2022-09-26)

### Bug Fixes

- **fhempy**: Fix asyncio warnings for WebSocketServerProtocol.handler()
  ([`cf11e97`](https://github.com/fhempy/fhempy/commit/cf11e97054c43d701ad9a864e834540ab6236ff7))

### Chores

- Update controls
  ([`89339e4`](https://github.com/fhempy/fhempy/commit/89339e45441a3c1eb35b6bc0e2d7f12867a124d8))


## v0.1.477 (2022-09-25)

### Bug Fixes

- **blue_connect**: Try to connect 10 times every 10s on failure
  ([`2571ab1`](https://github.com/fhempy/fhempy/commit/2571ab175d6eb29814ebc4bbadbdab7aa1acd2b0))

- **fhempy**: Improve log message
  ([`47598df`](https://github.com/fhempy/fhempy/commit/47598df0563c069983c73b5543280df2610d9c4f))

- **google_weather**: Use several user agent strings
  ([`7b0730c`](https://github.com/fhempy/fhempy/commit/7b0730c93ecff146a0df39d0a46c201e1303fef0))

- **tuya**: Do not rais exception on CancelledError
  ([`f9fe2f9`](https://github.com/fhempy/fhempy/commit/f9fe2f9a61c87d872c20a05254cc57f34489d937))

### Chores

- Update controls
  ([`3fac186`](https://github.com/fhempy/fhempy/commit/3fac186c2a97679417ec10a14db5dedc0dc500ac))

- **tuya**: Add reference comment
  ([`65a24dd`](https://github.com/fhempy/fhempy/commit/65a24dd1fee9df94107fff390796a8dbfc2388fc))

### Features

- **fhempy**: Add healthcheck possibility
  ([`11e2ef8`](https://github.com/fhempy/fhempy/commit/11e2ef8b700e5be56d0014bfb328c94948e3378f))


## v0.1.476 (2022-09-24)

### Chores

- Update controls
  ([`56c5862`](https://github.com/fhempy/fhempy/commit/56c5862bcb5fe627f23dab9d139974dc390d8707))

### Features

- **meross**: Support thermostat
  ([`842ad75`](https://github.com/fhempy/fhempy/commit/842ad750590a47b3a518b4c7e3f8d939af79f60b))


## v0.1.475 (2022-09-24)

### Bug Fixes

- **fhempy**: Fix max_payload_size websocket issues, add state info on first define
  ([`896ed11`](https://github.com/fhempy/fhempy/commit/896ed11ed34b1d6aed8db3522f06a5684c4937e0))

### Chores

- Update controls
  ([`2336ce3`](https://github.com/fhempy/fhempy/commit/2336ce3c0d9901a90a44d42639d1001ae2a4e752))


## v0.1.474 (2022-09-24)

### Bug Fixes

- **fhempy**: Recommend Python 3.8 or higher
  ([`1d44b53`](https://github.com/fhempy/fhempy/commit/1d44b538e79a2f01cca0e5ec96f66cc9ebe18aeb))

- **tuya**: Fix values wrong format
  ([`8c44946`](https://github.com/fhempy/fhempy/commit/8c44946b1aafbf7ffb96183794a4d0a4d8d9082d))

### Chores

- Update controls
  ([`0f77aa9`](https://github.com/fhempy/fhempy/commit/0f77aa9fdde712339b61c331ec261b27064d064c))


## v0.1.473 (2022-09-21)

### Bug Fixes

- **fhempy**: Better log when advertising fhempy on local network
  ([`bdff568`](https://github.com/fhempy/fhempy/commit/bdff5686eb9402e18c74aa733dba9fe7ee8021ed))

- **tuya**: Fix readings for local mapping
  ([`5f557cc`](https://github.com/fhempy/fhempy/commit/5f557cc3a453be89103707487cc2d667a459ace8))

- **zigbee2mqtt**: Start z2m after update
  ([`f6687aa`](https://github.com/fhempy/fhempy/commit/f6687aa7a566b748469d88d4e62fbbbc42a4ee55))

### Chores

- Update controls
  ([`2ac2376`](https://github.com/fhempy/fhempy/commit/2ac2376f07da75b55bc57ea11635fa573d4e38a3))

### Features

- **tuya**: Support productid utzgmksz7zj66als
  ([`af599ff`](https://github.com/fhempy/fhempy/commit/af599ffa664085f34ce29aeb86195763f6d7e840))


## v0.1.472 (2022-09-20)

### Bug Fixes

- **gfprobt**: Fix circular import
  ([`5b4670b`](https://github.com/fhempy/fhempy/commit/5b4670b7a06c1ff14f651eb0f1c142fceb3e6188))

### Chores

- Update controls
  ([`7ce24de`](https://github.com/fhempy/fhempy/commit/7ce24defb462e3a3b81b4513235dff3996ddfa6c))


## v0.1.471 (2022-09-20)

### Bug Fixes

- **blue_connect**: Do not round battery reading
  ([`30cf035`](https://github.com/fhempy/fhempy/commit/30cf03544c4b10060ac90a1db1c4f3da1ff217c1))

### Chores

- Update controls
  ([`f8f1d52`](https://github.com/fhempy/fhempy/commit/f8f1d52d37bea675f8856f0d3818e5cd22316080))


## v0.1.470 (2022-09-20)

### Bug Fixes

- **blue_connect**: Do not round battery reading
  ([`b7a5ccb`](https://github.com/fhempy/fhempy/commit/b7a5ccb3ef1d4043dea4d0c3f753a8ed713296d2))

### Chores

- Update controls
  ([`099db5d`](https://github.com/fhempy/fhempy/commit/099db5daea1f5916db53ff7fa77c38ed356f5ba3))


## v0.1.469 (2022-09-20)

### Bug Fixes

- **blue_connect**: Set readings 0 on errors
  ([`7d8d27c`](https://github.com/fhempy/fhempy/commit/7d8d27ccfd929b120e717b61176db9485f0ca496))

### Chores

- Update controls
  ([`d23d3b6`](https://github.com/fhempy/fhempy/commit/d23d3b674e62ca8706734c87689e5cdd046fef58))

### Features

- **blue_connect**: Support battery
  ([`f8d1360`](https://github.com/fhempy/fhempy/commit/f8d13603662a53ef6b19bf24fd0080c47c2a00ef))


## v0.1.468 (2022-09-19)

### Chores

- Update controls
  ([`ca03d1b`](https://github.com/fhempy/fhempy/commit/ca03d1b46cf9b38c972033b395cf9b977035bbe5))

### Features

- **blue_connect**: Add raw data reading
  ([`2d6b32c`](https://github.com/fhempy/fhempy/commit/2d6b32cee3dcc735baf68b2f047c1ce4510b2389))


## v0.1.467 (2022-09-18)

### Bug Fixes

- **blue_connect**: Fix retry
  ([`14e29d8`](https://github.com/fhempy/fhempy/commit/14e29d8fccaf97b4ea55ae9ab9bcc349a324aadd))

### Chores

- Update controls
  ([`96fa113`](https://github.com/fhempy/fhempy/commit/96fa1138b030de2ceb86e89b57978249947a0217))


## v0.1.466 (2022-09-18)

### Chores

- Update controls
  ([`d69903c`](https://github.com/fhempy/fhempy/commit/d69903c0cead55542386412bcb88670ce5865934))

### Features

- **esphome**: Update to 2022.8.3
  ([`eb93ae9`](https://github.com/fhempy/fhempy/commit/eb93ae95cf9451fbb239f73ea399f5e70ec734f7))


## v0.1.465 (2022-09-18)

### Chores

- Update controls
  ([`a4a3029`](https://github.com/fhempy/fhempy/commit/a4a30296dfafd9297b397913ba06cb7daf0d2a7c))

### Features

- **blue_connect**: Add state reading and ph/orp_state reading
  ([`fd682b8`](https://github.com/fhempy/fhempy/commit/fd682b865d40ccba5073120e528b6e91990cf2b3))


## v0.1.464 (2022-09-18)

### Bug Fixes

- **blue_connect**: Fix blue connect
  ([`63a0356`](https://github.com/fhempy/fhempy/commit/63a0356e36b242dad06c52cfca7f95a982d4aae2))

### Chores

- Update controls
  ([`9c08819`](https://github.com/fhempy/fhempy/commit/9c08819747f7f39eddb536704d3b5156290b7c6d))


## v0.1.463 (2022-09-16)

### Bug Fixes

- **blue_connect**: Add retries
  ([`49a8833`](https://github.com/fhempy/fhempy/commit/49a88330c07754631c990d8b86c74f111629cdcc))

### Chores

- Update controls
  ([`53761e6`](https://github.com/fhempy/fhempy/commit/53761e6097dc5ebd2c508a42a96579d3a5b4304d))

### Features

- **blue_connect**: Initial version
  ([`fa0b3fd`](https://github.com/fhempy/fhempy/commit/fa0b3fd6a156bffab9a740d7016a5e167780c5e8))

- **fhempy**: Force version update
  ([`4ac7a31`](https://github.com/fhempy/fhempy/commit/4ac7a31dd5cf792d9ede472928b4c7f2a1d447a4))


## v0.1.462 (2022-09-12)

### Bug Fixes

- **fhempy**: Fix docker installation?
  ([`31417aa`](https://github.com/fhempy/fhempy/commit/31417aa12d2dc4fa8ce71c069c0ca5064a14e433))

### Chores

- Update controls
  ([`f600f2a`](https://github.com/fhempy/fhempy/commit/f600f2ab9e9e9f75b0823186dc9e6e2d09f580da))


## v0.1.461 (2022-09-09)

### Bug Fixes

- **github_backup**: Only update file if sha1 sum changes
  ([`3cc7b7a`](https://github.com/fhempy/fhempy/commit/3cc7b7a2e9c68500ea556f5c51ea39aea134640c))

- **kia_hyundai**: Add pytz dependency
  ([`21eac89`](https://github.com/fhempy/fhempy/commit/21eac89b19f46af95e772b4925873cd78d813639))

### Chores

- Update controls
  ([`5b8649d`](https://github.com/fhempy/fhempy/commit/5b8649d733fed33e707ae1703630c3fc9b076d1b))


## v0.1.460 (2022-09-09)

### Bug Fixes

- **kia_hyundai**: Fix name of dateutil
  ([`ad28c6b`](https://github.com/fhempy/fhempy/commit/ad28c6bd7195fe5c3c8a24fe0f62d954f933c166))

### Chores

- Update controls
  ([`c7a47ef`](https://github.com/fhempy/fhempy/commit/c7a47ef6b2ed38b41847e3228962ce841c10ae50))


## v0.1.459 (2022-09-09)

### Bug Fixes

- **kia_hyundai**: Add dateutil
  ([`da3d112`](https://github.com/fhempy/fhempy/commit/da3d1125d4da5963024b32a5fc3fb8ded5f88171))

### Chores

- Update controls
  ([`26b1ad7`](https://github.com/fhempy/fhempy/commit/26b1ad7a8b82007b831a9be5bb9e4604c2b986f1))


## v0.1.458 (2022-09-08)

### Bug Fixes

- **skodaconnect**: Update Base Lib ([#88](https://github.com/fhempy/fhempy/pull/88),
  [`b2d2c8f`](https://github.com/fhempy/fhempy/commit/b2d2c8f14676cd3ab12374ef6981cd57942faa16))

### Chores

- Update controls
  ([`6aa59b9`](https://github.com/fhempy/fhempy/commit/6aa59b9abd03a34a70fe6ac503992e859422ab3d))

### Features

- **github_backup**: Improve commit message
  ([`dfb29ed`](https://github.com/fhempy/fhempy/commit/dfb29ed138ad4631e907c20c7a88af47c9ce1eb2))


## v0.1.457 (2022-09-06)

### Bug Fixes

- **fhempy**: Fix memory leak
  ([`45f8909`](https://github.com/fhempy/fhempy/commit/45f89092b95a7335322897f8d832970a875d9646))

### Chores

- Update controls
  ([`15f7b4d`](https://github.com/fhempy/fhempy/commit/15f7b4d78fc14863c64d4dce7198f2eb3cc6a200))


## v0.1.456 (2022-09-05)

### Bug Fixes

- **tuya**: Fix json loads
  ([`5037a89`](https://github.com/fhempy/fhempy/commit/5037a89b300e2220c2a01b398101f345838c8552))

### Chores

- Update controls
  ([`24a1c91`](https://github.com/fhempy/fhempy/commit/24a1c91c4edc68bb2e04ddb4dfad9c04e240efed))


## v0.1.455 (2022-09-05)

### Bug Fixes

- **tuya**: Fix translation again
  ([`754061d`](https://github.com/fhempy/fhempy/commit/754061dbd2ee2eba7c46eb4b0df13a38085077ed))

### Chores

- Fix newline
  ([`ad6d16b`](https://github.com/fhempy/fhempy/commit/ad6d16b64a098d05b97467418d56629f572c7949))

- Update controls
  ([`707ce01`](https://github.com/fhempy/fhempy/commit/707ce016d09b449016e8af00a19089c9c95b2e5a))


## v0.1.454 (2022-09-05)

### Chores

- Update controls
  ([`6fabe66`](https://github.com/fhempy/fhempy/commit/6fabe668bea945c8956842460d2d93623307e5bf))

### Features

- **skodaconnect**: Update base lib
  ([`811efce`](https://github.com/fhempy/fhempy/commit/811efce3ff4e6c906b3b9de05c6beae4edd6ec55))


## v0.1.453 (2022-09-05)

### Bug Fixes

- **tuya**: Fix translation error for local devices
  ([`7fd5dcb`](https://github.com/fhempy/fhempy/commit/7fd5dcbca46f47f852dbeaae4122ad33356a527f))

### Chores

- Update controls
  ([`1aa007b`](https://github.com/fhempy/fhempy/commit/1aa007b913a8eabb698a275d5017190fcfb02a7c))


## v0.1.452 (2022-09-05)

### Bug Fixes

- **tuya**: Fix set translation
  ([`6aac36d`](https://github.com/fhempy/fhempy/commit/6aac36d1fb1cea1a11d6bb5128e15dbcdaefa779))

### Chores

- Update controls
  ([`ebc36f2`](https://github.com/fhempy/fhempy/commit/ebc36f2c61a56633572458f24ec8836df1381be2))


## v0.1.451 (2022-09-04)

### Chores

- Update controls
  ([`3c44579`](https://github.com/fhempy/fhempy/commit/3c4457970c5c517f5c55cf853205484ac0c63adc))

### Features

- **tuya**: Support translation in mappings
  ([`2875c31`](https://github.com/fhempy/fhempy/commit/2875c31507712241f14e64af6da3d4aee499d85e))


## v0.1.450 (2022-09-04)

### Bug Fixes

- **fusionsolar**: Fix pv string current reading
  ([`1e94c42`](https://github.com/fhempy/fhempy/commit/1e94c428b7dcafdaea057d6a0f139530fecfc276))

- **github_backup**: Fix sha compare
  ([`96a7c07`](https://github.com/fhempy/fhempy/commit/96a7c072f0146bbe1bba3e3a859038a12734f10e))

### Chores

- Update controls
  ([`8b01ded`](https://github.com/fhempy/fhempy/commit/8b01dedc5e1f1eb5b3841edd8ba4b0490b3e3030))


## v0.1.449 (2022-09-03)

### Chores

- Update controls
  ([`42a17ae`](https://github.com/fhempy/fhempy/commit/42a17ae5fb7de8ee52a8dc7db1b41a93a5fec3da))

### Features

- **tuya**: Add kettle support
  ([`92d5a09`](https://github.com/fhempy/fhempy/commit/92d5a09428946a43a957fd982d2ca1457973db87))


## v0.1.448 (2022-09-03)

### Chores

- Update controls
  ([`1e1243a`](https://github.com/fhempy/fhempy/commit/1e1243aacb7c88402c240e7df42a60b57b44faad))

### Features

- **fusionsolar**: Add string voltage/current
  ([`f7d4b3d`](https://github.com/fhempy/fhempy/commit/f7d4b3da7703d460b45ec5403ddb8eb6b12dba8f))


## v0.1.447 (2022-09-02)

### Bug Fixes

- **fhempy**: Support function_param also without function parameter in set_conf
  ([`2c5bb67`](https://github.com/fhempy/fhempy/commit/2c5bb670b97721fb9b1a3093334d8d5b0e5fa8a3))

### Chores

- Update controls
  ([`272493c`](https://github.com/fhempy/fhempy/commit/272493c260d729b93535eb84d5b72e65160dc58d))

### Features

- **fusionsolar**: Correct ratio values when battery is used
  ([`6d190ba`](https://github.com/fhempy/fhempy/commit/6d190bad0579d4382fe09f70d3064a0088b6630a))


## v0.1.446 (2022-09-01)

### Bug Fixes

- **meross**: Fix on/off
  ([`fe931dc`](https://github.com/fhempy/fhempy/commit/fe931dca53ae4a520d3e617cae53103c328c98ca))

### Chores

- Update controls
  ([`0477245`](https://github.com/fhempy/fhempy/commit/047724535fe45befed2bc1566e08fade25e8b98c))


## v0.1.445 (2022-08-31)

### Bug Fixes

- **meross**: Fix channel handling again
  ([`c48c59e`](https://github.com/fhempy/fhempy/commit/c48c59efb130598dc2cf29b35edfc09adb2e3cf9))

### Chores

- Update controls
  ([`f530782`](https://github.com/fhempy/fhempy/commit/f53078270c43b3862fa0e5b3175cb54c36b193b6))


## v0.1.444 (2022-08-30)

### Bug Fixes

- **meross**: Fix channel support
  ([`a94020d`](https://github.com/fhempy/fhempy/commit/a94020db5358c84640297f6548dc02957ee705f9))

### Chores

- Disable Python 3.10 tests
  ([`4886469`](https://github.com/fhempy/fhempy/commit/4886469bc776e0b5c6f47214afdec9642e5c8da0))

- Update controls
  ([`46dc137`](https://github.com/fhempy/fhempy/commit/46dc137636271896c828a1e2d95dcf230b22e5ec))


## v0.1.443 (2022-08-29)

### Chores

- Update controls
  ([`345e90b`](https://github.com/fhempy/fhempy/commit/345e90bf15357592a4ed8b292eb4cbd84310e6c0))

### Features

- **fhempy**: Report error when fhempy takes longer than 5s to send back answer to fhem
  ([`9825a67`](https://github.com/fhempy/fhempy/commit/9825a67608b33d2108295c23a7c026a748f8b1e8))


## v0.1.442 (2022-08-28)

### Chores

- Update controls
  ([`9f59743`](https://github.com/fhempy/fhempy/commit/9f5974324049dd99b36620cdd378177ab47d9eda))

### Features

- **meross**: Support channels
  ([`7c89512`](https://github.com/fhempy/fhempy/commit/7c89512d10636da3f7e3f521120e31d6b6258828))


## v0.1.441 (2022-08-24)

### Bug Fixes

- **tuya**: Fix use API_KEY and API_SECRET reading
  ([`ad8db6c`](https://github.com/fhempy/fhempy/commit/ad8db6c5d34087c2ad10e3468f77f50b022ef5c6))

### Chores

- Update controls
  ([`20b8a76`](https://github.com/fhempy/fhempy/commit/20b8a765e7eacde77cbb03a9dd4b17d48b8cfe87))


## v0.1.440 (2022-08-22)

### Chores

- Update controls
  ([`de12c70`](https://github.com/fhempy/fhempy/commit/de12c7021bd38d3888dd58a408af8d8766927af4))

### Features

- **fhempy**: Support time format in set/attr
  ([`ecc84a3`](https://github.com/fhempy/fhempy/commit/ecc84a303d35afc1edcc636c071f8e6867106491))

- **github_backup**: New attr backup_time, support directories
  ([`2e26689`](https://github.com/fhempy/fhempy/commit/2e266895281081be544fe81ab5c8a2799e1d3d91))


## v0.1.439 (2022-08-21)

### Chores

- Update controls
  ([`d87824a`](https://github.com/fhempy/fhempy/commit/d87824a73c8a31eaa827faeb23280f0bcee2433b))

### Features

- **github_backup**: Support binary files
  ([`c94bb7f`](https://github.com/fhempy/fhempy/commit/c94bb7fbd1ad1e1a6f046a67a038de917b92ab37))


## v0.1.438 (2022-08-21)

### Bug Fixes

- **github_backup**: Fix do_backup call
  ([`0a83c07`](https://github.com/fhempy/fhempy/commit/0a83c070aa99353543d17448978ce7923904e1c0))

### Chores

- Update controls
  ([`23a8dfb`](https://github.com/fhempy/fhempy/commit/23a8dfb83109c021ca24f866aa8a871f97bb7741))


## v0.1.437 (2022-08-21)

### Bug Fixes

- **github_backup**: Fix set backup_now
  ([`e28e7af`](https://github.com/fhempy/fhempy/commit/e28e7afb8523ba6533b20afd3eca9ab54c5719a2))

### Chores

- Update controls
  ([`6f9ed08`](https://github.com/fhempy/fhempy/commit/6f9ed082224df57356fec01b267bd8574fd68a75))


## v0.1.436 (2022-08-21)

### Chores

- Update controls
  ([`3c4eb06`](https://github.com/fhempy/fhempy/commit/3c4eb06d7e5e87564ae71c1da82f57c4aa00313e))

### Features

- **github_backup**: New github_backup module
  ([`6bff115`](https://github.com/fhempy/fhempy/commit/6bff115b9825aeecad6eab2af0ddf9eb0a192a83))


## v0.1.435 (2022-08-20)

### Bug Fixes

- **fhempy**: Fix log level which caused delays
  ([`0b26f20`](https://github.com/fhempy/fhempy/commit/0b26f209e275e51834ffb7e55d6ea30e02635f2d))

### Chores

- Update controls
  ([`6a9b3b2`](https://github.com/fhempy/fhempy/commit/6a9b3b21654f4791c1ab82346376b08c01de38be))

### Features

- **ddnssde**: Add ddnssde
  ([`2c706ab`](https://github.com/fhempy/fhempy/commit/2c706ab5ecd73db20f110e0b472dcfa76245aefd))


## v0.1.434 (2022-08-20)

### Bug Fixes

- **object_detection**: Fix import
  ([`a815b68`](https://github.com/fhempy/fhempy/commit/a815b6854e6ebffe04d1c8017d24cdba28d5ec18))

### Chores

- Update controls
  ([`cf6185d`](https://github.com/fhempy/fhempy/commit/cf6185d9715f3266457a27615e29402ece8c75b2))


## v0.1.433 (2022-08-20)

### Bug Fixes

- **object_detection**: Fix import
  ([`7fc674e`](https://github.com/fhempy/fhempy/commit/7fc674e55a44302d3060e9f85d24ebdc91903c62))

### Chores

- Update controls
  ([`d55ced9`](https://github.com/fhempy/fhempy/commit/d55ced92f7a3e3ed6b2ac6f636114d46ce0ebaa9))


## v0.1.432 (2022-08-20)

### Bug Fixes

- **ddnssde**: Fix ip_check_interval attr
  ([`5ebca91`](https://github.com/fhempy/fhempy/commit/5ebca91b068b857a1d0da5f5a47fdc562c513e6b))

### Chores

- Update controls
  ([`109e94d`](https://github.com/fhempy/fhempy/commit/109e94d62afe226f6bba0039b3ae3f28980d00e7))


## v0.1.431 (2022-08-20)

### Bug Fixes

- **object_detection**: Update opencv lib
  ([`192f91d`](https://github.com/fhempy/fhempy/commit/192f91dd70f3396be52f3ad3627bc8b9187ff7f9))

- **object_detection**: Update tflite-runtime
  ([`b2f5880`](https://github.com/fhempy/fhempy/commit/b2f588005d9257a1252bdadcfdef9591105a9aa7))

### Chores

- Update controls
  ([`5c67d07`](https://github.com/fhempy/fhempy/commit/5c67d073fcd8e8c0f0986750d359888ab7e2954d))


## v0.1.430 (2022-08-20)

### Bug Fixes

- **geizhals**: Add missing dependency
  ([`1bab5a8`](https://github.com/fhempy/fhempy/commit/1bab5a8c0cc77d00545ccd5f70001d4bfd9a3999))

### Chores

- Update controls
  ([`ad76a82`](https://github.com/fhempy/fhempy/commit/ad76a8277e3e86513c39d727845b06f0b62d6cce))


## v0.1.429 (2022-08-20)

### Chores

- Add python 3.10
  ([`55b06df`](https://github.com/fhempy/fhempy/commit/55b06df3b55d3050234147878a9a4a0d525eaa79))

- Code style fixes
  ([`81f7b41`](https://github.com/fhempy/fhempy/commit/81f7b41450ccd65da2c7c8960e4ed1244b142da4))

- Fix python version
  ([`8df0f0a`](https://github.com/fhempy/fhempy/commit/8df0f0a36e4699ca4baaaf58510f4bf2cb0b0fa8))

- Fix tests
  ([`194f77f`](https://github.com/fhempy/fhempy/commit/194f77f3e83ee561ef345922d72c4c64ca662c2c))

- Update controls
  ([`1ed4b8f`](https://github.com/fhempy/fhempy/commit/1ed4b8f674391f8cf993d480f58ea966c023b245))

- Update setup-python to v4
  ([`7fe9f74`](https://github.com/fhempy/fhempy/commit/7fe9f74821b319dcdee6fd0d6e729f8967a34025))


## v0.1.428 (2022-08-20)

### Chores

- Update controls
  ([`012d3df`](https://github.com/fhempy/fhempy/commit/012d3dfb1a0ad90c4d1cecd065b98fd7a9e7af8f))


## v0.1.427 (2022-08-20)

### Chores

- Run tests on ubuntu-22.04
  ([`77bb85d`](https://github.com/fhempy/fhempy/commit/77bb85d9eca8e6d1a619cff5f963a9cc95c8da6c))

- Update controls
  ([`a9ffa57`](https://github.com/fhempy/fhempy/commit/a9ffa579da3d0e81a533fc1adb1c8688956faad1))


## v0.1.426 (2022-08-20)

### Chores

- Run tests on ubuntu 22.04
  ([`0ab5657`](https://github.com/fhempy/fhempy/commit/0ab5657ac69bbb20310dd0a5785832deef91ae85))

- Update controls
  ([`942db87`](https://github.com/fhempy/fhempy/commit/942db878bf1750894ded596ec8bd18cc4f265738))


## v0.1.425 (2022-08-20)

### Chores

- Update controls
  ([`f03ec5e`](https://github.com/fhempy/fhempy/commit/f03ec5e9932f749be6a906efb08233f8c49e17e0))

### Features

- **ddnssde**: Add ddnss.de IP updater
  ([`5ec7e04`](https://github.com/fhempy/fhempy/commit/5ec7e0413af4aae2bc8e777ff86a5c3cc2fe81f8))


## v0.1.424 (2022-08-13)

### Bug Fixes

- **fhempy**: Fix restart
  ([`4f7d452`](https://github.com/fhempy/fhempy/commit/4f7d45216fb967a69215d3b9ea20b0b9dcb62e69))

### Chores

- Update controls
  ([`bc288e1`](https://github.com/fhempy/fhempy/commit/bc288e1243dc778cc9f241d5c3ba61d8de82d0c2))


## v0.1.423 (2022-08-13)

### Bug Fixes

- **fhempy**: Stop sending msgs on shutdown
  ([`f1c9041`](https://github.com/fhempy/fhempy/commit/f1c90415e1af54b9dc07ed2ea303464f1abbf555))

### Chores

- Update controls
  ([`c37afab`](https://github.com/fhempy/fhempy/commit/c37afab7ccea45747dd75ee53ed410a02eef3000))


## v0.1.422 (2022-08-13)

### Bug Fixes

- **fhempy**: Handle close frame
  ([`d8e5b44`](https://github.com/fhempy/fhempy/commit/d8e5b44e5a37dce52d1ae531bf8f289637e7a00b))

### Chores

- Update controls
  ([`52f3b54`](https://github.com/fhempy/fhempy/commit/52f3b54221c64cd1df6f0bd8c4fc28bd06a9c3ac))


## v0.1.421 (2022-08-13)

### Bug Fixes

- **fhempy**: Fix long running set on define
  ([`24f99f8`](https://github.com/fhempy/fhempy/commit/24f99f8a21bc38e0dab396f816d40dc650a46b01))

### Chores

- Update controls
  ([`8ce1297`](https://github.com/fhempy/fhempy/commit/8ce12971b518ed00319b108c5437e7dc24e7255d))


## v0.1.420 (2022-08-13)

### Bug Fixes

- **fhempy**: Add more details to readme
  ([`402735e`](https://github.com/fhempy/fhempy/commit/402735ec9274ecfd756eeecfc225dc705b3b8342))

### Chores

- Update controls
  ([`70d4a31`](https://github.com/fhempy/fhempy/commit/70d4a315955ffad134b379406a68970600b7dfe2))


## v0.1.419 (2022-08-13)

### Bug Fixes

- **fhempy**: Logging seems to block fhempy
  ([`15872ee`](https://github.com/fhempy/fhempy/commit/15872eef3e5a3166d6d2c6982cab14cfc317a04e))

### Chores

- Update controls
  ([`0c7f81d`](https://github.com/fhempy/fhempy/commit/0c7f81d3c9a475d3b22bbc5b35bec79a866c7fb8))


## v0.1.418 (2022-08-13)

### Bug Fixes

- **fhempy**: Reduce timeout, fix hangup
  ([`f90b516`](https://github.com/fhempy/fhempy/commit/f90b5165d7157558024fbced8459b4e908fc7fae))

### Chores

- Update controls
  ([`6dee8e2`](https://github.com/fhempy/fhempy/commit/6dee8e29ed8e67216edca46c48cfd1686fbc433b))

### Features

- **fhempy**: Add long running log again
  ([`69ab9bc`](https://github.com/fhempy/fhempy/commit/69ab9bcb4c02f7fc5566a5dbdb7779c1d423b0e1))


## v0.1.417 (2022-08-13)

### Bug Fixes

- **fhempy**: Fix hang on startup
  ([`d943ddd`](https://github.com/fhempy/fhempy/commit/d943ddd2ebf2fb542a06ba124a5ce409e841a17e))

### Chores

- Update controls
  ([`9f89cdf`](https://github.com/fhempy/fhempy/commit/9f89cdfb72f5077978902523f9ce2a7134f1244c))


## v0.1.416 (2022-08-13)

### Chores

- Update controls
  ([`5302d10`](https://github.com/fhempy/fhempy/commit/5302d103fd9af44c04b4848520b5ec1646625bec))

### Features

- **fhempy**: Log error when fhempy takes over 100ms to reply to fhem
  ([`0649ec7`](https://github.com/fhempy/fhempy/commit/0649ec7c392da8b90dc5acecb8db864453fa4dd9))


## v0.1.415 (2022-08-13)

### Bug Fixes

- **xiaomi_tokens**: Fix logging
  ([`2859f1f`](https://github.com/fhempy/fhempy/commit/2859f1f0ac0c966401e21d3b482333d3975301d6))

### Chores

- Update controls
  ([`bed7c16`](https://github.com/fhempy/fhempy/commit/bed7c167b7e7b62bf8f2a1dfaf460ccd9eff5ca0))

### Features

- **fhempy**: Log error if fhem took longer than 200ms to handle cmd
  ([`2767776`](https://github.com/fhempy/fhempy/commit/27677769cb7372055ebdff5255771ca31203fad5))


## v0.1.414 (2022-08-13)

### Chores

- Update controls
  ([`852eb95`](https://github.com/fhempy/fhempy/commit/852eb9564e87ed35716a35bb151a2aa09e8187a3))


## v0.1.413 (2022-08-13)

### Bug Fixes

- **fhempy**: Better error handling for fhempy connection
  ([`a1fb108`](https://github.com/fhempy/fhempy/commit/a1fb10858b348f57fc6748af8e25ffc3b6444b53))

### Chores

- Touch BindingsIo insead of PythonModule
  ([`362c19f`](https://github.com/fhempy/fhempy/commit/362c19f3903c0481a7f93b1272f05cd133da9fb3))

- Update controls
  ([`21fae0a`](https://github.com/fhempy/fhempy/commit/21fae0a732e2e0fb27a26592f9662f3fdebde5a5))


## v0.1.412 (2022-08-13)

### Bug Fixes

- **fhempy**: Better error handling
  ([`9331279`](https://github.com/fhempy/fhempy/commit/933127998e0f1c1ca69ff0d647f18631e786fb2e))

- **fhempy**: Deactivate MOV for controls file
  ([`4bb248b`](https://github.com/fhempy/fhempy/commit/4bb248bac3e7956dbefa7667d9403f4d788d75ca))

### Chores

- Update controls
  ([`085a329`](https://github.com/fhempy/fhempy/commit/085a329f6afd09b58a532a59394e55f5adb65bdb))

### Features

- **fhempy**: Add fhem log entry on update
  ([`dc89f94`](https://github.com/fhempy/fhempy/commit/dc89f9428dec62ab6d49a9ef002fa25dc995d63f))


## v0.1.411 (2022-08-12)

### Bug Fixes

- **fhempy**: Fix continue in some cases and fix devStateIcon
  ([`5c98ef5`](https://github.com/fhempy/fhempy/commit/5c98ef5c987c5076debf5324bd26f9ba4bb1e310))

- **fhempy**: Set devio log level to 5
  ([`f5d9492`](https://github.com/fhempy/fhempy/commit/f5d94928e67a54c68c6348509505feb1b34ee9f9))

- **fhempy**: Skip non-utf8 messages
  ([`c1abfd1`](https://github.com/fhempy/fhempy/commit/c1abfd1662af378e15c70e753fdbaf4b79336e4b))

### Chores

- Update controls
  ([`d7b3ab4`](https://github.com/fhempy/fhempy/commit/d7b3ab4bde4ace997a136c18e99dcd08404babc9))

### Features

- **fhempy**: Receive all fhem events in fhempy
  ([`0aad85a`](https://github.com/fhempy/fhempy/commit/0aad85a1dccb1efb514fb2925175f7ee60199e67))


## v0.1.410 (2022-08-12)

### Bug Fixes

- **xiaomi_tokens**: Fix newline from readings
  ([`4bba6f3`](https://github.com/fhempy/fhempy/commit/4bba6f3398d5b6e95e29c6be637c4b73aaa67ae9))

### Chores

- Update controls
  ([`a20c818`](https://github.com/fhempy/fhempy/commit/a20c8183ca29a44c7617ca80a7fa0fddf91d1228))


## v0.1.409 (2022-08-12)

### Bug Fixes

- **xiaomi_tokens**: Fix rstrip
  ([`9e5bc0d`](https://github.com/fhempy/fhempy/commit/9e5bc0dfc486b9815c5b1dd8c614c1d04f2d40a8))

### Chores

- Update controls
  ([`6d1c1ad`](https://github.com/fhempy/fhempy/commit/6d1c1ad9712ac2433e8d6c61dc424e17ab8dc136))


## v0.1.408 (2022-08-12)

### Bug Fixes

- **fhempy**: Migrate to fhempy
  ([`33ad82a`](https://github.com/fhempy/fhempy/commit/33ad82ae0c0f3f212af442d6075c2b05beb8ce8a))

- **fhempy**: Migrate to fhempyServer
  ([`710f79e`](https://github.com/fhempy/fhempy/commit/710f79e281b522eec6a1de3ffeaefc04f2bca429))

- **xiaomi_tokens**: Remove newline from username, password
  ([`1e5ef64`](https://github.com/fhempy/fhempy/commit/1e5ef642e94df0d10e29fc118bbbc862b6332d97))

### Chores

- Update controls
  ([`d9a85c3`](https://github.com/fhempy/fhempy/commit/d9a85c3e09023b786527b244b9081591d2595f6c))


## v0.1.407 (2022-08-12)

### Bug Fixes

- **fhempy**: Log utf-8 decode error
  ([`5249cee`](https://github.com/fhempy/fhempy/commit/5249ceeb5b4fb966018be6815863cf918e4eedcd))

### Chores

- Update controls
  ([`0da79ba`](https://github.com/fhempy/fhempy/commit/0da79ba09ff219c55dbefdc57cf8124b52279b7a))


## v0.1.406 (2022-08-12)

### Bug Fixes

- **fhempy**: Fix sendBackError without id
  ([`c32c271`](https://github.com/fhempy/fhempy/commit/c32c271fdc63b4d9303a250af8c32f150f80e118))

### Chores

- Update controls
  ([`30bd1db`](https://github.com/fhempy/fhempy/commit/30bd1db13fe9ffab0be6e12c956691aa753ecfb0))


## v0.1.405 (2022-08-11)

### Bug Fixes

- **fhempy**: Send back error on json error
  ([`7d951d1`](https://github.com/fhempy/fhempy/commit/7d951d1dc87f4d8a879ffd0d785dc1440367e81e))

- **fhempy**: Send binary data via websocket
  ([`912f15f`](https://github.com/fhempy/fhempy/commit/912f15f06d08c9ced432ae2a6760d65c0d27ea80))

### Chores

- Update controls
  ([`a83d482`](https://github.com/fhempy/fhempy/commit/a83d48249a32231f1794eb9fc6261a154a893f49))


## v0.1.404 (2022-08-11)

### Bug Fixes

- **fhempy**: Fix message handling
  ([`6c3a835`](https://github.com/fhempy/fhempy/commit/6c3a8351ac1c6269d0208f4ea27a9d81c687a363))

### Chores

- Update controls
  ([`9b2de63`](https://github.com/fhempy/fhempy/commit/9b2de63a159c493e8bcbe8d27685b9889d2b0818))


## v0.1.403 (2022-08-11)

### Bug Fixes

- **esphome**: Update esphome lib
  ([`6cff272`](https://github.com/fhempy/fhempy/commit/6cff2724203a6ae50feaf909c59dce2dac7da3ad))

- **fhem_forum**: Fix state reading
  ([`6f42906`](https://github.com/fhempy/fhempy/commit/6f42906e7436303df50dd086d1cfb9e968b502aa))

### Chores

- Update controls
  ([`b9ecef7`](https://github.com/fhempy/fhempy/commit/b9ecef78f9818f10882f792614c3399cf6844788))

### Features

- **fhempy**: Support binary messages from fhem
  ([`63d8b92`](https://github.com/fhempy/fhempy/commit/63d8b92ecb6a0aa6eb08720eb6e20b9b43438176))


## v0.1.402 (2022-08-10)

### Bug Fixes

- **fhempy**: Fix disconnected icon
  ([`05994b9`](https://github.com/fhempy/fhempy/commit/05994b970a69b032abf2b8a35e213f2fcc11eb8f))

### Chores

- Update controls
  ([`4dd2092`](https://github.com/fhempy/fhempy/commit/4dd209287af731871f0c5a6da3a2c6a95df3872d))


## v0.1.401 (2022-08-10)

### Bug Fixes

- **fhempy**: Update available fhempy version every 12 hours
  ([`8af8092`](https://github.com/fhempy/fhempy/commit/8af8092ff0a76b39e3827b97a54223324967f441))

### Chores

- Update controls
  ([`27f5849`](https://github.com/fhempy/fhempy/commit/27f584967a76883da6114af3834fbe24c4a4fcfc))


## v0.1.400 (2022-08-10)

### Bug Fixes

- **fhempy**: Always show update icon in BindingsIo device
  ([`cb322da`](https://github.com/fhempy/fhempy/commit/cb322da3014d80f3f17686d81594eee54eaa4621))

### Chores

- Update controls
  ([`ff3e06e`](https://github.com/fhempy/fhempy/commit/ff3e06e30c52b2421b1428fbf700ae2e4088c91d))


## v0.1.399 (2022-08-10)

### Chores

- Update controls
  ([`6fe451c`](https://github.com/fhempy/fhempy/commit/6fe451c64be17fbfff673536d2f7b02063387a6c))

### Features

- **fhempy**: Add info about available update
  ([`23fd613`](https://github.com/fhempy/fhempy/commit/23fd613b9f6430b85c8371e1edbcdb4dd3f2f0f3))


## v0.1.398 (2022-08-10)

### Bug Fixes

- **fhem_forum**: Fix state reading
  ([`e0abe40`](https://github.com/fhempy/fhempy/commit/e0abe40e32ffe4b842e6f83252f00846c9159e8c))

- **fhempy**: Fix README for blocking code
  ([`81e332f`](https://github.com/fhempy/fhempy/commit/81e332fcad42a8c00f8ab2a270d4c65bca3b7a5b))

### Chores

- Update controls
  ([`a1f3b32`](https://github.com/fhempy/fhempy/commit/a1f3b32af2f04516732d4dd2d05e8abd194679e3))


## v0.1.397 (2022-08-10)

### Chores

- Update controls
  ([`a5910f2`](https://github.com/fhempy/fhempy/commit/a5910f26e63a816ef0f28f592db33ce3c8552dd3))

### Features

- **miio**: Update python-miio lib
  ([`b5b65ac`](https://github.com/fhempy/fhempy/commit/b5b65acab2ceabeb25b25eeab190021ccbfc7e0a))


## v0.1.396 (2022-08-10)

### Bug Fixes

- **fhem_forum**: Fix keyword handling and state reading
  ([`a6af955`](https://github.com/fhempy/fhempy/commit/a6af955e48fbed5457f18ceed794526856be6e23))

- **fhem_forum**: Fix state
  ([`7371bf4`](https://github.com/fhempy/fhempy/commit/7371bf40b6860ac585d606aa1812c1babc99668d))

- **fhempy**: Change timeout to 60s on shutdown/restart
  ([`0b87dbf`](https://github.com/fhempy/fhempy/commit/0b87dbfef46fcdc5b44ab7f9f6e44ccdbb297ba0))

### Chores

- Update controls
  ([`b608988`](https://github.com/fhempy/fhempy/commit/b60898869f7db0f09e16ddbfd9810f70973977f3))

### Features

- **geizhals**: Add alias attr, best store reading and store availability
  ([`874d5c9`](https://github.com/fhempy/fhempy/commit/874d5c9b6c437b2128d0131c0135e9457b3bd363))


## v0.1.395 (2022-08-10)

### Chores

- Update controls
  ([`6cdffbe`](https://github.com/fhempy/fhempy/commit/6cdffbe5b2d2fe3e76f7b787d01a0b53dca79d90))

### Features

- **fhem_forum**: Check FHEM forum for updates
  ([`4e843e0`](https://github.com/fhempy/fhempy/commit/4e843e024fb8cd7ad6f14a48f4c58b0929b9b33a))


## v0.1.394 (2022-08-09)

### Bug Fixes

- **fhempy**: Fix restart/shutdown issues
  ([`8198930`](https://github.com/fhempy/fhempy/commit/8198930a92ca50c86db8c91e8e12a3466dd98447))

- **geizhals**: Change default update interval
  ([`e11770e`](https://github.com/fhempy/fhempy/commit/e11770e95aa05cb509db6604572ae8f9941360a6))

- **google_weather**: Add headers
  ([`5b0d423`](https://github.com/fhempy/fhempy/commit/5b0d4237cd37df7bbf71d963f5cd834273969d66))

### Chores

- Update controls
  ([`f3d8c1b`](https://github.com/fhempy/fhempy/commit/f3d8c1bc39b11f8e1a3c9af5c969e8ee62164597))


## v0.1.393 (2022-08-08)

### Chores

- Update controls
  ([`2115f4b`](https://github.com/fhempy/fhempy/commit/2115f4b54675486416f7ef2186eae967060b9fdf))

### Features

- **geizhals**: Add link reading
  ([`fd9ee3a`](https://github.com/fhempy/fhempy/commit/fd9ee3a876fe624d2a6f8e14690b670521dd546c))


## v0.1.392 (2022-08-07)

### Bug Fixes

- **tuya**: Correct current, power values
  ([`229d549`](https://github.com/fhempy/fhempy/commit/229d54968dd365662ccde90bc81207715a638991))

- **warema**: Add README
  ([`f836930`](https://github.com/fhempy/fhempy/commit/f8369301590ee560fa25beeeeecdc3ad79aac107))

### Chores

- Update controls
  ([`369b14d`](https://github.com/fhempy/fhempy/commit/369b14d12743100f9d1fde1bdcfe0bbfca6db53b))


## v0.1.391 (2022-08-07)

### Bug Fixes

- **tuya**: Fix dp readings when locally not detected
  ([`e4b5f92`](https://github.com/fhempy/fhempy/commit/e4b5f928d6dc9e8f61bd6ebd35200016f51aa0fc))

### Chores

- Update controls
  ([`d5df523`](https://github.com/fhempy/fhempy/commit/d5df5235f4ce13682fdba6833bed0a88b135e172))


## v0.1.390 (2022-08-06)

### Bug Fixes

- **tuya**: Add debug msgs
  ([`53732a9`](https://github.com/fhempy/fhempy/commit/53732a97581df0b4e55037d751ebc92677b5d236))

### Chores

- Update controls
  ([`3066b47`](https://github.com/fhempy/fhempy/commit/3066b47172dd7ca578b2c8c6604471d708f533d7))


## v0.1.389 (2022-08-06)

### Chores

- Update controls
  ([`c10d115`](https://github.com/fhempy/fhempy/commit/c10d1156583cada247fcdb974a8d94a815710530))

### Features

- **kia_hyundai**: Support commands
  ([`4fa92bf`](https://github.com/fhempy/fhempy/commit/4fa92bfc36fc030b24a8ec8d19ea9deae1611119))


## v0.1.388 (2022-08-06)

### Chores

- Update controls
  ([`52d10a5`](https://github.com/fhempy/fhempy/commit/52d10a5e9f29b102075776adab8dd361c8d63be7))

### Features

- **kia_hyundai**: Initial release for Kia / Hyundai cars
  ([`08987cb`](https://github.com/fhempy/fhempy/commit/08987cbeedcf8ed235e952950a6f0d5cf13606eb))


## v0.1.387 (2022-08-06)

### Chores

- Update controls
  ([`95f07b7`](https://github.com/fhempy/fhempy/commit/95f07b7e2446cb25025d84c59e28b5b74f1acb26))

### Features

- **tuya**: Support Json for category zndb devices
  ([`53209ff`](https://github.com/fhempy/fhempy/commit/53209ff361fabfe3d8b6dc4014753234cbbe0487))


## v0.1.386 (2022-08-05)

### Bug Fixes

- **fhempy**: Support string format for flatten_json
  ([`d7457a8`](https://github.com/fhempy/fhempy/commit/d7457a851d0374fc1fda76ece0fa775f7c3234f0))

- **fusionsolar**: Better error handling
  ([`03d67f3`](https://github.com/fhempy/fhempy/commit/03d67f3e0b191be42d8c08f7b2e3d949624bbb85))

### Chores

- Update controls
  ([`91e6682`](https://github.com/fhempy/fhempy/commit/91e66822952117e99431bf6ddd2a6edd56d46a72))

### Features

- **tuya**: Split json into multiple readings
  ([`366d729`](https://github.com/fhempy/fhempy/commit/366d729267d27c9603bef1bbe1a929ef5cca9f97))


## v0.1.385 (2022-08-04)

### Chores

- Update controls
  ([`7a80ba6`](https://github.com/fhempy/fhempy/commit/7a80ba640fe3a991846248801df29dc026eb7319))

### Features

- **geizhals**: Add geizhals module
  ([`dda5f09`](https://github.com/fhempy/fhempy/commit/dda5f0989f2adb395c1ac9b3be9157f2a4421512))


## v0.1.384 (2022-08-04)

### Bug Fixes

- **google_weather**: Fix replace command
  ([`311ee9c`](https://github.com/fhempy/fhempy/commit/311ee9c9adc10d481b89819be532d1b212c905ec))

### Chores

- Update controls
  ([`3f225b7`](https://github.com/fhempy/fhempy/commit/3f225b7c7592480fe99bdbd46b7c5850b1e3cffd))

### Features

- **geizhals**: Retrieve best prices from geizhals
  ([`b6c935e`](https://github.com/fhempy/fhempy/commit/b6c935e75521d9432b18541aa9c2d55f86c19b6d))


## v0.1.383 (2022-08-04)

### Chores

- Update controls
  ([`07e723b`](https://github.com/fhempy/fhempy/commit/07e723b219b8342d6bc38b38c816b122726e69e6))

### Features

- **google_weather**: Add hourly weather data
  ([`65101c3`](https://github.com/fhempy/fhempy/commit/65101c33101c5a8996d3ab07cbccd1728fff8580))


## v0.1.382 (2022-08-03)

### Chores

- Update controls
  ([`60f37c9`](https://github.com/fhempy/fhempy/commit/60f37c98bf390c0ab39a975ab029bcc429f4195a))


## v0.1.381 (2022-08-03)

### Bug Fixes

- **gree_climate**: Update greeclimate lib
  ([`db874ed`](https://github.com/fhempy/fhempy/commit/db874ed9a002ecf6ba4906501a08fbf09ad4370c))

- **zigbee2mqtt**: Fix restart
  ([`d872abd`](https://github.com/fhempy/fhempy/commit/d872abd0581c045a4beac6c5f11a4bcc1fcbf1bc))

### Chores

- Update controls
  ([`f3d65ce`](https://github.com/fhempy/fhempy/commit/f3d65ce808aa12097c97a86391e230bfab4fe847))

- Update naming
  ([`e1aa1cc`](https://github.com/fhempy/fhempy/commit/e1aa1ccfcb32e72ea8195bc5212ef355dc73fb9b))

### Features

- **google_weather**: Add google weather
  ([`6a45ff5`](https://github.com/fhempy/fhempy/commit/6a45ff5f23a2fc545075ee22186507d44e0cf3a6))


## v0.1.380 (2022-07-16)

### Bug Fixes

- **fhempy**: Handle defmod/modify properly
  ([`c0e29df`](https://github.com/fhempy/fhempy/commit/c0e29df6ac8cb38c8c12bfe1185414bb3d85daf4))

### Chores

- Update controls
  ([`e09a9f2`](https://github.com/fhempy/fhempy/commit/e09a9f29abd3fe349f6c4157240dd3afea5462a7))


## v0.1.379 (2022-07-15)

### Bug Fixes

- **gree_climate**: Retry to establish connection on startup
  ([`4a8141c`](https://github.com/fhempy/fhempy/commit/4a8141c47d4a6829ac50e700df59d3ab358d3df3))

### Chores

- Update controls
  ([`43ec5aa`](https://github.com/fhempy/fhempy/commit/43ec5aaceef7a1b86bab6c66d963f02bf52002fb))


## v0.1.378 (2022-07-13)

### Bug Fixes

- **fusionsolar**: Fix login procedure
  ([`a2387c1`](https://github.com/fhempy/fhempy/commit/a2387c12f9ba53a5ac1b6d79b5785f41441aaf98))

### Chores

- Update controls
  ([`f639680`](https://github.com/fhempy/fhempy/commit/f63968072338b62ad397389b971dbc713879b6aa))


## v0.1.377 (2022-07-13)

### Bug Fixes

- **fusionsolar**: Add debug output
  ([`ba2c97f`](https://github.com/fhempy/fhempy/commit/ba2c97f52e0fded216cfb2231175a54bce1fe7c5))

### Chores

- Update controls
  ([`36ee2ee`](https://github.com/fhempy/fhempy/commit/36ee2ee64c96b35d752f65817af7ba49ce9361a9))


## v0.1.376 (2022-07-12)

### Bug Fixes

- **fhempy**: Fix ssdp
  ([`95febe2`](https://github.com/fhempy/fhempy/commit/95febe2d1b9f79d0ab8d267d77d8e683d7adec19))

### Chores

- Update controls
  ([`3d0e182`](https://github.com/fhempy/fhempy/commit/3d0e18280f1c5632a682c282e92766d03df387ee))


## v0.1.375 (2022-07-12)

### Bug Fixes

- **fhempy**: Update cryptography, aiohttp, async-upnp-client
  ([`7d7f654`](https://github.com/fhempy/fhempy/commit/7d7f65438335d5efaee9a2cc1cd113486562bd5d))

### Chores

- Update controls
  ([`62bcdb2`](https://github.com/fhempy/fhempy/commit/62bcdb257969e45990b941ea0950d7a17b42e63d))


## v0.1.374 (2022-07-12)

### Bug Fixes

- **dlna_dmr**: Fix manifest
  ([`98a7f03`](https://github.com/fhempy/fhempy/commit/98a7f036650546c7fc55303e568398569918d960))

### Chores

- Update controls
  ([`8beda46`](https://github.com/fhempy/fhempy/commit/8beda4660122d67fd4089443ec9f7bd84d12127c))


## v0.1.373 (2022-07-12)

### Bug Fixes

- **wienerlinien**: Fix requirements
  ([`85679d4`](https://github.com/fhempy/fhempy/commit/85679d48a1c970f0824b7f0aaeaced057fc7a136))

### Chores

- Update controls
  ([`258571b`](https://github.com/fhempy/fhempy/commit/258571b7c33977107954db1a50ef10e8d3f60287))


## v0.1.372 (2022-07-12)

### Bug Fixes

- **fhempy**: Fix aiohttp bug
  ([`2cd64fd`](https://github.com/fhempy/fhempy/commit/2cd64fd25819b47a749d6accd6741d1e22584625))

### Chores

- Update controls
  ([`29107a4`](https://github.com/fhempy/fhempy/commit/29107a442be79f2474e3b821c6f328b0cf310b10))


## v0.1.371 (2022-07-12)

### Bug Fixes

- **fhempy**: Disable events because of utf-8 bug
  ([`3a3bf25`](https://github.com/fhempy/fhempy/commit/3a3bf25f2535ff2fadc490c7a917c40b9e11b94e))

### Chores

- Update controls
  ([`9c95ef9`](https://github.com/fhempy/fhempy/commit/9c95ef9bc03c8fdc4e2d6b2c28966c9c54f2fee6))


## v0.1.370 (2022-07-10)

### Chores

- Update controls
  ([`923f781`](https://github.com/fhempy/fhempy/commit/923f781995a8a9048787c0fa694c20d442c4fcff))

### Features

- **fusionsolar**: Breaking CHANGE, see README. Username/password support instead of sessionid.
  ([`0a3d94d`](https://github.com/fhempy/fhempy/commit/0a3d94de9fa15d854e28076684fbf033039f0c0c))


## v0.1.369 (2022-07-09)

### Bug Fixes

- **fhempy**: Fix event handling
  ([`8649e04`](https://github.com/fhempy/fhempy/commit/8649e04cda8fde246a0ee4c187af1f74a4b3c79a))

- **fusionsolar**: Support new web api
  ([`31423a8`](https://github.com/fhempy/fhempy/commit/31423a8f1309eb4c46607c70e4608dbca13dab82))

- **googlecast**: Update pychromecast lib
  ([`d30c288`](https://github.com/fhempy/fhempy/commit/d30c288f020978b525ea2ef8d27f3d02b6afaa0c))

- **tuya**: Prevent error when attr dp_xx is not available localy
  ([`30ebebf`](https://github.com/fhempy/fhempy/commit/30ebebff1af3aaede5a8ff01ad96642229c970a0))

### Chores

- Update controls
  ([`e83bab5`](https://github.com/fhempy/fhempy/commit/e83bab50743074a05f2c57d19e2c376f594f7c83))

### Features

- **volvo_software_update**: New module which notifies about volvo software updates
  ([`aada589`](https://github.com/fhempy/fhempy/commit/aada58901979f5c79d2ddbc8640890cd21e6e957))


## v0.1.368 (2022-06-20)

### Bug Fixes

- **fhempy**: Fix ble disconnect failure
  ([`1142d94`](https://github.com/fhempy/fhempy/commit/1142d94de4a365449b531acdc71995045149fe35))

- **fhempy**: Fix naming
  ([`6b7ddc2`](https://github.com/fhempy/fhempy/commit/6b7ddc2dc71483d0b08bc3d9a38c354746ce4818))

- **fusionsolar**: Fix string energy
  ([`f015ac7`](https://github.com/fhempy/fhempy/commit/f015ac71d4b7c0908ecbaa74bc6f7ab29f020788))

### Chores

- Update controls
  ([`3c714dc`](https://github.com/fhempy/fhempy/commit/3c714dcb3325b9614c2d6804365c4b763aa1999b))


## v0.1.367 (2022-06-17)

### Bug Fixes

- **fusionsolar**: Fix string_output_power
  ([`4f83d8a`](https://github.com/fhempy/fhempy/commit/4f83d8ab6b3a04820ce7dc75b10a11d23f0a743c))

### Chores

- Update controls
  ([`5eaba85`](https://github.com/fhempy/fhempy/commit/5eaba855e445f587bb13b13289ff0a30f4ba1857))


## v0.1.366 (2022-06-16)

### Bug Fixes

- **fusionsolar**: Fix NoneType exception
  ([`9cc40c3`](https://github.com/fhempy/fhempy/commit/9cc40c3bc188b8a4deb1ed7c2193828b7f0a7264))

### Chores

- Update controls
  ([`e4ff7aa`](https://github.com/fhempy/fhempy/commit/e4ff7aa4b8eabb66bc1f54a7834e9e5bacbaebda))


## v0.1.365 (2022-06-15)

### Bug Fixes

- **tuya**: Do not raise exception if decoding fails
  ([`1371ca4`](https://github.com/fhempy/fhempy/commit/1371ca4376c5365b940d94074363796286cf418e))

### Chores

- Update controls
  ([`44bf295`](https://github.com/fhempy/fhempy/commit/44bf295a8a2ff10070c4f905eaed59c41037a581))


## v0.1.364 (2022-06-14)

### Bug Fixes

- **tuya**: Add logging if payload decoding fails
  ([`79953c5`](https://github.com/fhempy/fhempy/commit/79953c5de67e1f1e950336cbec6d32903af8da67))

### Chores

- Update controls
  ([`248d9d2`](https://github.com/fhempy/fhempy/commit/248d9d2e99473386c5bb6d9d2e0a9c860f73231e))


## v0.1.363 (2022-06-13)

### Bug Fixes

- **fusionsolar**: Prevent token to expire
  ([`9629bfb`](https://github.com/fhempy/fhempy/commit/9629bfb16133595248c6b5d3df856483c546e67b))

- **gfprobt**: Do not send parallel commands
  ([`3f1e504`](https://github.com/fhempy/fhempy/commit/3f1e504cf6992337abb0886d4f19316dd42c2915))

- **gfprobt**: Fix adjust
  ([`54427b2`](https://github.com/fhempy/fhempy/commit/54427b2e3f9aade0ba6400b58cbeea48574d1c95))

### Chores

- Update controls
  ([`fa43ebe`](https://github.com/fhempy/fhempy/commit/fa43ebe9ec7eb646800f11e993cadb61d59025c1))


## v0.1.362 (2022-06-10)

### Chores

- Update controls
  ([`3a1e82e`](https://github.com/fhempy/fhempy/commit/3a1e82ee5bb24ac5c2c8e1bc77d266072f0c0fb4))

### Features

- **fusionsolar**: Add string_output_power
  ([`84bdaa1`](https://github.com/fhempy/fhempy/commit/84bdaa155871bd199c21a46e87af5e690c803484))


## v0.1.361 (2022-06-10)

### Bug Fixes

- **fhempy**: Fix local restart
  ([`3842026`](https://github.com/fhempy/fhempy/commit/38420261e3176d6cc43b32f73c219833706efe50))

- **fusionsolar**: Add idle call
  ([`987a88a`](https://github.com/fhempy/fhempy/commit/987a88ab4f91e68f96e745db2acebb0a59f3bc28))

### Chores

- Update controls
  ([`d9319de`](https://github.com/fhempy/fhempy/commit/d9319deface61203b28ed17fca0734b88f313f51))


## v0.1.360 (2022-06-04)

### Bug Fixes

- **googlecast**: Update lib and fix protobuf
  ([`bf73a18`](https://github.com/fhempy/fhempy/commit/bf73a182363dc39bcafc9570ec0b3579f484c814))

### Chores

- Update controls
  ([`a978428`](https://github.com/fhempy/fhempy/commit/a97842866edda2d01650636f0561b1c0d35aa56a))


## v0.1.359 (2022-06-04)

### Bug Fixes

- **fusionsolar**: Fix division by zero exception
  ([`765982c`](https://github.com/fhempy/fhempy/commit/765982c9401c08aa1d400b23128888a3c4acaa19))

- **tuya**: Improve state text when device couldn't be discovered
  ([`2db8add`](https://github.com/fhempy/fhempy/commit/2db8addc3bcd993f6294b8211c72a2b065a0eab4))

### Chores

- Update controls
  ([`9b1ab09`](https://github.com/fhempy/fhempy/commit/9b1ab09ea3a698548585bf53e48336d971eace5d))


## v0.1.358 (2022-05-23)

### Bug Fixes

- **fhempy**: Downgrade libraries to working versions
  ([`8ba4662`](https://github.com/fhempy/fhempy/commit/8ba46629905c6233ef3a79ae204e0d7dc468fd8d))

### Chores

- Update controls
  ([`490f989`](https://github.com/fhempy/fhempy/commit/490f98974095cbc8cc0ac5dcfaf5e7f74f44411f))


## v0.1.357 (2022-05-19)

### Bug Fixes

- **fhempy**: Revert aiohttp version
  ([`905dfe0`](https://github.com/fhempy/fhempy/commit/905dfe01af0aeb3a7894aa945b855370e2486ec5))

### Chores

- Update controls
  ([`844fa03`](https://github.com/fhempy/fhempy/commit/844fa0321f51d4af9045c8d598bfe1d4b98a56b2))


## v0.1.356 (2022-05-19)

### Bug Fixes

- **fhempy**: Cleanup imports
  ([`d66b01a`](https://github.com/fhempy/fhempy/commit/d66b01a6e0ff1d70feb6b34b12910066dd558a0b))

- **fhempy**: Update libraries
  ([`20f40b8`](https://github.com/fhempy/fhempy/commit/20f40b86fbccc160f254cf2d184e301eccb8e8fe))

### Chores

- Update controls
  ([`ac89578`](https://github.com/fhempy/fhempy/commit/ac8957856330d068b8cae382a15261c2591c4bbc))


## v0.1.355 (2022-05-19)

### Bug Fixes

- **fhempy**: Update zeroconf to 0.38.6
  ([`4f60df8`](https://github.com/fhempy/fhempy/commit/4f60df8a79f804b97016588aefb80d3575e7bb5f))

### Chores

- Update controls
  ([`cdae011`](https://github.com/fhempy/fhempy/commit/cdae01102ea1eab807bac964132dda1b6df2283c))


## v0.1.354 (2022-05-19)

### Bug Fixes

- **fhempy**: Deactivate events
  ([`40bd9a4`](https://github.com/fhempy/fhempy/commit/40bd9a44c42ea9081f9db00c8b0e785dd4fcb21d))

### Chores

- Update controls
  ([`bd67ce2`](https://github.com/fhempy/fhempy/commit/bd67ce2a99d45a469b370441325328fa9ed90dfc))


## v0.1.353 (2022-05-19)

### Bug Fixes

- **fhempy**: Revert event handling
  ([`f020c34`](https://github.com/fhempy/fhempy/commit/f020c34d1c790ce831bf50db86f1ddd950735d82))

### Chores

- Update controls
  ([`296a0fe`](https://github.com/fhempy/fhempy/commit/296a0fe5c2d790aa520ffe648d2d3e992b9c136c))


## v0.1.352 (2022-05-19)

### Bug Fixes

- **fhempy**: Fix event handling (?)
  ([`ba5e9c4`](https://github.com/fhempy/fhempy/commit/ba5e9c42f3a28ded54d31ec6d2fb2e8a8291ecfe))

### Chores

- Update controls
  ([`44d36a6`](https://github.com/fhempy/fhempy/commit/44d36a67efa8fb8ef7d8eb84bdf9dfe3f933a1c8))


## v0.1.351 (2022-05-18)

### Chores

- Update controls
  ([`dc66fdd`](https://github.com/fhempy/fhempy/commit/dc66fdde6ce9740c69b0b5974af0389c09b55056))

### Features

- **fusionsolar**: Support battery values
  ([`f0a67cd`](https://github.com/fhempy/fhempy/commit/f0a67cd9362c324cf73cf413f2fa4a9a3b15fe5f))


## v0.1.350 (2022-05-18)

### Bug Fixes

- **fusionsolar**: Fix if battery in use
  ([`ad7c12f`](https://github.com/fhempy/fhempy/commit/ad7c12f6970b92a49bab10999498ef11daed3847))

### Chores

- Update controls
  ([`d0b02a8`](https://github.com/fhempy/fhempy/commit/d0b02a8ccaa65e2c17c3bebb5ebd6013059d6577))


## v0.1.349 (2022-05-18)

### Bug Fixes

- **fusionsolar**: Fix region usage in define
  ([`d388160`](https://github.com/fhempy/fhempy/commit/d38816072464b140ef774f0d003820935c640b8a))

### Chores

- Update controls
  ([`f38eef8`](https://github.com/fhempy/fhempy/commit/f38eef8822119638f391c654668f85c3f5ca1614))


## v0.1.348 (2022-05-16)

### Bug Fixes

- **fhempy**: Deactivate events as long as encoding issues are not fixed
  ([`55353e9`](https://github.com/fhempy/fhempy/commit/55353e922902a655d4efda95b9897e467bf56689))

- **fhempy**: Rename PyBinding class to fhempy
  ([`259507d`](https://github.com/fhempy/fhempy/commit/259507d668c101778f58a03bd22ba95632e05652))

### Chores

- Update controls
  ([`1dceb73`](https://github.com/fhempy/fhempy/commit/1dceb736129efa97c46569953cc58dbd59b18271))


## v0.1.347 (2022-05-16)

### Bug Fixes

- **fhempy**: Fix for non string events
  ([`fdccd1f`](https://github.com/fhempy/fhempy/commit/fdccd1f41a17ae0e41904bcff7dc7a7ec7466923))

### Chores

- Update controls
  ([`f5d5d42`](https://github.com/fhempy/fhempy/commit/f5d5d4219ad7f9545b36666e624ac37615e99905))


## v0.1.346 (2022-05-15)

### Bug Fixes

- **miio**: Set offline when no reply on status call
  ([`57c4908`](https://github.com/fhempy/fhempy/commit/57c49089e49119770b1ef673fcbbe30f2a98fef1))

### Chores

- Update controls
  ([`9180558`](https://github.com/fhempy/fhempy/commit/9180558b21491a7277baa294842eccb2e78d5f17))


## v0.1.345 (2022-05-15)

### Bug Fixes

- **fhempy**: Add SIGINT handling
  ([`c2ab429`](https://github.com/fhempy/fhempy/commit/c2ab42979241cce82cd250a72046023855330427))

### Chores

- Update controls
  ([`61ee2c4`](https://github.com/fhempy/fhempy/commit/61ee2c408863615cb7536754828fd9527455f9a6))

### Features

- **fhempy**: Support FHEM events (register_event_listener)
  ([`1c4e38b`](https://github.com/fhempy/fhempy/commit/1c4e38bc830b5a6bd9b3c2e05bd55ae7d041ff93))


## v0.1.344 (2022-05-14)

### Bug Fixes

- **esphome**: Fix long running set functions
  ([`48fbf28`](https://github.com/fhempy/fhempy/commit/48fbf28f7b0b7bc38137d4ad13ea6604064d9587))

- **gfprobt**: Fix loop on asyncio cancel
  ([`7fc9075`](https://github.com/fhempy/fhempy/commit/7fc9075e9cea31cd4609ad7b77446579e8c1b0dd))

### Chores

- Update controls
  ([`e112258`](https://github.com/fhempy/fhempy/commit/e112258216984638051ff02d4c511ff5557f0f8e))


## v0.1.343 (2022-05-14)

### Bug Fixes

- **zigbee2mqtt**: Fix function arguments
  ([`790b00a`](https://github.com/fhempy/fhempy/commit/790b00a646581eab4c1739814c2e6ee78fadca6b))

### Chores

- Update controls
  ([`3e942bc`](https://github.com/fhempy/fhempy/commit/3e942bc3d983356e0ef9348881b0db90736a43d0))


## v0.1.342 (2022-05-14)

### Bug Fixes

- **fhempy**: Use os._exit again
  ([`9c64c08`](https://github.com/fhempy/fhempy/commit/9c64c081f52edfe957cbcabec115021313a98c22))

- **zigbee2mqtt**: Some restart fixes, z2m takes about 15s to shutdown correctly
  ([`20d6761`](https://github.com/fhempy/fhempy/commit/20d676147c21a241f1beb9e28a853978d607b28b))

### Chores

- Update controls
  ([`b610481`](https://github.com/fhempy/fhempy/commit/b610481c3af82873100c817e00caf6733291e744))


## v0.1.341 (2022-05-14)

### Bug Fixes

- **esphome**: Fix possible zombie process
  ([`8140d62`](https://github.com/fhempy/fhempy/commit/8140d62cbb122e53f69770e9deffa64a1ec4cbd4))

- **zigbee2mqtt**: Fix possible zombie process
  ([`bc8102b`](https://github.com/fhempy/fhempy/commit/bc8102b2768685494080a1329c83c54baca0b1ce))

### Chores

- Update controls
  ([`647c4e5`](https://github.com/fhempy/fhempy/commit/647c4e58afe7fd2a1d7cd22bfd3d94f3b7169799))


## v0.1.340 (2022-05-14)

### Bug Fixes

- **fhempy**: Use os._exit if undefine fails to ensure exit
  ([`c634917`](https://github.com/fhempy/fhempy/commit/c63491715c28d1ba0020e20bf961fc34b507e226))

- **zigbee2mqtt**: Wait longer for z2m to stop
  ([`7bab4d9`](https://github.com/fhempy/fhempy/commit/7bab4d97c208e18d637bb22b90c19e7ef1e2ea0f))

### Chores

- Update controls
  ([`497cb2c`](https://github.com/fhempy/fhempy/commit/497cb2cbc0a0d7905bf58db653345966fb5ae0f1))


## v0.1.339 (2022-05-14)

### Bug Fixes

- **gfprobt**: Disconnect on Undefine
  ([`8ab7a81`](https://github.com/fhempy/fhempy/commit/8ab7a81f3ff80ed55a0d699171e92666b4abeac9))

### Chores

- Update controls
  ([`b6c9776`](https://github.com/fhempy/fhempy/commit/b6c97762c47d1249e042d8083e3ad446676cd8f6))


## v0.1.338 (2022-05-13)

### Bug Fixes

- **eq3bt**: Fix Undefine when not yet connected
  ([`ebdbe92`](https://github.com/fhempy/fhempy/commit/ebdbe92dcbbb1f3d5e57a6c311e8ef6a25b31900))

- **fhempy**: Fix Undefine calls when stopped
  ([`2f62033`](https://github.com/fhempy/fhempy/commit/2f620330e70c28d77137db840fd0570b0c56adf5))

### Chores

- Update controls
  ([`014f312`](https://github.com/fhempy/fhempy/commit/014f312c4c119403a91edaaef78558403565f95f))


## v0.1.337 (2022-05-13)

### Bug Fixes

- **eq3bt**: Disconnect on Undefine
  ([`bbd52d0`](https://github.com/fhempy/fhempy/commit/bbd52d0a3b91f0e0fe2088231e9a361fd152db86))

### Chores

- Update controls
  ([`29600bb`](https://github.com/fhempy/fhempy/commit/29600bbff1a1748468689679364a5cbb178162f9))


## v0.1.336 (2022-05-13)

### Bug Fixes

- **esphome**: Better stop process handling
  ([`8efa358`](https://github.com/fhempy/fhempy/commit/8efa3588f8565d1070054f439c4cfc17f0f14dfd))

- **zigbee2mqtt**: Better stop process handling
  ([`46ac614`](https://github.com/fhempy/fhempy/commit/46ac6143c1c85cde01365eaa62ee1d34d5088ef3))

- **zigbee2mqtt**: Code style improvement
  ([`39f6bca`](https://github.com/fhempy/fhempy/commit/39f6bcace4074195741973593e369c05737befbd))

### Chores

- Update controls
  ([`52a73b9`](https://github.com/fhempy/fhempy/commit/52a73b9ca53208eb203a230c51c0b3e218cdaa16))


## v0.1.335 (2022-05-10)

### Bug Fixes

- **spotify**: Update spotipy to 2.19.0
  ([`77d8ee2`](https://github.com/fhempy/fhempy/commit/77d8ee2589e14b32132a7458bad745c78118a829))

### Chores

- Update controls
  ([`5367e21`](https://github.com/fhempy/fhempy/commit/5367e21a980ab055506bf6654542d8b205d17c19))

### Features

- **fhempy**: Support peer restart from FHEM
  ([`ce7803a`](https://github.com/fhempy/fhempy/commit/ce7803a9672f460e6599cec899b0d1787f69dfea))


## v0.1.334 (2022-05-10)

### Bug Fixes

- **fhempy**: Add update info log
  ([`920d4c9`](https://github.com/fhempy/fhempy/commit/920d4c9fddd911a0fa0dc872d7bcd5b9ea61bb07))

- **fhempy**: Close websockets on restart
  ([`729a65e`](https://github.com/fhempy/fhempy/commit/729a65e83f8d322ecaf05b2dbef1818fdfc96935))

- **fhempy**: Fix stash for release script
  ([`ef9fada`](https://github.com/fhempy/fhempy/commit/ef9fadad91908550ac7bac17d381266b67fa887e))

- **fhempy**: Update websockets to 10.3
  ([`b0313d0`](https://github.com/fhempy/fhempy/commit/b0313d03148f35e45858e8ffd7ee0a0c772dc4bc))

- **zigbee2mqtt**: Stop task on restart
  ([`6fea8af`](https://github.com/fhempy/fhempy/commit/6fea8af00f58e2f83117ca1c8051ad06d155c4ad))

### Chores

- Update controls
  ([`d1c2a49`](https://github.com/fhempy/fhempy/commit/d1c2a494555d53e5f434e71f03ca4f578b98c45a))


## v0.1.333 (2022-05-10)

### Bug Fixes

- **zigbee2mqtt**: Fix stop zigbee2mqtt process
  ([`ab44052`](https://github.com/fhempy/fhempy/commit/ab44052bf25e64fa8d84685c152d43aeb877080a))

### Chores

- Update controls
  ([`9353317`](https://github.com/fhempy/fhempy/commit/9353317fd7a7b3eb26ba398ce77d779fc0d4e751))


## v0.1.332 (2022-05-10)

### Bug Fixes

- **discover_upnp**: Code style improvements
  ([`b0eb47b`](https://github.com/fhempy/fhempy/commit/b0eb47bc0a301581cbc03652366a0654d446df04))

- **fhempy**: Asyncio improvements
  ([`7d2e005`](https://github.com/fhempy/fhempy/commit/7d2e00579b1b3d85ce7004381c0055b1f2ef02b4))

- **fhempy**: Code style improvements
  ([`1c6744c`](https://github.com/fhempy/fhempy/commit/1c6744c3220852f45cf0246492c774640fc9aa33))

- **fhempy**: Import cleanup
  ([`427f826`](https://github.com/fhempy/fhempy/commit/427f8267ae8dcd4a12e376c82e59d33cb5e8b154))

- **fhempy**: Log exit code
  ([`7dee7c8`](https://github.com/fhempy/fhempy/commit/7dee7c8914a420aab8c4c6185d395859c572a6d8))

- **tuya**: Fix usage without api key/secret
  ([`4e716d7`](https://github.com/fhempy/fhempy/commit/4e716d7163b216a1a1555612626fd6c5ee456a1f))

- **zigbee2mqtt**: Code style improvements
  ([`560d061`](https://github.com/fhempy/fhempy/commit/560d06133996aa34bd1cc50b1531845e90cf11b5))

### Chores

- Update controls
  ([`1933aa8`](https://github.com/fhempy/fhempy/commit/1933aa84c840ecb6b0d43031e199f9fc74e82a2e))

- Update controls
  ([`342aee0`](https://github.com/fhempy/fhempy/commit/342aee0ccb1cf53f1cccc6445ca7e1bc839b00c7))


## v0.1.331 (2022-05-09)

### Bug Fixes

- **discover_upnp**: Delete unused variable
  ([`e30f2c6`](https://github.com/fhempy/fhempy/commit/e30f2c692496cc4980f9bd0995654a14f72a2c11))

- **esphome**: Kill instead of terminate
  ([`0040297`](https://github.com/fhempy/fhempy/commit/0040297d934398a3027059c090cac0a31cc908e9))

- **zigbee2mqtt**: Kill instead of terminate
  ([`dbeeb36`](https://github.com/fhempy/fhempy/commit/dbeeb36a77981fe360f70149c97f7b619c0b0ba5))

### Chores

- Update controls
  ([`ba91a3a`](https://github.com/fhempy/fhempy/commit/ba91a3a0b70a08d022ab6453d54a17afbf63671b))


## v0.1.330 (2022-05-09)

### Bug Fixes

- **fhempy**: Better restart/shutdown handling
  ([`4e97c58`](https://github.com/fhempy/fhempy/commit/4e97c58b02573cdee0ee9dd11fee30667abb7ad8))

- **miio**: Fix send_command, sort imports
  ([`737eeef`](https://github.com/fhempy/fhempy/commit/737eeefbbf37f9a263ea4527248834ef351cef3c))

- **tuya**: Import only Cloud, deviceScan
  ([`3f92df2`](https://github.com/fhempy/fhempy/commit/3f92df2412409541f55a70e49d26b1fe0dbc5337))

- **tuya**: Remove unused attributes
  ([`1beab02`](https://github.com/fhempy/fhempy/commit/1beab02553dcee4c265cc49131e1afe93fe0c0b0))

- **tuya**: Sort imports
  ([`1a3acfd`](https://github.com/fhempy/fhempy/commit/1a3acfd020c853e08ad3f8a93915a7682c5b9844))

### Chores

- Update controls
  ([`fc3a649`](https://github.com/fhempy/fhempy/commit/fc3a6498575f44bd55c30bda6cb52a192e0426e3))


## v0.1.329 (2022-05-08)

### Bug Fixes

- **miio**: Fix tuple usage
  ([`d97751a`](https://github.com/fhempy/fhempy/commit/d97751ad8c7c0ca31fc2bce6f7991a14f4f3c6a3))

- **tuya**: Fix tests
  ([`dd9ce3c`](https://github.com/fhempy/fhempy/commit/dd9ce3cda1f98ed73c743051f2ea1abe72d62721))

### Chores

- Update controls
  ([`302ff77`](https://github.com/fhempy/fhempy/commit/302ff777d83f07c98c161e426961cd0aeb7a85d8))


## v0.1.328 (2022-05-08)

### Bug Fixes

- **fhempy**: Fix shutdown again
  ([`6e0e1f1`](https://github.com/fhempy/fhempy/commit/6e0e1f1a4cf13a30803087f2f337dfc3e46728a1))

### Chores

- Update controls
  ([`c3287a0`](https://github.com/fhempy/fhempy/commit/c3287a0eb4c88759e1e748555fe6754467990333))

### Features

- **fhempy**: Log version on startup
  ([`63ecc62`](https://github.com/fhempy/fhempy/commit/63ecc627966b3aaa8647f6eb06e2b6bf1dd51fda))


## v0.1.327 (2022-05-08)

### Bug Fixes

- **fhempy**: Fix shutdown handler
  ([`d246ca8`](https://github.com/fhempy/fhempy/commit/d246ca8cdb7aa44c1a7e7c2b0f17e217b24836dc))

### Chores

- Update controls
  ([`f672002`](https://github.com/fhempy/fhempy/commit/f6720022a62e45f7f14fb9c92ba2b4d8a149aafe))


## v0.1.326 (2022-05-08)

### Bug Fixes

- **esphome**: Call stop_process on Undefine
  ([`8402760`](https://github.com/fhempy/fhempy/commit/84027609c91ff675634165f8c0a25511b32541b1))

- **esphome**: Set proc None when terminated
  ([`81f10b0`](https://github.com/fhempy/fhempy/commit/81f10b0f8c68a0b3ad424201574aa9d2b50c0920))

- **fhempy**: Handle SIGTERM for graceful shutdown
  ([`35dff0a`](https://github.com/fhempy/fhempy/commit/35dff0aac289f97fceb15ceff3f7b51469b2e778))

- **zigbee2mqtt**: Call stop_process on Undefine
  ([`e3626e5`](https://github.com/fhempy/fhempy/commit/e3626e518b171b0610dd0d95f5356a9ac72e7a89))

- **zigbee2mqtt**: Fix blocking calls
  ([`a980bf3`](https://github.com/fhempy/fhempy/commit/a980bf3000341e43ffd83dec9c8b1b4784f971dc))

### Chores

- Update controls
  ([`372e844`](https://github.com/fhempy/fhempy/commit/372e844e13736379a12f82dd1fd0f8259bf46978))


## v0.1.325 (2022-05-08)

### Bug Fixes

- **tuya**: Always use cloud specs when APIKEY and APISECRET is provided
  ([`d9d3812`](https://github.com/fhempy/fhempy/commit/d9d381292fe731fccf4b04a11dcc06dfe0514d7c))

### Chores

- Update controls
  ([`8f73869`](https://github.com/fhempy/fhempy/commit/8f73869796888d17a65dfb08a11d34a511d70aff))


## v0.1.324 (2022-05-08)

### Bug Fixes

- **fusionsolar**: Update takes a bit longer, extend to full 5min + 30s
  ([`79cb26a`](https://github.com/fhempy/fhempy/commit/79cb26a08008f6b30c00598244e0117a39f2b4b6))

### Chores

- Update controls
  ([`704e41f`](https://github.com/fhempy/fhempy/commit/704e41f8bf6c62f561380c4cc12449408776993c))


## v0.1.323 (2022-05-08)

### Bug Fixes

- **tuya**: Fix local found counter
  ([`a8b708c`](https://github.com/fhempy/fhempy/commit/a8b708cfa13d6266966ce27b70cdc98216594dc1))

### Chores

- Update controls
  ([`5b6f315`](https://github.com/fhempy/fhempy/commit/5b6f31520e80e71c165ceb4fba8a80bb6a3ba7ec))


## v0.1.322 (2022-05-08)

### Bug Fixes

- **esphome**: Code style improvements
  ([`f8a091b`](https://github.com/fhempy/fhempy/commit/f8a091be9dd6505c4416217309e1307246b81abc))

- **fusionnsolar**: Code style improvements
  ([`dd01e29`](https://github.com/fhempy/fhempy/commit/dd01e29c433ab4593536060a9d8f829cb452c6d2))

- **fusionsolar**: Fix update interval
  ([`a33dc00`](https://github.com/fhempy/fhempy/commit/a33dc005daf44920d921c4283a824feb859b6eff))

- **tuya**: Code style improvements
  ([`b014060`](https://github.com/fhempy/fhempy/commit/b01406066a0b460ee0d63a011755f96423263a06))

- **tuya_cloud**: Code style improvements
  ([`46c90ca`](https://github.com/fhempy/fhempy/commit/46c90ca41b62a2bd24d46dff20a333bb3ced5f00))

- **wienerlinien**: Code style improvements
  ([`c5207f4`](https://github.com/fhempy/fhempy/commit/c5207f47970d689a7b4ed5c0ee9fa8356072f6fe))

### Chores

- Update controls
  ([`f610b05`](https://github.com/fhempy/fhempy/commit/f610b05ac2cfcda63f03b3354d1012cdffa4ad07))


## v0.1.321 (2022-05-08)

### Bug Fixes

- **fusionsolar**: Delete unused file
  ([`45f7bb8`](https://github.com/fhempy/fhempy/commit/45f7bb8ad4d4ca2882d7c9b4cce0c13dd9a04ad9))

- **fusionsolar**: Fix div/0
  ([`57bbc51`](https://github.com/fhempy/fhempy/commit/57bbc51ad9e51637d70bbba57902aa73ddd3937f))

### Chores

- Update controls
  ([`0d8404e`](https://github.com/fhempy/fhempy/commit/0d8404e1edaf41e84736b0f500fd8e1a0eb914fd))

### Features

- **fusionsolar**: Update on fusionsolar update (every full 5min)
  ([`b338277`](https://github.com/fhempy/fhempy/commit/b338277d1e42e93b681dd8e1344d72d13d97c032))

- **tuya**: Support wifi devices which are not online all the time (e.g. water leak sensor, smoke
  detector, ...)
  ([`035429c`](https://github.com/fhempy/fhempy/commit/035429ceab4508ba94c4e9e2253f2ba736e62bea))


## v0.1.320 (2022-05-07)

### Bug Fixes

- **miio**: Fix tuple type
  ([`4282a99`](https://github.com/fhempy/fhempy/commit/4282a995425efc1940d4a27ca11cd1fd08dac692))

### Chores

- Update controls
  ([`41fa99b`](https://github.com/fhempy/fhempy/commit/41fa99b32c1f92ed0ecc26e0bb48da88ee4e3ee1))


## v0.1.319 (2022-05-07)

### Bug Fixes

- **fhempy**: Wait max 10s for restart
  ([`896d80b`](https://github.com/fhempy/fhempy/commit/896d80bd065e4f3670e0b66df706bc64ccd2fb32))

### Chores

- Update controls
  ([`74b2fe1`](https://github.com/fhempy/fhempy/commit/74b2fe17169b9d4eef51eed30fe2341a354b8e4c))


## v0.1.318 (2022-05-07)

### Chores

- Update controls
  ([`f338b0d`](https://github.com/fhempy/fhempy/commit/f338b0d24a20ca75db181d92c60416b5a68259b2))

### Features

- **fusionsolar**: Add daily_self_use_solar_ratio reading
  ([`4abd020`](https://github.com/fhempy/fhempy/commit/4abd02016a99e319afcb04ab0c99fe3668a255ff))


## v0.1.317 (2022-05-07)

### Bug Fixes

- **fusionsolar**: Fix daily_self_use_ratio
  ([`84ea1e0`](https://github.com/fhempy/fhempy/commit/84ea1e0ab36a2a66a5e6caabe86c9aff92ed71d4))

### Chores

- Update controls
  ([`29d4111`](https://github.com/fhempy/fhempy/commit/29d41115f85fdde1f92d5f3b7db8e77ba96f602d))


## v0.1.316 (2022-05-07)

### Bug Fixes

- **fusionsolar**: Small fixes
  ([`cdbd06c`](https://github.com/fhempy/fhempy/commit/cdbd06ced4a2bcfedd43dd70fce916a4cab30ea9))

### Chores

- Update controls
  ([`3316a52`](https://github.com/fhempy/fhempy/commit/3316a52ca5b4a9bd3130a13d62592018928ec76f))


## v0.1.315 (2022-05-07)

### Chores

- Update controls
  ([`b2468af`](https://github.com/fhempy/fhempy/commit/b2468af3fdfac6941c0164b12578d676a2501cf4))

### Features

- **fusionsolar**: Add further readings
  ([`f3432af`](https://github.com/fhempy/fhempy/commit/f3432af9b8bbfa9708747680b91adac1eaf6a0b7))


## v0.1.314 (2022-05-07)

### Bug Fixes

- **fusionsolar**: Fix define
  ([`f421b51`](https://github.com/fhempy/fhempy/commit/f421b51e741e7e042e4dd38906c515ad7fd56191))

### Chores

- Update controls
  ([`d01e584`](https://github.com/fhempy/fhempy/commit/d01e5842f464d148f066ab1d62f6ebb443967023))


## v0.1.313 (2022-05-07)

### Chores

- Update controls
  ([`4175ffa`](https://github.com/fhempy/fhempy/commit/4175ffa2d057522f970d5ac4d74909b8592eeefb))

### Features

- **fusionsolar**: Breaking: no more kiosk mode, all values are taken from REST API. See README for
  details
  ([`221e88c`](https://github.com/fhempy/fhempy/commit/221e88c67bc6697c4a1f45144a321467b4ca7912))


## v0.1.312 (2022-05-07)

### Bug Fixes

- **fusionsolar**: Fix wrong default region
  ([`bea81bf`](https://github.com/fhempy/fhempy/commit/bea81bf0ea2f84871b34ee1af9aadad8321fc9a6))

### Chores

- Update controls
  ([`4288994`](https://github.com/fhempy/fhempy/commit/4288994918810fecd0dda043a461fe55b333cba6))


## v0.1.311 (2022-05-07)

### Bug Fixes

- **fusionsolar**: Fix from/to_grid_power
  ([`fe7bea1`](https://github.com/fhempy/fhempy/commit/fe7bea111b286e6c3cf8287cbe09f51c9c8ae456))

### Chores

- Update controls
  ([`f0054d8`](https://github.com/fhempy/fhempy/commit/f0054d8f5f77bed9370fc34efe0519234a81de25))


## v0.1.310 (2022-05-07)

### Chores

- Update controls
  ([`ae754cc`](https://github.com/fhempy/fhempy/commit/ae754cc0378766fae37cad9fe14a570e8c4ac5ab))

### Features

- **fusionsolar**: Support from/to_grid, electrical_load, grid_power and inverter_output_power
  ([`3c73b83`](https://github.com/fhempy/fhempy/commit/3c73b8312ae71d9fa74e23d7d9299e40ece61951))


## v0.1.309 (2022-05-06)

### Bug Fixes

- **fhempy**: Fix task exception handling
  ([`81225c1`](https://github.com/fhempy/fhempy/commit/81225c12840754ea691b7d9624c1fd3446babd89))

### Chores

- Update controls
  ([`0b68a64`](https://github.com/fhempy/fhempy/commit/0b68a64c14563fa1940623547f070f199fb9ad43))


## v0.1.308 (2022-05-06)

### Bug Fixes

- **fhempy**: Handle exceptions in asyncio tasks
  ([`6708650`](https://github.com/fhempy/fhempy/commit/670865014807e9aceb636b03f81106fca466ba88))

- **tuya**: Remove unused function
  ([`3b8b785`](https://github.com/fhempy/fhempy/commit/3b8b785d459a815bc9890227a572f554857b8a3a))

### Chores

- Update controls
  ([`7ac1605`](https://github.com/fhempy/fhempy/commit/7ac160520d5e15db404180aabdb8a1984ca213f0))


## v0.1.307 (2022-05-05)

### Bug Fixes

- **tuya**: Get info before connection setup
  ([`fd5edcc`](https://github.com/fhempy/fhempy/commit/fd5edcc20ff04ee7cf7c3f6523168cb7372b0453))

### Chores

- Update controls
  ([`562b56d`](https://github.com/fhempy/fhempy/commit/562b56db31bf3fb6d3c4c9c2ae6527f96ad16e00))


## v0.1.306 (2022-05-03)

### Bug Fixes

- **tuya**: Handle exception
  ([`0b3c77b`](https://github.com/fhempy/fhempy/commit/0b3c77b29caf58aa18257e763664237cac9a36f8))

### Chores

- Update controls
  ([`a4674e8`](https://github.com/fhempy/fhempy/commit/a4674e82c0cb1fa8b94bc2017395889e2268b8d5))


## v0.1.305 (2022-05-02)

### Chores

- Update controls
  ([`292edac`](https://github.com/fhempy/fhempy/commit/292edac97d9cf0846377f1ea1623b26bbd8fb261))

### Features

- **tuya**: Try to support water leak sensor
  ([`b3229d6`](https://github.com/fhempy/fhempy/commit/b3229d6790cfcb73be963490d2f641c374bc02d0))


## v0.1.304 (2022-05-01)

### Bug Fixes

- **nespresso_ble**: Remove unused requirement
  ([`889e582`](https://github.com/fhempy/fhempy/commit/889e582813c225f481db4fbfc5110f263e57cbc3))

### Chores

- Update controls
  ([`5a56457`](https://github.com/fhempy/fhempy/commit/5a56457b4f312ed87c9c036c7d021dd1462ad726))


## v0.1.303 (2022-05-01)

### Bug Fixes

- **fhempy**: Remove Python 3.7 test
  ([`d1c2b7b`](https://github.com/fhempy/fhempy/commit/d1c2b7b2438c4429d05b4c329d8c8c3440f48ad8))

### Chores

- Update controls
  ([`7a3007d`](https://github.com/fhempy/fhempy/commit/7a3007d44a8be7f6e8668efbbaf71e63f41b1603))


## v0.1.302 (2022-05-01)

### Bug Fixes

- **rct_power**: Fix commands
  ([`4efb800`](https://github.com/fhempy/fhempy/commit/4efb8002ab923878c761aabf65e95263c7a44d77))

### Chores

- Update controls
  ([`0ce270c`](https://github.com/fhempy/fhempy/commit/0ce270ceefcc15ef775e4707f8f5d9104caf4924))


## v0.1.301 (2022-05-01)

### Bug Fixes

- **discover_mdns**: Fix exception handling
  ([`f2bb640`](https://github.com/fhempy/fhempy/commit/f2bb6409005b3d7bac9ae6d2db05dbd3f9264ef3))

- **eq3bt**: Fix possible infinite loop
  ([`7c21c2a`](https://github.com/fhempy/fhempy/commit/7c21c2a49bb645a7071259799b22c4c85f96dae5))

- **fhempy**: Code cleanup
  ([`9e123cf`](https://github.com/fhempy/fhempy/commit/9e123cfea795629f8e2c52a6e2e88a93bcb62c2b))

- **fhempy**: Code style fixes
  ([`23db77b`](https://github.com/fhempy/fhempy/commit/23db77bee65481d844c3fc6fcc66f8e43f1050c6))

- **fhempy**: Cryptography 3.4.8
  ([`0bf5665`](https://github.com/fhempy/fhempy/commit/0bf56652a74ad231c4c3b9cbb9b281f68971c44d))

- **fhempy**: Fix exception handling
  ([`db7c74b`](https://github.com/fhempy/fhempy/commit/db7c74b9d9810d4ee3a9b9cdb0e2be4fb2318f59))

- **fhempy**: Fix ssdp stop_search
  ([`5d998d6`](https://github.com/fhempy/fhempy/commit/5d998d65c39c7e262551255d88b67361e0ffb56e))

- **fhempy**: Update cryptography
  ([`52afbf7`](https://github.com/fhempy/fhempy/commit/52afbf71510ad985d156d19941336319032c0fab))

- **gfprobt**: Deactivate not working adjust values
  ([`73c5aae`](https://github.com/fhempy/fhempy/commit/73c5aae511e5e28a4c250e0d45c074e6597ee92c))

- **gfprobt**: Fix invalid type
  ([`93f2873`](https://github.com/fhempy/fhempy/commit/93f28736e577d69e489ce680904c0a596b7fe61f))

- **gfprobt**: Prepare adjust
  ([`51cc4bb`](https://github.com/fhempy/fhempy/commit/51cc4bb5fd369d124a2a3c84ffe639b4a0bf5c8c))

- **gree_climate**: Fix commands
  ([`1f2779a`](https://github.com/fhempy/fhempy/commit/1f2779a9e71954ddddfc53a75272398dcb5e91fd))

- **gree_climate**: Fix function call on error
  ([`0bcedbe`](https://github.com/fhempy/fhempy/commit/0bcedbe75c8b0ab4f062edd2c2448b689826a4c9))

- **gree_climate**: Fix missing off cmd
  ([`fdcb422`](https://github.com/fhempy/fhempy/commit/fdcb422e3c8e473596217ef5bd0656de7ec1521f))

- **gree_climate**: Fix set temperature
  ([`fcc825f`](https://github.com/fhempy/fhempy/commit/fcc825fe177f0bb35163d65473cb76ae32a7525d))

- **gree_climate**: Fix usage
  ([`0023119`](https://github.com/fhempy/fhempy/commit/00231192441a53284e3789a9b540242c8753ee08))

- **gree_climate**: Remove set cmds for scan device
  ([`45c2d2f`](https://github.com/fhempy/fhempy/commit/45c2d2fe1afa5953cb6d6eeb36c55e7cedb06240))

- **helloworld**: Remove unused import
  ([`ebe9245`](https://github.com/fhempy/fhempy/commit/ebe92454e0658c8f420fa6f65c767a22486dc4cf))

- **miio**: Support Tuple data type
  ([`3b8dce5`](https://github.com/fhempy/fhempy/commit/3b8dce51f65a6c0b9f47ea9397ec7ee81162ef65))

- **nefit**: Fix Undefine
  ([`e9b0168`](https://github.com/fhempy/fhempy/commit/e9b016828cc5fb00254d538cc5a11fd2d9925c6d))

- **rct_power**: Fix commands
  ([`5753a35`](https://github.com/fhempy/fhempy/commit/5753a35bc2f67bcb58af0ae6cf8fd0dde570bc97))

- **rct_power**: Fix commands ([#75](https://github.com/fhempy/fhempy/pull/75),
  [`4dbe2f7`](https://github.com/fhempy/fhempy/commit/4dbe2f765040f42e5056c0984b5b8175fb028c8c))

Read/Write: Einen Fehler im Kommentar beseitigt, einen Slider angeglichen, Formatierungsänderung in
  den Kommentaren

- **rct_power**: Fix commands ([#76](https://github.com/fhempy/fhempy/pull/76),
  [`bf88baa`](https://github.com/fhempy/fhempy/commit/bf88baaed7f13a63956baa3e68e7bf91e3e83c36))

- **rct_power**: Remove slider ([#74](https://github.com/fhempy/fhempy/pull/74),
  [`e45006d`](https://github.com/fhempy/fhempy/commit/e45006d7d04fce3768a90830a83492e316ab758e))

- **ring**: Change update order
  ([`75016f6`](https://github.com/fhempy/fhempy/commit/75016f6e263420eb9fb24e58bf529d638d2a05a7))

- **ring**: Fix test
  ([`b637c09`](https://github.com/fhempy/fhempy/commit/b637c092e03f5b233f0b64c34d242c7d1729aa11))

- **ring**: Fix Undefine
  ([`56ceda2`](https://github.com/fhempy/fhempy/commit/56ceda2b38528f89bf63c649d7279e425ffa4b63))

- **ring**: Fix Undefine endless loop
  ([`e1ce34f`](https://github.com/fhempy/fhempy/commit/e1ce34fb1d20757ac4d4a4e4fe566ae0a20388fa))

- **ring**: Show errors in state
  ([`32d2a4b`](https://github.com/fhempy/fhempy/commit/32d2a4b39de821895407157352e6cfb2a79c8ddf))

- **tuya**: Fix create device
  ([`6b4c524`](https://github.com/fhempy/fhempy/commit/6b4c5247dd052ba42f766268b92253c9d1d49561))

- **tuya**: Fix for existing mappings
  ([`1d5d301`](https://github.com/fhempy/fhempy/commit/1d5d301dd69d0cef8b7b84655d01dc325c161375))

- **tuya**: Fix local scan
  ([`6a850d4`](https://github.com/fhempy/fhempy/commit/6a850d4ced3cb3bf573943e9269383ce930ce728))

- **tuya**: Fix local scan
  ([`eed15a2`](https://github.com/fhempy/fhempy/commit/eed15a2198e9c856a95dd052323438e031b401bc))

- **tuya**: Fix tests
  ([`fd7c390`](https://github.com/fhempy/fhempy/commit/fd7c390aece3c7477203c1e78d516a4680a7dbf4))

- **tuya**: Optimize define runtime
  ([`2109d7a`](https://github.com/fhempy/fhempy/commit/2109d7a7273c1ba857b32ee50d5cf9b70b18a3fc))

- **tuya**: Update tuya cloud instructions
  ([`84dd50c`](https://github.com/fhempy/fhempy/commit/84dd50cce90cb990ac727459a5e263c74d26bd8b))

- **tuya_cloud**: Update README link
  ([`507ffb0`](https://github.com/fhempy/fhempy/commit/507ffb038daa1e033f2b80293a39dab40a5c8ddc))

### Chores

- Update controls
  ([`15ec021`](https://github.com/fhempy/fhempy/commit/15ec021b1eb440f3b95072b5bee0c26a35c458e6))

- Update controls
  ([`9503134`](https://github.com/fhempy/fhempy/commit/950313473468826e1713464e78898730f04b36cf))

- Update controls
  ([`e9c1d92`](https://github.com/fhempy/fhempy/commit/e9c1d92c581aabaa0e412693523a46e824c797c9))

- Update controls
  ([`d95c829`](https://github.com/fhempy/fhempy/commit/d95c8292cc1321e92498979529ba7e3a417d3159))

- Update controls
  ([`e6f2cff`](https://github.com/fhempy/fhempy/commit/e6f2cff51fa012435166c656f5c802f92e129ba0))

- Update controls
  ([`cdc18c6`](https://github.com/fhempy/fhempy/commit/cdc18c6366e18e6fce3aaed69c23fdb5a522fe84))

- Update controls
  ([`3d79674`](https://github.com/fhempy/fhempy/commit/3d796746c01b7759242a3a06ba57a3a34b8c02c6))

- Update controls
  ([`6bee800`](https://github.com/fhempy/fhempy/commit/6bee8005a70e56feea11da3db104ce189734cf6a))

- Update controls
  ([`c1d7b7a`](https://github.com/fhempy/fhempy/commit/c1d7b7a37fa8cb771a0edbc799f2809c3bfe3bc9))

- Update controls
  ([`7b6c1ee`](https://github.com/fhempy/fhempy/commit/7b6c1ee1aecdeee2c29cb1ad1b520094bc9849e9))

- Update controls
  ([`f37f26c`](https://github.com/fhempy/fhempy/commit/f37f26cc885a686e7f3f187968443d7f0ea16cfa))

- Update controls
  ([`12e9f7c`](https://github.com/fhempy/fhempy/commit/12e9f7ce5985678c019490ab2fc5e0d585e37e65))

- Update controls
  ([`8cddfd7`](https://github.com/fhempy/fhempy/commit/8cddfd76ca714a8a047459e69728d623526a63d4))

- Update controls
  ([`68ccd1a`](https://github.com/fhempy/fhempy/commit/68ccd1a2d87c0d6b9893a183382913ca89fa5e15))

- Update controls
  ([`3855ac0`](https://github.com/fhempy/fhempy/commit/3855ac0e5115be016d83e65da8a55a640f53b6e4))

- Update controls
  ([`09a7b48`](https://github.com/fhempy/fhempy/commit/09a7b485f0de373fbd762568582dc15e8e17c4c2))

- Update controls
  ([`36c3255`](https://github.com/fhempy/fhempy/commit/36c3255974b116e756924acffe0932cb2e31af4d))

- Update controls
  ([`20cf55d`](https://github.com/fhempy/fhempy/commit/20cf55daa5d9b650b05666622eec9e72b17c22f3))

- Update controls
  ([`c8f9d02`](https://github.com/fhempy/fhempy/commit/c8f9d02e541eed4d8c8ef07c95e02eaa27a3cbfa))

- Update controls
  ([`7c9de04`](https://github.com/fhempy/fhempy/commit/7c9de04531b20dee3a6ee7b43aa0b9fbe38dfdba))

- Update controls
  ([`7f735b9`](https://github.com/fhempy/fhempy/commit/7f735b9ab5bd4a7d50a5a61a419f4ed6d5806ef7))

- Update controls
  ([`6245498`](https://github.com/fhempy/fhempy/commit/62454986110a25488ce4ab8fd5efe6db08a38c98))

- Update controls
  ([`6e14a4e`](https://github.com/fhempy/fhempy/commit/6e14a4e0925afeea9a3a9055ce5f72d29322ca50))

- Update controls
  ([`80115e1`](https://github.com/fhempy/fhempy/commit/80115e1cdbd4e93378406c7fe2935f4be9cb86ec))

- Update controls
  ([`23630d7`](https://github.com/fhempy/fhempy/commit/23630d75afe860fcebc513bc8bd657826c77eb6d))

- Update controls
  ([`45c7715`](https://github.com/fhempy/fhempy/commit/45c7715ec541b96993491d0b1c520dd7a0f4242d))

- Update controls
  ([`8a9c0b0`](https://github.com/fhempy/fhempy/commit/8a9c0b08d457dd38e39da65c70e4d09ed24bbfd7))

- Update controls
  ([`0058ee8`](https://github.com/fhempy/fhempy/commit/0058ee8064b516b4c38bf8bff2ffe02691799d32))

- Update controls
  ([`b4b58d7`](https://github.com/fhempy/fhempy/commit/b4b58d75d085992e889f0427ab4fb623eef505dd))

- Update controls
  ([`a2ae209`](https://github.com/fhempy/fhempy/commit/a2ae2093eb099d059d5ce575f64d9906f33f05ac))

- Update test actions
  ([`4642379`](https://github.com/fhempy/fhempy/commit/4642379aae33613cd068117c581a69bc1d99bd4f))

- Update tuya readme
  ([`e88275a`](https://github.com/fhempy/fhempy/commit/e88275abdb5485f8ece48c5ca7fce6a8b93c9f24))

### Features

- **erelax_vaillant**: Use vaillant-netatmo-api
  ([`f138b6b`](https://github.com/fhempy/fhempy/commit/f138b6b1a9e852a70ba545a1afb5a11224c8842c))

- **esphome**: Update to 2022.3.1
  ([`3abba2f`](https://github.com/fhempy/fhempy/commit/3abba2f6b02c52a252b5705b6d0226a121c2e4cd))

- **esphome**: Update to 2022.4.0
  ([`59683c2`](https://github.com/fhempy/fhempy/commit/59683c2f7c0bc125334320ae0dfa8ae198cbafa7))

- **gfprobt**: Prepare adjust
  ([`115fc60`](https://github.com/fhempy/fhempy/commit/115fc6060a78d3949dd2d5a022429b2dac0f1219))

- **gree_climate**: Add to readme
  ([`7ed6b1e`](https://github.com/fhempy/fhempy/commit/7ed6b1eae89690f2576115c396eb4e8fb8ac70da))

- **gree_climate**: First release
  ([`c526e10`](https://github.com/fhempy/fhempy/commit/c526e10a6e38d07793ffc0d3584730c763528a1c))

- **rct_power**: Further readings and commands ([#72](https://github.com/fhempy/fhempy/pull/72),
  [`85981f4`](https://github.com/fhempy/fhempy/commit/85981f430b18c7d2821861ce1af014a231c9002d))

- **rct_power**: Update commands ([#71](https://github.com/fhempy/fhempy/pull/71),
  [`ee8ea0d`](https://github.com/fhempy/fhempy/commit/ee8ea0d5b8aa3622a9aec43f24090aef1fa48d27))

-Update of address of battery soc limits. Old values were from a wrong module in the inverter
  -Update of address of battery current limits. Old values were not writable

- **rct_power**: Update help ([#73](https://github.com/fhempy/fhempy/pull/73),
  [`b67e0a6`](https://github.com/fhempy/fhempy/commit/b67e0a606a8abaacf19ac1c529ee23def8746fbd))

- **tuya**: Add info readings
  ([`f1817ad`](https://github.com/fhempy/fhempy/commit/f1817ada60d07a83f1274b38f240694298d929b4))

- **tuya**: Support tuya local real-time updates
  ([`9104867`](https://github.com/fhempy/fhempy/commit/9104867f51edb1a22ec3d8d34ff0dda4fbabfaf6))


## v0.1.272 (2022-04-10)

### Bug Fixes

- **ble_monitor**: Code structure changes
  ([`aa6e14f`](https://github.com/fhempy/fhempy/commit/aa6e14f4b673d98b998df761678e3cfa995eb0da))

- **ble_monitor**: Fix codestyle
  ([`9c8e691`](https://github.com/fhempy/fhempy/commit/9c8e6919fbbe8e8aa0e811ca28d160e9ba4a664c))

- **ble_monitor**: Fix possible unregister error
  ([`264f1fb`](https://github.com/fhempy/fhempy/commit/264f1fb50f55fa0296d9aeca1fe45c385d952a11))

- **ble_monitor**: Make it working
  ([`dec3186`](https://github.com/fhempy/fhempy/commit/dec31860d40b545cb3b6ad328c08e0344e858d44))

- **ble_monitor**: Remove unneeded function
  ([`206d62e`](https://github.com/fhempy/fhempy/commit/206d62ec888b15564750908b029ca52ac426cbc4))

- **ble_monitor**: Support more devs with same mac
  ([`2c18861`](https://github.com/fhempy/fhempy/commit/2c18861934fa83908bbefae0901922a98899ffe5))

- **ble_monitor**: Update readme
  ([`dc82d3d`](https://github.com/fhempy/fhempy/commit/dc82d3d9d9e88ec1286cdbb4ba1d4ad0ae6be025))

- **ble_monitor**: Working again
  ([`5399399`](https://github.com/fhempy/fhempy/commit/5399399b8ad45350d83a52dc74ef8343f6bbeba1))

- **esphome**: Fix esphome start
  ([`e4c1697`](https://github.com/fhempy/fhempy/commit/e4c1697cc62aa4734c2ca5879a35207889e641e7))

- **fhempy**: Add python version check to perl code
  ([`2452f37`](https://github.com/fhempy/fhempy/commit/2452f37fa7a0312fb480d8b078dd06b22d6b1b02))

- **fhempy**: Do not call set_attr on define
  ([`f32f12f`](https://github.com/fhempy/fhempy/commit/f32f12ff173b410492c4184b48085373046163e1))

- **fhempy**: Downgrade requests to fix errors
  ([`82a5eb5`](https://github.com/fhempy/fhempy/commit/82a5eb566601a1e18118914cf8c65fb5ab596027))

- **fhempy**: Fix installation errors
  ([`b3dfa34`](https://github.com/fhempy/fhempy/commit/b3dfa3446dceb2cce4d7be5a9c3c06d564f1b19e))

- **fhempy**: Fix IODev missing when disconnected
  ([`9244dd3`](https://github.com/fhempy/fhempy/commit/9244dd366b137cb5270fe24eadf44b49b21b20a3))

- **fhempy**: Fix port parameter
  ([`1f55020`](https://github.com/fhempy/fhempy/commit/1f5502006678b2161fd6ee7393541bd5a3f91a88))

- **fhempy**: Fix python version error handling
  ([`f9c1d89`](https://github.com/fhempy/fhempy/commit/f9c1d899ac312d3e70a5c4d3dffa21124f91d407))

- **fhempy**: Fix quotes
  ([`934a344`](https://github.com/fhempy/fhempy/commit/934a344d5cfc10479799e73434bf6bf8440be466))

- **fhempy**: Fix reading
  ([`5bbba76`](https://github.com/fhempy/fhempy/commit/5bbba76743abe5ec6089fc603ed134001b4d8841))

- **fhempy**: Fix readme processing
  ([`df9d48d`](https://github.com/fhempy/fhempy/commit/df9d48d1055562627c2492335ce28bba73abcad3))

- **fhempy**: Fix restart
  ([`04ac131`](https://github.com/fhempy/fhempy/commit/04ac13107deda0eb044daba1dbf98ad2960b8dba))

- **fhempy**: Fix sartup
  ([`5d23162`](https://github.com/fhempy/fhempy/commit/5d2316218912c8e51cbd970a0f3de3c13d85e255))

- **fhempy**: Fix startup
  ([`2145a4d`](https://github.com/fhempy/fhempy/commit/2145a4d5fc6fbc4731025625d1b081f389735842))

- **fhempy**: Keep disconnected state for bindings
  ([`4f6621c`](https://github.com/fhempy/fhempy/commit/4f6621c2b38eeb5572bddb4cbf96549f4cbd8c8b))

- **fhempy**: Python reading font correction
  ([`3284f3c`](https://github.com/fhempy/fhempy/commit/3284f3c332bef010dd00dad409fe69c00e09a80e))

- **fhempy**: Replace \n in help text
  ([`7a02515`](https://github.com/fhempy/fhempy/commit/7a02515a1f73b8a6e4aaca23baa05d08090b59a5))

- **fhempy**: Use fhempy instead of PythonModule
  ([`8d8abb4`](https://github.com/fhempy/fhempy/commit/8d8abb485286945156d60b77f6ee6f128ee0e46d))

- **fusionsolar**: Fix usage
  ([`76e4858`](https://github.com/fhempy/fhempy/commit/76e485828b35179dd5bd8de11700c7e2e3e806c0))

- **miio**: Fix error when no helptext available
  ([`e22c55c`](https://github.com/fhempy/fhempy/commit/e22c55cf8654791895f6b220b349f1044a9c008b))

- **miio**: Fixes for new library
  ([`edeab1f`](https://github.com/fhempy/fhempy/commit/edeab1f7ecc437fc017e474fb4304cf0f889d488))

- **miscale**: Fix missing method
  ([`dbb4c3a`](https://github.com/fhempy/fhempy/commit/dbb4c3a29b6faccf9466ed261e0a913bdef0f574))

- **miscale**: Fix usage
  ([`2492790`](https://github.com/fhempy/fhempy/commit/2492790f803f5455403048dd3cfa89e6a2deb1d5))

- **miscale**: Working version
  ([`e30988a`](https://github.com/fhempy/fhempy/commit/e30988adc9e2e488617f93b2441bd9e3cfd38abe))

- **rct_power**: Use textfield for set *_soc_target
  ([`ba9a923`](https://github.com/fhempy/fhempy/commit/ba9a92370159b35c33f87778c977173a5915f941))

- **ring**: Fix Undefine?
  ([`c6d9d6a`](https://github.com/fhempy/fhempy/commit/c6d9d6af60297eba29800ccb8ce1df5e6114b5b1))

- **seatconnect**: Fix Seatconnect Login ([#67](https://github.com/fhempy/fhempy/pull/67),
  [`d67cce0`](https://github.com/fhempy/fhempy/commit/d67cce057f73e6e91f731fc2196abc14d0e8feef))

- **tuya_cloud**: Fix circular import
  ([`48b0d5d`](https://github.com/fhempy/fhempy/commit/48b0d5dfe7a48219af74d0379e1ce4d553b57523))

- **tuya_cloud**: Fix logging
  ([`f384975`](https://github.com/fhempy/fhempy/commit/f38497553e662633c139b7825fe3c047b0bf932f))

- **tuya_cloud**: Try to fix circular import
  ([`7187a88`](https://github.com/fhempy/fhempy/commit/7187a88bf401c531419cda3bbe2251f66ff783fa))

- **tuya_cloud**: Try to fix circular import
  ([`d5cf08f`](https://github.com/fhempy/fhempy/commit/d5cf08faeabee835432fec80c6eb2a4406caf8d3))

- **xiaomi_gateway3**: Fix disable
  ([`16830d1`](https://github.com/fhempy/fhempy/commit/16830d1ae68a1da82cb1a7454d9bef6beb4c3947))

- **xiaomi_gateway3**: Fix disable
  ([`591612d`](https://github.com/fhempy/fhempy/commit/591612de340b4ed7e0162e441dddbc817dcb7086))

- **xiaomi_gateway3**: Support disable
  ([`1b2a59c`](https://github.com/fhempy/fhempy/commit/1b2a59c7488c7c3e0047e8a3b3a2433c94e81f16))

- **zigbee2mqtt**: Fix restart
  ([`54545c2`](https://github.com/fhempy/fhempy/commit/54545c2b1935c7cc7f14ec9961188101fe540846))

- **zigbee2mqtt**: Fix restart
  ([`d36bea4`](https://github.com/fhempy/fhempy/commit/d36bea4249350ea493757406328602f1b8e7a400))

- **zigbee2mqtt**: Fix weblink
  ([`ca6c105`](https://github.com/fhempy/fhempy/commit/ca6c105ed6140a7d308a69c5f98cf29abd0996ec))

### Chores

- Fix version
  ([`0e741bc`](https://github.com/fhempy/fhempy/commit/0e741bcaf70dd640df1021299ffdfd3ad0129738))

- Update controls
  ([`0f7c5fe`](https://github.com/fhempy/fhempy/commit/0f7c5fee1c0ccf25236e03fc11d7685df19b4f6f))

- Update controls
  ([`c66a753`](https://github.com/fhempy/fhempy/commit/c66a75336f61eef939ca8ee1dcb1740dae31fd59))

- Update controls
  ([`5bcea05`](https://github.com/fhempy/fhempy/commit/5bcea052d3b34dfb64fb51d265682d762b98bad5))

- Update controls
  ([`e856946`](https://github.com/fhempy/fhempy/commit/e856946361f1e05eab094a718ce24f3e29b91dcb))

- Update controls
  ([`1604526`](https://github.com/fhempy/fhempy/commit/16045267987db64506ae2fff7de62aa02e1850d2))

- Update controls
  ([`3813297`](https://github.com/fhempy/fhempy/commit/3813297d3f33d1c0a3b3a7f8edb1ab6cfd433fd0))

- Update controls
  ([`42dfeba`](https://github.com/fhempy/fhempy/commit/42dfeba959af473babb24d607223c6cf31ea93cd))

- Update controls
  ([`7ef5be9`](https://github.com/fhempy/fhempy/commit/7ef5be9755fd624b1835672e2ad3d0980a139f9b))

- Update controls
  ([`fe0f1be`](https://github.com/fhempy/fhempy/commit/fe0f1befe1c6b42a741b007289a1cce4fbf88fda))

- Update controls
  ([`bb1815f`](https://github.com/fhempy/fhempy/commit/bb1815f400ee08580f7176d4050f0b4d33b82521))

- Update controls
  ([`bf19bdb`](https://github.com/fhempy/fhempy/commit/bf19bdbce049e252ab6d55d7792fc5eb5521d276))

- Update controls
  ([`cd80ef1`](https://github.com/fhempy/fhempy/commit/cd80ef19d24ca5b5601350e686175455b5315fa8))

- Update controls
  ([`dd3b8f0`](https://github.com/fhempy/fhempy/commit/dd3b8f0e76c0c5e105b43300a7e2a0c4f9c4d5cd))

- Update controls
  ([`550e949`](https://github.com/fhempy/fhempy/commit/550e949173ac187b434df40929ed85c2cb25d1c7))

- Update controls
  ([`07861d4`](https://github.com/fhempy/fhempy/commit/07861d4bb8241da30769a8e511ce6412adcaea48))

- Update controls
  ([`48bd50d`](https://github.com/fhempy/fhempy/commit/48bd50d9cc63bcb770e1e4444c41c73f11d237aa))

- Update controls
  ([`bd512d9`](https://github.com/fhempy/fhempy/commit/bd512d97238e38ea1be01a425c6aab70ff98fcd8))

- Update controls
  ([`484dcde`](https://github.com/fhempy/fhempy/commit/484dcde9d56da4d47e4786e21aec72f7d0b81982))

- Update controls
  ([`bf86f4f`](https://github.com/fhempy/fhempy/commit/bf86f4f21ee88c54f0a9c6cfb59cd988cc2589d7))

- Update controls
  ([`d14642f`](https://github.com/fhempy/fhempy/commit/d14642f87bc78118d42f299bdc627ce321d91acc))

- Update controls
  ([`2edc20b`](https://github.com/fhempy/fhempy/commit/2edc20bdb57117c82258bfe595e1d864fc3d495e))

- Update controls
  ([`7163851`](https://github.com/fhempy/fhempy/commit/7163851d879a6803830589019facf7d6a2ca837a))

- Update controls
  ([`4aea9eb`](https://github.com/fhempy/fhempy/commit/4aea9eb1f85e0a8029e34b74188ebc07411b5a13))

- Update controls
  ([`499ca45`](https://github.com/fhempy/fhempy/commit/499ca459df244e3e607bf8129beb85d21c6c06fe))

- Update controls
  ([`0c969af`](https://github.com/fhempy/fhempy/commit/0c969af3fbacaabbdaa97b3091c8a410878f30aa))

- Update controls
  ([`0258fe0`](https://github.com/fhempy/fhempy/commit/0258fe0ceee0a8a555409dfe854393e1d53f793f))

- Update controls
  ([`1161c59`](https://github.com/fhempy/fhempy/commit/1161c5970ab790b15348ec9d2d2adc83c04280a3))

- Update controls
  ([`562fd61`](https://github.com/fhempy/fhempy/commit/562fd61b29559287cfe1a8666db636d044f71bcc))

- Update controls
  ([`1d4c65c`](https://github.com/fhempy/fhempy/commit/1d4c65c4973c29e3834e689386d1ff2aa9bb9ffa))

- Update controls
  ([`8712f8b`](https://github.com/fhempy/fhempy/commit/8712f8b2e39f4218188db6781cc8d1229c3dae15))

- Update controls
  ([`4f2d4e9`](https://github.com/fhempy/fhempy/commit/4f2d4e95ea066c01c5db9e0385f01b0a54a7531f))

- Update controls
  ([`ef42630`](https://github.com/fhempy/fhempy/commit/ef4263012a3f9fafa04c81f1765b418b6edf0820))

- Update controls
  ([`d992cb8`](https://github.com/fhempy/fhempy/commit/d992cb89fedfec31105d19b787114442992fb84a))

- Update controls
  ([`5a2309c`](https://github.com/fhempy/fhempy/commit/5a2309c25e8af0f41e0c4761d75433e0b543d70e))

- Update controls
  ([`98f3b02`](https://github.com/fhempy/fhempy/commit/98f3b02c44c394114d866c2ae3fa0d9f546cd698))

- Update controls
  ([`8d21d47`](https://github.com/fhempy/fhempy/commit/8d21d474408b01e0bf119faf7dc4aef7987a6a8e))

- Update controls
  ([`ea99be2`](https://github.com/fhempy/fhempy/commit/ea99be24e8a4683162705dc77ab6265776623578))

- Update controls
  ([`4dc5dee`](https://github.com/fhempy/fhempy/commit/4dc5deebd33245ca2f1d15e65b373bb117962146))

- Update controls
  ([`b64397a`](https://github.com/fhempy/fhempy/commit/b64397a9a2d41288ee680370d74cb2268c4d0f80))

- Update controls
  ([`e68b55f`](https://github.com/fhempy/fhempy/commit/e68b55f0a4b2b0fa0c026a80f50b6c532b675e0f))

- Update controls
  ([`edbb47c`](https://github.com/fhempy/fhempy/commit/edbb47c8ee58bf3c90befc84a26d44f220b1aea0))

- Update controls
  ([`fb4d1fa`](https://github.com/fhempy/fhempy/commit/fb4d1fa5d68b622a38123b4c032f3563f1b286b4))

### Features

- **ble_monitor**: First working release
  ([`24eb78e`](https://github.com/fhempy/fhempy/commit/24eb78e3328bea123a1c17c75d404373ef526a9a))

- **ble_monitor**: Prepare ble_monitor
  ([`c6098fa`](https://github.com/fhempy/fhempy/commit/c6098faf16fe140631c470a1e72d3def6eeae07d))

- **ble_monitor**: Support encryption key attr
  ([`cdd1521`](https://github.com/fhempy/fhempy/commit/cdd1521c5fe0d6d23792c7b7283d2ecff0c1fdd9))

- **fhempy**: Add ble_monitor, miscale
  ([`819e678`](https://github.com/fhempy/fhempy/commit/819e6789a2d141287daa6f6a10b865013f27c5ce))

- **fhempy**: Add fusionsolar
  ([`a449c5e`](https://github.com/fhempy/fhempy/commit/a449c5e22b632f8a486a9d17a7e5dc8c7707cda6))

- **fhempy**: Add more info about peer
  ([`54c320d`](https://github.com/fhempy/fhempy/commit/54c320d050cb2ce200b39a405ac413350d28603c))

- **fhempy**: No more BETA
  ([`bac69fc`](https://github.com/fhempy/fhempy/commit/bac69fc659dbcc5224d907d867bc5d7424eae278))

- **fhempy**: Support datetime for readings
  ([`3a9cf74`](https://github.com/fhempy/fhempy/commit/3a9cf740b946d80bf9673a04d98c3ed21301bf03))

- **fhempy**: Support git+https requirements
  ([`7987489`](https://github.com/fhempy/fhempy/commit/7987489abbaf31cfc9b8bd2305609e4e460f39c7))

- **fusionsolar**: Get data from fusionsolar kiosk
  ([`85f1a1f`](https://github.com/fhempy/fhempy/commit/85f1a1fc3dc98c21ecaca66a70ef5950531b8266))

- **meross**: Support mod100
  ([`6c0b7e2`](https://github.com/fhempy/fhempy/commit/6c0b7e2a94e29299d54104592d11acdad6c8fbcd))

- **miio**: Update lib
  ([`828bcec`](https://github.com/fhempy/fhempy/commit/828bcec59e385d242cf1cf4c0c69c7e5dabcf44a))

- **miscale**: Support miscale
  ([`b9dc4d6`](https://github.com/fhempy/fhempy/commit/b9dc4d698d9df2dc88e7fb888df3157ffd9d6509))

- **rct_power**: Add min_soc_maint_charge
  ([`7695d8e`](https://github.com/fhempy/fhempy/commit/7695d8eb1129d0fe0ca505c62f9b28b79cdbf1f0))

- **rct_power**: Support ext_power_reduction
  ([`3d72be9`](https://github.com/fhempy/fhempy/commit/3d72be98c9d6348413f32086aeea2c184b8516dc))

- **rct_power**: Support max_(dis)charge_current
  ([`0612cae`](https://github.com/fhempy/fhempy/commit/0612cae475e10e54da7f428cd14f104fcc267e47))

- **rct_power**: Support max_power_ac
  ([`f4f6d8c`](https://github.com/fhempy/fhempy/commit/f4f6d8c89792ed3c4e8e2b84a0dc4d92f0a1081f))

- **xiaomi_gateway3**: Support ble smoke detector
  ([`3dee86f`](https://github.com/fhempy/fhempy/commit/3dee86f38fd2550fc0f30b88cccfbe8c79cfc832))

- **zigbee2mqtt**: First release
  ([`ac1cd73`](https://github.com/fhempy/fhempy/commit/ac1cd73555f2edf0b0d34baa68e77a545377aa42))

- **zigbee2mqtt**: First working release
  ([`8f9d26a`](https://github.com/fhempy/fhempy/commit/8f9d26a503966edef49950d62c2b26e3350fc531))

- **zigbee2mqtt**: Prepare zigbee2mqtt
  ([`9810678`](https://github.com/fhempy/fhempy/commit/98106780b9699a7be17ba713b79e188402d94c55))


## v0.1.233 (2022-02-13)

### Bug Fixes

- **meross**: Remove stopped state
  ([`450fbf4`](https://github.com/fhempy/fhempy/commit/450fbf4ec7d412a08e86c8173ce0933212fdd945))

- **rct_power**: Fix display_brightness
  ([`89c8d92`](https://github.com/fhempy/fhempy/commit/89c8d92b3ce3e1db89cd909d1a97fc3b6a918e1d))

- **rct_power**: Fix function call
  ([`995c6ba`](https://github.com/fhempy/fhempy/commit/995c6ba5d9ab78c906ff2c7d320e46ea122f1b73))

- **rct_power**: Fix set *_soc_target
  ([`f867b78`](https://github.com/fhempy/fhempy/commit/f867b7882ea37441e91ee0ace3760e3f74720946))

- **skodaconnect**: Fix login
  ([`d3a92df`](https://github.com/fhempy/fhempy/commit/d3a92df885c40d5a500bfc640cef191c5e2a6124))

### Chores

- Update controls
  ([`dae639b`](https://github.com/fhempy/fhempy/commit/dae639b7c875a774f5158a31ae76b521a271543d))

- Update controls
  ([`35ecf0b`](https://github.com/fhempy/fhempy/commit/35ecf0b55ad4c86b9c4d2295a9ff13ca793fe6d6))

- Update controls
  ([`36e20d2`](https://github.com/fhempy/fhempy/commit/36e20d2ebceb3abbb09025fa890f7b5a1ed86e77))

- Update controls
  ([`cc19d33`](https://github.com/fhempy/fhempy/commit/cc19d334b5871f23409d00e6d171a0c9b78f260e))

- Update controls
  ([`8ddea26`](https://github.com/fhempy/fhempy/commit/8ddea265e7de1a462973e30c7d4a9985a3e0dc69))

- Update controls
  ([`dd802c4`](https://github.com/fhempy/fhempy/commit/dd802c480e9cc0b385bdd79bd9c1916eb18a4fc5))

### Features

- **rct_power**: Further set functions
  ([`27812d0`](https://github.com/fhempy/fhempy/commit/27812d066ee58689aab681b066180705f5805b5d))

- **rct_power**: Support disable/update_readings
  ([`f511879`](https://github.com/fhempy/fhempy/commit/f51187962b5357406e97fabe24e7203d85faaa2f))


## v0.1.227 (2022-02-12)

### Chores

- Update controls
  ([`37bf694`](https://github.com/fhempy/fhempy/commit/37bf6949c9edae15a7bb15765747af4e7ef08a2e))

### Features

- **rct_power**: Support display brightness
  ([`533954a`](https://github.com/fhempy/fhempy/commit/533954ac61b9fa84ce07a1edc692c712ff3d2a70))


## v0.1.226 (2022-02-11)

### Bug Fixes

- **fhempy**: Change fhempy_remote to _peer
  ([`570afc8`](https://github.com/fhempy/fhempy/commit/570afc8d469e2e498b1320928f359fa52628d2db))

- **fhempy**: Fix fhempy_log error msg
  ([`da0f71c`](https://github.com/fhempy/fhempy/commit/da0f71c9d1230c4cc83980711797f42a6d84a3ae))

- **fhempy**: Fix naming
  ([`b9c9cf1`](https://github.com/fhempy/fhempy/commit/b9c9cf1fa3562fe24d8c4601a9520c565f1bb09c))

- **fhempy**: Fix utf8 issues
  ([`36383c5`](https://github.com/fhempy/fhempy/commit/36383c5141a7ed48e386c73dfac9074bb1b3d28d))

- **helloworld**: Add README
  ([`7f12567`](https://github.com/fhempy/fhempy/commit/7f12567ab7a5e84adeab4dfb5395e76bdc38011f))

- **meross**: Fix stop
  ([`b22b7a0`](https://github.com/fhempy/fhempy/commit/b22b7a0d232b0312aeb8eb62974f0dfdcd020fe6))

- **nefit**: Change default interval to 900s
  ([`48a69e8`](https://github.com/fhempy/fhempy/commit/48a69e8cd819fe443a7e5ff2ef5e432e8972827f))

- **nefit**: Fix system_pressure
  ([`1804780`](https://github.com/fhempy/fhempy/commit/1804780e585ca796277346d57da87810f9ec1349))

- **nefit**: Update dayassunday readings asap
  ([`9f55182`](https://github.com/fhempy/fhempy/commit/9f55182cd8231bf397d824b43cfeff0b36ab6111))

- **rct_power**: Change interval to 10s, fix state
  ([`72dced8`](https://github.com/fhempy/fhempy/commit/72dced8eb70b4082a317254b9be6eac35d608c2e))

- **rct_power**: Support json/array format
  ([`c282ac9`](https://github.com/fhempy/fhempy/commit/c282ac979ee79e53a08593b169619b046b86f362))

- **ring**: Fix circular import?
  ([`a061667`](https://github.com/fhempy/fhempy/commit/a061667c55ec1e58d57ef0bd2ed6452a2acf0c0c))

- **skodaconnect**: Update Base Lib ([#64](https://github.com/fhempy/fhempy/pull/64),
  [`c1eefd4`](https://github.com/fhempy/fhempy/commit/c1eefd4dd91c5563453b14469b2a41777208afda))

- **skodaconnect**: Update Base Lib ([#65](https://github.com/fhempy/fhempy/pull/65),
  [`7ef4a13`](https://github.com/fhempy/fhempy/commit/7ef4a13358312ef14f764d5f81e754fc47732dcf))

Fixed timestamps for requests in Base Lib

- **skodaconnect**: Update manifest.json ([#60](https://github.com/fhempy/fhempy/pull/60),
  [`df00380`](https://github.com/fhempy/fhempy/commit/df0038006fece2eee2ff176255d1113a09037633))

Update Base-Lib to 1.1.14 due to change of login form

- **tuya_cloud**: Add pulsar activation error msg
  ([`faab929`](https://github.com/fhempy/fhempy/commit/faab92932949a2eea85414704397d50aa8270e4b))

- **xiaomi_gateway3**: Fix ble devices
  ([`3c100d9`](https://github.com/fhempy/fhempy/commit/3c100d990ae16ddd2af94508c89545dd735414a7))

- **xiaomi_gateway3**: Fix BT devices
  ([`81f8aea`](https://github.com/fhempy/fhempy/commit/81f8aea5ffc16f55a239a3579c15ca5b1fc9b547))

- **xiaomi_gateway3**: Fix BT devices
  ([`be7b30d`](https://github.com/fhempy/fhempy/commit/be7b30d6117c77b0c8e9d6fcfce995d7a619bfca))

- **xiaomi_gateway3**: Fix dict changed during iter
  ([`8c5bd74`](https://github.com/fhempy/fhempy/commit/8c5bd74e3262d60b9afbe3af472c1b3944c92d54))

### Chores

- Readme fixes
  ([`ecd1c81`](https://github.com/fhempy/fhempy/commit/ecd1c81da95287d49c650d00f103d2e6b1773555))

- Update controls
  ([`df4b634`](https://github.com/fhempy/fhempy/commit/df4b6343c4f78a327248c512e34190cc4d0939cf))

- Update controls
  ([`6e5a9b9`](https://github.com/fhempy/fhempy/commit/6e5a9b9e95ee224be3923b4bc6c35c92a0c70857))

- Update controls
  ([`493e2d8`](https://github.com/fhempy/fhempy/commit/493e2d827ff4ae50900481860615eec7b318a777))

- Update controls
  ([`816dc07`](https://github.com/fhempy/fhempy/commit/816dc0712d22f6fc765f86ce20504930e1f69e6e))

- Update controls
  ([`9597c3a`](https://github.com/fhempy/fhempy/commit/9597c3a57c6b44ac5d86c3fb7c5f647912a6f6b6))

- Update controls
  ([`5b15569`](https://github.com/fhempy/fhempy/commit/5b155690b3eb82e8bdd879bcba7b6756c949c6df))

- Update controls
  ([`9248eb4`](https://github.com/fhempy/fhempy/commit/9248eb4407a10c0264e05941a4e951dfbab752e3))

- Update controls
  ([`69ffec3`](https://github.com/fhempy/fhempy/commit/69ffec33eada0a4831ec3f28409fef92e6ede725))

- Update controls
  ([`c6bf93a`](https://github.com/fhempy/fhempy/commit/c6bf93a875d06df34872faf900b5a46ff1462a72))

- Update controls
  ([`e14160b`](https://github.com/fhempy/fhempy/commit/e14160bb6defd3fe988128dccf936b0acd351010))

- Update controls
  ([`3b2b538`](https://github.com/fhempy/fhempy/commit/3b2b538a44f8e0bc3c5b79a84e76aff6757ee150))

- Update controls
  ([`0d85cfa`](https://github.com/fhempy/fhempy/commit/0d85cfa08d64928c2f637a142960bbf80b3c4244))

- Update controls
  ([`0171c2a`](https://github.com/fhempy/fhempy/commit/0171c2ada8471e86fc18566b0c2849ab8ef9a71b))

- Update controls
  ([`8a5f332`](https://github.com/fhempy/fhempy/commit/8a5f332b18c97dc92f45727b882ac54c21bc55af))

- Update controls
  ([`6976d94`](https://github.com/fhempy/fhempy/commit/6976d94d75a7fd746cd7ca1346b6d644753c919a))

- Update controls
  ([`4a5f0c3`](https://github.com/fhempy/fhempy/commit/4a5f0c3dfa595a2ee431ef430ae39d65295fa9ff))

- Update controls
  ([`d29fb65`](https://github.com/fhempy/fhempy/commit/d29fb65d75ad436b7b702d2d8af438ed1d263ef2))

- Update controls
  ([`e275794`](https://github.com/fhempy/fhempy/commit/e275794bcdc94b6162ff0fbec6a75ef9c50de0b5))

- Update controls
  ([`310695a`](https://github.com/fhempy/fhempy/commit/310695aba0e1f1b8e46f877f334079eb951be2c1))

### Features

- **eq3bt**: Support max_retries attr
  ([`b483878`](https://github.com/fhempy/fhempy/commit/b483878b89e05fe78df9db4df4cbe2498468799c))

- **meross**: Support roller shutter
  ([`eba7e27`](https://github.com/fhempy/fhempy/commit/eba7e2744e80549dd2efd5c733f17222481527b1))

- **nefit**: Support system pressure
  ([`c90669e`](https://github.com/fhempy/fhempy/commit/c90669e3e1a053691eca2356c22fac30bc7a1ce6))

- **pyit600**: Additional attributes added ([#59](https://github.com/fhempy/fhempy/pull/59),
  [`1753761`](https://github.com/fhempy/fhempy/commit/1753761290a41ba11e8959e6010a879554e8b0c9))

- **rct_power**: Add format, add error reading
  ([`0772e76`](https://github.com/fhempy/fhempy/commit/0772e7693cefb66f84bc90b9a633b8cd11f22f56))

- **rct_power**: Attr error_reading, default_...
  ([`584e849`](https://github.com/fhempy/fhempy/commit/584e8495ae323e4f71d2d4db9e4ac4af98bc000a))

- **rct_power**: New attributes
  ([`0651dc5`](https://github.com/fhempy/fhempy/commit/0651dc5dbe48e3ecaf8454a20ad357ecac61be35))

- **rct_power**: Support RCT Power inverter
  ([`76f316f`](https://github.com/fhempy/fhempy/commit/76f316fd280a3209c44e0f6fc91a21bb8f206079))

- **tuya_cloud**: Add tuya open pulsar messaging
  ([`2c49000`](https://github.com/fhempy/fhempy/commit/2c4900090738a80113512877a3a65172246514cb))

- **xiaomi_gateway3**: Support 1371 sensor
  ([`3c04477`](https://github.com/fhempy/fhempy/commit/3c044779f1ccf3d7fafcd7fcdc238425169c90f1))

- **xiaomi_gateway3**: Support BT smoke alarm
  ([`983fe78`](https://github.com/fhempy/fhempy/commit/983fe78877eefa9232091273276a127776bd143b))


## v0.1.207 (2022-01-23)

### Bug Fixes

- **eq3bt**: Fix windowOpenTime/Temp
  ([`47ad1d2`](https://github.com/fhempy/fhempy/commit/47ad1d2c24fb50dba7f1f1ed09041eb4375ac56e))

- **eq3bt**: Windowopentemp starts at 5 degrees
  ([`3ef7e36`](https://github.com/fhempy/fhempy/commit/3ef7e36bdfe2b90cd5f9780ac390decb5d0a3775))

- **esphome**: Fix attr sortby on restart
  ([`a605adf`](https://github.com/fhempy/fhempy/commit/a605adfe0c0704f3e04db94fbb4d59697a4bef3f))

- **esphome**: Fix checkIfDeviceExists
  ([`2b67d7d`](https://github.com/fhempy/fhempy/commit/2b67d7d6dbfc14e1e800dcdd957f5d7a0355bfbd))

- **esphome**: Fix create weblinks
  ([`e4ec22f`](https://github.com/fhempy/fhempy/commit/e4ec22f6597ee96307bc1ea5de6a4d2c22f67264))

- **esphome**: Fix esphome_installer device
  ([`7b0d925`](https://github.com/fhempy/fhempy/commit/7b0d92581d0700e295164e125a909687f97dfd2f))

- **esphome**: Fix weblinks device
  ([`9e93ef0`](https://github.com/fhempy/fhempy/commit/9e93ef00a44e15845906196536651dd858fab87a))

- **fhempy**: Add sentry requirement
  ([`0df8c52`](https://github.com/fhempy/fhempy/commit/0df8c522e369b225878d656a291cf22714e66157))

- **fhempy**: Change sentry sample rate
  ([`3a0d3e5`](https://github.com/fhempy/fhempy/commit/3a0d3e5b4d617cc73f4107801ad4237d4e596672))

- **fhempy**: Clarify peer installation
  ([`9d9a5d3`](https://github.com/fhempy/fhempy/commit/9d9a5d3415afd500948f4043ae02847245998d8f))

- **fhempy**: Fix CoProcess error
  ([`397edde`](https://github.com/fhempy/fhempy/commit/397edde0b39d52b0175454c2fd071b5ce8b2e973))

- **fhempy**: Fix dbus dependency
  ([`09c5717`](https://github.com/fhempy/fhempy/commit/09c5717cee2fd8aa13c911ca5466d1a50dba7f6d))

- **fhempy**: Fix timeout again
  ([`6f920cb`](https://github.com/fhempy/fhempy/commit/6f920cbc79fb1ebfe4394ae147fa908213555d2a))

- **fhempy**: Hopefully fixed a timeout bug
  ([`1c4f6be`](https://github.com/fhempy/fhempy/commit/1c4f6be11f7c8d06b57094bfffafb5ec9fda6ecc))

- **fhempy**: Iodev selection fix
  ([`495e41d`](https://github.com/fhempy/fhempy/commit/495e41da6c4b6054ffa8de5b0cde2ca2e297141c))

- **fhempy**: Link to github releases
  ([`7e3f326`](https://github.com/fhempy/fhempy/commit/7e3f326b3f8cf34728510ada4d2bffc07b6408a4))

- **fhempy**: Remove perf sentry
  ([`cc5d4f8`](https://github.com/fhempy/fhempy/commit/cc5d4f8985ecd3c904f5c9bac78f50170f6da830))

- **fhempy**: Remove sentry as I'm not using it
  ([`0fefcf0`](https://github.com/fhempy/fhempy/commit/0fefcf0dfd67d94f20678cf50dee8f9847233b86))

- **fhempy**: Remove temporary for log
  ([`957a14b`](https://github.com/fhempy/fhempy/commit/957a14b92368af0b8a329bb2fc601eff98518a38))

- **fhempy**: Update zeroconf
  ([`650f7ad`](https://github.com/fhempy/fhempy/commit/650f7ad6176d0d89a54fa638b12da75e50619740))

- **fhempy**: Update zeroconf 0.36.12
  ([`768df9e`](https://github.com/fhempy/fhempy/commit/768df9e8a27d0ac06b1f8e7ccd95ff01a7ec34f5))

- **fhempy**: Use markdown2 instead of markdown
  ([`f2403e6`](https://github.com/fhempy/fhempy/commit/f2403e6457e860afc4b69485e48caf90a0a8c24a))

- **fhempy**: Wait max60s for fhem reply
  ([`1dbcf1e`](https://github.com/fhempy/fhempy/commit/1dbcf1e5e929815864f2791dc6407c3415b30688))

- **googlecast**: Do not stop zeroconf
  ([`720b007`](https://github.com/fhempy/fhempy/commit/720b007c81f3ff41da84485feedd7a0660e5fc5e))

- **googlecast**: Fix endless loop on undefine
  ([`655e3ad`](https://github.com/fhempy/fhempy/commit/655e3adc13a4d7d79036055a2595893f6b98ad60))

- **googlecast**: Fix speak
  ([`5a37d57`](https://github.com/fhempy/fhempy/commit/5a37d57ac0ce598827598918dbe3c50d261f9cf7))

- **googlecast**: Report token errors to user
  ([`a65c64e`](https://github.com/fhempy/fhempy/commit/a65c64ea956e415afa0a2e52dce7e293ba8b5d65))

- **googlecast**: Update lib and change discovery
  ([`13f02e1`](https://github.com/fhempy/fhempy/commit/13f02e1eeba09a4f6f61452727b5a4f3825c64fd))

- **googlecast**: Update lib to 10.1.1
  ([`334d171`](https://github.com/fhempy/fhempy/commit/334d171f3ead33f6b108bd519d0e5d01a2577779))

- **googlecast**: Update lib to 9.4.0
  ([`82a1d6b`](https://github.com/fhempy/fhempy/commit/82a1d6b8431343d4d5ed1a1c9dd8c07de2ac2e28))

- **googlecast**: Update lib/zeroconf
  ([`cab72a7`](https://github.com/fhempy/fhempy/commit/cab72a71694f9754af29d8ccdb64050697717dea))

- **meross**: Fix typo
  ([`08f332e`](https://github.com/fhempy/fhempy/commit/08f332e8c2f08e70429b2f54b40988c37654c01f))

- **mitemp2**: Try to fix mitemp2
  ([`ba558c0`](https://github.com/fhempy/fhempy/commit/ba558c07a56841c998166709447902e6fb671fa7))

- **nefit**: Fix again tomorrow/todayAsSunday
  ([`6449ad2`](https://github.com/fhempy/fhempy/commit/6449ad21485ce005e34d88853b2b71c44192d28e))

- **nefit**: Fix consumption
  ([`11ce422`](https://github.com/fhempy/fhempy/commit/11ce4222a7c9ddbf214eca26a5fdec6b03bea882))

- **nefit**: Fix consumption again
  ([`def458c`](https://github.com/fhempy/fhempy/commit/def458c970e5deae0e60b237a973e3cdcfb93338))

- **nefit**: Fix reconnect, rename readings
  ([`0705e8d`](https://github.com/fhempy/fhempy/commit/0705e8d44ab84743cb99b05ca8252a5a2e0e31e4))

- **nefit**: Fix retrieve dayassunday
  ([`c78e836`](https://github.com/fhempy/fhempy/commit/c78e836598aabf7289213200ce12aad3843e2423))

- **nefit**: Fix some readings
  ([`e4613f9`](https://github.com/fhempy/fhempy/commit/e4613f909156015c190d2d39603f241e4d2769b3))

- **nefit**: Fix today/tomorrowAsSunday
  ([`ff11294`](https://github.com/fhempy/fhempy/commit/ff1129413f761ee9d9badff2d5080ac525c8e469))

- **nefit**: Fix umlaut issue
  ([`76710bf`](https://github.com/fhempy/fhempy/commit/76710bf279eef26303edff96f7cce3de968c5983))

- **nefix**: Readme fixes
  ([`7f698e8`](https://github.com/fhempy/fhempy/commit/7f698e898a7281f3a789ac54284c44261c86fb9f))

- **pyit600**: Minor fixes ([#56](https://github.com/fhempy/fhempy/pull/56),
  [`3bdbaff`](https://github.com/fhempy/fhempy/commit/3bdbaff9f374b4ab7b5fae250b76921b8ea2a98a))

- **pyit600**: Usage description updated ([#58](https://github.com/fhempy/fhempy/pull/58),
  [`9ce8405`](https://github.com/fhempy/fhempy/commit/9ce84058d648878e06cb720d1abdfc505124d388))

- **ring**: Correctly stop update thread
  ([`cec6b74`](https://github.com/fhempy/fhempy/commit/cec6b746886a8991cacb95a10ec361b6f0d7085b))

- **ring**: Ding poll in separate thread
  ([`7fc27a6`](https://github.com/fhempy/fhempy/commit/7fc27a683177ce84b2aaac7eac541c66b6bde574))

- **ring**: Update test
  ([`cef1d64`](https://github.com/fhempy/fhempy/commit/cef1d643813884af75ff54e24296d56fe79aa422))

- **skodaconnect**: Update lib to 1.1.10
  ([`eb19421`](https://github.com/fhempy/fhempy/commit/eb19421b9ddc7c17cddb84847503fa1f5f608fcb))

- **tuya**: Remove error when offline
  ([`91cfa6c`](https://github.com/fhempy/fhempy/commit/91cfa6cf58df2dd789d9675c420849a7c1a04a35))

- **tuya_cloud**: Better error handling
  ([`0d94229`](https://github.com/fhempy/fhempy/commit/0d94229f70039e7b650462101fd3940c8cb26e95))

- **tuya_cloud**: Change lib to 0.4.1
  ([`8ef2e9f`](https://github.com/fhempy/fhempy/commit/8ef2e9f03c64bb0ef69ab6e14aaddd73806251b0))

- **tuya_cloud**: Fix AuthType
  ([`777edc0`](https://github.com/fhempy/fhempy/commit/777edc0327b71e424864f9478e0fbc2564ac51f2))

- **tuya_cloud**: Fix colour_data
  ([`d2fd1ac`](https://github.com/fhempy/fhempy/commit/d2fd1ac0b56540ff589c234489416e95f1973fc4))

- **tuya_cloud**: Fix lib usage
  ([`9b2dccf`](https://github.com/fhempy/fhempy/commit/9b2dccfc4469b0f186d3097b2f4aa1a3898ff058))

- **tuya_cloud**: Fix pow() bug
  ([`275ef99`](https://github.com/fhempy/fhempy/commit/275ef996e953cf65224af85d606d517db07cc8b3))

- **tuya_cloud**: Fix python 3.7
  ([`b28cf4e`](https://github.com/fhempy/fhempy/commit/b28cf4e0213e9ee802c8aec94b40d1840d92ba3f))

- **tuya_cloud**: Fix typo
  ([`e7b8b62`](https://github.com/fhempy/fhempy/commit/e7b8b62c1acf7cc65de83c8cd8688e4c0808fa05))

- **tuya_cloud**: Remove update API calls
  ([`2aac25c`](https://github.com/fhempy/fhempy/commit/2aac25c2426850ee0fa3d419b5eff9e4474b150a))

- **tuya_cloud**: Restart mqtt loop deactivated
  ([`3cbad93`](https://github.com/fhempy/fhempy/commit/3cbad9381002299d3b64f51887838e92dc9fb4fd))

- **tuya_cloud**: Retrieve status every 900s
  ([`c085381`](https://github.com/fhempy/fhempy/commit/c085381fe00d1087feba2afd1a44dea88b0b5e3b))

- **tuya_cloud**: Support python 3.7 again
  ([`b54b5b8`](https://github.com/fhempy/fhempy/commit/b54b5b82683d177691df0a7c0c3bb85ab9670f38))

- **tuya_cloud**: Update lib to 0.6.3 (python>=3.8)
  ([`d2448d7`](https://github.com/fhempy/fhempy/commit/d2448d764ece18b4387420216e86b83f15adb495))

- **tuya_cloud**: Update lib, python>3.7 required!!
  ([`ea69096`](https://github.com/fhempy/fhempy/commit/ea690962be90d0c8713b503008ea52d8d4fe338d))

- **tuya_cloud**: Update tuya iot lib
  ([`3ef9f5b`](https://github.com/fhempy/fhempy/commit/3ef9f5bbddf53aa03d07044b881fedf069733f91))

- **xiaomi_gateway3**: Fix connected state
  ([`08005c0`](https://github.com/fhempy/fhempy/commit/08005c0634846aa21e9b56b977b41d24497bc288))

- **xiaomi_gateway3**: Fix pairing
  ([`26848db`](https://github.com/fhempy/fhempy/commit/26848db865253f70a95851fa44621adc0e783b51))

- **xiaomi_gateway3**: Fix z2m mode
  ([`14f3f5b`](https://github.com/fhempy/fhempy/commit/14f3f5b305e7a76bb61092819c5dc404f66e6206))

- **xiaomi_gateway3**: Fix zigbee2mqtt
  ([`fd10b93`](https://github.com/fhempy/fhempy/commit/fd10b93e9719626add8604b913743a5bcba41694))

- **xiaomi_tokens**: Fix for de server
  ([`63c6c4b`](https://github.com/fhempy/fhempy/commit/63c6c4b458f2432cef97dade4d490f2cc0be7369))

### Chores

- Add pyit600 to readme
  ([`80c28db`](https://github.com/fhempy/fhempy/commit/80c28db765d742ba0e8393bdf2106169918eec6e))

- Fix git
  ([`0b37201`](https://github.com/fhempy/fhempy/commit/0b37201a93357761c4a8f40d588f31f72118b3fc))

- Update controls
  ([`f527d60`](https://github.com/fhempy/fhempy/commit/f527d6019f107645dc0e29883ad8664fb2fcbe2a))

- Update controls
  ([`429b3d8`](https://github.com/fhempy/fhempy/commit/429b3d84bb895e46afe76878938c6cf345c3776a))

- Update controls
  ([`5f28193`](https://github.com/fhempy/fhempy/commit/5f2819320d2cc76c242e043271ee79fbffc4ee7d))

- Update controls
  ([`ba6c953`](https://github.com/fhempy/fhempy/commit/ba6c95394eeb4b9f8b5804223501bc8cf9f076c8))

- Update controls
  ([`83cada6`](https://github.com/fhempy/fhempy/commit/83cada6effb60f1180eaed6d70debba5e52cd73c))

- Update controls
  ([`a75062b`](https://github.com/fhempy/fhempy/commit/a75062bc302f7ed0bec517fdf20320c0fa0e0d46))

- Update controls
  ([`5d92283`](https://github.com/fhempy/fhempy/commit/5d9228324bb764710a4e12c9912ac3eea0d424eb))

- Update controls
  ([`47869ac`](https://github.com/fhempy/fhempy/commit/47869ac31202bc7ab3ce34791b3868027f94598f))

- Update controls
  ([`4184693`](https://github.com/fhempy/fhempy/commit/418469335f3aed21ee3da46fe869b2adf5c0d937))

- Update controls
  ([`7a37281`](https://github.com/fhempy/fhempy/commit/7a37281d77c0a2fd5edabdfe2fc0d81a8e67e740))

- Update controls
  ([`0bc615a`](https://github.com/fhempy/fhempy/commit/0bc615ad8c0ecf7b1fb688f7442ef7bbe0d66035))

- Update controls
  ([`6ec971d`](https://github.com/fhempy/fhempy/commit/6ec971dae7734d12e1e0c6039e50f6644b32fac2))

- Update controls
  ([`d8090e5`](https://github.com/fhempy/fhempy/commit/d8090e537d64044041139ba0aad662d388eb7069))

- Update controls
  ([`c7f17ce`](https://github.com/fhempy/fhempy/commit/c7f17ce64b9e4c240f92cdd044b2515365a7c96f))

- Update controls
  ([`bb837c0`](https://github.com/fhempy/fhempy/commit/bb837c03fc5d407c5a4d50b2dc1d40c2c161c2d0))

- Update controls
  ([`0bc3efa`](https://github.com/fhempy/fhempy/commit/0bc3efa064042e973b8bea2d64aef6cd0163288c))

- Update controls
  ([`bb49b66`](https://github.com/fhempy/fhempy/commit/bb49b663ce3e6230ac5763beab46dd159bb66d0c))

- Update controls
  ([`bf282e5`](https://github.com/fhempy/fhempy/commit/bf282e5cdeffee690284bbc0d3c8bb98b76058ca))

- Update controls
  ([`ac19ade`](https://github.com/fhempy/fhempy/commit/ac19ade79e56e4b29ebd16d3672e374727321617))

- Update controls
  ([`b348a81`](https://github.com/fhempy/fhempy/commit/b348a8147e7362c287270fbe138d696842d8e337))

- Update controls
  ([`1b6f060`](https://github.com/fhempy/fhempy/commit/1b6f060c832f6d380258d4afbf0c607378cafc84))

- Update controls
  ([`c96979b`](https://github.com/fhempy/fhempy/commit/c96979b931abbee09ba3b555a6b0d7f9df2ec80b))

- Update controls
  ([`35278ff`](https://github.com/fhempy/fhempy/commit/35278ff0aac1b5169adaf27af498dcaad391e23c))

- Update controls
  ([`efe8030`](https://github.com/fhempy/fhempy/commit/efe8030c9424ca89c96187d81007cc3162c9224f))

- Update controls
  ([`929d536`](https://github.com/fhempy/fhempy/commit/929d536164930eee659cec387c7dbd2763a37af8))

- Update controls
  ([`832bc6e`](https://github.com/fhempy/fhempy/commit/832bc6ebacca6dc2b5282ca938f9251468467b58))

- Update controls
  ([`0262d7c`](https://github.com/fhempy/fhempy/commit/0262d7cc8a27bbe149cb6a8bdae79c21b94e12a0))

- Update controls
  ([`5fb112d`](https://github.com/fhempy/fhempy/commit/5fb112d732356c546bccd88525c93d76307cd496))

- Update controls
  ([`15e9c53`](https://github.com/fhempy/fhempy/commit/15e9c53e88d778b82ffcd6cfdd77f7996cffc749))

- Update controls
  ([`962df60`](https://github.com/fhempy/fhempy/commit/962df601d9d4a57bf900bbd1015a336b550d1cdc))

- Update controls
  ([`d01a9b8`](https://github.com/fhempy/fhempy/commit/d01a9b8c874a2aab2ddb59321e382e657b66dcdb))

- Update controls
  ([`7ca1a09`](https://github.com/fhempy/fhempy/commit/7ca1a0975bd0c4713f01738b0dac2ec20f247994))

- Update controls
  ([`11cf452`](https://github.com/fhempy/fhempy/commit/11cf45276fbaf06b02c5115e6539a0c8f3b6598c))

- Update controls
  ([`725f580`](https://github.com/fhempy/fhempy/commit/725f580c404375fd02262b97ffb833c085faf8c7))

- Update controls
  ([`1b463bf`](https://github.com/fhempy/fhempy/commit/1b463bf0ef572e8635211476bc5c2cf9bef0633c))

- Update controls
  ([`e28ae40`](https://github.com/fhempy/fhempy/commit/e28ae40aab04f5318d7e1f1d99c16a18160d120b))

- Update controls
  ([`1be3fc0`](https://github.com/fhempy/fhempy/commit/1be3fc0f145ca812585813b7f26c9b81f16c4fc3))

- Update controls
  ([`17fad34`](https://github.com/fhempy/fhempy/commit/17fad34f9398c35a944199c52674f6c0e55d514f))

- Update controls
  ([`3d5f8eb`](https://github.com/fhempy/fhempy/commit/3d5f8ebcda4022895f72d6e5c1e7431e00494c02))

- Update controls
  ([`5de3350`](https://github.com/fhempy/fhempy/commit/5de33500bd4245629f0615df30ce0083dc042f12))

- Update controls
  ([`10ca462`](https://github.com/fhempy/fhempy/commit/10ca462df34df0d271dc080b60801b5b05d634d3))

- Update controls
  ([`2252342`](https://github.com/fhempy/fhempy/commit/22523425d024d920676128432e0d848601efa2c4))

- Update controls
  ([`ca2938d`](https://github.com/fhempy/fhempy/commit/ca2938dafbb73256af8d0230bf399e2a97610ad6))

- Update controls
  ([`e3c76f4`](https://github.com/fhempy/fhempy/commit/e3c76f44b10936d097dc1e2e0fcb02bccd0e8b00))

- Update controls
  ([`a772c14`](https://github.com/fhempy/fhempy/commit/a772c14ea08151ca04c66cdc9814f3cf1d6c164f))

- Update controls
  ([`0e7c318`](https://github.com/fhempy/fhempy/commit/0e7c318eb8c6b178d0eee7c6a308341222abf236))

- Update controls
  ([`ebd668b`](https://github.com/fhempy/fhempy/commit/ebd668bb9f7158148158774653471cd7041db0b3))

- Update controls
  ([`d5835a7`](https://github.com/fhempy/fhempy/commit/d5835a76a3da70035797393864d95a104bc39bfb))

- Update controls
  ([`bb0f4cc`](https://github.com/fhempy/fhempy/commit/bb0f4cc2d29a7a823da3cf621ba537f364211d9d))

- Update controls
  ([`b070894`](https://github.com/fhempy/fhempy/commit/b070894f583c0e6ec7fec05df095fe1088abedec))

- Update controls
  ([`9f86a91`](https://github.com/fhempy/fhempy/commit/9f86a91718935eed54bf7bfac7decc8c39862d89))

- Update controls
  ([`ff44704`](https://github.com/fhempy/fhempy/commit/ff447044d08e731a06292e2dfb7ed0e49b2d82f7))

- Update controls
  ([`9d0964b`](https://github.com/fhempy/fhempy/commit/9d0964b56601c82098fcd629fa0180b73506242d))

- Update controls
  ([`c89bb9c`](https://github.com/fhempy/fhempy/commit/c89bb9c1ccc3c856a1f98f97d2ff1e5195dcf855))

### Features

- **esphome**: Attr port_dashboard
  ([`c52fa7a`](https://github.com/fhempy/fhempy/commit/c52fa7aa7f50bf195803c4b81435832c391c9d7c))

- **fhempy**: Add sentry logging
  ([`4d3cab6`](https://github.com/fhempy/fhempy/commit/4d3cab6a833d21fcb87136550e00b5bd96fffdb6))

- **fhempy**: Support "all" notification in ble
  ([`ea1f5eb`](https://github.com/fhempy/fhempy/commit/ea1f5ebb0d40f5b3efdde39e04d38fd1350a8302))

- **fhempy**: Support iodev select in attr
  ([`3f64c63`](https://github.com/fhempy/fhempy/commit/3f64c633721cee69d9d4042e6a941ae6f97a8895))

- **meross**: Support rgb,bri,ct
  ([`a23f34d`](https://github.com/fhempy/fhempy/commit/a23f34ddb496feba162f51542a6c1f66af26b62b))

- **nefit**: Add outdoor temperature
  ([`ecaadb1`](https://github.com/fhempy/fhempy/commit/ecaadb159dad75b96ea13d1149ca893b588af922))

- **nefit**: Retrieve dayassunday
  ([`8462ba4`](https://github.com/fhempy/fhempy/commit/8462ba421fc30c793b178d4f7b0ea7509f794dbf))

- **nefit**: Support dayassunday set functions
  ([`0ed99f2`](https://github.com/fhempy/fhempy/commit/0ed99f2ddb49d03bf1112efa50684d01c6e2afea))

- **nefit**: Support nefit devices
  ([`ea41aa8`](https://github.com/fhempy/fhempy/commit/ea41aa8d608e19a11c61fafae0c708f9fb7df140))

- **xiaomi_gateway3**: Support non xiaomi zigbee
  ([`be74c22`](https://github.com/fhempy/fhempy/commit/be74c22428b890bf30650f0031eba02bd7507bc9))

- **xiaomi_gateway3**: Support zigbee2mqtt
  ([`3829860`](https://github.com/fhempy/fhempy/commit/3829860d8cdf9ace4b181b3769579874d62eee43))

- **xiaomi_gateway3**: Update to 1.6.0rc2 xgw3 lib
  ([`bcf7f8d`](https://github.com/fhempy/fhempy/commit/bcf7f8d9d303efadafc5f33c0166b5d38fa575c0))


## v0.1.153 (2021-10-23)

### Bug Fixes

- **eq3bt**: Fix circular import
  ([`0ffe738`](https://github.com/fhempy/fhempy/commit/0ffe7383c645ceecfa7d4411437a8f009245e9a9))

- **esphome**: Fix path again
  ([`d35b0af`](https://github.com/fhempy/fhempy/commit/d35b0af64b8a2603385f9bc499c40fd549d18c89))

- **esphome**: Fix weblink creation
  ([`60ebbcf`](https://github.com/fhempy/fhempy/commit/60ebbcf2896802410dd5b1f8c2b6d96cef2bddae))

- **esphome**: Fix weblink creation (2)
  ([`3df3ec0`](https://github.com/fhempy/fhempy/commit/3df3ec013400939ce17a6ba1883ef8eff256a964))

- **esphome**: Revert path change
  ([`7452ebb`](https://github.com/fhempy/fhempy/commit/7452ebb20fa012bda4a6a52bc955e20cf7dd24b1))

- **esphome**: Set path for esphome
  ([`5b80c65`](https://github.com/fhempy/fhempy/commit/5b80c65b4ffcb3acbeca3dff2725f980b2cfa34d))

- **esphome**: Update library
  ([`56af685`](https://github.com/fhempy/fhempy/commit/56af685dba0cf25c362a3dd320acc8ae795695e4))

- **fhempy**: Better logging
  ([`d35fff7`](https://github.com/fhempy/fhempy/commit/d35fff7c6bf35197ddb0e0323d10e9029dd0fab7))

- **fhempy**: Better logging
  ([`38337ea`](https://github.com/fhempy/fhempy/commit/38337ea15575c56cc3cb3d4edad2e6050e1413f3))

- **fhempy**: Do not use legacy websockets
  ([`c5ea3c1`](https://github.com/fhempy/fhempy/commit/c5ea3c1e1969058a03f71314598491477c5f4b79))

- **fhempy**: Fix circular imports
  ([`6feb2e9`](https://github.com/fhempy/fhempy/commit/6feb2e9641f0122402f6840030fc1b0a41d7b1ef))

- **fhempy**: Fix fhem help
  ([`220bf15`](https://github.com/fhempy/fhempy/commit/220bf1544dee7103dc40b5afdc6bd0f93d945ee0))

- **fhempy**: Fix fhempyServer module
  ([`c969a27`](https://github.com/fhempy/fhempy/commit/c969a279c2ee1ba0b60afac96091695d72d9a243))

- **fhempy**: Make installation easier on debian 11
  ([`6857d47`](https://github.com/fhempy/fhempy/commit/6857d475dd67cba27fdf074949e87741fadcc4e2))

- **fhempy**: Reducing >100ms "blocking"
  ([`a4d2799`](https://github.com/fhempy/fhempy/commit/a4d27996c83ae197145b5ebd1dbcace3f90b2471))

- **fhempy**: Revert websockets change
  ([`4c4bf7e`](https://github.com/fhempy/fhempy/commit/4c4bf7e27f286cf1f794a0b4c41f142b7de95612))

- **googlecast**: Fix circular import
  ([`6d705de`](https://github.com/fhempy/fhempy/commit/6d705def909adef171a8d461d10ea5cbf9a44a8a))

- **meross**: Fix garage readings
  ([`b65e004`](https://github.com/fhempy/fhempy/commit/b65e004ad9942063cc6d24eefcec6e4292a1e7ea))

- **meross**: Fix open/close
  ([`63e25bd`](https://github.com/fhempy/fhempy/commit/63e25bdda3adcb54ee75109601a52e0fee3219b4))

- **tuya_cloud**: Change info to debug
  ([`55b5ed5`](https://github.com/fhempy/fhempy/commit/55b5ed5aea41c94fc97ab5ac6edd6692c98415bf))

- **xiaomi_gateway3**: Fix circular import
  ([`d9402b9`](https://github.com/fhempy/fhempy/commit/d9402b9e4d3554ac15532351e15b684f081f42ca))

- **xiaomi_gateway3**: Update readme
  ([`541d941`](https://github.com/fhempy/fhempy/commit/541d941f5f0a08b9c5e5f04e2bd3dba4e41e3a6f))

### Chores

- Add markdown
  ([`58a0e45`](https://github.com/fhempy/fhempy/commit/58a0e455e4d5baa754a66ff20f8eb7f1ca11739c))

- Update controls
  ([`7b8532e`](https://github.com/fhempy/fhempy/commit/7b8532e4926c960dc96203a6dba6b6a38a377032))

- Update controls
  ([`cd92aa5`](https://github.com/fhempy/fhempy/commit/cd92aa54dd0255fc70003e4b494c262712d87f33))

- Update controls
  ([`5465581`](https://github.com/fhempy/fhempy/commit/5465581ff9bef8af7f751e08c6e0107450601085))

- Update controls
  ([`10df7d2`](https://github.com/fhempy/fhempy/commit/10df7d2a67e4726640c272b012757652cfc7825d))

- Update controls
  ([`772c654`](https://github.com/fhempy/fhempy/commit/772c654a5c24a97f5f272f1f7509c5d9426aba38))

- Update controls
  ([`7636dc2`](https://github.com/fhempy/fhempy/commit/7636dc2b30b759867958aa7ee20b46ac9d71d7f7))

- Update controls
  ([`9a95963`](https://github.com/fhempy/fhempy/commit/9a9596356caac7fbb5a614b4c9c6d173326f5725))

- Update controls
  ([`4d8be12`](https://github.com/fhempy/fhempy/commit/4d8be12a366332383a06bb09c599d7c3d10d58df))

- Update controls
  ([`7647557`](https://github.com/fhempy/fhempy/commit/764755777c26bc5161bd535ca8c236acfe88f84d))

- Update controls
  ([`249c4c0`](https://github.com/fhempy/fhempy/commit/249c4c0e3b005f5800f0accd62a7b2dca0df0525))

- Update controls
  ([`eb6d5aa`](https://github.com/fhempy/fhempy/commit/eb6d5aa61185320dce534e9cfc51d111daf8085d))

- Update controls
  ([`9b6a2df`](https://github.com/fhempy/fhempy/commit/9b6a2dfe95e5fb052bcae95debebaa410d0a722f))

- Update controls
  ([`e42e8e3`](https://github.com/fhempy/fhempy/commit/e42e8e38c44cfdbe69fdc8e15fd635783291b438))

- Update controls
  ([`fe7303d`](https://github.com/fhempy/fhempy/commit/fe7303df768fa542c04470a551fa26d4d5ca2650))

- Update controls
  ([`841f3ce`](https://github.com/fhempy/fhempy/commit/841f3ce04a7fda8444b4869dfd48b5534256a741))

- Update controls
  ([`493f86d`](https://github.com/fhempy/fhempy/commit/493f86dc2788a4a94317e4bb9387a381656d94d4))

### Features

- **erelax_vaillant**: Add duration for temp
  ([`d96f897`](https://github.com/fhempy/fhempy/commit/d96f897a18b29bb03af3838869b710aa996968ae))

- **esphome**: Add install link
  ([`6a22557`](https://github.com/fhempy/fhempy/commit/6a225570b39d201f670061cbe96b288ad0fdd99b))

- **fhempy**: Use readme as help in fhem
  ([`faf245f`](https://github.com/fhempy/fhempy/commit/faf245f403af6da5d752a2ebce248bb2d3d0c212))

- **meross**: Support garage opener
  ([`dd4136e`](https://github.com/fhempy/fhempy/commit/dd4136e3ded61788242771ddd70fe37cfaff2e8e))


## v0.1.137 (2021-10-12)

### Bug Fixes

- **BindingsIo**: Fix possible 100% cpu bug
  ([`947a90e`](https://github.com/fhempy/fhempy/commit/947a90e472034186656128676ba7d16f728950b3))

- **discover_mdns**: Use async zeroconf
  ([`6ad6445`](https://github.com/fhempy/fhempy/commit/6ad6445e202e5cbe0a486b2701a775b6b32d599d))

- **dlna_dmr**: Fix get_local_ip
  ([`e12f602`](https://github.com/fhempy/fhempy/commit/e12f60233cb5bd703d091a47bc21a3261d926331))

- **erelax_vaillant**: Fix away/manual readings
  ([`ab0cc0c`](https://github.com/fhempy/fhempy/commit/ab0cc0ca69a24b66dbef4ff7343f11297588425f))

- **erelax_vaillant**: Fix away/manual readings
  ([`31dfb46`](https://github.com/fhempy/fhempy/commit/31dfb464fc2a79121cbe0ea89a2e890954244f5c))

- **erelax_vaillant**: Fix readings again
  ([`4fcb9d2`](https://github.com/fhempy/fhempy/commit/4fcb9d24c6deadbc1b622dc7dd9df4d26a6be645))

- **erelax_vaillant**: Set endtime 0 if not active
  ([`9103634`](https://github.com/fhempy/fhempy/commit/91036349b24ded901051833a79aecf920af23f0f))

- **esphome**: Fix deprecation warning
  ([`49af229`](https://github.com/fhempy/fhempy/commit/49af2290a0527370857292c23bc51b9a9a522b2f))

- **esphome**: Fix restart
  ([`be47a72`](https://github.com/fhempy/fhempy/commit/be47a7221fc1814c091992393652c4c767a8b203))

- **fhempy**: Add 3.8,3.9 tests
  ([`d06989d`](https://github.com/fhempy/fhempy/commit/d06989d3bd9aa713cb8eea87c163aa9471be0ae0))

- **fhempy**: Add debug output
  ([`3b09a35`](https://github.com/fhempy/fhempy/commit/3b09a351db8851dfc5b34b684768d093e1a8ba45))

- **fhempy**: Add exception handling
  ([`bcaaf97`](https://github.com/fhempy/fhempy/commit/bcaaf970f4b0f2e239bba52fe7c136f92c95218c))

- **fhempy**: Add use Color
  ([`89c8264`](https://github.com/fhempy/fhempy/commit/89c8264adab1a2d788d73c0e1caaa438aa7af850))

- **fhempy**: Better error handling
  ([`5910b6a`](https://github.com/fhempy/fhempy/commit/5910b6ae1fe3a6ea2e2cb97cdcf45ba782a25024))

- **fhempy**: Better error handling
  ([`e4f2ba2`](https://github.com/fhempy/fhempy/commit/e4f2ba2a2d1c46b9bc767119ff4f4519e61ce724))

- **fhempy**: Change log name to fhempy
  ([`ce8fac5`](https://github.com/fhempy/fhempy/commit/ce8fac5e3faa8fa8db360d787dc481288ba045f0))

- **fhempy**: Change logfile name to fhempy
  ([`2dc88df`](https://github.com/fhempy/fhempy/commit/2dc88df1177c69990926d5e55852656ee365f666))

- **fhempy**: Fix cryptography installation
  ([`a7b4b6e`](https://github.com/fhempy/fhempy/commit/a7b4b6e5a5357f6b409656f4f79d99ce1b6154a3))

- **fhempy**: Fix github sec alert
  ([`6be1403`](https://github.com/fhempy/fhempy/commit/6be14039106babb653faa048336827e1719533bb))

- **fhempy**: Fix log
  ([`d3d11c4`](https://github.com/fhempy/fhempy/commit/d3d11c440c107fa21a871e331c7834add1e820ad))

- **fhempy**: Fix no response
  ([`a2656a0`](https://github.com/fhempy/fhempy/commit/a2656a0e0c00260e299e0593751fd22f503d67bc))

- **fhempy**: Fix NO RESPONSE msgs
  ([`3413202`](https://github.com/fhempy/fhempy/commit/341320259b85f2d545c62cf898c060025181db5a))

- **fhempy**: Fix possible crash on reconnect
  ([`d68d60b`](https://github.com/fhempy/fhempy/commit/d68d60bcf9f52c145ad6be221fb6a7fe7388ee03))

- **fhempy**: Fix pythontype handling
  ([`8c43843`](https://github.com/fhempy/fhempy/commit/8c4384324501b03fdbeb712bacf0ca1fa773800f))

- **fhempy**: Fix release script
  ([`de82f89`](https://github.com/fhempy/fhempy/commit/de82f891c300feda26bc35168119293a520991f6))

- **fhempy**: Fix room for fhempy log
  ([`9662148`](https://github.com/fhempy/fhempy/commit/966214849c577e085dd3e796bb4ba71a7367a721))

- **fhempy**: Fix shutdown after update
  ([`3d7d556`](https://github.com/fhempy/fhempy/commit/3d7d5569ee5416e08ed793791a55b5d3e15531d8))

- **fhempy**: Fix tests
  ([`8cd8c71`](https://github.com/fhempy/fhempy/commit/8cd8c7116eab1c0e53f55413c4e82bacb7eaa324))

- **fhempy**: Fix tests
  ([`b1e68a8`](https://github.com/fhempy/fhempy/commit/b1e68a88ff25565a63c89b45a9a550fd45434d26))

- **fhempy**: Fix tests for 3.7
  ([`c620d09`](https://github.com/fhempy/fhempy/commit/c620d0992acd3e94b309b9bda493e92775abf30f))

- **fhempy**: Fix update
  ([`6f381c1`](https://github.com/fhempy/fhempy/commit/6f381c1be050f3ee26d4cbd236b2e2da447c581f))

- **fhempy**: Fix version
  ([`ed0159d`](https://github.com/fhempy/fhempy/commit/ed0159da60a40da8077cee4cf77855965084062a))

- **fhempy**: Fix zeroconf
  ([`bf048e3`](https://github.com/fhempy/fhempy/commit/bf048e322a58949eef11f305ecf09435b24ebda9))

- **fhempy**: Fix zeroconf exception
  ([`7ad2e73`](https://github.com/fhempy/fhempy/commit/7ad2e73c4140fa99ccac5a9a28fcc094fa890a61))

- **fhempy**: Flake8 fixes
  ([`519658c`](https://github.com/fhempy/fhempy/commit/519658ccbad6ebc9c8eb27f4dc9025913f7fdb4f))

- **fhempy**: Handle zeroconf exceptions
  ([`eebf78f`](https://github.com/fhempy/fhempy/commit/eebf78f761909ded5228cb0e32e99a89bd7cbeab))

- **fhempy**: Log successfull update
  ([`2a3e37f`](https://github.com/fhempy/fhempy/commit/2a3e37f75db9b7277344e8fe0e255f31f1a59f9f))

- **fhempy**: Raise error if pkg install fails
  ([`8b15dcd`](https://github.com/fhempy/fhempy/commit/8b15dcd19180451b45f3de4aa420938334f951d2))

- **fhempy**: Rename to fhempy
  ([`3ee719c`](https://github.com/fhempy/fhempy/commit/3ee719c336ba7ddb834ecd236e4e66961c6cb7d7))

- **fhempy**: Rename to fhempy
  ([`74442ea`](https://github.com/fhempy/fhempy/commit/74442ea9c4c03e748e4734df95ae6c4c93ef72ce))

- **fhempy**: Rename to fhempy
  ([`53c68c0`](https://github.com/fhempy/fhempy/commit/53c68c0f95b584ade1d6283a8208295f8e5038be))

- **fhempy**: Rename to fhempy
  ([`7aac6cb`](https://github.com/fhempy/fhempy/commit/7aac6cb07e8195835c5b28b5227caeaa8b7fa81d))

- **fhempy**: Rename to fhempy
  ([`058ba5f`](https://github.com/fhempy/fhempy/commit/058ba5f385c90a6ae79a27f575fcd90390af4448))

- **fhempy**: Rename to fhempy
  ([`11e8f99`](https://github.com/fhempy/fhempy/commit/11e8f99f033481a4bd44e58007831d9036d823f2))

- **fhempy**: Rename to fhempy
  ([`38121ce`](https://github.com/fhempy/fhempy/commit/38121ce24260cf4dfd8291901c760008d6ee48e8))

- **fhempy**: Update aiohttp library
  ([`f00540a`](https://github.com/fhempy/fhempy/commit/f00540abbc6daf6c8b8ba81772c3bef6769499fd))

- **fhempy**: Update cryptography
  ([`b154eb6`](https://github.com/fhempy/fhempy/commit/b154eb6b592cb672dbaabefc45b37e11ef304bce))

- **fhempy**: Update requirements
  ([`3dd10df`](https://github.com/fhempy/fhempy/commit/3dd10dfa1e86c88c3b68aa1b8a3d89f15aaf553b))

- **fhempy**: Update requirements
  ([`f327a5a`](https://github.com/fhempy/fhempy/commit/f327a5a5e5abd3393c336743a376618d5136176a))

- **fhempy**: Update requirements
  ([`02de53d`](https://github.com/fhempy/fhempy/commit/02de53de90b910c9a00a16267961869e5848ee41))

- **fhempy**: Update zeroconf lib
  ([`40eefeb`](https://github.com/fhempy/fhempy/commit/40eefebec873f5ebba506bbd0aa9bb47f73db44c))

- **googlecast**: Fix spotify play
  ([`08ea929`](https://github.com/fhempy/fhempy/commit/08ea929003d6966c587aed433f6fefbe70e13cdf))

- **googlecast**: Fix spotify, add speak_lang attr
  ([`6a81f15`](https://github.com/fhempy/fhempy/commit/6a81f15dbce5d2b57489b1c0cffec88fe5653c53))

- **googlecast**: Remove spotify_token dependency
  ([`ab8f872`](https://github.com/fhempy/fhempy/commit/ab8f8726158eb7037a62e98517a61b2760fbc47f))

- **meross**: Add usage
  ([`ccd7a4c`](https://github.com/fhempy/fhempy/commit/ccd7a4cd9b84573fbc472a024c0e1854fb509038))

- **miflora**: Fix deadlocks
  ([`21810f8`](https://github.com/fhempy/fhempy/commit/21810f8f6680186b329db31e5a6de8fc0010b0aa))

- **miio**: Update miio lib
  ([`32cbc78`](https://github.com/fhempy/fhempy/commit/32cbc78d21326edc760425c32727ddea5f7a380b))

- **mitemp**: Latest mitemp lib not working
  ([`9e2dcfc`](https://github.com/fhempy/fhempy/commit/9e2dcfc092d9102248bc8b4ef28c340505d5fc46))

- **mitemp**: Update library
  ([`6919917`](https://github.com/fhempy/fhempy/commit/691991759cbc9909ede6aa44b23c030d9350d234))

- **object_detection**: Fix image detection
  ([`cc5c8de`](https://github.com/fhempy/fhempy/commit/cc5c8defa3457d5a60d812c062623654ed3b0e9e))

- **object_detection**: Update lib
  ([`8273a31`](https://github.com/fhempy/fhempy/commit/8273a314ed001c7b54ff324f3831be389bc09e1d))

- **ring**: Fix battery/volume updates
  ([`936cc49`](https://github.com/fhempy/fhempy/commit/936cc495c86040d13fc34e11668daf6d32967aa1))

- **ring**: Fix ring auth
  ([`ebc454d`](https://github.com/fhempy/fhempy/commit/ebc454d5302b3f9356b9d54efab6d76f833c5d35))

- **ring**: Fix update_health_data
  ([`747a129`](https://github.com/fhempy/fhempy/commit/747a12996a9b2552256fe0492086150c94586e5d))

- **ring**: Revert ring_doorbell lib to 0.6.2
  ([`71b9511`](https://github.com/fhempy/fhempy/commit/71b9511e47751eb93e2365f0861918aabfe738cd))

- **skodaconnect**: Climatisation fix
  ([`8f2bc7d`](https://github.com/fhempy/fhempy/commit/8f2bc7da3d0767897d31269a5fba91e2c3854f0c))

- **skodaconnect**: Fix climater with new library
  ([`bdc8058`](https://github.com/fhempy/fhempy/commit/bdc8058c2d759454e6919b16d04aa36238de1d2e))

- **skodaconnect**: Fix climatisation
  ([`1870427`](https://github.com/fhempy/fhempy/commit/18704278f393203e487899b79ca6fe2b7b065745))

- **skodaconnect**: Fix climatisation
  ([`527214f`](https://github.com/fhempy/fhempy/commit/527214fa5be15a7ba52b726472f1900b43262f61))

- **skodaconnect**: Fix typo auxiliary
  ([`9455fc2`](https://github.com/fhempy/fhempy/commit/9455fc2b8fd66c329f4eb3e30b67e9fabd31cee6))

- **skodaconnect**: Fix update readings ([#21](https://github.com/fhempy/fhempy/pull/21),
  [`cd0aef9`](https://github.com/fhempy/fhempy/commit/cd0aef9dec0350570b9b6667e356db53216e631e))

Fix Error: Traceback (most recent call last): File
  "/opt/fhem/.local/lib/python3.7/site-packages/fhempy/lib/skodaconnect/skodaconnect.py", line 243,
  in update_readings_once if self._update_readings == "always": AttributeError: 'skodaconnect'
  object has no attribute '_update_readings'

- **skodaconnect**: Fix update_interval/_readings
  ([`8ee0686`](https://github.com/fhempy/fhempy/commit/8ee0686595e22337b0f5bf8c17720ec09a3a33a8))

- **skodaconnect**: Update lib to 1.1.2
  ([`a012022`](https://github.com/fhempy/fhempy/commit/a012022ae7ccb7c746df448d0b99975251fa25ce))

- **skodaconnect**: Update lib to 1.1.3
  ([`ae47357`](https://github.com/fhempy/fhempy/commit/ae4735782c9d15a7a408de965b27bcdb422c1d23))

- **skodaconnect**: Update lib to 1.1.4
  ([`192c4f3`](https://github.com/fhempy/fhempy/commit/192c4f3ac70b1b2ee33298f8d23d3aba7b025e79))

update to latest lib with fix honkandflash and turn pheater off

- **skodaconnect**: Update library
  ([`dc2035b`](https://github.com/fhempy/fhempy/commit/dc2035bb80810343eae441279ce52d1d1eddbbea))

- **skodaconnect**: Update library to 1.0.52
  ([`f14583e`](https://github.com/fhempy/fhempy/commit/f14583ef3b6beb5032064aeb016fe0966238cbe8))

- **spotify**: Change auth url
  ([`63319ba`](https://github.com/fhempy/fhempy/commit/63319bad78301caae4b0273745e459969fcf308f))

- **spotify**: Fix deprecation warning
  ([`a852b75`](https://github.com/fhempy/fhempy/commit/a852b75cd13a06ae90ad8b004225fb04014b0b45))

- **spotify_connect_player**: Fix deprecation warn
  ([`e9bc04b`](https://github.com/fhempy/fhempy/commit/e9bc04bc61cf439b12e6ad4b5101ca57f1bab2e6))

- **tests**: Fix ring test
  ([`9098245`](https://github.com/fhempy/fhempy/commit/90982456484aec502ceeefe08c3a4be9e0ff9db4))

- **tests**: Fix update test
  ([`b170df1`](https://github.com/fhempy/fhempy/commit/b170df1cfb06185c83aad5aa8a8c05aa183d89c9))

- **tuya**: Create unknown devices
  ([`3a57f5b`](https://github.com/fhempy/fhempy/commit/3a57f5bb5bbd3697ad19e8d58a0cff5da9267ad2))

- **tuya**: Fix attributes
  ([`1bd998e`](https://github.com/fhempy/fhempy/commit/1bd998e478ff6e278b889169baeb89d0493031cb))

- **tuya_cloud**: Better error handling
  ([`056ab5c`](https://github.com/fhempy/fhempy/commit/056ab5c4c5583f490c17b7d007b347f1d08ca2a4))

- **tuya_cloud**: Fix again colour_data
  ([`82998c7`](https://github.com/fhempy/fhempy/commit/82998c757357c9c9aee4fbc0b7c83ac8d9170cfb))

- **tuya_cloud**: Fix autocreation of new devices
  ([`80607f2`](https://github.com/fhempy/fhempy/commit/80607f2c566e6cf548e3eee786cc00df516e50ec))

- **tuya_cloud**: Fix colour_data
  ([`c87c985`](https://github.com/fhempy/fhempy/commit/c87c9857c67b164cca75f87f5ff2b28fc284b5ac))

- **tuya_cloud**: Fix colour_data
  ([`b46189c`](https://github.com/fhempy/fhempy/commit/b46189c60d0f0e58797b2dd0e8024ddfd97a66f8))

- **tuya_cloud**: Fix colour_data again
  ([`fd37524`](https://github.com/fhempy/fhempy/commit/fd37524f94bc30667b75849b1933e223d92df361))

- **tuya_cloud**: Fix default code for state
  ([`deedac5`](https://github.com/fhempy/fhempy/commit/deedac5f4853c92d3d79b6848b89542134dfdaf0))

- **tuya_cloud**: Fix devnames with dashes
  ([`54e2f7c`](https://github.com/fhempy/fhempy/commit/54e2f7cb1de5f8bc844eb18f4332fbbbb8c7151d))

- **tuya_cloud**: Fix reading updates
  ([`572c088`](https://github.com/fhempy/fhempy/commit/572c0880747a8535f9092f87cc12ee91e0910f6c))

- **tuya_cloud**: Fix reading updates
  ([`54a1259`](https://github.com/fhempy/fhempy/commit/54a12595ec52bb6bb13a6619a77e26d16b161654))

- **tuya_cloud**: Fix readings for unsupported devs
  ([`8dea541`](https://github.com/fhempy/fhempy/commit/8dea541efce093b80eb187a051d00fc1051f55a0))

- **tuya_cloud**: Fix reset_reading
  ([`48410ec`](https://github.com/fhempy/fhempy/commit/48410ecfbe89b1c0310e83c4676c9407900551ad))

- **tuya_cloud**: Fix rgb readings
  ([`5257ff2`](https://github.com/fhempy/fhempy/commit/5257ff2428219e75767b4f756734d7dbf1982bbf))

- **tuya_cloud**: Fix set_json
  ([`246584f`](https://github.com/fhempy/fhempy/commit/246584fc1fd7adc6d4743e6dc9be9c43c8a28498))

- **tuya_cloud**: Fix startup issues
  ([`a9c2e99`](https://github.com/fhempy/fhempy/commit/a9c2e99db2fd0730b95bb3a1dab5e8f853753ec1))

- **tuya_cloud**: Fix switch
  ([`d1d1e03`](https://github.com/fhempy/fhempy/commit/d1d1e03f629985175a0bae88f797f5cc49ab1b0d))

- **tuya_cloud**: Fix tuya lib version
  ([`9cb101e`](https://github.com/fhempy/fhempy/commit/9cb101e9ba9812e5060039eebb105e4f95855385))

- **tuya_cloud**: Handle exception on mqtt stop
  ([`de40876`](https://github.com/fhempy/fhempy/commit/de4087678f95429e9c86bf4ee3cd767f6836a326))

- **tuya_cloud**: Handle stop() exceptions
  ([`8bb081a`](https://github.com/fhempy/fhempy/commit/8bb081aa46f55a98a3900fc062b77fdd8369c16f))

- **tuya_cloud**: Handle unsupported devices
  ([`0c224bd`](https://github.com/fhempy/fhempy/commit/0c224bd5d05825c6da004890574640442df6566c))

- **tuya_cloud**: One more fix
  ([`4a8dc19`](https://github.com/fhempy/fhempy/commit/4a8dc199c0fbb5ea99105e7ee47e0c83a0acbc96))

- **tuya_cloud**: Some fixes
  ([`357ddf1`](https://github.com/fhempy/fhempy/commit/357ddf1299a123e28c3b18571b64ced5da2aeac4))

- **tuya_cloud**: Support devices with umlauts
  ([`df937dc`](https://github.com/fhempy/fhempy/commit/df937dc0c9298ac0dea0a795510ea14330b0b2d9))

- **tuya_cloud**: Update tuya lib
  ([`8059a68`](https://github.com/fhempy/fhempy/commit/8059a68023c693e0035bd163cdb6a393a53a63d4))

- **xiaomi_gateway3**: Fix attr usage
  ([`eb1f4b1`](https://github.com/fhempy/fhempy/commit/eb1f4b180944d28697fd49a0c4b7be5730d9e326))

- **xiaomi_gateway3**: Fix gateway device
  ([`24f0b13`](https://github.com/fhempy/fhempy/commit/24f0b13aa29f557ec3ccee32e78c18fc03a619ef))

- **xiaomi_gateway3**: Fix motion sensor reset
  ([`37222fc`](https://github.com/fhempy/fhempy/commit/37222fcd1d52c09cb97ba5943d939436c40d56a8))

- **xiaomi_gateway3**: Fix reading updates
  ([`d8a7ff0`](https://github.com/fhempy/fhempy/commit/d8a7ff04545b8411c0692df3f5d42cf44f14bec8))

- **xiaomi_gateway3**: Fix temp symbol
  ([`b033d42`](https://github.com/fhempy/fhempy/commit/b033d421c0634375fda99512b91e99b5dcb9e27c))

- **xiaomi_gateway3**: Remove added_device reading
  ([`700e361`](https://github.com/fhempy/fhempy/commit/700e361417c9fc4ea634874b2f447396657c85fc))

- **xiaomi_gateway3**: Small fixes
  ([`d96bbc8`](https://github.com/fhempy/fhempy/commit/d96bbc849c24fb275e8bc3e3f3b0095f81464ccc))

- **xiaomi_gateway3**: Sort imports
  ([`89c14bc`](https://github.com/fhempy/fhempy/commit/89c14bc1477a91be51c86a80666f12e94430cb04))

- **xiaomi_tokens**: Fix create miio device
  ([`f8e4352`](https://github.com/fhempy/fhempy/commit/f8e43525f62f00939f60d0ee30349246203682db))

- **xiaomi_tokens**: Fix device creation
  ([`ebbc3bb`](https://github.com/fhempy/fhempy/commit/ebbc3bb61f20fba4ff8d1eadd1af61017abe956e))

- **xiaomi_tokens**: Make readings country specific
  ([`efe1b7a`](https://github.com/fhempy/fhempy/commit/efe1b7a4f37d3530b2f92a906e45f202d67e6d21))

### Chores

- Add git to apt installation
  ([`7139cea`](https://github.com/fhempy/fhempy/commit/7139cea69debcfe74bb06b1b8879169ac363e51b))

- Add relax_vaillant
  ([`5c649c9`](https://github.com/fhempy/fhempy/commit/5c649c9fae3a8bf7ab1466976e9a716079712491))

- Add skodaconnect
  ([`65077a3`](https://github.com/fhempy/fhempy/commit/65077a30a4ab466ad2ae2ff0318bcdccd693dbc2))

- Add tox-gh-actions
  ([`d0072a3`](https://github.com/fhempy/fhempy/commit/d0072a3fbb6415ffc8f3d5da2ca8ee4641dfe562))

- Add tuya_cloud
  ([`b79ce33`](https://github.com/fhempy/fhempy/commit/b79ce33e81877e4a7d4ca80d0d612b15b5af9b76))

- Add tuya_cloud recommandation
  ([`cc8dfb8`](https://github.com/fhempy/fhempy/commit/cc8dfb85a08e052d240ba20cfe8424af42dca529))

- Add update test
  ([`6870fc7`](https://github.com/fhempy/fhempy/commit/6870fc78f2424d24cc8f37c97666745793b80eb9))

- Add warema
  ([`9ed5a7b`](https://github.com/fhempy/fhempy/commit/9ed5a7b9d049eb9aadd6c75e9d804c37b58760de))

- Add xiaomi_gateway3 tests
  ([`46e9e62`](https://github.com/fhempy/fhempy/commit/46e9e62172ab6405130400c617536a9a43d20458))

- Change to tuya cloud
  ([`4416307`](https://github.com/fhempy/fhempy/commit/4416307d60801b46fa8f6f938d85de242fab65db))

- Fix gh actions
  ([`1da180e`](https://github.com/fhempy/fhempy/commit/1da180eeca798da27f8f4369315a54daab61abfc))

- Fix namings
  ([`e6f986b`](https://github.com/fhempy/fhempy/commit/e6f986b38e5f2471b95a2eaeb4ead6646342ea45))

- Fix readme for pypi
  ([`34c8587`](https://github.com/fhempy/fhempy/commit/34c8587fc278b29cdcbd6c042c9d605755a6eedf))

- Fix requirements for dev
  ([`60a6bea`](https://github.com/fhempy/fhempy/commit/60a6beabcdb125e7872dcd1bcad735de9a0756bd))

- Fix staticmethod annotation
  ([`02b11ab`](https://github.com/fhempy/fhempy/commit/02b11abc0fe63d22169e48b9fc3ccb39dd3d9804))

- Gh actions tests
  ([`9d80155`](https://github.com/fhempy/fhempy/commit/9d801556a90a5ea609b0de80907f64a89dbbdd35))

- Install apt deps
  ([`ba7cb89`](https://github.com/fhempy/fhempy/commit/ba7cb89b748647e4e741fd936186716f520f7d61))

- Minor code style changes
  ([`2204f05`](https://github.com/fhempy/fhempy/commit/2204f0575ea3e8f097b2ee70762b9cc5161a794e))

- Remove return
  ([`f62078e`](https://github.com/fhempy/fhempy/commit/f62078e3091b1bfe4401d950c92a9a232ebb9b7c))

- Rename
  ([`81af60c`](https://github.com/fhempy/fhempy/commit/81af60cdefec262cccb1e7d50d7409b600f4155e))

- Run tests only for python 3.7
  ([`a73d685`](https://github.com/fhempy/fhempy/commit/a73d685ccc296d355877bf0abbf04ce5473fa5c0))

- Update controls
  ([`c041fb9`](https://github.com/fhempy/fhempy/commit/c041fb9df4ba93aa36f49c3cfda01ab3053d8372))

- Update controls
  ([`5ddb39d`](https://github.com/fhempy/fhempy/commit/5ddb39d89832deb1ef0048074f9bb07a973adcb6))

- Update controls
  ([`af1f4ee`](https://github.com/fhempy/fhempy/commit/af1f4ee466e069b9db2b1bdb9cb630018792a7f2))

- Update controls
  ([`ee0068a`](https://github.com/fhempy/fhempy/commit/ee0068ad00bc176470559b00aec80540310b2078))

- Update controls
  ([`27c2b9e`](https://github.com/fhempy/fhempy/commit/27c2b9e26b96cb2cd02810cbb02b908cca42c75d))

- Update controls
  ([`55c98f7`](https://github.com/fhempy/fhempy/commit/55c98f7409fef5f8961d67d7812415a6b15618cb))

- Update controls
  ([`8a57e41`](https://github.com/fhempy/fhempy/commit/8a57e4165d2dd0700054121b4eb37c93f655ffa3))

- Update controls
  ([`1cac9ea`](https://github.com/fhempy/fhempy/commit/1cac9ea509bacb31a9cfb6a600edd11c3d6d4adc))

- Update controls
  ([`b633b62`](https://github.com/fhempy/fhempy/commit/b633b622c527cef70e6078ecfc2325fa4ea5d189))

- Update controls
  ([`006eaac`](https://github.com/fhempy/fhempy/commit/006eaac232342f179c2b4c4a1b0746970a74af80))

- Update controls
  ([`c16b02d`](https://github.com/fhempy/fhempy/commit/c16b02d240638078ce1a846b0efc053e229bf6ab))

- Update controls
  ([`71e280d`](https://github.com/fhempy/fhempy/commit/71e280dacebc377218dacb715bf05c0eb60a851a))

- Update controls
  ([`f051427`](https://github.com/fhempy/fhempy/commit/f0514276d6b13b26b12e810cbf75685cd5cfcef4))

- Update controls
  ([`b96b783`](https://github.com/fhempy/fhempy/commit/b96b783e3b5a2f5bcfe125c1c992e5f85aad2248))

- Update controls
  ([`ae0d620`](https://github.com/fhempy/fhempy/commit/ae0d6205e3becbfbc3f089f3ef05cf22e44817d9))

- Update controls
  ([`b1da53f`](https://github.com/fhempy/fhempy/commit/b1da53fa2a253da511bc1289dc8e6e5044cacc95))

- Update controls
  ([`0c970ec`](https://github.com/fhempy/fhempy/commit/0c970ec0ac5af4a86b649f91753e048559834bae))

- Update controls
  ([`909cfe4`](https://github.com/fhempy/fhempy/commit/909cfe4e0d2fbaf40c420bc4024ba97bfe9f0702))

- Update controls
  ([`07ceb34`](https://github.com/fhempy/fhempy/commit/07ceb34f90f46a54e5f8577cd5eaee3fa8440d4a))

- Update controls
  ([`a889cf8`](https://github.com/fhempy/fhempy/commit/a889cf818495a33f19b40888bbd792e5b92e4c0c))

- Update controls
  ([`3cf277c`](https://github.com/fhempy/fhempy/commit/3cf277c3027e510192d0080954e75d45ca4ce662))

- Update controls
  ([`3e66626`](https://github.com/fhempy/fhempy/commit/3e666267244babe388ab8c68da724ebd6b312560))

- Update controls
  ([`df3c3f7`](https://github.com/fhempy/fhempy/commit/df3c3f76be35524603e55ab1865cdba87ba79ee3))

- Update controls
  ([`a140b77`](https://github.com/fhempy/fhempy/commit/a140b77dafe0a1544fa3f7f82029437091cac710))

- Update controls
  ([`2b47dd1`](https://github.com/fhempy/fhempy/commit/2b47dd1bf94babba90b31a680268db0ed4de139c))

- Update controls
  ([`00fb5b1`](https://github.com/fhempy/fhempy/commit/00fb5b1a637895c8f6f7eec0526f2b03b3bed638))

- Update controls
  ([`a7feb25`](https://github.com/fhempy/fhempy/commit/a7feb25a961402c212dfef5235b410e8514689f7))

- Update controls
  ([`29d0eaf`](https://github.com/fhempy/fhempy/commit/29d0eaf2c69244c6c6b5e76387183d3e73481555))

- Update controls
  ([`328c5d1`](https://github.com/fhempy/fhempy/commit/328c5d1643b8bb3e88282952c46a85f2b5f31550))

- Update controls
  ([`71d37e8`](https://github.com/fhempy/fhempy/commit/71d37e8de15ccdb46e68627982e2e1403703d8ad))

- Update controls
  ([`587a6e3`](https://github.com/fhempy/fhempy/commit/587a6e3fafff63c0a4fc5795e2f0e781c6888c74))

- Update controls
  ([`8f04a40`](https://github.com/fhempy/fhempy/commit/8f04a407cb87c273085b4ba9ae79dbd81234cb45))

- Update controls
  ([`26c764e`](https://github.com/fhempy/fhempy/commit/26c764e3c382a81705806f1193bf8569f7e09d14))

- Update controls
  ([`a05fe81`](https://github.com/fhempy/fhempy/commit/a05fe81fdf10b48b4e067aa9282e2109f9c482ad))

- Update controls
  ([`ba92c55`](https://github.com/fhempy/fhempy/commit/ba92c5557d0982d3712e4c24cca634ee6ae3a82e))

- Update controls
  ([`021610c`](https://github.com/fhempy/fhempy/commit/021610cfe8fa38a141db350d623c347d51e3af74))

- Update controls
  ([`94e39c5`](https://github.com/fhempy/fhempy/commit/94e39c5f318ed495bf60c31eb8674746c0541e74))

- Update controls
  ([`1f0f97e`](https://github.com/fhempy/fhempy/commit/1f0f97e2c1f2f554ed5c57da8d6ade1e1415db27))

- Update controls
  ([`f0ca2cd`](https://github.com/fhempy/fhempy/commit/f0ca2cdb1284a09e9efe13436576a5c4ea742c9e))

- Update controls
  ([`ae63614`](https://github.com/fhempy/fhempy/commit/ae636142b92b2a767c5070f905c57dda3e48c0ac))

- Update controls
  ([`2dca780`](https://github.com/fhempy/fhempy/commit/2dca780fa40ef16163aad22c39029dbd2570c9f9))

- Update controls
  ([`c4d1321`](https://github.com/fhempy/fhempy/commit/c4d1321d2c4a7f29f8b16a09e8237d784f38f19e))

- Update controls
  ([`c68b93c`](https://github.com/fhempy/fhempy/commit/c68b93c947910e7ef2216d0206efceb0d956591f))

- Update controls
  ([`554f5c2`](https://github.com/fhempy/fhempy/commit/554f5c225333f0566540a40e7efefb41b5f6beb7))

- Update controls
  ([`3f4ef0f`](https://github.com/fhempy/fhempy/commit/3f4ef0f90f8251830297709dc98f5817fb6e677d))

- Update controls
  ([`6f7a40f`](https://github.com/fhempy/fhempy/commit/6f7a40f6ab34eabc9e452bb5db351099c2d60e2d))

- Update controls
  ([`0f84541`](https://github.com/fhempy/fhempy/commit/0f84541d908494afb67cedd1681f888e6c65d855))

- Update controls
  ([`fe4c0d5`](https://github.com/fhempy/fhempy/commit/fe4c0d54efdc04cfa0ffb820cdbb652f7a96870c))

- Update controls
  ([`3b3a7fa`](https://github.com/fhempy/fhempy/commit/3b3a7faea979ded5d2afcdfeabeb3a6e2a1ad487))

- Update controls
  ([`d2fe795`](https://github.com/fhempy/fhempy/commit/d2fe7951c73e356f3134cb1a147c02a73715d1e3))

- Update controls
  ([`551440b`](https://github.com/fhempy/fhempy/commit/551440bc5f61724584865a6e89505386a491ce58))

- Update controls
  ([`0d7594f`](https://github.com/fhempy/fhempy/commit/0d7594f2e5a94df737357144c79b7043719f59ad))

- Update controls
  ([`10f2b37`](https://github.com/fhempy/fhempy/commit/10f2b37e99ab35a901a3afeaf8473a99aa346c0d))

- Update controls
  ([`171d05f`](https://github.com/fhempy/fhempy/commit/171d05fecdc1000a865aabde9b7b940714d5139c))

- Update controls
  ([`d87c1e7`](https://github.com/fhempy/fhempy/commit/d87c1e7d5f0f7f4d9a26166253bcf01c73b86300))

- Update controls
  ([`dd1e430`](https://github.com/fhempy/fhempy/commit/dd1e430cb1c3b9eb6b03594c055231171fa572e7))

- Update controls
  ([`3d30eed`](https://github.com/fhempy/fhempy/commit/3d30eed4c5e5b3fd2d597164300857a45e690ae2))

- Update controls
  ([`c7ab798`](https://github.com/fhempy/fhempy/commit/c7ab79878365b3908cf1b58a2dc1168a04656b78))

- Update controls
  ([`fc9ede4`](https://github.com/fhempy/fhempy/commit/fc9ede4690e71d8f6e8734e72fb1381d974e12af))

- Update controls
  ([`6b2e046`](https://github.com/fhempy/fhempy/commit/6b2e04674a071b9d78365050368139cc6172548a))

- Update controls
  ([`fdccf32`](https://github.com/fhempy/fhempy/commit/fdccf32c0addb463ac868180ac4e42e4cb659aa2))

- Update controls
  ([`e2afb0b`](https://github.com/fhempy/fhempy/commit/e2afb0b5b32f896b55122f04a9a37123350bd9df))

- Update controls
  ([`e7539eb`](https://github.com/fhempy/fhempy/commit/e7539eb94b90d3962945ff50ec528797ca664236))

- Update controls
  ([`5fa5261`](https://github.com/fhempy/fhempy/commit/5fa5261ef3eacc356199f99f98f93f2f33653aad))

- Update controls
  ([`e07e1eb`](https://github.com/fhempy/fhempy/commit/e07e1ebd306294566af0e1d5d0fbd5592ba22f72))

- Update controls
  ([`1fa7794`](https://github.com/fhempy/fhempy/commit/1fa77942fb22cfce9fcc8a7a2be5e72dca06262b))

- Update controls
  ([`553f64e`](https://github.com/fhempy/fhempy/commit/553f64e96c3c052256d7f16d54f9b4de64b11201))

- Update controls
  ([`f4fc5f4`](https://github.com/fhempy/fhempy/commit/f4fc5f49fade9fa80acb988f738df9e1198e9526))

- Update controls
  ([`2ff9d21`](https://github.com/fhempy/fhempy/commit/2ff9d21905986eef4604da0cea3c27afd1d304a5))

- Update controls
  ([`254443f`](https://github.com/fhempy/fhempy/commit/254443f16c7198238c4eb8ebe3ae704b31bfe2c8))

- Update controls
  ([`cea6119`](https://github.com/fhempy/fhempy/commit/cea6119897f83899144b8bd7f4dc5c70ee64c2a0))

- Update controls
  ([`2aa48be`](https://github.com/fhempy/fhempy/commit/2aa48be75108d6f5b47e5a711ee705c1661cc68a))

- Update controls
  ([`b09ccef`](https://github.com/fhempy/fhempy/commit/b09ccef0c03f44c2230f0c551d08b7f0aa7c5377))

- Update controls
  ([`a3f2dac`](https://github.com/fhempy/fhempy/commit/a3f2dacbe4757113817c9532859438b2484be935))

- Update controls
  ([`030e102`](https://github.com/fhempy/fhempy/commit/030e1021748f8bca186b590063f9566286ad9b6c))

- Update controls
  ([`6c035b7`](https://github.com/fhempy/fhempy/commit/6c035b758ac97092f264c33dd84b7d4ede7c42de))

- Update controls
  ([`276f594`](https://github.com/fhempy/fhempy/commit/276f5947ee63ddab1b43670fa6bf3ce0bb6ccd74))

- Update controls
  ([`b0bd831`](https://github.com/fhempy/fhempy/commit/b0bd8319543ef5c27cd495595a43b9f1e7708f08))

- Update controls
  ([`d139e2f`](https://github.com/fhempy/fhempy/commit/d139e2fb19de73ba0ece4d7b75015a83ce734c0d))

- Update controls
  ([`3e4fb25`](https://github.com/fhempy/fhempy/commit/3e4fb25a4d6f8856139975c3e60c19c84e17140c))

- Update controls
  ([`b43d8de`](https://github.com/fhempy/fhempy/commit/b43d8deb274ac4e32854f375664c44ab25fde808))

- Update controls
  ([`ab3baa1`](https://github.com/fhempy/fhempy/commit/ab3baa187c55b8eddc215646bfe2893eaa2923ff))

- Update controls
  ([`a3427e6`](https://github.com/fhempy/fhempy/commit/a3427e61dec6a8161d62beb4c7d0e5ad62c0a731))

- Update controls
  ([`df19a35`](https://github.com/fhempy/fhempy/commit/df19a35a3a2d9333a2673fe820ca09da941ab9eb))

- Update controls
  ([`f18ff8a`](https://github.com/fhempy/fhempy/commit/f18ff8adab923f2cfd5faaf4b548d527a149146e))

- Update controls
  ([`fb01f45`](https://github.com/fhempy/fhempy/commit/fb01f45d01657d90b73ddf22e11c948e44b5c7d2))

- Update controls
  ([`4cd400e`](https://github.com/fhempy/fhempy/commit/4cd400e1bb574febb9e110445cdee90d7145d59d))

- Update controls
  ([`b79dcf2`](https://github.com/fhempy/fhempy/commit/b79dcf215c29fa7b8a0e031593c2ea5b391befb6))

- Update controls
  ([`4fb08ec`](https://github.com/fhempy/fhempy/commit/4fb08ecd1506e20de15c60ae200597af8c6da870))

- Update controls
  ([`67dfc23`](https://github.com/fhempy/fhempy/commit/67dfc2344c47bb4ad62ecb9d311eb364963cc87a))

- Update controls
  ([`d1c4502`](https://github.com/fhempy/fhempy/commit/d1c4502ba1a0a45c2e2bc3658670ea87944474a2))

- Update controls
  ([`ab7643c`](https://github.com/fhempy/fhempy/commit/ab7643c2060b80d1110a3ab1a2e62bd228552e6d))

- Update controls
  ([`5727798`](https://github.com/fhempy/fhempy/commit/57277988b360b9d7b0ebe6854e0bd0f981e6b93c))

- Update controls
  ([`a3758fa`](https://github.com/fhempy/fhempy/commit/a3758facffb5d145d051c4166ad554bb71036695))

- Update controls
  ([`597ca03`](https://github.com/fhempy/fhempy/commit/597ca037b44cf446d4b23bb0967a7f0ae191a332))

- Update controls
  ([`62a8054`](https://github.com/fhempy/fhempy/commit/62a8054516f582383bc65857067455c60d808d73))

- Update controls
  ([`89b7e07`](https://github.com/fhempy/fhempy/commit/89b7e0788a3ba591022ce4ea079889f5aad093e3))

- Update controls
  ([`069587b`](https://github.com/fhempy/fhempy/commit/069587b327a16ae8c556e069d798a2ba1399ae9c))

- Update controls
  ([`d9cb6a6`](https://github.com/fhempy/fhempy/commit/d9cb6a61a6e75f966573d10bae6c3bb234903cd6))

- Update controls
  ([`f3474b4`](https://github.com/fhempy/fhempy/commit/f3474b46234c0525d23804f6e870ed54e81c2864))

- Update readme to specify supported devices
  ([`bc1ca28`](https://github.com/fhempy/fhempy/commit/bc1ca28fc3c277dadd050a088f3bccf5d3f4a006))

- **admin**: Checkout development after release
  ([`75ae44a`](https://github.com/fhempy/fhempy/commit/75ae44a9edb6189c796173ac5f5720e3dd7d77f8))

- **admin**: Update release script
  ([`02288bd`](https://github.com/fhempy/fhempy/commit/02288bd332219ffd6ae08613edd9f6b8dc95a7ab))

- **fhempy**: Show downloads per month
  ([`5173340`](https://github.com/fhempy/fhempy/commit/5173340eead9c680e59ee267a404997971819b1d))

- **googlecast**: Update play command
  ([`3a03191`](https://github.com/fhempy/fhempy/commit/3a031910a626d76d41ea91ea9da29122c61b59e7))

- **tuya_cloud**: Clarify readme
  ([`2c9b282`](https://github.com/fhempy/fhempy/commit/2c9b282a89bbe4414a855aef4e97bef5f89d30de))

- **tuya_cloud**: Update readme
  ([`263da1a`](https://github.com/fhempy/fhempy/commit/263da1aa090d231a265d9318cfb5823e4e50dba5))

### Features

- **eq3bt**: Support wndOpnTime/Temp, eco/cmftTemp
  ([`107805f`](https://github.com/fhempy/fhempy/commit/107805fd5d85fde76a49e2fabe1994943d27a169))

- **erelax_vaillant**: Add away, manual readings
  ([`2e49418`](https://github.com/fhempy/fhempy/commit/2e494188b5e5c84603e2994bf4cb977b33b4c586))

- **erelax_vaillant**: Support erelax vaillant
  ([`0c7f12c`](https://github.com/fhempy/fhempy/commit/0c7f12c7f8709687cdf2d477b055c03bb3c6e38a))

- **erelax_vaillant**: Support home/away
  ([`b29edde`](https://github.com/fhempy/fhempy/commit/b29eddeb16eb50c86f22eceb7cd8b2277e87f718))

- **fhempy**: Add gen_fhemdev_name fct
  ([`6cf9829`](https://github.com/fhempy/fhempy/commit/6cf9829124d6c3f759360b176be34510b319b7c7))

- **fhempy**: Add new devices to room/group
  ([`c197110`](https://github.com/fhempy/fhempy/commit/c197110a26df50acea79ae9abdac7832ac0182f6))

- **fhempy**: Support init_done
  ([`c807582`](https://github.com/fhempy/fhempy/commit/c80758235165e50f9256cc060db2930a5b97b738))

- **fhempy**: Update to asynczeroconf
  ([`7b319e3`](https://github.com/fhempy/fhempy/commit/7b319e347601634894c458c7ac2b3782b99dee5e))

- **fhempy**: Use fhempy room instead of hidden
  ([`ae2ffdc`](https://github.com/fhempy/fhempy/commit/ae2ffdc9672e467d0ae68294acb6b79b559c8a04))

- **googlecast**: Update libraries ([#25](https://github.com/fhempy/fhempy/pull/25),
  [`856eeac`](https://github.com/fhempy/fhempy/commit/856eeac940659974458b323c6aa2d266a576040d))

working with pychromecast==9.2.0 and youtube_dl>=2021.06.06 tested. if spotify should work a
  modification must be made in base library controller spotify.py as followed: ``` """ Controller to
  interface with Spotify. """ import logging import threading import requests import json

from . import BaseController from ..config import APP_SPOTIFY from ..error import LaunchError

APP_NAMESPACE = "urn:x-cast:com.spotify.chromecast.secure.v1" TYPE_GET_INFO = "getInfo"
  TYPE_GET_INFO_RESPONSE = "getInfoResponse" #TYPE_SET_CREDENTIALS = "setCredentials"
  #TYPE_SET_CREDENTIALS_ERROR = "setCredentialsError" #TYPE_SET_CREDENTIALS_RESPONSE =
  "setCredentialsResponse" TYPE_ADD_USER = "addUser" TYPE_ADD_USER_RESPONSE = "addUserResponse"
  TYPE_ADD_USER_ERROR = "addUserError"

# pylint: disable=too-many-instance-attributes class SpotifyController(BaseController):
  """Controller to interact with Spotify namespace."""

def __init__(self, access_token=None, expires=None): super().__init__(APP_NAMESPACE, APP_SPOTIFY)

self.logger = logging.getLogger(__name__) self.session_started = False self.access_token =
  access_token self.expires = expires self.is_launched = False self.device = None
  self.credential_error = False self.waiting = threading.Event()

def receive_message(self, _message, data: dict): """ Handle the auth flow and active player
  selection.

Called when a message is received. """ if data["type"] == TYPE_GET_INFO_RESPONSE: self.device =
  data["payload"]["deviceID"] self.client = data["payload"]["clientID"] headers = { 'authority':
  'spclient.wg.spotify.com', 'authorization': 'Bearer {}'.format(self.access_token), 'content-type':
  'text/plain;charset=UTF-8' }

request_body = json.dumps({'clientId': self.client, 'deviceId': self.device})

response = requests.post('https://spclient.wg.spotify.com/device-auth/v1/refresh', headers=headers,
  data=request_body) json_resp = response.json() self.send_message({ "type": TYPE_ADD_USER,
  "payload": { "blob": json_resp["accessToken"], "tokenType": "accesstoken" } }) if data["type"] ==
  TYPE_ADD_USER_RESPONSE: self.is_launched = True self.waiting.set()

if data["type"] == TYPE_ADD_USER_ERROR: self.device = None self.credential_error = True
  self.waiting.set() return True

def launch_app(self, timeout=10): """ Launch Spotify application.

Will raise a LaunchError exception if there is no response from the Spotify app within timeout
  seconds. """

if self.access_token is None or self.expires is None: raise ValueError("access_token and expires
  cannot be empty")

def callback(): """Callback function""" self.send_message({"type": TYPE_GET_INFO, "payload": {}})

self.device = None self.credential_error = False self.waiting.clear()
  self.launch(callback_function=callback)

counter = 0 while counter < (timeout + 1): if self.is_launched: return self.waiting.wait(1) counter
  += 1

if not self.is_launched: raise LaunchError( "Timeout when waiting for status response from Spotify
  app" )

# pylint: disable=too-many-locals def quick_play(self, **kwargs): """ Launches the spotify
  controller and returns when it's ready. To actually play media, another application using spotify
  connect is required. """ self.access_token = kwargs["access_token"] self.expires =
  kwargs["expires"]

self.launch_app(timeout=20) ```

- **googlecast**: Update to pychromecast 9.1.1
  ([`fdaab50`](https://github.com/fhempy/fhempy/commit/fdaab50f99006806464603a2ecfd2f4adf137967))

- **meross**: Support meross on/off
  ([`d08c927`](https://github.com/fhempy/fhempy/commit/d08c927361771164d8dc7665e0687fdc3420e777))

- **miflora**: Change conductivity to fertility
  ([`6d27f47`](https://github.com/fhempy/fhempy/commit/6d27f47f196c889c0c80cbaf0f5fcf2af0c2ae51))

- **mitemp2**: Test version of mitemp2
  ([`31e17a4`](https://github.com/fhempy/fhempy/commit/31e17a4e439ab92463659c20c0e494cd33f85947))

- **ring**: Update library to 0.7.1 ([#24](https://github.com/fhempy/fhempy/pull/24),
  [`9aa2360`](https://github.com/fhempy/fhempy/commit/9aa236079a81f483294be41e0a84a167b2ae5bed))

Version 0.7.1 tested since release and workin with fhempy

- **ring**: Update to latest ring_doorbell lib
  ([`a7295ca`](https://github.com/fhempy/fhempy/commit/a7295ca3fcfb3e6f62cdcc969556b79f8198f468))

- **seatconnect**: Bugfixing ([#39](https://github.com/fhempy/fhempy/pull/39),
  [`a5996f5`](https://github.com/fhempy/fhempy/commit/a5996f557c12ce4a7390faee31d0cbaeb05dbe71))

- **seatconnect**: First Version of seatconnect ([#35](https://github.com/fhempy/fhempy/pull/35),
  [`124f715`](https://github.com/fhempy/fhempy/commit/124f71588f3bd54e20118baf37029760809cdfe8))

- **seatconnect**: Integration of Timer Schedule for Climatisation
  ([#38](https://github.com/fhempy/fhempy/pull/38),
  [`f3a130d`](https://github.com/fhempy/fhempy/commit/f3a130d92948ce9eaa5cb65c61ce7e68c7049251))

* First Version of seatconnect

* Bug Climatisation and first integration of Timer

* seprated schedule timer

* added climatisation description

* timer configuration formated

* climatisation temp from int to float

- **skodaconnect**: Add honk and flash support
  ([`623c3d3`](https://github.com/fhempy/fhempy/commit/623c3d3bef608edfa0ed5c00f157e8f90fcc908d))

- **skodaconnect**: Add skoda connect support
  ([`ab507e8`](https://github.com/fhempy/fhempy/commit/ab507e872293014fedad786bf5d85c4e82eb36a4))

- **skodaconnect**: Change vehicle.update() to connection.update(), add UpdateInterval, add
  UpdateReading, add ForceUpdate, add missing set_ commands,
  ([`1de20c3`](https://github.com/fhempy/fhempy/commit/1de20c34fe61541d42a1628a05b6b526aa439698))

- **tuya**: Support another heating device
  ([`8843138`](https://github.com/fhempy/fhempy/commit/884313823231407a2155518cc01d04930246313c))

- **tuya**: Support miio lib 0.5.5.2
  ([`88fb98b`](https://github.com/fhempy/fhempy/commit/88fb98bdd7e9f73bff231e64236832685e12f47b))

- **tuya**: Support unknown tuya devices
  ([`d42d30d`](https://github.com/fhempy/fhempy/commit/d42d30d2f91b4266eabf13a8e0985a24dee10f32))

- **tuya**: Update to latest tinytuya lib
  ([`0edc476`](https://github.com/fhempy/fhempy/commit/0edc476557bf54da6c7775b0101b68eb35894115))

- **tuya_cloud**: Set state for some devices
  ([`de4f07a`](https://github.com/fhempy/fhempy/commit/de4f07a9d47c19c536464670081ef5f80f3789cf))

- **tuya_cloud**: Support all tuya devices
  ([`ddceb85`](https://github.com/fhempy/fhempy/commit/ddceb855fe6758d5884346ea93a6e84a06625c34))

- **tuya_cloud**: Support colorpicker
  ([`fbef95d`](https://github.com/fhempy/fhempy/commit/fbef95d49466342270833adb428b466312ef372c))

- **tuya_cloud**: Support json commands
  ([`fdc9170`](https://github.com/fhempy/fhempy/commit/fdc9170129fb0d45298eb9d3d323169fdba857a0))

- **tuya_cloud**: Use switch_led for state
  ([`a5f7e65`](https://github.com/fhempy/fhempy/commit/a5f7e659af1ba32ae9f15567f061122a6312c22c))

- **upnp**: Update upnp library
  ([`f2c5120`](https://github.com/fhempy/fhempy/commit/f2c512079c665e8dd84c1efa288b08873cc98fed))

- **xiaomi_gateway3**: Support motion sensor
  ([`478db7a`](https://github.com/fhempy/fhempy/commit/478db7ad578ae6fef5a18066b2a4058fe561f745))

- **xiaomi_gateway3**: Support sensor_wleak.aq1
  ([`bc8cf61`](https://github.com/fhempy/fhempy/commit/bc8cf6183bb4568b5f47b98e07669e3e8cda4f4e))

- **xiaomi_gateway3**: Update to latest version
  ([`9643837`](https://github.com/fhempy/fhempy/commit/96438373925c4c583dfbe4a9d8433fbc98aa678a))

- **xiaomi_gateway3**: Update xg3 library
  ([`62352da`](https://github.com/fhempy/fhempy/commit/62352da7581f1f338d34078ebfc2822fd38e217a))

### Refactoring

- *****: Sort imports
  ([`ed84897`](https://github.com/fhempy/fhempy/commit/ed84897fca897f01b6fc87a3ec5b25a9bb9eeef8))


## v0.1.38 (2021-01-28)

### Bug Fixes

- Loop
  ([`b968e3d`](https://github.com/fhempy/fhempy/commit/b968e3d97485a7d3b216edaaad772236052bc28a))

- Need module
  ([`de7c2fa`](https://github.com/fhempy/fhempy/commit/de7c2fac248ec45ae1bb21e188cc86d251aab741))

- Param is optional
  ([`6112d9a`](https://github.com/fhempy/fhempy/commit/6112d9a7da98dff9ce14dad6b14218296a917e05))

- Pychromecast min version
  ([`8a58a53`](https://github.com/fhempy/fhempy/commit/8a58a5374c25ffcaf1f3c9a9f37b5ebb83272d96))

- Str concat int
  ([`c693afb`](https://github.com/fhempy/fhempy/commit/c693afbc131e4f53db0f6a8efa8aba436c670a20))

- **admin**: Another try
  ([`e592500`](https://github.com/fhempy/fhempy/commit/e592500ba431e5bd112e594f38b9a96f2bb0e65d))

- **eq3bt**: Fix set temperatureOffset
  ([`429afcd`](https://github.com/fhempy/fhempy/commit/429afcd4f61f17b248dce60161d7418ec5770a54))

- **fhempy**: Set IODev after CommandDefine
  ([`b1a1299`](https://github.com/fhempy/fhempy/commit/b1a12993b76cebe3949f510add7a7e1857b91869))

- **readme**: Another fix
  ([`fc11bc4`](https://github.com/fhempy/fhempy/commit/fc11bc4426023161c219b2ea7b3daedf9f9696a6))

- **release**: Hopefully fix release script
  ([`cea2a16`](https://github.com/fhempy/fhempy/commit/cea2a165abd64ac7410ecb387dbf1d36f50cb468))

- **release**: One more try to get gh token working
  ([`f7f0f04`](https://github.com/fhempy/fhempy/commit/f7f0f04443b9b2a05d05dbb8bd76cc46132a8f70))

- **setup**: Fix excludes in manifest
  ([`9c3b255`](https://github.com/fhempy/fhempy/commit/9c3b255e90fbc8c8f0ab11a85531795c6239fd84))

- **xiaomi_gateway3**: Add import time
  ([`7ef7a9e`](https://github.com/fhempy/fhempy/commit/7ef7a9ecabb2e8f765f6e1223bcaaaed365c6644))

- **xiaomi_gateway3**: Add missing imports
  ([`b54aa4a`](https://github.com/fhempy/fhempy/commit/b54aa4a2529f1c7c23c3bfbb457c05790dcc0014))

- **xiaomi_gateway3**: Remove unused imports
  ([`1758909`](https://github.com/fhempy/fhempy/commit/175890932f4efeeedba79ae6b2d1dfe81839abcc))

- **xiaomi_gateway3**: Set last_update on update
  ([`146487d`](https://github.com/fhempy/fhempy/commit/146487daf69f9ed5219043c444fdfbac9f90021c))

### Chores

- Add controls update script
  ([`a08d81e`](https://github.com/fhempy/fhempy/commit/a08d81e4258ec907ce723f43d81ec61445e5af00))

- Add info for .env
  ([`531e4b8`](https://github.com/fhempy/fhempy/commit/531e4b8e952c1135ec34977ce9ad594ca03e52a8))

- Add message to git merge
  ([`37dc281`](https://github.com/fhempy/fhempy/commit/37dc281e9f16c55ec6ad511686dd56277756a20d))

- Prepare release scripts
  ([`ba3e51f`](https://github.com/fhempy/fhempy/commit/ba3e51fca7e549bbd4d632488aa753a49bdb8859))

- Update controls
  ([`e3b801c`](https://github.com/fhempy/fhempy/commit/e3b801ce9bdc27dcd551bf329b59e73131c157b9))

- Update controls
  ([`0536e1a`](https://github.com/fhempy/fhempy/commit/0536e1aebd81ce0b8424d23a0c7dc81626035ca0))

- Update controls
  ([`e4ab8ac`](https://github.com/fhempy/fhempy/commit/e4ab8ac071fb82e42fe7257c7010eb4adc2b36ee))

- Update controls
  ([`a792112`](https://github.com/fhempy/fhempy/commit/a792112f5f8f5e39eae7cd3f00f57337c797e1a5))

- Update controls
  ([`7c905ff`](https://github.com/fhempy/fhempy/commit/7c905ff0913e39083c65674f3681e549f08b3734))

- Update controls
  ([`a60d32a`](https://github.com/fhempy/fhempy/commit/a60d32a21fb599b5b4913c3f2595984c071b49df))

- Update controls
  ([`d8db6b2`](https://github.com/fhempy/fhempy/commit/d8db6b298ec78ac1c03722f30cf62c941aa188bc))

- Update controls
  ([`3c8a3d4`](https://github.com/fhempy/fhempy/commit/3c8a3d442734e5d064b638252226e7be77cafede))

- Update controls
  ([`7fbf8cb`](https://github.com/fhempy/fhempy/commit/7fbf8cbd3dabc56374993a5ab8b7add46e899c86))

- Update controls
  ([`01e5c16`](https://github.com/fhempy/fhempy/commit/01e5c16e703aef16c436eeefa3662c14103a6640))

- Use patch level for rls, fix .env usage
  ([`57389f1`](https://github.com/fhempy/fhempy/commit/57389f18cd813636768c6620fcae3bb61458efc3))

### Documentation

- Remove useless stuff
  ([`7401907`](https://github.com/fhempy/fhempy/commit/74019075190fb53b2cc7fdf6e4721360a698974e))

### Features

- New reading pairing on/off
  ([`ee42b9c`](https://github.com/fhempy/fhempy/commit/ee42b9c1dc822993ee882e94be056b311f87bd8e))

- **tuya**: Add keep_connected attr
  ([`b2c1ca4`](https://github.com/fhempy/fhempy/commit/b2c1ca47cf1b7adda9eb86731f21e0f755cf3dcd))
