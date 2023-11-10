# CHANGELOG



## v0.1.673 (2023-11-10)

### Fix

* fix(huawei_modbus): moved import to ensure event loop running ([`ada2d4f`](https://github.com/fhempy/fhempy/commit/ada2d4f10af2ebdf6632e0e8998c60f56d47a724))


## v0.1.672 (2023-11-10)

### Chore

* chore: update fhem-controls-actions ([`4fd76af`](https://github.com/fhempy/fhempy/commit/4fd76afd760f9ca007122ec8c5b1d997e120933b))

* chore: add quick &amp; dirty development instructions ([`f3e7d18`](https://github.com/fhempy/fhempy/commit/f3e7d18d3b180283c27273df9d61daaf4403243b))

### Feature

* feat(huawei_modbus): add Huawei ModBus module ([`28abee1`](https://github.com/fhempy/fhempy/commit/28abee157e7a09fa4389a83b314f5df3c46168ac))

### Unknown

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`37f17a5`](https://github.com/fhempy/fhempy/commit/37f17a50eba618fc0e2e2ad67b53aaf0e627fba1))


## v0.1.671 (2023-11-10)

### Chore

* chore: install poetry ([`96b8610`](https://github.com/fhempy/fhempy/commit/96b861069e9a4b9bf4805aede5ab5a8e677974ff))

### Fix

* fix(ring): Ring Doorbell - Update BaseLib (#213)

* Update BaseLibs SkodaConnect and Ring

* Ring Doorbell - Update BaseLib

* Important Update in BaseLib.
Versions &lt;1.3.8 not working anymore

* Ring Update to latest BaseLib

---------

Co-authored-by: Dominik &lt;dominik.karall@gmail.com&gt; ([`c59b3e4`](https://github.com/fhempy/fhempy/commit/c59b3e4485c2cd19e19ef12ce6afbf8920fe59fa))

* fix(skodaconnect): update base lib (#217)

Bump skodaconnect to 1.3.8

This Version is needed:
&#34;Updated User-Agent in order to get code on par with recent Android and IOS apps.

Outdated User-Agent from older app version seems to be blocked now at token endpoints. This change is confirmed working with Enyaq owners.&#34; ([`2de2114`](https://github.com/fhempy/fhempy/commit/2de211469867eceaf10d357e94657dbc96d1257b))

* fix(fhempy): use poetry for tox ([`c579343`](https://github.com/fhempy/fhempy/commit/c579343200c340afb7f98b33f28d41451971d63b))

* fix(fhempy): add dev dependencies, min version python 3.8 ([`fcde943`](https://github.com/fhempy/fhempy/commit/fcde9432ae87377dab1fcfdd67ab3a21b7078e2e))


## v0.1.670 (2023-10-08)

### Ci

* ci: move release.sh functionality to github actions ([`2661fa1`](https://github.com/fhempy/fhempy/commit/2661fa10f7afcbcaaca13110906cb6a19dcee371))

### Fix

* fix(googlecast): try to fix spotify playback (#196) ([`30eea09`](https://github.com/fhempy/fhempy/commit/30eea09b1a64a2b31db4aca164423c720d6b8672))


## v0.1.669 (2023-10-08)

### Chore

* chore: fix versioning ([`a99193e`](https://github.com/fhempy/fhempy/commit/a99193e35e8cda66edd174ebb9070962758e58c6))


## v0.1.668 (2023-10-08)

### Chore

* chore: Update release.yml ([`9704eee`](https://github.com/fhempy/fhempy/commit/9704eee16a68e2e19f6bb281e6b340bd13126154))


## v0.1.667 (2023-10-08)

### Unknown

* Update BaseLibs SkodaConnect and Ring (#197)

Thx! ([`98eb8b9`](https://github.com/fhempy/fhempy/commit/98eb8b9b6b18a8b762427925f2df36ae046c3748))


## v0.1.666 (2023-10-08)

### Chore

* chore: add semantic_release with poetry ([`3068664`](https://github.com/fhempy/fhempy/commit/30686640aac50274d30c85c920e846e12770ac7f))

* chore: Update release.yml ([`e0bb41e`](https://github.com/fhempy/fhempy/commit/e0bb41e91ed469781deefd150a93278291bce422))

* chore: use poetry ([`a0e2385`](https://github.com/fhempy/fhempy/commit/a0e238573bf1c44dd59532ef8485f295827eb3ed))

* chore: use poetry ([`9fdbbef`](https://github.com/fhempy/fhempy/commit/9fdbbef1d84e5ab43a9512afda8205827eb5746a))

* chore: Update release.yml ([`951ef9a`](https://github.com/fhempy/fhempy/commit/951ef9a819401335d86b305c5f8054ead64b7054))

* chore: Update release.yml ([`799bbd7`](https://github.com/fhempy/fhempy/commit/799bbd7ae7cdf0c08f5f02667e907d0f0c0a008b))

* chore: fix semantic_release build ([`8e54690`](https://github.com/fhempy/fhempy/commit/8e5469067c1f063e9a34b0319f2ac4048d66aaa0))

* chore: try to fix build ([`62b069c`](https://github.com/fhempy/fhempy/commit/62b069cd4e843c6219b2cab6ace23af7c79dd459))

* chore: Update release.yml ([`d906c87`](https://github.com/fhempy/fhempy/commit/d906c8729c93ac98af7e16685babc64a6fb489c0))

* chore: fix build with pyproject.toml ([`a16f7ee`](https://github.com/fhempy/fhempy/commit/a16f7ee9667e852498266e4fa4ac1289401587f4))

* chore: try to use pyproject.toml ([`5abc23a`](https://github.com/fhempy/fhempy/commit/5abc23a472d0282194999a6b0ae92ffd1b926e5d))

* chore: Update release.yml ([`c15db54`](https://github.com/fhempy/fhempy/commit/c15db5433ea31fdb741c981c230dd7e0f62a79f9))

* chore: Update release.yml ([`a692907`](https://github.com/fhempy/fhempy/commit/a692907dd49fe65574d190e9fffe1b3553c098a3))

* chore: Update release.yml ([`7b56ab4`](https://github.com/fhempy/fhempy/commit/7b56ab498a57a806d06526bbeac4779202b24bdb))

* chore: auto update controls ([`e72edde`](https://github.com/fhempy/fhempy/commit/e72edde61dfee0298d8e43945e71008a0430f7dd))

* chore: auto update controls ([`0fdc06c`](https://github.com/fhempy/fhempy/commit/0fdc06c8a2d2b152e2be1a1accca22b16e8f54c2))

* chore: Update release.yml ([`15b861b`](https://github.com/fhempy/fhempy/commit/15b861bb128e94e88c19a67b1ad95a6f8a3116a4))

* chore: Try to fix checkout permissions ([`d04c963`](https://github.com/fhempy/fhempy/commit/d04c96310d0b5aeb56e28f63cb010c695ae81d50))

* chore: Try to fix commit ([`ac8c329`](https://github.com/fhempy/fhempy/commit/ac8c329d1be5b3d7e2449a439a495bfcceb78f19))

* chore: Try to fix perl setup ([`957a9cf`](https://github.com/fhempy/fhempy/commit/957a9cfbf3be71ac11d700668297e45a28b97f36))

* chore: Test gh actions release ([`37698a9`](https://github.com/fhempy/fhempy/commit/37698a984d7c810c68e424f69802753f3ff0aad8))

### Fix

* fix(googlecast): update libraries (#202) ([`db5b444`](https://github.com/fhempy/fhempy/commit/db5b4449bb44eced89a45542262391f8298bccd9))

### Unknown

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`d0bb039`](https://github.com/fhempy/fhempy/commit/d0bb0397e25c46ffc0efa924cd4d42ee7a6b53f4))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`05546d9`](https://github.com/fhempy/fhempy/commit/05546d98a84e2dca37140ab8cdb8a6f3cdaa01a0))

* Merge branch &#39;development&#39; ([`9711c7e`](https://github.com/fhempy/fhempy/commit/9711c7e4d159d89d9ef24e4d91dec140985aace6))


## v0.1.665 (2023-09-09)

### Fix

* fix(object_detection): support python 3.10 ([`62e0183`](https://github.com/fhempy/fhempy/commit/62e0183694dbe68f57ee082ee8cf6fc5c9c6c306))

### Unknown

* Merge branch &#39;development&#39; ([`c0ad0f7`](https://github.com/fhempy/fhempy/commit/c0ad0f78edba763b41779a8c03f951137eda63e0))


## v0.1.664 (2023-09-09)

### Fix

* fix(skodaconnect): fix possible installation issues ([`fb360d3`](https://github.com/fhempy/fhempy/commit/fb360d3d2be591d51b9cd79c9ee29acca9bb8ed0))

### Unknown

* Merge branch &#39;development&#39; ([`03b155c`](https://github.com/fhempy/fhempy/commit/03b155cc4df74b207d71929a96a8051b6701ea35))


## v0.1.663 (2023-09-09)

### Chore

* chore: add test for python 3.10 ([`ab8e2a0`](https://github.com/fhempy/fhempy/commit/ab8e2a01ac86343a4b5f31a02160bd3fd64b2ebf))

### Fix

* fix(homekit): update aiohomekit lib ([`fb5c4fc`](https://github.com/fhempy/fhempy/commit/fb5c4fccd88ea1cc48a7913bad46b454083aead0))

* fix(skodaconnect): fix installation dependency ([`b78ec37`](https://github.com/fhempy/fhempy/commit/b78ec375a41244ad70f88bdf69857a08179fbaab))

### Unknown

* Merge branch &#39;development&#39; ([`6d9ebe6`](https://github.com/fhempy/fhempy/commit/6d9ebe62235c3a7570e15423389981e170e05ba9))


## v0.1.662 (2023-09-09)

### Fix

* fix(seatconnect): update seatconnect lib (#190) ([`d2ae3ef`](https://github.com/fhempy/fhempy/commit/d2ae3ef34cc36119027ac1847e43715c28bb07e4))

### Unknown

* Merge branch &#39;development&#39; ([`efcdc9a`](https://github.com/fhempy/fhempy/commit/efcdc9affe2d3b18d56c3f0e6147d8f57a043d89))


## v0.1.661 (2023-08-16)

### Chore

* chore(deps): bump markdown2 from 2.4.8 to 2.4.10 (#177)

Bumps [markdown2](https://github.com/trentm/python-markdown2) from 2.4.8 to 2.4.10.
- [Changelog](https://github.com/trentm/python-markdown2/blob/master/CHANGES.md)
- [Commits](https://github.com/trentm/python-markdown2/compare/2.4.8...2.4.10)

---
updated-dependencies:
- dependency-name: markdown2
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`884e47a`](https://github.com/fhempy/fhempy/commit/884e47a59bfdc0378835411aae91b13b0ffe9694))

* chore(deps): bump aiohttp[speedups] from 3.8.4 to 3.8.5 (#175)

Bumps [aiohttp[speedups]](https://github.com/aio-libs/aiohttp) from 3.8.4 to 3.8.5.
- [Release notes](https://github.com/aio-libs/aiohttp/releases)
- [Changelog](https://github.com/aio-libs/aiohttp/blob/v3.8.5/CHANGES.rst)
- [Commits](https://github.com/aio-libs/aiohttp/compare/v3.8.4...v3.8.5)

---
updated-dependencies:
- dependency-name: aiohttp[speedups]
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`43e684c`](https://github.com/fhempy/fhempy/commit/43e684c3ceff1c6caa220608406419a0933753c5))

### Feature

* feat(skodaconnect): add some features (#180)

- added setting for EV Cars
- added &#34;connected&#34; state
- added int-cast to charge_limit ([`4662110`](https://github.com/fhempy/fhempy/commit/46621102f7bd0b13bad19f99e33a24bb05b5562c))


## v0.1.660 (2023-07-10)

### Fix

* fix(fhempy): add async upnp client to requirements ([`bbb68f5`](https://github.com/fhempy/fhempy/commit/bbb68f5f8dcc33eed0e2f5f3af16a67cc6eea097))

### Unknown

* Merge branch &#39;development&#39; ([`9fef42d`](https://github.com/fhempy/fhempy/commit/9fef42d2c712d8fc3a3b0e7be3f25ccaf2756113))


## v0.1.659 (2023-07-10)

### Fix

* fix(kia_hyundai): update base lib to 3.3.12 ([`8f4b732`](https://github.com/fhempy/fhempy/commit/8f4b73289750ac647b570b45c40d6bc8ac2603fb))

* fix(skodaconnect): update base lib to 1.3.6 ([`34460fc`](https://github.com/fhempy/fhempy/commit/34460fc55cf2e32d75f675ecf931ac39fcbdbec5))

* fix(seatconnect): update base lib to 1.1.7 (#168) ([`72acd0d`](https://github.com/fhempy/fhempy/commit/72acd0d5f316b9a577ec13b7ca0e3a751388661d))

* fix(tuya): fix energy calculation ([`aa9a52b`](https://github.com/fhempy/fhempy/commit/aa9a52b818937e075e9cc0c32c65414c105dccfc))

### Unknown

* Merge branch &#39;development&#39; ([`ec1297e`](https://github.com/fhempy/fhempy/commit/ec1297e92104a035c464515772cde8a1f9bde76f))


## v0.1.658 (2023-06-17)

### Fix

* fix(tuya): fix localkey attr on create_device (#162) ([`b45555d`](https://github.com/fhempy/fhempy/commit/b45555d6d74c44dd98b52868f38ee5bf75ec66b4))

### Unknown

* Merge branch &#39;development&#39; ([`905b8e2`](https://github.com/fhempy/fhempy/commit/905b8e2f16d5e0b6dccdbb77f471a45ab49ea3da))


## v0.1.657 (2023-06-17)

### Fix

* fix(fhempy): add pyOpenSSL for cryptography ([`1dc4a78`](https://github.com/fhempy/fhempy/commit/1dc4a78d76082b199502fc08548ccf140a1da69e))

* fix(homekit): do set call async ([`9e0821e`](https://github.com/fhempy/fhempy/commit/9e0821ed4df01608abb5826a909de05ab98a0a7f))

* fix(fhempy): add pyOpenSSL for cryptography ([`9494bc4`](https://github.com/fhempy/fhempy/commit/9494bc49844311ae5c488ee16c61c048b94f9cf1))

* fix(homekit): do set call async ([`b5fd2eb`](https://github.com/fhempy/fhempy/commit/b5fd2ebbc51f3864703397b3e0c7bb11211108e5))

### Unknown

* Merge branch &#39;development&#39; ([`15f7fb9`](https://github.com/fhempy/fhempy/commit/15f7fb9779ad3ff465cacc0606e50cf4dcdec2f8))


## v0.1.656 (2023-06-11)

### Fix

* fix(fhempy): fix cryptography imports ([`3eddf85`](https://github.com/fhempy/fhempy/commit/3eddf853ef9571b0ebee49250ffd8e826f20ce7b))

### Unknown

* Merge branch &#39;development&#39; ([`281b0a9`](https://github.com/fhempy/fhempy/commit/281b0a9b6c8e0934e22a3d40df77bbf5f1047447))


## v0.1.655 (2023-06-11)

### Fix

* fix(homekit): fix cryptography version ([`2d66139`](https://github.com/fhempy/fhempy/commit/2d661398dc99d035a91b5e2738b56df21cfa8c69))

### Unknown

* Merge branch &#39;development&#39; ([`b1ee392`](https://github.com/fhempy/fhempy/commit/b1ee392611acefc77aba77044f7e5dc4aea378ba))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`3862530`](https://github.com/fhempy/fhempy/commit/3862530f3c0ad7b76a2c83e44900c63d1bbd8eb2))


## v0.1.654 (2023-06-11)

### Chore

* chore: update controls ([`83b0ae1`](https://github.com/fhempy/fhempy/commit/83b0ae1454cea1ae16bb76dd3111d1f543476d70))

### Feature

* feat(fhempy): update zeroconf ([`509cddd`](https://github.com/fhempy/fhempy/commit/509cdddd865d56a150d62dfd12d2101b94fd4c77))

### Unknown

* Merge branch &#39;development&#39; ([`5516547`](https://github.com/fhempy/fhempy/commit/55165476ab5fbe4406d123b1f6f5ce5486a2e89a))


## v0.1.653 (2023-06-11)

### Feature

* feat(homekit): initial version of homekit support (very basic!) ([`4171521`](https://github.com/fhempy/fhempy/commit/4171521e34b6b712e1330e7e41abda3cbbe9de99))

### Unknown

* Merge branch &#39;development&#39; ([`e81b1b0`](https://github.com/fhempy/fhempy/commit/e81b1b0ddf96db9846f4dcee62da292eadcac324))


## v0.1.652 (2023-06-05)

### Fix

* fix(tuya): fix localkey attr on create ([`e8d620a`](https://github.com/fhempy/fhempy/commit/e8d620af06119ed421a7c42453eb35ee6ff458ae))

* fix(tuya): fix localkey attr on create ([`e697616`](https://github.com/fhempy/fhempy/commit/e697616aae47973b3655da1ed74e05d73c5b2160))

### Unknown

* Merge branch &#39;development&#39; ([`a318860`](https://github.com/fhempy/fhempy/commit/a3188601683ea74bdea0bf896a56d835e0e4985c))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`25df5cb`](https://github.com/fhempy/fhempy/commit/25df5cb1ea8a63e4512d072816b1e74414ea6e01))


## v0.1.651 (2023-05-27)

### Chore

* chore: update controls ([`07f4df4`](https://github.com/fhempy/fhempy/commit/07f4df4aa310d9144f1582240fccc664ae81c07f))

### Fix

* fix(skodaconnect): update baselib and use cryptography 3.3.2 ([`43be1b2`](https://github.com/fhempy/fhempy/commit/43be1b2eff7b00cb378f460cedef315ce7e21ab1))

* fix(seatconnect): use cryptography 3.3.2 ([`3e7f943`](https://github.com/fhempy/fhempy/commit/3e7f94300cec1bb78eec5bdf0078957c4b7c5d41))

### Unknown

* Merge branch &#39;development&#39; ([`693ca05`](https://github.com/fhempy/fhempy/commit/693ca05dc03f1604deb0c205711df0ffa1c71676))


## v0.1.650 (2023-05-27)

### Chore

* chore(deps): bump websockets from 10.4 to 11.0.3 (#154)

Bumps [websockets](https://github.com/aaugustin/websockets) from 10.4 to 11.0.3.
- [Release notes](https://github.com/aaugustin/websockets/releases)
- [Commits](https://github.com/aaugustin/websockets/compare/10.4...11.0.3)

---
updated-dependencies:
- dependency-name: websockets
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`3f0acee`](https://github.com/fhempy/fhempy/commit/3f0acee4bacacc16d72b79735e48a1dc82bbf9a4))

* chore(deps): bump pycryptodomex from 3.17 to 3.18.0 (#157)

Bumps [pycryptodomex](https://github.com/Legrandin/pycryptodome) from 3.17 to 3.18.0.
- [Release notes](https://github.com/Legrandin/pycryptodome/releases)
- [Changelog](https://github.com/Legrandin/pycryptodome/blob/master/Changelog.rst)
- [Commits](https://github.com/Legrandin/pycryptodome/compare/v3.17.0...v3.18.0)

---
updated-dependencies:
- dependency-name: pycryptodomex
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`1b642cb`](https://github.com/fhempy/fhempy/commit/1b642cb6f127c50bf85824a11519f332f0525564))

* chore(deps): bump requests from 2.28.2 to 2.31.0 (#158)

Bumps [requests](https://github.com/psf/requests) from 2.28.2 to 2.31.0.
- [Release notes](https://github.com/psf/requests/releases)
- [Changelog](https://github.com/psf/requests/blob/main/HISTORY.md)
- [Commits](https://github.com/psf/requests/compare/v2.28.2...v2.31.0)

---
updated-dependencies:
- dependency-name: requests
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`7d73a7d`](https://github.com/fhempy/fhempy/commit/7d73a7d09351b484f89efd988fd3cee789d7d7fa))


## v0.1.649 (2023-05-27)

### Feature

* feat(esphome): update esphome to 2023.5.4 ([`5e6a585`](https://github.com/fhempy/fhempy/commit/5e6a58516cb726c9e88b99e413b88481483ea462))

* feat(ikos): new module for ikos hotels ([`6b0f38c`](https://github.com/fhempy/fhempy/commit/6b0f38c87305c67b9c2c4a196db694084d38b492))

### Fix

* fix(tuya): support locakeys with special characters. localkey is used from attr instead of define (#156) ([`a0dad2b`](https://github.com/fhempy/fhempy/commit/a0dad2b3d09e78f746fab56f69e4ded593c68415))

### Unknown

* Merge branch &#39;development&#39; ([`0056fdb`](https://github.com/fhempy/fhempy/commit/0056fdbe045a8009cecaa72a3b69d45e243a7675))


## v0.1.648 (2023-04-20)

### Feature

* feat(geizhals): add image and get store from offer 0 ([`0397ef4`](https://github.com/fhempy/fhempy/commit/0397ef4b35a8c2b3c53df0074cd986e73e53fcdd))

* feat(geizhals): add image and get store from offer 0 ([`6b04f0c`](https://github.com/fhempy/fhempy/commit/6b04f0c8a364b4fad63e3131f80f0b72bfbce1d4))

### Fix

* fix(fhempy): fix special characters in readings and device names ([`e81d6d0`](https://github.com/fhempy/fhempy/commit/e81d6d009b37f7a9dfd18eadbe70fc2b88f707f3))

* fix(fhempy): fix special characters in readings and device names ([`6ed1f18`](https://github.com/fhempy/fhempy/commit/6ed1f181579e6565df0d27afbc69adad53d460aa))

### Unknown

* Merge branch &#39;development&#39; ([`e886055`](https://github.com/fhempy/fhempy/commit/e88605546a0d06b6732c9dcb4b6aeb7a79420dda))


## v0.1.647 (2023-04-16)

### Fix

* fix(tuya): update aiotinytuya 1.12.3 ([`46f8fa9`](https://github.com/fhempy/fhempy/commit/46f8fa960a518d493f82cb02651f1702c6b71396))

### Unknown

* Merge branch &#39;development&#39; ([`b19d02d`](https://github.com/fhempy/fhempy/commit/b19d02d72e77b8049c0c6a988e56494d7e7ce987))


## v0.1.646 (2023-04-11)

### Feature

* feat(mqtt_ha_discovery): MQTT HomeAssistant discovery support ([`34e04cf`](https://github.com/fhempy/fhempy/commit/34e04cf6c80d59a47360b0283f0ebc2058f1b0db))

### Unknown

* Merge branch &#39;development&#39; ([`ac80589`](https://github.com/fhempy/fhempy/commit/ac80589e643411fe85e2b2860807627fc40f8dd1))


## v0.1.645 (2023-04-09)

### Fix

* fix(kia_hyundai): fix login with lib update to 3.1.8 ([`8e630af`](https://github.com/fhempy/fhempy/commit/8e630afceddf48d4620ccfe6fdb6b41ccb3901f0))

### Unknown

* Merge branch &#39;development&#39; ([`453221e`](https://github.com/fhempy/fhempy/commit/453221ee926ab10b2531a273c998a7e4424a57ee))


## v0.1.644 (2023-04-08)

### Feature

* feat(esphome): update esphome to 2023.3.2 ([`a4f81b2`](https://github.com/fhempy/fhempy/commit/a4f81b2f6b751d8191541878026a6ce3d6b6ae20))

### Fix

* fix(tuya_cloud): add values in exception log ([`0d16830`](https://github.com/fhempy/fhempy/commit/0d16830b90a6c126f97cd0d2e21ce6563ffce67a))

* fix(skodaconnect): Minor improvements in BaseLib (#140) ([`9033dbd`](https://github.com/fhempy/fhempy/commit/9033dbdb4ad9e2e7fd2a2f9483b2eff5377e2c3b))

### Unknown

* Merge branch &#39;development&#39; ([`6daaf21`](https://github.com/fhempy/fhempy/commit/6daaf2107aebdfc5b21343cd6d17af42d6cf4dbb))


## v0.1.643 (2023-03-25)

### Fix

* fix(zigbee2mqtt): fix z2m version reading again ([`e64b707`](https://github.com/fhempy/fhempy/commit/e64b7077b39335dab640cfe30d1972008d1705f7))

### Unknown

* Merge branch &#39;development&#39; ([`4d57fae`](https://github.com/fhempy/fhempy/commit/4d57fae533cd15085a0447aee6dfa3c21f99937e))


## v0.1.642 (2023-03-25)

### Fix

* fix(zigbee2mqtt): fix startup ([`4444db7`](https://github.com/fhempy/fhempy/commit/4444db7d4c4d1206b9e3df42d44b56f0d1c0838b))

### Unknown

* Merge branch &#39;development&#39; ([`fbaf449`](https://github.com/fhempy/fhempy/commit/fbaf449d2d4b361c76a492602d0fb05ae4df9201))


## v0.1.641 (2023-03-25)

### Feature

* feat(zigbee2mqtt): add z2m_version reading ([`ed09190`](https://github.com/fhempy/fhempy/commit/ed091906442f7de603a04632615d704598c83c5f))

### Unknown

* Merge branch &#39;development&#39; ([`d6d4a64`](https://github.com/fhempy/fhempy/commit/d6d4a64bc64a746b98da09dc28ea9d1c2bbe9571))


## v0.1.640 (2023-03-25)

### Fix

* fix(wienernetze_smartmeter): clear cookies on login (#136) ([`5567821`](https://github.com/fhempy/fhempy/commit/5567821ea4615c947f29dd2300decb1028ba9a34))

### Unknown

* Merge branch &#39;development&#39; ([`64cba39`](https://github.com/fhempy/fhempy/commit/64cba39bf27733aa02bcb266e95944cc2f3a9e10))


## v0.1.639 (2023-03-23)

### Fix

* fix(wienernetze_smartmeter): add more log output (#136) ([`17f77a5`](https://github.com/fhempy/fhempy/commit/17f77a53c3415eddfa0aaf93ebe1352f07167dfe))

### Unknown

* Merge branch &#39;development&#39; ([`a1838b8`](https://github.com/fhempy/fhempy/commit/a1838b8d83067b83d20b789210e4241aa3799c4c))


## v0.1.638 (2023-03-23)

### Chore

* chore: test manifest dependencies ([`c1ad29b`](https://github.com/fhempy/fhempy/commit/c1ad29b2b360f0afc7f8dee66fa933fe4e654662))

* chore: test manifest dependencies ([`48e7221`](https://github.com/fhempy/fhempy/commit/48e72218bd9914d8710a85e427bb6c6d94531231))

### Feature

* feat(fhem_forum): support private messages ([`78eeb03`](https://github.com/fhempy/fhempy/commit/78eeb03b12ff3e47724355887f069da40349f7ad))

* feat(esphome): update lib to 2023.3.1 ([`f3e9ecb`](https://github.com/fhempy/fhempy/commit/f3e9ecb7b9a8cc070c31a6d641f01b8ced6c18cd))

### Fix

* fix(fhempy): handle github api rate limits on latest release check ([`564f7a1`](https://github.com/fhempy/fhempy/commit/564f7a1720d6fb36537e74bbf2953e093411fc4d))

### Unknown

* Merge branch &#39;development&#39; ([`5b59aea`](https://github.com/fhempy/fhempy/commit/5b59aea8fddd438eb603afaf51ad25bc50c5c8c3))


## v0.1.637 (2023-03-21)

### Chore

* chore(deps): bump importlib-metadata from 4.8.1 to 6.1.0 (#138) ([`ad9babe`](https://github.com/fhempy/fhempy/commit/ad9babe769213b56f732ffd497096b8374a41359))

* chore(deps): bump requests from 2.26.0 to 2.28.2 (#131) ([`aa913d3`](https://github.com/fhempy/fhempy/commit/aa913d3987e4b00991e51843fb4ba85d93610ff0))

* chore(deps): bump pycryptodomex from 3.16.0 to 3.17 (#135)

Bumps [pycryptodomex](https://github.com/Legrandin/pycryptodome) from 3.16.0 to 3.17.
- [Release notes](https://github.com/Legrandin/pycryptodome/releases)
- [Changelog](https://github.com/Legrandin/pycryptodome/blob/master/Changelog.rst)
- [Commits](https://github.com/Legrandin/pycryptodome/compare/v3.16.0...v3.17.0)

---
updated-dependencies:
- dependency-name: pycryptodomex
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`4e5aba1`](https://github.com/fhempy/fhempy/commit/4e5aba183dc20887d726df7ac0ff5350d5755b1b))

* chore(deps): bump markdown2 from 2.4.2 to 2.4.8 (#133)

Bumps [markdown2](https://github.com/trentm/python-markdown2) from 2.4.2 to 2.4.8.
- [Release notes](https://github.com/trentm/python-markdown2/releases)
- [Changelog](https://github.com/trentm/python-markdown2/blob/master/CHANGES.md)
- [Commits](https://github.com/trentm/python-markdown2/compare/2.4.2...2.4.8)

---
updated-dependencies:
- dependency-name: markdown2
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`592c4b2`](https://github.com/fhempy/fhempy/commit/592c4b229482fc6fc085a99e2d1514f06ac556a5))


## v0.1.636 (2023-03-21)

### Fix

* fix(volvo_software_update): fix update headers ([`d024d99`](https://github.com/fhempy/fhempy/commit/d024d994868fa5d8699746ee238079ee2e826415))

### Unknown

* Merge branch &#39;development&#39; ([`dd4a867`](https://github.com/fhempy/fhempy/commit/dd4a867fece97528eaceac25589b9705c7fdf5fb))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`ac5100e`](https://github.com/fhempy/fhempy/commit/ac5100e90bd645dbe9b7094a211ea777aebe09c8))


## v0.1.635 (2023-03-20)

### Fix

* fix(fhempy): fix perl syntax ([`09b4377`](https://github.com/fhempy/fhempy/commit/09b4377ebfacabf11f9747c1197b95835868c452))

### Unknown

* Merge branch &#39;development&#39; ([`faa84dd`](https://github.com/fhempy/fhempy/commit/faa84dd15ce140e786912680aaadfbaf7a68bc6a))


## v0.1.634 (2023-03-20)

### Fix

* fix(fhempy): run received commands for max 300ms within fhem ([`18a26a2`](https://github.com/fhempy/fhempy/commit/18a26a2832d6039fe1d5719008acdb74bd62ecbb))

### Unknown

* Merge branch &#39;development&#39; ([`7152261`](https://github.com/fhempy/fhempy/commit/7152261166d32260b99f3595dc958d1f945e12db))


## v0.1.633 (2023-03-19)

### Fix

* fix(fhem_forum): support new forum software ([`2cb1134`](https://github.com/fhempy/fhempy/commit/2cb1134df4fb9d3796ead7344ddd64a206ee9637))

### Unknown

* Merge branch &#39;development&#39; ([`f6757cd`](https://github.com/fhempy/fhempy/commit/f6757cdf646e5d9d818d17fbb12b0956b7351fc8))


## v0.1.632 (2023-03-19)

### Feature

* feat(aktionsfinder): support multiple arguments as search items ([`6e20578`](https://github.com/fhempy/fhempy/commit/6e20578d6222af26e3bb1c61aa4ae84928f02d7c))

### Fix

* fix(wienernetze_smartmeter): add exception handling (#136) ([`af66eb2`](https://github.com/fhempy/fhempy/commit/af66eb2fc5e5fcec40a7dab3224c64724ebbfda4))

* fix(volvo_software_update): support new volvo urls, please update your url! ([`7b13a5e`](https://github.com/fhempy/fhempy/commit/7b13a5e966598e8b6b8a05e368791e424da76881))

### Unknown

* Merge branch &#39;development&#39; ([`2e7cec9`](https://github.com/fhempy/fhempy/commit/2e7cec95d31f052ceee9a4d1b9e9a1a778390c18))


## v0.1.631 (2023-03-18)

### Fix

* fix(fhempy): remove () in dev and reading names ([`19aadef`](https://github.com/fhempy/fhempy/commit/19aadefc5841063a929a34de83ee79a213ef61e7))

### Unknown

* Merge branch &#39;development&#39; ([`eaed677`](https://github.com/fhempy/fhempy/commit/eaed677c20ff3f5c0472a91766116bfac7fbc5ea))


## v0.1.630 (2023-03-12)

### Fix

* fix(goodwe): fix reading names ([`0c466ca`](https://github.com/fhempy/fhempy/commit/0c466ca8d758bb6db595393cd5910bff35e91f16))

### Unknown

* Merge branch &#39;development&#39; ([`781f0ec`](https://github.com/fhempy/fhempy/commit/781f0ec861692b0d9665b4d5862f0db06a4fdeb3))


## v0.1.629 (2023-03-12)

### Chore

* chore: Update dependabot.yml ([`d8692e0`](https://github.com/fhempy/fhempy/commit/d8692e083b7bf3085d09665b4628b39fa5c18453))

* chore: Create .github/dependabot.yml ([`cdfa87b`](https://github.com/fhempy/fhempy/commit/cdfa87bb81eede1b17d05dfa1c98976e484e81b9))

### Feature

* feat(goodwe): new module for goodwe inverters ([`04a98f2`](https://github.com/fhempy/fhempy/commit/04a98f2d031387f477755d5bdc909f1212b3ba25))

### Unknown

* Merge branch &#39;development&#39; ([`0990205`](https://github.com/fhempy/fhempy/commit/09902059267c2953a02041289c8ed8ba2ace42a3))


## v0.1.628 (2023-03-11)

### Feature

* feat(aktionsfinder): new module aktionsfinder ([`4edcad3`](https://github.com/fhempy/fhempy/commit/4edcad3f30ec4e48027c6d97e0b2f6cbf777f6d9))

* feat(blue_connect): add icon ([`3ad3964`](https://github.com/fhempy/fhempy/commit/3ad396497972983244404d09d30e2e1a6f08e886))

* feat(arp_presence): add icon ([`33f29c4`](https://github.com/fhempy/fhempy/commit/33f29c4a0b528edddcb95138a2465ca9ca332b65))

### Unknown

* Merge branch &#39;development&#39; ([`6b176e6`](https://github.com/fhempy/fhempy/commit/6b176e6b27cb7497639b48c658f63fc29763a4bb))


## v0.1.627 (2023-03-11)

### Fix

* fix(kia_hyundai): fix dateutil requirement ([`c5dc94c`](https://github.com/fhempy/fhempy/commit/c5dc94c31b8d09efe84d8188be9c5497cbf9de10))

### Unknown

* Merge branch &#39;development&#39; ([`aca74f8`](https://github.com/fhempy/fhempy/commit/aca74f8c121849fd7849aae28e84b560bc4369ad))


## v0.1.626 (2023-03-11)


## v0.1.625 (2023-03-11)

### Fix

* fix(kia_hyundai): add further dependencies which are missing in the base library ([`6f6134b`](https://github.com/fhempy/fhempy/commit/6f6134b8275d541755b6adecb2017eccf255dfef))

### Unknown

* Merge branch &#39;development&#39; ([`e8f6fa3`](https://github.com/fhempy/fhempy/commit/e8f6fa3742dd653e24c309d0f1e9d31be9f942fe))


## v0.1.624 (2023-03-11)

### Fix

* fix(kia_hyundai): add missing pytz requirement ([`d5be5bf`](https://github.com/fhempy/fhempy/commit/d5be5bf255adf6fdd561068b2c17fb476dd8fef0))

### Unknown

* Merge branch &#39;development&#39; ([`8f9a7ee`](https://github.com/fhempy/fhempy/commit/8f9a7ee9678258d55b7e09a15b963af2b6cc4e08))


## v0.1.623 (2023-03-11)

### Fix

* fix(kia_hyundai): use library instead of    own code ([`51aa0b4`](https://github.com/fhempy/fhempy/commit/51aa0b47ff1ca814c89b70955ac20ccf89e25e31))

* fix(tuya): fix testcase by using aiotinytuya ([`148e2bb`](https://github.com/fhempy/fhempy/commit/148e2bbb481093addeafd768c7e6aef73a5be4f6))

### Unknown

* Merge branch &#39;development&#39; ([`e99f76f`](https://github.com/fhempy/fhempy/commit/e99f76f7e003355c241fbda5dff4b2b599f3e2bf))


## v0.1.622 (2023-03-11)

### Fix

* fix(tuya): use aiotinytuya ([`264f2db`](https://github.com/fhempy/fhempy/commit/264f2db8d7cfb1e4a1104789907c074c4727f00e))

### Unknown

* Merge branch &#39;development&#39; ([`b32abbc`](https://github.com/fhempy/fhempy/commit/b32abbc27fa543c8733b68355ed6243bfc3c4c90))


## v0.1.621 (2023-03-11)

### Feature

* feat(tuya): update to latest tinytuya release (1.11.0) ([`1740bf0`](https://github.com/fhempy/fhempy/commit/1740bf0ef90638ea63ca67709d89e4a89636c3d1))

### Unknown

* Merge branch &#39;development&#39; ([`ebfc899`](https://github.com/fhempy/fhempy/commit/ebfc899c76dfd571359f45f2b65802e7c7d82e69))


## v0.1.620 (2023-03-10)

### Fix

* fix(wienernetze_smartmeter): fix login via logwien ([`99e0872`](https://github.com/fhempy/fhempy/commit/99e087231ab6db0672ea7cfcbb92359317fc32e4))

### Unknown

* Merge branch &#39;development&#39; ([`febbda9`](https://github.com/fhempy/fhempy/commit/febbda9ecd9b8d80668cc9987291209d800cdd44))


## v0.1.619 (2023-03-07)

### Fix

* fix(tuya): allow float values ([`1484727`](https://github.com/fhempy/fhempy/commit/148472771da6472610f2bb76dbfbea1e70c77d2e))

### Unknown

* Merge branch &#39;development&#39; ([`c0bd1c4`](https://github.com/fhempy/fhempy/commit/c0bd1c48f42671a746e89b84054125423a3ec538))


## v0.1.618 (2023-03-07)

### Fix

* fix(tuya): revert last change ([`bd66d41`](https://github.com/fhempy/fhempy/commit/bd66d414009c1c55556230476aed168f0da6f55a))

### Unknown

* Merge branch &#39;development&#39; ([`d8901e1`](https://github.com/fhempy/fhempy/commit/d8901e148764bafa6c8cf20dc31124921c99b358))


## v0.1.617 (2023-03-07)

### Fix

* fix(tuya): retry connect on failure ([`a370795`](https://github.com/fhempy/fhempy/commit/a370795822976227b5b5b821a83c77738c77a291))

* fix(erelax_vaillant): use vaillant-netatmo-api library ([`bc61d49`](https://github.com/fhempy/fhempy/commit/bc61d49278f2c370ad1a8533e2caa1f34c00e49e))

### Unknown

* Merge branch &#39;development&#39; ([`3195a0f`](https://github.com/fhempy/fhempy/commit/3195a0f97a791b408cbf913e3cc04b12520861c7))


## v0.1.616 (2023-03-03)

### Fix

* fix(google_weather): update get images ([`91db97d`](https://github.com/fhempy/fhempy/commit/91db97d7060db5df6e31a4ac442da0947fd78ca3))

### Unknown

* Merge branch &#39;development&#39; ([`e472498`](https://github.com/fhempy/fhempy/commit/e47249873877d042a7a794236efeb7dbf77f44ee))


## v0.1.615 (2023-03-03)

### Fix

* fix(fhempy): update aiohttp to support Python 3.11 ([`9a5975a`](https://github.com/fhempy/fhempy/commit/9a5975a4c69fc61717fbf29fb9e18b434b83d9f5))

### Unknown

* Merge branch &#39;development&#39; ([`b7a3337`](https://github.com/fhempy/fhempy/commit/b7a33370ee428a734f072b85faff4a57330ac5a3))


## v0.1.614 (2023-03-03)

### Fix

* fix(tuya): colour_data = A, colour_data_v2 = B for rgb bulbs ([`022e2f1`](https://github.com/fhempy/fhempy/commit/022e2f1ccb9a1ad0148cfa38d8950d9c285911a8))

### Unknown

* Merge branch &#39;development&#39; ([`9e7333c`](https://github.com/fhempy/fhempy/commit/9e7333c503b5a3116e85a19075614e41ab3d3ff1))


## v0.1.613 (2023-03-01)

### Fix

* fix(wienernetze_smartmeter): fix login (#120) ([`542e308`](https://github.com/fhempy/fhempy/commit/542e308d4e8f23d856db59ac830235a827cd73af))

### Unknown

* Merge branch &#39;development&#39; ([`7b6257e`](https://github.com/fhempy/fhempy/commit/7b6257e27e8ae3b6cc7a26bde079b354ad20f3cd))


## v0.1.612 (2023-02-27)

### Fix

* fix(volvo): add domain in reading name ([`fb8f93c`](https://github.com/fhempy/fhempy/commit/fb8f93c6135b13813f6d3ccf4144739c58dd1074))

### Unknown

* Merge branch &#39;development&#39; ([`08d808e`](https://github.com/fhempy/fhempy/commit/08d808e8678a2f7ef00ae4d9dd6f2765ba061839))


## v0.1.611 (2023-02-27)

### Feature

* feat(tuya): support reset_energy ([`fb5f25f`](https://github.com/fhempy/fhempy/commit/fb5f25f36f0364cd4881d386b6b8ecc234dbee86))

* feat(tuya_cloud): support reset_energy ([`0a0b12c`](https://github.com/fhempy/fhempy/commit/0a0b12c90c2228f35d8c6d65df467c63a2b3f90e))

* feat(fhempy): add set_icon method ([`42b4260`](https://github.com/fhempy/fhempy/commit/42b4260cf74dd7b0ef68d7353244fd9e06abf9b4))

### Fix

* fix(volvo): remove sunRoofOpen as currently not working, handle exceptions on update_readings ([`e8d8e45`](https://github.com/fhempy/fhempy/commit/e8d8e45d3564d9288fa24b171099c0510a928e1f))

* fix(energie_gv_at): set label to 0 if no data received for that label ([`d88dc5d`](https://github.com/fhempy/fhempy/commit/d88dc5d6c0f1c7c2500acacf4bd23fe3b9d7afd7))

### Unknown

* Merge branch &#39;development&#39; ([`f3d04e8`](https://github.com/fhempy/fhempy/commit/f3d04e89c27507c91187a0beb14acdb2e7888a40))


## v0.1.610 (2023-02-26)

### Fix

* fix(wienernetze_smartmeter): fix imports (#120) ([`f1b2c80`](https://github.com/fhempy/fhempy/commit/f1b2c80317c298ac25fa2b1e5b7888fb993c3000))

### Unknown

* Merge branch &#39;development&#39; ([`02e1d43`](https://github.com/fhempy/fhempy/commit/02e1d439b3cc0512ac19e1f4aafe0f253a693563))


## v0.1.609 (2023-02-26)

### Fix

* fix(tuya_cloud): fix wrong scale for some product ids ([`e1008d3`](https://github.com/fhempy/fhempy/commit/e1008d3e30de58290a1f9c69501fe3a4587ec3bf))

### Unknown

* Merge branch &#39;development&#39; ([`8d122b6`](https://github.com/fhempy/fhempy/commit/8d122b6e86e4faced02407cf6c4c4f549247dec7))


## v0.1.608 (2023-02-26)

### Fix

* fix(wienernetze_smartmeter): update wiener netze api (#120) ([`2f917c1`](https://github.com/fhempy/fhempy/commit/2f917c1ef286e85962f71d71cdfd10e560ffd051))

* fix(mitemp2): fix wrong number of arguments ([`b3f4066`](https://github.com/fhempy/fhempy/commit/b3f4066613e9cd2c4cd13f2cb75768134071ea2c))

### Unknown

* Merge branch &#39;development&#39; ([`597dbbf`](https://github.com/fhempy/fhempy/commit/597dbbf70cecfa91585e134c87366b26d28bdc48))


## v0.1.607 (2023-02-25)

### Feature

* feat(wienernetze_smartmeter): testing wiener netze smartmeter ([`c8cb33d`](https://github.com/fhempy/fhempy/commit/c8cb33dc342083afe8e985596f92ce56f6ed3728))

* feat(volvo): initial release of volvo new api module ([`a69bd1b`](https://github.com/fhempy/fhempy/commit/a69bd1b42d399a66ccf5ad33a344a874f905aacc))

* feat(energie_gv_at): add more details about the current source of electricity ([`66ea3db`](https://github.com/fhempy/fhempy/commit/66ea3db36992876efa6879ba10c7a105d054470c))

### Fix

* fix(tuya): fix cur_power for prodid wifvoilfrqeo6hvu ([`b10a374`](https://github.com/fhempy/fhempy/commit/b10a374b63b8d837c993cfbbfb2432d8a2930b3e))

### Unknown

* Merge branch &#39;development&#39; ([`21eeab5`](https://github.com/fhempy/fhempy/commit/21eeab5c299a9a7851852ec2cf08ed846c745fce))


## v0.1.606 (2023-02-22)

### Feature

* feat(tuya_cloud): add energy reading ([`1ad2090`](https://github.com/fhempy/fhempy/commit/1ad2090c455fb47903007b61f32bdf4d20e6d336))

### Unknown

* Merge branch &#39;development&#39; ([`99fd2fd`](https://github.com/fhempy/fhempy/commit/99fd2fd40254fc0bfb32c8f328cc0202c158917c))


## v0.1.605 (2023-02-22)

### Fix

* fix(tuya): fix energy formula ([`f2d25b7`](https://github.com/fhempy/fhempy/commit/f2d25b79d228967915693af4972deafda21ee887))

### Unknown

* Merge branch &#39;development&#39; ([`d7a5748`](https://github.com/fhempy/fhempy/commit/d7a574833da52c00f88eefc0a18aee5cabea7c8c))


## v0.1.604 (2023-02-22)

### Feature

* feat(tuya): add energy reading ([`7231691`](https://github.com/fhempy/fhempy/commit/72316919794aec137e9243ba4808a49667e99c9f))

### Unknown

* Merge branch &#39;development&#39; ([`a74f2b0`](https://github.com/fhempy/fhempy/commit/a74f2b0d839f4eda31c814208ec996b54448d745))


## v0.1.603 (2023-02-20)

### Fix

* fix(fhempy): fix disable for modules without attributes ([`f85134d`](https://github.com/fhempy/fhempy/commit/f85134db71dd53d188fa9d3f3ceb8ae8e1598c23))

### Unknown

* Merge branch &#39;development&#39; ([`497b237`](https://github.com/fhempy/fhempy/commit/497b23781df270af8bcce0f32afb4fb05a523f00))


## v0.1.602 (2023-02-20)

### Fix

* fix(fhempy): fix disable (#118) ([`fed397a`](https://github.com/fhempy/fhempy/commit/fed397afc36ef41e54907fdadc1deecc45299501))

### Unknown

* Merge branch &#39;development&#39; ([`96da7c9`](https://github.com/fhempy/fhempy/commit/96da7c98a234cd122acac5b741a26dc07aa0b5a3))


## v0.1.601 (2023-02-20)

### Feature

* feat(fhempy): activate disable attr for all fhempy modules (#118) ([`0072cb6`](https://github.com/fhempy/fhempy/commit/0072cb6999b9727b60812e6c2393ea67d7c0d7e7))

### Unknown

* Merge branch &#39;development&#39; ([`fec4801`](https://github.com/fhempy/fhempy/commit/fec48018aacdcf2d8dbfe4c77bc39a08f6a310fd))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`72a8667`](https://github.com/fhempy/fhempy/commit/72a8667b5ca3514a4607ed181528623323e69136))


## v0.1.600 (2023-02-20)

### Feature

* feat(fhempy): support disable attr for all fhempy devices ([`196ee60`](https://github.com/fhempy/fhempy/commit/196ee602d395310222f845d849a60c87a125b8f0))

### Fix

* fix(spotify_connect_player): fix define ([`80df09c`](https://github.com/fhempy/fhempy/commit/80df09c1086cdb011801fd9cb8768dedd2ca074a))

### Unknown

* Merge branch &#39;development&#39; ([`045fcfe`](https://github.com/fhempy/fhempy/commit/045fcfe138c8ea6cbe00169d291f06ad123daae6))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`9625dc0`](https://github.com/fhempy/fhempy/commit/9625dc0589b25554e3d15337b3640c226d80f68b))


## v0.1.599 (2023-02-19)

### Feature

* feat(tuya): add productid keym9qkuywghyrvs (#128) ([`b5d9ec6`](https://github.com/fhempy/fhempy/commit/b5d9ec676e85fcb16c52a0e18dbfa68d2a6ba8bd))

### Fix

* fix(fhempy): use set ? cache only when connected ([`1c59259`](https://github.com/fhempy/fhempy/commit/1c59259d4147e95cbec9dc0473ea261c8f7833bd))

* fix(fhempy): fix tests ([`e312537`](https://github.com/fhempy/fhempy/commit/e31253790b800197b656f6a721af48989a89723e))

### Unknown

* Merge branch &#39;development&#39; ([`61b8617`](https://github.com/fhempy/fhempy/commit/61b8617d2dfa9ad0f3dba23419ed7d9800065705))


## v0.1.598 (2023-02-17)

### Fix

* fix(fhempy): fix attr handling 2 ([`322cecb`](https://github.com/fhempy/fhempy/commit/322cecb2f6ea63701add23ddfe87f3b5a3a093a6))

* fix(fhempy): fix attr handling ([`58bf90d`](https://github.com/fhempy/fhempy/commit/58bf90d95a9146383385e680fa09954a1ebd5b51))

### Unknown

* Merge branch &#39;development&#39; ([`7fd9f0b`](https://github.com/fhempy/fhempy/commit/7fd9f0b54a5364bc50394f5fb80ec2ad0f603813))


## v0.1.597 (2023-02-17)

### Fix

* fix(fhempy): fix set error ([`d651009`](https://github.com/fhempy/fhempy/commit/d6510097548d04454c1efa8336ad7b5f2375a863))

### Unknown

* Merge branch &#39;development&#39; ([`3cb7a3b`](https://github.com/fhempy/fhempy/commit/3cb7a3baebeb1e8a3fd49d888a614224886ab107))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`8de3547`](https://github.com/fhempy/fhempy/commit/8de3547a59317e7b70f55c1626b02d74f01b89a2))


## v0.1.596 (2023-02-17)

### Feature

* feat(fhempy): support set ? cache in BindingsIo ([`0615960`](https://github.com/fhempy/fhempy/commit/061596046f72d0ceb61e6f677913630f4104c164))

### Fix

* fix(fhempy): cleanup websocket message handling ([`8421824`](https://github.com/fhempy/fhempy/commit/84218242e3ca1c47a579a1c604256b7163b89899))

* fix(fhempy): use DevIo_SimpleRead ([`2fcc386`](https://github.com/fhempy/fhempy/commit/2fcc386484e96337646598874104a63f750c81c3))

### Unknown

* Merge branch &#39;development&#39; ([`abbf048`](https://github.com/fhempy/fhempy/commit/abbf04863264ee8431931703c66858a4fb405e2c))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`afb566c`](https://github.com/fhempy/fhempy/commit/afb566c782d919882e9f2b9248880b76972e8b97))


## v0.1.595 (2023-02-08)

### Fix

* fix(fhempy): fix deep recursion ([`685c12e`](https://github.com/fhempy/fhempy/commit/685c12e84bc0eef454c9cd9b1088667d25fd19da))

### Unknown

* Merge branch &#39;development&#39; ([`994683a`](https://github.com/fhempy/fhempy/commit/994683a56695ca25591e475f3fe7b32ae8d09c74))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`c0885e0`](https://github.com/fhempy/fhempy/commit/c0885e0afc92c1eeb453f1fe1af91df58b32c8a9))


## v0.1.594 (2023-02-08)

### Fix

* fix(fhempy): increase fhem timeout to 180s ([`919b5c3`](https://github.com/fhempy/fhempy/commit/919b5c3429c59bb3364c07d79c06dddd186936d7))

* fix(fhempy): do not drop messags on high load ([`30b43dd`](https://github.com/fhempy/fhempy/commit/30b43ddc069d159a785943d11dd3eb3bde595e0d))

* fix(tuya_cloud): do not update readings if they didn&#39;t change - reduce load on fhem ([`7bd27bb`](https://github.com/fhempy/fhempy/commit/7bd27bb252b3bc220096e3e4e777048f5386cf6c))

* fix(fhempy): support Python 3.9 and higher ([`1a672c5`](https://github.com/fhempy/fhempy/commit/1a672c582fc8e1651f832e933f3f6c37bb427c23))

### Unknown

* Merge branch &#39;development&#39; ([`17251b1`](https://github.com/fhempy/fhempy/commit/17251b156cebff5615cf954c64ad36fad21d6391))


## v0.1.593 (2023-02-04)

### Fix

* fix(fhempy): revert readingsBulkUpdate lock ([`dada627`](https://github.com/fhempy/fhempy/commit/dada6278574018b4b19890859978149c218b701b))

### Unknown

* Merge branch &#39;development&#39; ([`37d6858`](https://github.com/fhempy/fhempy/commit/37d6858dccf4d090b2db7d91da3da464c6e2a226))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`bfaf653`](https://github.com/fhempy/fhempy/commit/bfaf65335bb9f6dd0484d72eaeac4c9ea4885e58))


## v0.1.592 (2023-02-04)

### Fix

* fix(fhempy): revert ping/pong support ([`ff5a3b3`](https://github.com/fhempy/fhempy/commit/ff5a3b33d37635c94a24c9db05508ad652228631))

### Unknown

* Merge branch &#39;development&#39; ([`06743c7`](https://github.com/fhempy/fhempy/commit/06743c7abbae3983458864882ee1d0d9fb0e10e4))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`b770166`](https://github.com/fhempy/fhempy/commit/b77016653440deff44205bbbb9fedeaab6262589))


## v0.1.591 (2023-02-04)

### Fix

* fix(fhempy): fix websocket ping/pong ([`5ab09fc`](https://github.com/fhempy/fhempy/commit/5ab09fc28bacde1277d9f25459f41cf817d41434))

### Unknown

* Merge branch &#39;development&#39; ([`516879d`](https://github.com/fhempy/fhempy/commit/516879dcd7a087bc6aa2769c7eb94b771ebb2a9a))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`49a5eee`](https://github.com/fhempy/fhempy/commit/49a5eee72eab673ebebaae016e8aaaf200630d04))


## v0.1.590 (2023-02-04)

### Fix

* fix(fhempy): support websocket ping/pong ([`814c009`](https://github.com/fhempy/fhempy/commit/814c009a06e1a42b80fbbc15c4f380fc471ae193))

* fix(fhempy): do not mix different readingsBulkUpdates, increase fhem timeout to 180s ([`b0d377e`](https://github.com/fhempy/fhempy/commit/b0d377ed80f26ea069d53d856343cc53e79568b6))

### Unknown

* Merge branch &#39;development&#39; ([`f372170`](https://github.com/fhempy/fhempy/commit/f37217020e07b13473bdbc523fc531c00b376fff))


## v0.1.589 (2023-02-03)

### Chore

* chore: always update controls first ([`25e86d3`](https://github.com/fhempy/fhempy/commit/25e86d3d54501ff871287b7cdf17379a6b0c44c1))

### Fix

* fix(tuya): set DEVICEID for offline devices ([`4bc9951`](https://github.com/fhempy/fhempy/commit/4bc9951faf0a24e867f484f1d61add681bdc64b0))

### Unknown

* Merge branch &#39;development&#39; ([`7458617`](https://github.com/fhempy/fhempy/commit/74586178009c74a27264452c2093906814f939bb))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`a359e41`](https://github.com/fhempy/fhempy/commit/a359e41d691cdb47f301558a45194e17cd27298f))


## v0.1.588 (2023-02-02)

### Feature

* feat(fhempy): enable readme again ([`761dc85`](https://github.com/fhempy/fhempy/commit/761dc853a23e1c8a7fd6f7806838d30d74db7a50))

* feat(fhempy): log error when fhempy took longer than 1s to reply to fhem ([`af15f07`](https://github.com/fhempy/fhempy/commit/af15f073bc51c63cb2a5fe72fcb52933b19abdce))

### Fix

* fix(tuya_cloud): fix undefine ([`cc06489`](https://github.com/fhempy/fhempy/commit/cc06489669512bfdc32d24ab264043a038414f86))

* fix(fhempy): fix NO RESPONSE in some situations ([`9b05dba`](https://github.com/fhempy/fhempy/commit/9b05dba39fc7442de602a94bef0612283ab17e93))

* fix(fhempy): fix checkIfDeviceExists, log error when fhem takes longer than 5s, ensure BeginUpdate call before EndUpdate ([`40119f9`](https://github.com/fhempy/fhempy/commit/40119f97e0643898e115827450b2bd968a23d47b))

* fix(fhempy): update websockets library ([`fc18898`](https://github.com/fhempy/fhempy/commit/fc18898fb559a97779d476b6f0f0e9aeaeb89220))

### Unknown

* Merge branch &#39;development&#39; ([`5c05c74`](https://github.com/fhempy/fhempy/commit/5c05c749a7995094587866f639b03fde5340fada))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`985d549`](https://github.com/fhempy/fhempy/commit/985d549884b9cd2eada0c4ae4589f5c3b5012e26))


## v0.1.587 (2023-02-01)

### Fix

* fix(fhempy): always handle messages on the receiver queue ([`bbeb97c`](https://github.com/fhempy/fhempy/commit/bbeb97c467c9d7a5f2046044081567540bd71fa4))

### Unknown

* Merge branch &#39;development&#39; ([`b75a19e`](https://github.com/fhempy/fhempy/commit/b75a19e1b38510840f5d7601b87179fa53941dcb))


## v0.1.586 (2023-02-01)

### Feature

* feat(fhempy): set rssi reading for all ble devices ([`faa743a`](https://github.com/fhempy/fhempy/commit/faa743a81875a39886723b36d61e75618fac0834))

### Fix

* fix(blue_connect): remove rssi as it is covered within core ble ([`a30591f`](https://github.com/fhempy/fhempy/commit/a30591f1bf5708f9f2acf7a6323e6737a845343d))

### Unknown

* Merge branch &#39;development&#39; ([`f00d3db`](https://github.com/fhempy/fhempy/commit/f00d3dbe936a4d32090c787c8bbba885bec4cf94))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`4f5059f`](https://github.com/fhempy/fhempy/commit/4f5059f81b7eef26b5845a6fa99df95c9727f673))


## v0.1.585 (2023-01-31)

### Fix

* fix(fhempy): update devStateIcon for all users ([`b438bcc`](https://github.com/fhempy/fhempy/commit/b438bccf2f4d3c6cf2725544aaacd125b545d7a7))

* fix(fhempy): add devicename to log output ([`c928e23`](https://github.com/fhempy/fhempy/commit/c928e23a1962a157359391583de5448b16563c69))

### Unknown

* Merge branch &#39;development&#39; ([`b18c17c`](https://github.com/fhempy/fhempy/commit/b18c17cbfb3403e39cf0bcf64113f7e19e14c860))


## v0.1.584 (2023-01-31)

### Fix

* fix(fhempy): change init_done response to int ([`c0a1b9b`](https://github.com/fhempy/fhempy/commit/c0a1b9bcd86469f67929ffb638129e7e371464fa))

### Unknown

* Merge branch &#39;development&#39; ([`b4ef798`](https://github.com/fhempy/fhempy/commit/b4ef798670195abb2ad31e92373fd1e54ce4ce54))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`35f85fe`](https://github.com/fhempy/fhempy/commit/35f85fe9d90290c0e1d0186902eb2c9a558d5c71))


## v0.1.583 (2023-01-31)

### Fix

* fix(fhempy): update attr_ver ([`83ac51d`](https://github.com/fhempy/fhempy/commit/83ac51de976afbae6b88aefb2f9cb70560df1e2c))

### Unknown

* Merge branch &#39;development&#39; ([`38bbbdc`](https://github.com/fhempy/fhempy/commit/38bbbdc177f702af0a1006ef41cc5bc844d72de5))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`e118c2f`](https://github.com/fhempy/fhempy/commit/e118c2f615616f3a91aaea8e00856d2a0837bcea))


## v0.1.582 (2023-01-31)

### Fix

* fix(fhempy): do not skip messages older than 10s ([`afc3961`](https://github.com/fhempy/fhempy/commit/afc39612a91a370fe670591e6eb83a8da6144414))

* fix(tuya_cloud): fix warning when searching for DEVICEID ([`4e8f80e`](https://github.com/fhempy/fhempy/commit/4e8f80eb0f8b62aa3ffc6986e16bf7be7637f8e5))

* fix(fhempy): fix restart button ([`253fb16`](https://github.com/fhempy/fhempy/commit/253fb16b9e3c63538e35761c3656465e5214a59e))

### Unknown

* Merge branch &#39;development&#39; ([`580a6de`](https://github.com/fhempy/fhempy/commit/580a6defd1ce75de515bdc13db2df306b4e2d875))


## v0.1.581 (2023-01-30)

### Fix

* fix(fhempy): add logging if readingsBeginUpdate call is missing ([`fd893dd`](https://github.com/fhempy/fhempy/commit/fd893dd6ce81428b703fd41e14be4dade3df3115))

### Unknown

* Merge branch &#39;development&#39; ([`cc34732`](https://github.com/fhempy/fhempy/commit/cc347320e427bfb2f0392fdbf0091c742464ba83))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`f5e85dc`](https://github.com/fhempy/fhempy/commit/f5e85dc08849b5b8df1c891f0c70454f8b374ceb))


## v0.1.580 (2023-01-29)

### Feature

* feat(tuya_cloud): create only devices which do not exist as tuya or tuya_cloud device ([`299f393`](https://github.com/fhempy/fhempy/commit/299f393a65d176b3ca26396fc7084a5fc6803d63))

### Fix

* fix(fhempy): change PYTHONTYPE to FHEMPYTYPE ([`b8d464e`](https://github.com/fhempy/fhempy/commit/b8d464e90fab9a0718c63e0c2b948f424f307048))

* fix(fhempy): handle WARNINGS in log message ([`2d19476`](https://github.com/fhempy/fhempy/commit/2d194760ce40905b01293dbb7b978f3cfc69cda7))

* fix(fhempy): update text for hard restart ([`22fe106`](https://github.com/fhempy/fhempy/commit/22fe106d93e89e5343d533ceaeccc7c959376950))

### Unknown

* Merge branch &#39;development&#39; ([`af32a11`](https://github.com/fhempy/fhempy/commit/af32a11f4a953ee544ef87cf05571bcee91e6c60))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`2acee77`](https://github.com/fhempy/fhempy/commit/2acee77e407a9905150d10e5f32c6f5db90727b4))


## v0.1.579 (2023-01-29)

### Feature

* feat(fhempy): add restart button ([`13c93d1`](https://github.com/fhempy/fhempy/commit/13c93d1d8d5c16218618d3daf180e861f68b75d1))

### Unknown

* Merge branch &#39;development&#39; ([`83dd602`](https://github.com/fhempy/fhempy/commit/83dd602f861bf3858460fb793304bd0d5363a4e4))

* Merge branch &#39;master&#39; into development ([`1929a2a`](https://github.com/fhempy/fhempy/commit/1929a2aa1aad38d349c8cb9f5332dfee5f5117dc))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`570bbd4`](https://github.com/fhempy/fhempy/commit/570bbd458d47342701b90736118e7da835aef3c4))


## v0.1.578 (2023-01-26)

### Feature

* feat(fhempy): support debug with verbose 5 ([`6d96d9b`](https://github.com/fhempy/fhempy/commit/6d96d9b71a6eba1914b0faef3a5098cd2b9554ef))

### Unknown

* Merge branch &#39;development&#39; ([`120093d`](https://github.com/fhempy/fhempy/commit/120093df776f310fe759b89a1ef9051d25ad7537))


## v0.1.577 (2023-01-26)

### Unknown

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`fb30dff`](https://github.com/fhempy/fhempy/commit/fb30dff486b38cb42ee30718cd4f8d4551626b04))


## v0.1.576 (2023-01-26)

### Feature

* feat(fhempy): update devStateIcon ([`69ba9e1`](https://github.com/fhempy/fhempy/commit/69ba9e1e521eca19bd5853e24f1953a20c4bb748))

* feat(fhempy): update devStateIcon ([`457d60b`](https://github.com/fhempy/fhempy/commit/457d60bfbd3196b2d1629f29cdcdd05300a875e7))

### Fix

* fix(fhempy): debug log cleanup ([`7a54c9d`](https://github.com/fhempy/fhempy/commit/7a54c9d04a12c6531fb92b8eb53da88f7724e5ba))

### Unknown

* Merge branch &#39;development&#39; ([`b7239c4`](https://github.com/fhempy/fhempy/commit/b7239c4a6cf459ed66d433ac4e9deacdeef37475))


## v0.1.575 (2023-01-24)

### Fix

* fix(tuya): try to reconnect every 15s ([`8f13ab2`](https://github.com/fhempy/fhempy/commit/8f13ab2b12639afc844ea594ade19653cb603cc1))

### Unknown

* Merge branch &#39;development&#39; ([`48cca7e`](https://github.com/fhempy/fhempy/commit/48cca7e53f97cc42028d9eab300ffa98d9c34e5c))


## v0.1.574 (2023-01-24)


## v0.1.573 (2023-01-24)

### Fix

* fix(tuya): proper import of fhempy tinytuya ([`d9eb64b`](https://github.com/fhempy/fhempy/commit/d9eb64bbe783d23a34b78bc0850b3b731cd6a766))

### Unknown

* Merge branch &#39;development&#39; ([`40799a9`](https://github.com/fhempy/fhempy/commit/40799a9d1c8c70424efdc0bc1f6abe5f738a6f6f))


## v0.1.572 (2023-01-24)

### Fix

* fix(eq3bt): fix set comfort ([`c4c0d57`](https://github.com/fhempy/fhempy/commit/c4c0d576c8d9578a1865ec721fbc9a1c3c09a97f))

### Unknown

* Merge branch &#39;development&#39; ([`46cf99e`](https://github.com/fhempy/fhempy/commit/46cf99e27e34f5b74c0517e087a76f559178fd18))


## v0.1.571 (2023-01-23)

### Feature

* feat(tuya): support logging in tt core ([`495a85a`](https://github.com/fhempy/fhempy/commit/495a85a24ff07d674ab1735799846c3532ff347d))

### Unknown

* Merge branch &#39;development&#39; ([`0a10ffe`](https://github.com/fhempy/fhempy/commit/0a10ffe8165845999f08eb214183f87a7f83515e))


## v0.1.570 (2023-01-23)

### Fix

* fix(tuya): fix update loops ([`28b66c8`](https://github.com/fhempy/fhempy/commit/28b66c8076981c9af2251e4d7e19c4cf77dfc97f))

### Unknown

* Merge branch &#39;development&#39; ([`b579ae8`](https://github.com/fhempy/fhempy/commit/b579ae883609a0ea779a708d91742a6350af9c9b))


## v0.1.569 (2023-01-23)

### Feature

* feat(esphome): update to 2022.12.5 ([`9007f0e`](https://github.com/fhempy/fhempy/commit/9007f0e606c9f6a73da82675acca2bad4eea26be))

### Fix

* fix(fhempy): use services property as get_services is deprecated ([`6930105`](https://github.com/fhempy/fhempy/commit/6930105cb48097ae7decd040cbe5debc22e666bf))

### Unknown

* Merge branch &#39;development&#39; ([`a0e2733`](https://github.com/fhempy/fhempy/commit/a0e27333ddc1f591b2ea55b69990064a54f749ac))


## v0.1.568 (2023-01-23)

### Fix

* fix(fhempy): fix unknown bluetooth manufacturer error ([`376aaa1`](https://github.com/fhempy/fhempy/commit/376aaa14dca71fef5e29844916b8ab6aa319cb69))

### Unknown

* Merge branch &#39;development&#39; ([`f3aa2fb`](https://github.com/fhempy/fhempy/commit/f3aa2fb7a98504617767221bd18c0adfe9ab8a59))


## v0.1.567 (2023-01-21)

### Fix

* fix(tuya): fix factor 10 for productid 37mnhia3pojleqfh ([`4e9f479`](https://github.com/fhempy/fhempy/commit/4e9f479d9c254a587450f81e93fd0038cf88a5f9))

* fix(tuya_cloud): create device with tuya_cloud_DEVICEID ([`39b8bf0`](https://github.com/fhempy/fhempy/commit/39b8bf050271e477d7431c7d49ed36dd0cfc893d))

### Unknown

* Merge branch &#39;development&#39; ([`162c4ea`](https://github.com/fhempy/fhempy/commit/162c4ea37dd782eac7d06e5117efee823e4c2eb1))


## v0.1.566 (2023-01-20)

### Fix

* fix(tuya): do not poll device on scan ([`7540c16`](https://github.com/fhempy/fhempy/commit/7540c16b96255e1f0eebd68a37ceaa3fc216f8e7))

### Unknown

* Merge branch &#39;development&#39; ([`f1956a9`](https://github.com/fhempy/fhempy/commit/f1956a998ef0378fd750ca1d748eca20b402226a))


## v0.1.565 (2023-01-20)

### Fix

* fix(tuya): fix another possible high load bug ([`735f0f0`](https://github.com/fhempy/fhempy/commit/735f0f0ff0ec06dfbf8f65faea084bad6af0e893))

### Unknown

* Merge branch &#39;development&#39; ([`a2508fd`](https://github.com/fhempy/fhempy/commit/a2508fd530d498a6901ce37ea24a4d83298babdf))


## v0.1.564 (2023-01-20)

### Feature

* feat(esphome): update esphome library ([`5ba11a9`](https://github.com/fhempy/fhempy/commit/5ba11a9f2621b7623e49373f527a77a73ae761aa))

### Fix

* fix(tuya): possible high load fix ([`f177628`](https://github.com/fhempy/fhempy/commit/f177628924616669e159d47f7482b2961fb32aa3))

### Unknown

* Merge branch &#39;development&#39; ([`e06182b`](https://github.com/fhempy/fhempy/commit/e06182b37b0af26ab831343b313692cd0f0bda7a))


## v0.1.563 (2023-01-19)

### Fix

* fix(tuya): do not run update_readings in parallel ([`43a588e`](https://github.com/fhempy/fhempy/commit/43a588ef989f50f9b46526c8d4a1bfe50d57b793))

### Unknown

* Merge branch &#39;development&#39; ([`1c6e621`](https://github.com/fhempy/fhempy/commit/1c6e6211f1e5665229f6baf736987a00f095f2fc))


## v0.1.562 (2023-01-19)

### Feature

* feat(tuya): show error message in state reading on getdevices error ([`f1ebfb2`](https://github.com/fhempy/fhempy/commit/f1ebfb2007e0c59aba768908b44eb7303de831b6))

### Unknown

* Merge branch &#39;development&#39; ([`c2551f9`](https://github.com/fhempy/fhempy/commit/c2551f9b5f8b0c99abdab36e4d3dc65655463371))


## v0.1.561 (2023-01-17)

### Feature

* feat(blue_connect): support blue_connect restart ([`1d6cb45`](https://github.com/fhempy/fhempy/commit/1d6cb458451a5cdfbae03349b2a012a23f640f27))

### Fix

* fix(mitemp2): notifications are enabled in ble lib ([`75918bf`](https://github.com/fhempy/fhempy/commit/75918bfa09ec8c40be88c3fefa5b92b2ac558040))

* fix(blue_connect): write gatt event when not connected - lib automatically reconnects ([`29b71c0`](https://github.com/fhempy/fhempy/commit/29b71c0714bcfdecce42a126488ecd64952b2a4c))

### Unknown

* Merge branch &#39;development&#39; ([`0da94f3`](https://github.com/fhempy/fhempy/commit/0da94f3e68b48d411f3a67a6383231e654a34886))


## v0.1.560 (2023-01-17)

### Fix

* fix(fhempy): disable asyncio debug ([`b08559b`](https://github.com/fhempy/fhempy/commit/b08559bc64382b26e91bd5aef984e0c78f2b8d2d))

* fix(fhempy): bluetooth fixes ([`68db2d6`](https://github.com/fhempy/fhempy/commit/68db2d6e1bbfda46f3287a84cb457537cb224e6e))

* fix(skodaconnect): Skoda Connect Update BaseLib (#121) ([`08a363f`](https://github.com/fhempy/fhempy/commit/08a363f989cf4cb399455c96cbd104633155b5cc))

### Unknown

* Merge branch &#39;development&#39; ([`dfb922f`](https://github.com/fhempy/fhempy/commit/dfb922f8968cc5ed4e319efe6de48529da54da68))


## v0.1.559 (2023-01-16)

### Fix

* fix(fhempy): services not working, use get_services() ([`fbea26f`](https://github.com/fhempy/fhempy/commit/fbea26f3d15b7bdc5384b9c84fa18d3c75bfc2fa))

### Unknown

* Merge branch &#39;development&#39; ([`850717d`](https://github.com/fhempy/fhempy/commit/850717d710ba62bd4eb8936c63d45784d235cde6))


## v0.1.558 (2023-01-16)

### Fix

* fix(fhempy): fix ble notification subscription ([`a3fc5e5`](https://github.com/fhempy/fhempy/commit/a3fc5e5f412a9cbd232ff70601ecbeb76b9d7660))

### Unknown

* Merge branch &#39;development&#39; ([`3b82a00`](https://github.com/fhempy/fhempy/commit/3b82a009e39604661cbbf557d764d30275e00fbb))


## v0.1.557 (2023-01-16)

### Fix

* fix(eq3bt): handle timeout ([`c18783e`](https://github.com/fhempy/fhempy/commit/c18783e52f7c23a161e1f09ff4a415681e764171))

* fix(fhempy): increase timeout ([`6c9166b`](https://github.com/fhempy/fhempy/commit/6c9166b81a956d2c88f55c84abf1cae46230ea2a))

* fix(eq3bt): add exception instead of error logging ([`7a6c2bc`](https://github.com/fhempy/fhempy/commit/7a6c2bca20bae055b96fa8deaeff41dd37035375))

* fix(fhempy): fix bluetooth reconnect ([`5a6b6bc`](https://github.com/fhempy/fhempy/commit/5a6b6bc94c998ac1ce8a027fe5d6622d5d0288e7))

### Unknown

* Merge branch &#39;development&#39; ([`e9aafa8`](https://github.com/fhempy/fhempy/commit/e9aafa8418fdc3ca90fe0fe33bfcdba31eb4ed11))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`1095c19`](https://github.com/fhempy/fhempy/commit/1095c194fd46c4c7587019bf92618ccb9c236a38))


## v0.1.556 (2023-01-15)


## v0.1.555 (2023-01-15)

### Feature

* feat(fhempy): add restart icon and change colour of update icon if update available ([`ed8342d`](https://github.com/fhempy/fhempy/commit/ed8342dc4e742e94026f0c9055957c3663a1e244))

### Fix

* fix(mitemp2): setup notify before write ([`5cb7ba1`](https://github.com/fhempy/fhempy/commit/5cb7ba10148dcc663875266176131b9d588a5ae2))

* fix(gfprobt): fix circular import ([`c09a74c`](https://github.com/fhempy/fhempy/commit/c09a74c4eec0e32154467e48a20f856fc8356be0))

* fix(mitemp2): fix circular import ([`3828bad`](https://github.com/fhempy/fhempy/commit/3828badb3af7c2bc18eefb57cbc703bf396fe090))

* fix(blue_connect): stop loop when cancelled ([`380d9aa`](https://github.com/fhempy/fhempy/commit/380d9aa739a85d35a4cfbfeb61f555aa404c2ba7))

* fix(eq3bt): remove presence reading, stop loop on cancel ([`5a3b1a1`](https://github.com/fhempy/fhempy/commit/5a3b1a12f2643d9e74e9b8a7824255737b48dc2e))

* fix(eq3bt): wait a few seconds after each thermostat query, fix friday schedule query ([`fe0d183`](https://github.com/fhempy/fhempy/commit/fe0d18372c0cc596534c068e45b917e3625ad123))

* fix(eq3bt): fix notification callback argument ([`c35c354`](https://github.com/fhempy/fhempy/commit/c35c354b25552f90b20ef65b41b081e4aad62bc5))

* fix(eq3bt): fix circular import ([`f1240b2`](https://github.com/fhempy/fhempy/commit/f1240b2bc28526c78ce99560cd6b8c059b62d114))

* fix(eq3bt): fix arguments ([`fe7d56c`](https://github.com/fhempy/fhempy/commit/fe7d56cdf259c5ee43d99a15786c943ff812b0f8))

* fix(eq3bt): bleak fixes ([`56365a3`](https://github.com/fhempy/fhempy/commit/56365a3fe7f555a63faaa889bc4c5852aca82604))

* fix(eq3bt): use uuid instead of handle ([`97947c2`](https://github.com/fhempy/fhempy/commit/97947c2b1e6285a83d1f8f4aa766268dbcbf13d2))

* fix(eq3bt): add await for disconnect ([`80edfcc`](https://github.com/fhempy/fhempy/commit/80edfccc9b7ef49aa9f29178661b64cfaeeced67))

* fix(blue_connect): connect only when not connected ([`5f2d39e`](https://github.com/fhempy/fhempy/commit/5f2d39e6db366c0eb771fb3f586b8e2656b62376))

* fix(fhempy): ble disconnect only when connected ([`598b4f8`](https://github.com/fhempy/fhempy/commit/598b4f8e17f71ee66847e534bbedcc873e91adc7))

* fix(fhempy): remove old bluepy library ([`6f8b046`](https://github.com/fhempy/fhempy/commit/6f8b0469d1b59ce83aba4901c757763909f50f7f))

* fix(fhempy): add bluetooth libs to modules instead of fhempy installation requirement ([`a0d321e`](https://github.com/fhempy/fhempy/commit/a0d321edd045109eb50f0ecabaafd48055be37fb))

* fix(discover_ble): update bleak library ([`3e46df8`](https://github.com/fhempy/fhempy/commit/3e46df892a52c9abfc8d8b70debe05732d747ddf))

* fix(eq3bt): use bleak library ([`6de3ef2`](https://github.com/fhempy/fhempy/commit/6de3ef29648d839e369fb0b2ec40dfef29964b53))

* fix(gfprobt): use bleak library ([`407eec6`](https://github.com/fhempy/fhempy/commit/407eec69cd5be79d0c3b0fc52cf3f766d89d4e8a))

* fix(mitemp2): use bleak library ([`3ff7d74`](https://github.com/fhempy/fhempy/commit/3ff7d7478ecb78f6c67952045203ce91fad28d63))

* fix(ble_reset): add missing import ([`c5f3c55`](https://github.com/fhempy/fhempy/commit/c5f3c55ccd0dab6cc6afbce5ff505ec619fa54e7))

* fix(fhempy): fix BluetoothLE update_adapters ([`e6b91f8`](https://github.com/fhempy/fhempy/commit/e6b91f8f5af1d3308aaa9cf85ddc8d35e4beb217))

* fix(ble_reset): new ble reset based on bluetooth-auto-recovery lib ([`0fed3e7`](https://github.com/fhempy/fhempy/commit/0fed3e74c247a43136f99fa03d9404752de3b2d7))

* fix(blue_connect): BluetoothLE core fixes for reconnects ([`0cce921`](https://github.com/fhempy/fhempy/commit/0cce921a725dc0f9fca6a2c86beef9bc8d26342e))

### Unknown

* Merge branch &#39;development&#39; ([`d68c9d4`](https://github.com/fhempy/fhempy/commit/d68c9d439ff59d93a320933b6e6fee3e794b37ad))


## v0.1.554 (2023-01-12)

### Fix

* fix(fhempy): fix bluetoothle core ([`5db91b5`](https://github.com/fhempy/fhempy/commit/5db91b53ebf85713c744253eebd3e5e11be28189))

### Unknown

* Merge branch &#39;development&#39; ([`f72fa26`](https://github.com/fhempy/fhempy/commit/f72fa265c44d388458edb5a72ae9336168632a95))


## v0.1.553 (2023-01-12)

### Unknown

* Merge branch &#39;development&#39; ([`8dc29f9`](https://github.com/fhempy/fhempy/commit/8dc29f9f90ca1dea33c50cea5192953b5b0a22b5))

* BREAKING CHANGE: remove 3.8 support due to bluetooth change ([`d2dd1c7`](https://github.com/fhempy/fhempy/commit/d2dd1c7d1f58066eb1fab37e3537a85bd0362385))

* Remove 3.8 support ([`f134296`](https://github.com/fhempy/fhempy/commit/f134296933926d0a98412a6d9c75f0b70382d2f7))


## v0.1.552 (2023-01-12)

### Fix

* fix(blue_connect): fix register_disconnect_listener ([`21d01fc`](https://github.com/fhempy/fhempy/commit/21d01fcb24e355e2eaab56e4b89f3fa5e1d3bd5b))

### Unknown

* Merge branch &#39;development&#39; ([`8f40c6f`](https://github.com/fhempy/fhempy/commit/8f40c6f069d46e44860d28e736b0c013f1574361))


## v0.1.551 (2023-01-12)

### Feature

* feat(fhempy): add bleak bluetooth support ([`109d88f`](https://github.com/fhempy/fhempy/commit/109d88f767c61d29944d62ba137ef9c6c3bb4652))

### Fix

* fix(blue_connect): use fhempy bluetoothle core ([`2c31854`](https://github.com/fhempy/fhempy/commit/2c31854f4bab7bedfbc6b4a84789fc9511525406))

### Unknown

* Merge branch &#39;development&#39; ([`70d03e6`](https://github.com/fhempy/fhempy/commit/70d03e626d2ad401acb0ab2e7fa61f88b2fad2f5))


## v0.1.550 (2023-01-10)

### Feature

* feat(blue_connect): add connection reading ([`b3eddac`](https://github.com/fhempy/fhempy/commit/b3eddac38715039bdd972e35493beab5b5b2f713))

### Fix

* fix(blue_connect): fix max ph value ([`88d2333`](https://github.com/fhempy/fhempy/commit/88d23335e99e44618abbee30efbd1277bd601dac))

* fix(blue_connect): set variable to None on disconnect, change exception logging ([`6e1957d`](https://github.com/fhempy/fhempy/commit/6e1957d5ffd85b9fe7aae797809ec36b4b8ab7d4))

* fix(blue_connect): disconnect on Undefine, wait 30s if device couldn&#39;t be discovered ([`26ae0fe`](https://github.com/fhempy/fhempy/commit/26ae0fef29cbbd56e1c185a931905b67cd8c6155))

### Unknown

* Merge branch &#39;development&#39; ([`2470c97`](https://github.com/fhempy/fhempy/commit/2470c97b630b52916fa5e24d6eb2a7110f4beae3))


## v0.1.549 (2023-01-10)

### Fix

* fix(tuya): fix master_switch error in log ([`c245438`](https://github.com/fhempy/fhempy/commit/c245438c58d37a62db9632cf9fecaa5631c26357))

* fix(blue_connect): fix bleak connection ([`92beb09`](https://github.com/fhempy/fhempy/commit/92beb09a0d1afa9edd83014ec772d34052a830f4))

* fix(blue_connect): fix Undefine if no task started yet ([`8ef8f5d`](https://github.com/fhempy/fhempy/commit/8ef8f5dcc2058a73ffe3c85451172cad269d9e0e))

### Unknown

* Merge branch &#39;development&#39; ([`89cf769`](https://github.com/fhempy/fhempy/commit/89cf7691e7df87dfd0501ee0b1f080ffc1808704))


## v0.1.548 (2023-01-10)

### Fix

* fix(blue_connect): testing use of bleak instead of bluepy ([`0a6d93d`](https://github.com/fhempy/fhempy/commit/0a6d93dbc0f965b92cfb275f9a64bc6fdd8ff2e5))

### Unknown

* Merge branch &#39;development&#39; ([`e06b633`](https://github.com/fhempy/fhempy/commit/e06b6338e2b32acdcaaee5ebbd748a46eb4e5263))


## v0.1.547 (2023-01-08)

### Feature

* feat(tuya): change to colour mode when changing colour data ([`5c64e4d`](https://github.com/fhempy/fhempy/commit/5c64e4d0fd9254b7178097b6460528e15c7d50bf))

### Unknown

* Merge branch &#39;development&#39; ([`831c600`](https://github.com/fhempy/fhempy/commit/831c6004ef96c8f8da3eabca204570da3a6a60cc))


## v0.1.546 (2023-01-08)

### Feature

* feat(tuya): add generic master switch detection ([`65c4023`](https://github.com/fhempy/fhempy/commit/65c40239d381277e46bc417bdbc3f5f85f848e62))

### Unknown

* Merge branch &#39;development&#39; ([`19b6eb0`](https://github.com/fhempy/fhempy/commit/19b6eb08c72d86190e54fc4099deb76f8f3f18fa))


## v0.1.545 (2023-01-07)

### Fix

* fix(tuya): fix RGB colour_data_v2 ([`c991e09`](https://github.com/fhempy/fhempy/commit/c991e0940ce8213ebac3b803d243dc0174e90257))

### Unknown

* Merge branch &#39;development&#39; ([`76a93e4`](https://github.com/fhempy/fhempy/commit/76a93e467fff91cf89036ea78ada62d33651afd9))


## v0.1.544 (2023-01-07)

### Fix

* fix(meross): fix http api calls by meross-iot lib upgrade ([`f17047d`](https://github.com/fhempy/fhempy/commit/f17047d7fd8e40f478c503df3cd4b43e3d579a78))

### Unknown

* Merge branch &#39;development&#39; ([`12ecff2`](https://github.com/fhempy/fhempy/commit/12ecff21589662e7d5eb706daa4b530f0ea29998))


## v0.1.543 (2023-01-06)

### Fix

* fix(fhempy): increase timeouts for function handling as fhem answers sometimes take more time on high load ([`e3693a2`](https://github.com/fhempy/fhempy/commit/e3693a297cf05d5c7783c80c887193478bae0eb5))

### Unknown

* Merge branch &#39;development&#39; ([`e4dcd80`](https://github.com/fhempy/fhempy/commit/e4dcd804193af11bc906879309aa79226519672b))


## v0.1.542 (2023-01-06)

### Feature

* feat(tuya): add error handling if getdevices returns error from tuya cloud ([`175d35a`](https://github.com/fhempy/fhempy/commit/175d35a7f6bd97400c2d5c7bf51c4fc0f8142dfe))

### Fix

* fix(skodaconnect): Update BaseLib to 1.3.2 (#115)

* Update BaseLib to 1.3.0 (New token handling URLs)

* Update BaseLib to 1.3.2,
Modify skodaconnect.py  to work with BaseLib &gt; 1.3.0 ([`dbbb549`](https://github.com/fhempy/fhempy/commit/dbbb549d81dd876f1dead23fac0b2619cf03e6e6))

### Unknown

* Merge branch &#39;development&#39; ([`913b8ff`](https://github.com/fhempy/fhempy/commit/913b8ffaf10a089ebb520a1721db19c1bf4aff41))


## v0.1.541 (2023-01-05)

### Fix

* fix(fhempy): fix device rename ([`4f1f5ea`](https://github.com/fhempy/fhempy/commit/4f1f5ea1979fd9810c3364696768dd627e35b238))

### Unknown

* Merge branch &#39;development&#39; ([`fcc8876`](https://github.com/fhempy/fhempy/commit/fcc887639d01efa2a062c59a3a1da8852b52bd2f))


## v0.1.540 (2023-01-04)

### Fix

* fix(skodaconnect): Update BaseLib to 1.3.0 (New token handling URLs) (#111) ([`8d4f53e`](https://github.com/fhempy/fhempy/commit/8d4f53e8a78f45669833a1db4c27f737b753ec8a))

### Unknown

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`5c6f99c`](https://github.com/fhempy/fhempy/commit/5c6f99c70e3bfa150a2b2b2eea2b986a549470ab))


## v0.1.539 (2023-01-04)

### Fix

* fix(fhempy): create fhempy_log only on first setup ([`309ce46`](https://github.com/fhempy/fhempy/commit/309ce46ef504f592d483c8ff625522f18f381141))

### Unknown

* Merge branch &#39;development&#39; ([`eb287c1`](https://github.com/fhempy/fhempy/commit/eb287c172dcd1d94456cc6af35b8646d912c0f86))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`f9ef180`](https://github.com/fhempy/fhempy/commit/f9ef1807fc7ac22bbbe00abfc8169b5175098e6d))


## v0.1.538 (2023-01-02)

### Fix

* fix(fhempy): fix fhempy_log ([`b5125ab`](https://github.com/fhempy/fhempy/commit/b5125abfcd4ecff0609d15453cbb335f6500afc2))

### Unknown

* Merge branch &#39;development&#39; ([`b21c266`](https://github.com/fhempy/fhempy/commit/b21c2661924062cf4e401775caf395e330fc4986))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`c17bd25`](https://github.com/fhempy/fhempy/commit/c17bd2542ce89911401b59f4f45e15e43e5e45fd))


## v0.1.537 (2023-01-02)

### Fix

* fix(fhempy): fix fhempy_log creation ([`b3d3f76`](https://github.com/fhempy/fhempy/commit/b3d3f766f0409e6441288a295229559bd965bf32))

### Unknown

* Merge branch &#39;development&#39; ([`c5fb297`](https://github.com/fhempy/fhempy/commit/c5fb297b055ed09f20cd27908c103aaffac7c34a))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`190f8ab`](https://github.com/fhempy/fhempy/commit/190f8abe580681663f3704e998ab1876a8a25ebe))


## v0.1.536 (2023-01-02)

### Feature

* feat(tuya): support colour_data reading ([`d7e3241`](https://github.com/fhempy/fhempy/commit/d7e3241b9bbd9f91fbc0c24d8e4b36324c152dc9))

* feat(fhempy): add restart info in state reading ([`bf3b54d`](https://github.com/fhempy/fhempy/commit/bf3b54dc422692022a350255fcd260692dcccc4f))

* feat(fhempy): add get_fhempy_root() ([`410fa8e`](https://github.com/fhempy/fhempy/commit/410fa8e6ddf0e5824095530c49bd4c6fcb687664))

### Fix

* fix(fhempy): use get_fhempy_root() ([`11bb24a`](https://github.com/fhempy/fhempy/commit/11bb24a23a28039f3a70f7221c53c6edc599890b))

* fix(fhempy): create fhempy_log only if it doesn&#39;t exist ([`781adc1`](https://github.com/fhempy/fhempy/commit/781adc195159dbce5750053ef1c93603c2807246))

* fix(gree_climate): fix discovery loop creating too many open udp sockets ([`edba7e9`](https://github.com/fhempy/fhempy/commit/edba7e962219eb155ccef3c6e1569563b565d416))

* fix(blue_connect): remove unknown_handle_18 reading ([`729aac3`](https://github.com/fhempy/fhempy/commit/729aac323d986f532acaaf764bc8ec5ecd04afb6))

* fix(tuya): fix incorrect scaled values ([`ac3c4a3`](https://github.com/fhempy/fhempy/commit/ac3c4a37491e876c78b09ee38e3d7fa98dfe1362))

### Unknown

* Merge branch &#39;development&#39; ([`0431c6f`](https://github.com/fhempy/fhempy/commit/0431c6fb481ea6dc620d0142631b4d61b3f9335d))


## v0.1.535 (2022-12-20)

### Fix

* fix(tuya): fix device IAYz2WK1th0cMLmL ([`500fcd1`](https://github.com/fhempy/fhempy/commit/500fcd175d602024ed9504870fef5d546a244b69))

### Unknown

* Merge branch &#39;development&#39; ([`9194ea1`](https://github.com/fhempy/fhempy/commit/9194ea141a39289a8bb73fc1a8294b715aec36f9))


## v0.1.534 (2022-12-18)

### Fix

* fix(tuya): connect to cloud only if no tuya attr available ([`b624b1e`](https://github.com/fhempy/fhempy/commit/b624b1e43add88c0ab9f085207eae28a265898d5))

### Unknown

* Merge branch &#39;development&#39; ([`ada5cfd`](https://github.com/fhempy/fhempy/commit/ada5cfd648a427bef23da4d47fbfe99f9fc383aa))


## v0.1.533 (2022-12-18)

### Fix

* fix(tuya): fix thermostat productid IAYz2WK1th0cMLmL values ([`21cca36`](https://github.com/fhempy/fhempy/commit/21cca36d3bd41113780eeef27ecbd6d1ef3c4100))

### Unknown

* Merge branch &#39;development&#39; ([`3871d61`](https://github.com/fhempy/fhempy/commit/3871d611f8283fc0090ed6f9f1eee68cf5357f0e))


## v0.1.532 (2022-12-17)

### Fix

* fix(tuya): fix value scaling ([`fb32943`](https://github.com/fhempy/fhempy/commit/fb329431728c5830c3fcf84ae97829861638e4ec))

### Unknown

* Merge branch &#39;development&#39; ([`ccbbe1d`](https://github.com/fhempy/fhempy/commit/ccbbe1d01482816a132d7317e7dc84061e191c33))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`8ac1049`](https://github.com/fhempy/fhempy/commit/8ac1049715a24fe1dd51db7dc94fa80a91c6c97e))


## v0.1.531 (2022-12-17)

### Fix

* fix(tuya): fix step/scale usage for integer values ([`170181b`](https://github.com/fhempy/fhempy/commit/170181b10aa3bde9da015263da0fc404fa98fd81))

* fix(fhempy): create fhempy_log device ([`82e63b7`](https://github.com/fhempy/fhempy/commit/82e63b710de1045f822204d6a9fa8d8485cf717f))

### Unknown

* Merge branch &#39;development&#39; ([`7e26bf2`](https://github.com/fhempy/fhempy/commit/7e26bf29a08eb36c2f55ad8334093df04aa7b432))


## v0.1.530 (2022-12-17)

### Fix

* fix(tuya): fix cur_voltage scale ([`8220acb`](https://github.com/fhempy/fhempy/commit/8220acb1abcd8a6de2d961f2b7d685e03cf25482))

### Unknown

* Merge branch &#39;development&#39; ([`43cb250`](https://github.com/fhempy/fhempy/commit/43cb2507879f5c9a3169a0d64813cbef2b10a4eb))


## v0.1.529 (2022-12-17)

### Fix

* fix(fhempy): support kubernetes ([`e7be7ac`](https://github.com/fhempy/fhempy/commit/e7be7ac30b00e17a1796515e564e636f2a731bb2))

* fix(fhempy): Expand Container Check for Kubernetes (#108) ([`529f46c`](https://github.com/fhempy/fhempy/commit/529f46c956a0b6459271856e799511139714bbff))

* fix(fhempy): release readingsBeginUpdate lock after 120s if no readingsEndUpdate received ([`3607d18`](https://github.com/fhempy/fhempy/commit/3607d18ececf487cf32c60882edd1b84000c4b66))

### Unknown

* Merge branch &#39;development&#39; ([`721dd26`](https://github.com/fhempy/fhempy/commit/721dd261b235373ade78048c0726fabea00a990f))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`9d31dae`](https://github.com/fhempy/fhempy/commit/9d31dae65711af4d014b4b12c5e4747701b45d01))


## v0.1.528 (2022-12-17)

### Feature

* feat(tuya): support v3.4 devices, fix &#34;no reading updates&#34; ([`cc1414b`](https://github.com/fhempy/fhempy/commit/cc1414b6b039e597ed659d7cb4a3e4e12bcbed56))

### Unknown

* Merge branch &#39;development&#39; ([`60c4c73`](https://github.com/fhempy/fhempy/commit/60c4c73474fbab39d8e0fb7ea45a61f67b8eb02b))


## v0.1.527 (2022-12-11)

### Fix

* fix(fhempy): replace cryptography with pycryptodome ([`a4965a3`](https://github.com/fhempy/fhempy/commit/a4965a31877c4417007f13ab7bf8fed0a66cabaa))

### Unknown

* Merge branch &#39;development&#39; ([`ad286a3`](https://github.com/fhempy/fhempy/commit/ad286a34ed8152caa86090bdb177d5c9b8c67afa))


## v0.1.526 (2022-12-05)

### Chore

* chore: add energie_gv_at ([`72e7a37`](https://github.com/fhempy/fhempy/commit/72e7a379aad97c6a467979c085486c083c319748))

### Feature

* feat(blue_connect): support salt and conductivity ([`3e78ef7`](https://github.com/fhempy/fhempy/commit/3e78ef781555ae083f783b9ba23ec4489c3bf132))

### Fix

* fix(energie_gv_at): fix update interval ([`c02acd9`](https://github.com/fhempy/fhempy/commit/c02acd9422a6391fcd7d5ba22991270293a909ce))

* fix(blue_connect): change salt to salinity ([`4880b33`](https://github.com/fhempy/fhempy/commit/4880b338ff1396d0c6b499e2e69ede0bd24827fc))

### Unknown

* Merge branch &#39;development&#39; ([`b6b7fa4`](https://github.com/fhempy/fhempy/commit/b6b7fa44e0307a5d0a390c8229eecf4b69dae45e))


## v0.1.525 (2022-12-04)

### Feature

* feat(energie_gv_at): add module to retrieve hours for energy saving ([`0ab3689`](https://github.com/fhempy/fhempy/commit/0ab3689750842dc7834739cb72c83df9f073d9fe))

### Unknown

* Merge branch &#39;development&#39; ([`b2bd775`](https://github.com/fhempy/fhempy/commit/b2bd775df5b2111ac90f3a7bd1bd7ed4a95dd928))


## v0.1.524 (2022-11-26)

### Fix

* fix(github_backup): handle upload error ([`d5d3a86`](https://github.com/fhempy/fhempy/commit/d5d3a8631dbb350603e4288fbac5dda66a06b98f))

### Unknown

* Merge branch &#39;development&#39; ([`1d68ea8`](https://github.com/fhempy/fhempy/commit/1d68ea892730940bf4f5bc2303c888fb89b0aca7))


## v0.1.523 (2022-11-26)

### Chore

* chore: fetch all commits (#107)

* Update fhem_test.yml

fetch all commits

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;
Co-authored-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`e968bcf`](https://github.com/fhempy/fhempy/commit/e968bcf6092b8dce0943f2e6d78f7a5c53865fca))

### Fix

* fix(fusionsolar): use pycryptodome, re-login on error ([`1427342`](https://github.com/fhempy/fhempy/commit/1427342f2c547c411276e5821a7a37feadfea8df))

### Unknown

* Merge branch &#39;development&#39; ([`da23ab1`](https://github.com/fhempy/fhempy/commit/da23ab1ebc0a2d7270e58e48540df2666b7b8b13))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`95e5a59`](https://github.com/fhempy/fhempy/commit/95e5a59859e3b255fa19aad1dee97ba4888f952f))


## v0.1.522 (2022-11-21)

### Feature

* feat(fusionsolar): add more signals data, fix empty battery error ([`07df9c1`](https://github.com/fhempy/fhempy/commit/07df9c10af8f7ce468a9c0016c2a04963386dbbd))

### Fix

* fix(fusionsolar): fix region ([`f1a49f0`](https://github.com/fhempy/fhempy/commit/f1a49f0b9ddaeb3e120962cc0469159548e508b2))

### Unknown

* Merge branch &#39;development&#39; ([`ede1c5e`](https://github.com/fhempy/fhempy/commit/ede1c5e345b31739990a121ccdd54c9c7283e1ee))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`b7d3bb6`](https://github.com/fhempy/fhempy/commit/b7d3bb69c0e6dad8bbf090e38b4ef2db4d3295e5))


## v0.1.521 (2022-11-21)

### Fix

* fix(tuya): add connection check loop ([`32942f4`](https://github.com/fhempy/fhempy/commit/32942f4dc3e2e022d8876e6c5d7898bf861a92d8))

### Unknown

* Merge branch &#39;development&#39; ([`f4d0215`](https://github.com/fhempy/fhempy/commit/f4d021505689c01d78e29749a605f3fdfb22507d))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`192ea77`](https://github.com/fhempy/fhempy/commit/192ea77746c2de4bbd1662c285ee452a69fbd47c))


## v0.1.520 (2022-11-19)

### Fix

* fix(fhempy): downgrade cryptography due to installation errors with newer version ([`7f2f14c`](https://github.com/fhempy/fhempy/commit/7f2f14c7a75feb8b73231dd496c43afcb21e3594))

* fix(blue_connect): handle broken pipe ([`256acae`](https://github.com/fhempy/fhempy/commit/256acae7159666f7ae031a63e11a2e4404e4cb6a))

### Unknown

* Merge branch &#39;development&#39; ([`9d4995d`](https://github.com/fhempy/fhempy/commit/9d4995dafdc1a510103c954d99d98f9b4beb93cc))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`69e714a`](https://github.com/fhempy/fhempy/commit/69e714a1c6b1ff3a047901207600cd77325325af))


## v0.1.519 (2022-11-19)

### Chore

* chore(deps): bump cryptography from 37.0.4 to 38.0.3 (#104)

Bumps [cryptography](https://github.com/pyca/cryptography) from 37.0.4 to 38.0.3.
- [Release notes](https://github.com/pyca/cryptography/releases)
- [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/pyca/cryptography/compare/37.0.4...38.0.3)

---
updated-dependencies:
- dependency-name: cryptography
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`e6ffd8e`](https://github.com/fhempy/fhempy/commit/e6ffd8efc14419f7782393565a13532e8411cc4f))

### Feature

* feat(meross): add state per channel ([`ad734d8`](https://github.com/fhempy/fhempy/commit/ad734d8b78b155469b8437eaf5f89a065cf57471))

### Unknown

* Merge branch &#39;development&#39; ([`ceca120`](https://github.com/fhempy/fhempy/commit/ceca120fc0a0f84e19a715258328ff774f4249a1))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`7e884f7`](https://github.com/fhempy/fhempy/commit/7e884f7b1a3cd36ea938db1f4932c3976859109c))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`54440aa`](https://github.com/fhempy/fhempy/commit/54440aac87ee491a84eac78c61d0e71b314c99c2))


## v0.1.518 (2022-11-19)

### Fix

* fix(fusionsolar): finally support v3 auth ([`af63a3c`](https://github.com/fhempy/fhempy/commit/af63a3cde738aa49be5d599bcefb0c234734cd0f))

### Unknown

* Merge branch &#39;development&#39; ([`0d495f3`](https://github.com/fhempy/fhempy/commit/0d495f355cee9b4789dfebc5209fc56e01d457a3))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`063f78c`](https://github.com/fhempy/fhempy/commit/063f78c4215e3062013fbca84bd74843209a4621))


## v0.1.517 (2022-11-19)

### Fix

* fix(fusionsolar): try again to fix v3 auth ([`8e27c6c`](https://github.com/fhempy/fhempy/commit/8e27c6c6e6a9d3ad4bd19d194bc4f436ea63edf2))

### Unknown

* Merge branch &#39;development&#39; ([`3d85e8d`](https://github.com/fhempy/fhempy/commit/3d85e8da818dbe9a34821ceffa813dd370b36674))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`c862ca6`](https://github.com/fhempy/fhempy/commit/c862ca6316c9732b454c83e3b8303dd080c57892))


## v0.1.516 (2022-11-19)

### Fix

* fix(fusionsolar): fix region usage ([`a90746a`](https://github.com/fhempy/fhempy/commit/a90746ad3d12d02ad3b6c6e1174ef03a00f5b414))

### Unknown

* Merge branch &#39;development&#39; ([`fa6aa63`](https://github.com/fhempy/fhempy/commit/fa6aa63bc6f4d249a4f52149d9a020abdca75d5f))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`2a0919d`](https://github.com/fhempy/fhempy/commit/2a0919dfce9dd5e35593df600bf60039ebc9aef4))


## v0.1.515 (2022-11-19)

### Fix

* fix(volvo_software_update): fix headers to prevent blocking ([`09a7bdf`](https://github.com/fhempy/fhempy/commit/09a7bdf40053dac3b0273602f895bd0b0f9e9c4a))

### Unknown

* Merge branch &#39;development&#39; ([`ab21bf5`](https://github.com/fhempy/fhempy/commit/ab21bf5cb03d928a2aa42c82934230ef0fedcf4b))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`d74ace6`](https://github.com/fhempy/fhempy/commit/d74ace6ccd994301b9f2baed4a9dc02bcda73c7d))


## v0.1.514 (2022-11-19)

### Unknown

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`9379e49`](https://github.com/fhempy/fhempy/commit/9379e4972f4624025062a5961b85b94c423a64b1))


## v0.1.513 (2022-11-19)

### Fix

* fix(fusionsolar): retry login max 10 times ([`66076e4`](https://github.com/fhempy/fhempy/commit/66076e4c656f231d282340ce3fdc629e05ec067e))

* fix(fusionsolar): retry login max 10 times ([`4f7c619`](https://github.com/fhempy/fhempy/commit/4f7c61980ed1ba16dd21a28fbdc801dff5312efa))

### Unknown

* Merge brach &#39;development&#39; ([`bdff381`](https://github.com/fhempy/fhempy/commit/bdff381a0753b61d063dc882be6b681c0840ba09))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`8d15581`](https://github.com/fhempy/fhempy/commit/8d15581963afc7606cf21bc26c45bdc38711e31d))


## v0.1.510 (2022-11-19)

### Fix

* fix(fusionsolar): try to implement v3 authentication ([`ddb7283`](https://github.com/fhempy/fhempy/commit/ddb72838fe4ece4d5b98e93b5debad87096a2948))

* fix(fhempy): Fix DefineFn and some other fixes by @side79 (#100)

* fix define function

- BindingsIo_Define
- remove protypes from BindingsIo_Initialize
- Store Fn References as coderefs

* Add workflow for testing fhem module
 use perl with multi threading support

* added some ignores .gitignore

* update setup-fhem

* add plan to test

don&#39;t run tests parallel, because we need fhemweb with port binding

run update controls in separate job

* Create .gitattributes

Set Line endings to crlf for perlModule files.

* changed lineendings

* declare variable from main program

* changed search for existing devspec to devspec2array fn

add variable from main program

* avoid duplicate defines of same device
small search improvement

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;

* added check for bindingtype

added tests

* Added support for &#34;Python&#34; as Bindingtype

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;

* add python binary to FHEM modules updater controls file

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;
Co-authored-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;
Co-authored-by: Dominik &lt;dominik.karall@gmail.com&gt; ([`f896ea4`](https://github.com/fhempy/fhempy/commit/f896ea438888ec32f1198f13a65d328c31161431))

### Unknown

* Merge branch &#39;development&#39; ([`60b45c2`](https://github.com/fhempy/fhempy/commit/60b45c2c95ae6c23ee76794d5142ab6721102ad4))

* action: auto update controls

Signed-off-by: github-actions &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`e2060ff`](https://github.com/fhempy/fhempy/commit/e2060ff70b03a50c1bea58344e2ce8fe4b0f6d67))


## v0.1.509 (2022-11-12)

### Chore

* chore: update controls ([`1c96321`](https://github.com/fhempy/fhempy/commit/1c963216231324cc2c1d189af828170123e57daa))

### Fix

* fix(fhempy): fix innerHTML error ([`23c95b8`](https://github.com/fhempy/fhempy/commit/23c95b87bb5c739f6793e15e47f3bf33f09e146c))

* fix(fhempy): fix ble stop_helper ([`5e48356`](https://github.com/fhempy/fhempy/commit/5e483568919f90425a14be65b0423a4eafcd3969))

### Unknown

* Merge branch &#39;development&#39; ([`1702490`](https://github.com/fhempy/fhempy/commit/17024903500a7478ead85ec1960f20a9cb593184))


## v0.1.508 (2022-10-16)

### Chore

* chore: update controls ([`56e3239`](https://github.com/fhempy/fhempy/commit/56e3239764a424716b50432ee389db62126c1eed))

### Feature

* feat(blue_connect): reconnect on BrokenPipeError ([`533d218`](https://github.com/fhempy/fhempy/commit/533d21803699f17d257471f89b8e04901e0704c0))

* feat(fhempy): support stop BLE helper to reconnect ([`5edf2da`](https://github.com/fhempy/fhempy/commit/5edf2dab63d8ddbe5123d760504e86f928c7aeaf))

* feat(websitetests): add websitetests ([`6482aca`](https://github.com/fhempy/fhempy/commit/6482acac6a62d873da1bbc122a47d70b0a33d130))

* feat(fusionsolar): retry get request if it fails ([`975e787`](https://github.com/fhempy/fhempy/commit/975e7872b601a0e4e25bbf04bfab57d3e62d4d48))

### Unknown

* Merge branch &#39;development&#39; ([`d0ab81d`](https://github.com/fhempy/fhempy/commit/d0ab81de08081dc7950e0d0da508919debdc0f68))


## v0.1.507 (2022-10-14)

### Chore

* chore: update controls ([`d34311f`](https://github.com/fhempy/fhempy/commit/d34311f0807dc0961c9dad09a6d4f48a6cbde28a))

### Feature

* feat(websitetests): add simple response check ([`84ecf90`](https://github.com/fhempy/fhempy/commit/84ecf90fe248a093cb11731dba9f8ced108d530a))

* feat(arp_presence): add update command ([`48ef150`](https://github.com/fhempy/fhempy/commit/48ef150eff0d5fa339788e45de8cbf5f918d5517))

### Fix

* fix(ddnss): fix connection issues ([`bca55e3`](https://github.com/fhempy/fhempy/commit/bca55e372654085c2c91e55d39f8f934ad915238))

### Unknown

* Merge branch &#39;development&#39; ([`1c0e6e2`](https://github.com/fhempy/fhempy/commit/1c0e6e229cf21660bf1c2304626d75db2447b061))


## v0.1.506 (2022-10-11)

### Chore

* chore: update controls ([`f81fb9f`](https://github.com/fhempy/fhempy/commit/f81fb9f97e6a09994e7e3fa124fee8c7e3e8a852))

### Feature

* feat(arp_presence): check presene based on arp table, works also for iOS devices ([`7608dcd`](https://github.com/fhempy/fhempy/commit/7608dcd16bcc46d877973a05176bee5b655ac609))

### Fix

* fix(fhempy): fix description ([`57cc650`](https://github.com/fhempy/fhempy/commit/57cc65063900db746152f0b4fa0d38b19b8c3abe))

* fix(kia_hyundai): retry login every 2min if it fails ([`e5a1005`](https://github.com/fhempy/fhempy/commit/e5a10059707386fbccf223ebfcdaf22b5c7b9ca8))

* fix(fusionsolar): fix issues when some values are not reported by fusionsolar api ([`9018cb9`](https://github.com/fhempy/fhempy/commit/9018cb937ce2738f1cbc9a33e253764e01282948))

* fix(esphome): remove insaller link, it&#39;s part of esphome dashboard now ([`7657c38`](https://github.com/fhempy/fhempy/commit/7657c3814271a1b30166a96cedce4328910e4385))

### Unknown

* Merge branch &#39;development&#39; ([`72b814e`](https://github.com/fhempy/fhempy/commit/72b814e79a5c87078f45021654cc29cc0a2a4886))


## v0.1.505 (2022-10-10)

### Chore

* chore: update controls ([`b246252`](https://github.com/fhempy/fhempy/commit/b246252a19c3600b058336133be4610f9d64d830))

### Fix

* fix(tuya): fix colour_data ([`2dc4f07`](https://github.com/fhempy/fhempy/commit/2dc4f075adbec7fb6eafb25293920d15f0779246))

* fix(tuya): set state on startup only if there is no state reading ([`68c7f65`](https://github.com/fhempy/fhempy/commit/68c7f65c2201e85b07b6c8fc594681679304e206))

### Unknown

* Merge branch &#39;development&#39; ([`7964fcd`](https://github.com/fhempy/fhempy/commit/7964fcdf27304f3fa52f416932066674015cb343))


## v0.1.504 (2022-10-09)

### Chore

* chore: update controls ([`005194e`](https://github.com/fhempy/fhempy/commit/005194e592e3275ce6f242bb39a20e9fcd127cd6))

### Fix

* fix(zigbee2mqtt): fix update ([`7c4bb66`](https://github.com/fhempy/fhempy/commit/7c4bb663aefc102d911ab1cfdbd535a565a6aadb))

### Unknown

* Merge branch &#39;development&#39; ([`78206d4`](https://github.com/fhempy/fhempy/commit/78206d48c8dd8a695a929d01706ad1e7e83fd8f3))


## v0.1.503 (2022-10-09)

### Chore

* chore: update controls ([`495cbc5`](https://github.com/fhempy/fhempy/commit/495cbc5f43a58bf689a44f3cb00dffcad87b05be))

### Fix

* fix(tuya): add dp_ attributes even if they are not detected ([`fe295dc`](https://github.com/fhempy/fhempy/commit/fe295dc74c34312244626e621fd73e8171a49e62))

* fix(esphome): update esphome==2022.9.4 ([`ed2e4d0`](https://github.com/fhempy/fhempy/commit/ed2e4d08bc7ed2b774dc72793c97d3da8bc56211))

### Unknown

* Merge branch &#39;development&#39; ([`d79e1b3`](https://github.com/fhempy/fhempy/commit/d79e1b325d6eb33e526e1791f5df2326382efd42))


## v0.1.502 (2022-10-09)

### Chore

* chore: update controls ([`5a745a3`](https://github.com/fhempy/fhempy/commit/5a745a34abb2988a81c92a4d0713c57a5a665897))

### Fix

* fix(tuya): update tinytuya==1.7.1 ([`d8e2c66`](https://github.com/fhempy/fhempy/commit/d8e2c66c3e8744171360a255dff10b10de526129))

* fix(fusionsolar): retry login if it fails ([`de70e9c`](https://github.com/fhempy/fhempy/commit/de70e9c26f00f8c954a30fbeb3ae2bfc1e1a90e8))

* fix(fhempy): disable events for the moment ([`5c6dee0`](https://github.com/fhempy/fhempy/commit/5c6dee08151f2b33e87fa14101915e542ecacc89))

* fix(google_weather): add further user agent ([`5c8ecaa`](https://github.com/fhempy/fhempy/commit/5c8ecaa4df6fb56c9e30bf17e63af45ea53e5fec))

### Unknown

* Merge branch &#39;development&#39; ([`ef5695e`](https://github.com/fhempy/fhempy/commit/ef5695ed24ab321e3f205802bc061891bb38b5ea))


## v0.1.501 (2022-10-05)

### Chore

* chore: update controls ([`69baa35`](https://github.com/fhempy/fhempy/commit/69baa35c879489f1e8a8ca27d07024b447199e67))

### Feature

* feat(skodaconnect): New sensors for Enyaq iV (#98) ([`a157ab9`](https://github.com/fhempy/fhempy/commit/a157ab9d24ebcd84eb4efcd5fdb02937a5b93dac))


## v0.1.500 (2022-10-05)

### Chore

* chore: update controls ([`1e52036`](https://github.com/fhempy/fhempy/commit/1e52036c92d7c5203cc6233159eba9442ebfd07f))

### Fix

* fix(kia_hyundai): check refresh token before update ([`041c732`](https://github.com/fhempy/fhempy/commit/041c732d5ee12977f91c3600592b33db825ad46a))

### Unknown

* Merge branch &#39;development&#39; ([`de3d028`](https://github.com/fhempy/fhempy/commit/de3d02812317de79c23c3cf1d2616683c2db5b26))


## v0.1.499 (2022-10-05)

### Chore

* chore: update controls ([`72ec615`](https://github.com/fhempy/fhempy/commit/72ec615ca74c6a24b510696857a072f4be82afb2))

### Feature

* feat(tuya): support led colours ([`852f522`](https://github.com/fhempy/fhempy/commit/852f522533e97c00421ffddfc36595906d48f3b2))

### Unknown

* Merge branch &#39;development&#39; ([`fc52ca5`](https://github.com/fhempy/fhempy/commit/fc52ca5923f2642194d9b182280c84852c8f6ee7))


## v0.1.498 (2022-10-04)

### Chore

* chore: update controls ([`bd00cda`](https://github.com/fhempy/fhempy/commit/bd00cdaeaf8aa02b6a617b1d7789e2c3bb1220b2))

### Fix

* fix(tuya): set tuya state reading to ready when finished initializing ([`79c247e`](https://github.com/fhempy/fhempy/commit/79c247e4a133e2f8d974f361c720eccb4804c882))

### Unknown

* Merge branch &#39;development&#39; ([`ef0f6df`](https://github.com/fhempy/fhempy/commit/ef0f6df99baf6582833acf5cb6e5fe88062b73fd))


## v0.1.497 (2022-10-03)

### Chore

* chore: update controls ([`1b4c1f0`](https://github.com/fhempy/fhempy/commit/1b4c1f06e1b5e520317641f5404839993355b07c))

### Fix

* fix(fhempy): disable readme help for the moment due to websocket issues ([`30eb51f`](https://github.com/fhempy/fhempy/commit/30eb51f92edb34924c2de62f34a7c51b9d5ba88a))

* fix(fhempy): add logging if sending to fhem needs to wait too long ([`36f12ec`](https://github.com/fhempy/fhempy/commit/36f12ec66e3972bdb122d8c6426c7ba514b2508a))

* fix(fhempy): reinit frames on error ([`ccbb284`](https://github.com/fhempy/fhempy/commit/ccbb284035bd03c384b5ab066ada4a914ec6ab66))

### Unknown

* Merge branch &#39;development&#39; ([`0bc2f37`](https://github.com/fhempy/fhempy/commit/0bc2f37454b27a525a88079f3907745b457678dd))


## v0.1.496 (2022-10-03)

### Chore

* chore: update controls ([`144855a`](https://github.com/fhempy/fhempy/commit/144855a198b2e6c4435e96b210088b7e832f630e))

### Fix

* fix(fhempy): fix websocket write_limit ([`3023385`](https://github.com/fhempy/fhempy/commit/302338574c0c2a6eba329c91df2d51b7e2bc1e2b))

### Unknown

* Merge branch &#39;development&#39; ([`fed3a7e`](https://github.com/fhempy/fhempy/commit/fed3a7ef0f1c2018082ec136d8e38a6690c75d29))


## v0.1.495 (2022-10-02)

### Chore

* chore: update controls ([`b5d17cb`](https://github.com/fhempy/fhempy/commit/b5d17cb35c2ebbe69e919f93c7157c24fe236f49))

### Fix

* fix(fhempy): fix some websocket issues ([`587d0f0`](https://github.com/fhempy/fhempy/commit/587d0f0f78f7c4ba794a161eb0df19705cdbef75))

### Unknown

* Merge branch &#39;development&#39; ([`d813e00`](https://github.com/fhempy/fhempy/commit/d813e00cbe752fd1f991c772b82de10712c3159b))


## v0.1.494 (2022-10-02)

### Chore

* chore: update controls ([`79064a9`](https://github.com/fhempy/fhempy/commit/79064a924163180ed1e57f8fc7490eaf626a9ba4))

### Fix

* fix(fusionsolar): fix to_grid values ([`12e57eb`](https://github.com/fhempy/fhempy/commit/12e57eb08afec8088197d44659974b65a778f12c))

### Unknown

* Merge branch &#39;development&#39; ([`9176275`](https://github.com/fhempy/fhempy/commit/9176275ac56e023f5ebfd7fac3fbed15a0892e0e))


## v0.1.493 (2022-10-02)

### Chore

* chore: update controls ([`29cf186`](https://github.com/fhempy/fhempy/commit/29cf186222100293e5f91a8d25b6a8259a142c6e))

### Fix

* fix(tuya): fix non-str spec values ([`baa5977`](https://github.com/fhempy/fhempy/commit/baa59774279d1e54a1ef4c4e06a8e2993fde917b))

### Unknown

* Merge branch &#39;development&#39; ([`3c654ac`](https://github.com/fhempy/fhempy/commit/3c654ac0825fc6f190f986c9c425bb9b611ff29a))


## v0.1.492 (2022-10-02)

### Chore

* chore: update controls ([`303b57f`](https://github.com/fhempy/fhempy/commit/303b57f7ddd99d22f5cf6df5683af0cf1faa85d3))

### Feature

* feat(kia_hyundai): set state readings to online/error ([`dd5190d`](https://github.com/fhempy/fhempy/commit/dd5190d946d861dbd97514a07ced6b20b78a298f))

### Fix

* fix(kia_hyundai): always update readings ([`e221894`](https://github.com/fhempy/fhempy/commit/e2218944d2d6231fe35394b84a70e2272ca7133c))

### Unknown

* Merge branch &#39;development&#39; ([`fdc79ac`](https://github.com/fhempy/fhempy/commit/fdc79ac18be0ce2b9d83095421e3c06c9765dc84))


## v0.1.491 (2022-10-01)

### Chore

* chore: update controls ([`e2b5a23`](https://github.com/fhempy/fhempy/commit/e2b5a23161d7d204bd9aaf8dde53220ae7574818))

### Fix

* fix(tuya): fix issue with boolean specs ([`7b3910f`](https://github.com/fhempy/fhempy/commit/7b3910fe285a300e300bcdd2fdc942ed06ac9fdf))

### Unknown

* Merge branch &#39;development&#39; ([`ef3198e`](https://github.com/fhempy/fhempy/commit/ef3198efd3009a2ee9a65f09d25aff74aa450180))


## v0.1.490 (2022-10-01)

### Chore

* chore: update controls ([`d0763bf`](https://github.com/fhempy/fhempy/commit/d0763bf92011f5bccff51544775b167041c80573))

### Fix

* fix(gree_climate): add missing self.device = None ([`2a7657f`](https://github.com/fhempy/fhempy/commit/2a7657ff21d2d1f20ed943c726a708fc86e41f26))

### Unknown

* Merge branch &#39;development&#39; ([`fb21110`](https://github.com/fhempy/fhempy/commit/fb2111072f7eb735d739e2023b73046c5fbc0f60))


## v0.1.489 (2022-10-01)

### Chore

* chore: update controls ([`f6f0b51`](https://github.com/fhempy/fhempy/commit/f6f0b5163fb618da30d79e5481ecb9db734f6b8f))

### Fix

* fix(gree_climate): retry connect if first connection attempt fails ([`1eee34a`](https://github.com/fhempy/fhempy/commit/1eee34af7fc6bfc06ef6f7c8c440b4afd35643f0))

### Unknown

* Merge branch &#39;development&#39; ([`a91672c`](https://github.com/fhempy/fhempy/commit/a91672c7f2ae4d264cc31617cddd525fc704ccf8))


## v0.1.488 (2022-10-01)

### Chore

* chore: update controls ([`a3ec896`](https://github.com/fhempy/fhempy/commit/a3ec896ec7ecaed1191ea68215ee442c3f526cc2))

### Feature

* feat(kia_hyundai): update to latest kia_uvo code ([`638a7c8`](https://github.com/fhempy/fhempy/commit/638a7c808d6537e998deace600814e327fbd4a6f))

* feat(kia_hyundai): support update_data command ([`7b4876b`](https://github.com/fhempy/fhempy/commit/7b4876bf6f8466d2287b21819a3dda058e9e6a43))

### Fix

* fix(fusionsolar): better logging on data errors ([`adb5902`](https://github.com/fhempy/fhempy/commit/adb590267127e277a6932f01d56be129f56e7e78))

* fix(websitetests): fix reading response_status ([`a0371a8`](https://github.com/fhempy/fhempy/commit/a0371a854d12ddeea1b0b087f34fa5035dd2a021))

### Unknown

* Merge branch &#39;development&#39; ([`e91096a`](https://github.com/fhempy/fhempy/commit/e91096a37ae1b65b32a4429fcaf36e9719f4e3a2))


## v0.1.487 (2022-09-29)

### Chore

* chore: update controls ([`5021c5f`](https://github.com/fhempy/fhempy/commit/5021c5f8ca691d240de8e948c024b1fffaca2cd1))

### Fix

* fix(websitetests): support URLs with = ([`97a4cce`](https://github.com/fhempy/fhempy/commit/97a4cce3a3b0074d50699516c297a3d2033f76ac))

* fix(blue_connect): keep connection active ([`88f6f49`](https://github.com/fhempy/fhempy/commit/88f6f491be7d08aa78ad421949fc725931b2a6c1))

### Unknown

* Merge branch &#39;development&#39; ([`b170290`](https://github.com/fhempy/fhempy/commit/b170290b6817440e078e846a256485725d0f1e7e))


## v0.1.486 (2022-09-28)

### Chore

* chore: update controls ([`0d90f3f`](https://github.com/fhempy/fhempy/commit/0d90f3f412d98fb9fbb4c6d956dbe6fdc0b42fef))

### Feature

* feat(websitetests): small module to test speed of web responses ([`48e5c4e`](https://github.com/fhempy/fhempy/commit/48e5c4e8c3d741006b9a49a1e73aa7072f866c7a))

### Fix

* fix(websitetests): limit response reading to 5000 characters ([`f350798`](https://github.com/fhempy/fhempy/commit/f3507988b4b9776fffde807ef2609313ca79d8a1))

### Unknown

* Merge branch &#39;development&#39; ([`17f2d49`](https://github.com/fhempy/fhempy/commit/17f2d497795ef04f9bfc14b90c05830b7d72c605))


## v0.1.485 (2022-09-28)

### Chore

* chore: update controls ([`e202dbe`](https://github.com/fhempy/fhempy/commit/e202dbed437b7a9229a80aa2e360a14319b2a839))

### Fix

* fix(fhempy): fix &#34;continue&#34; response to FHEM ([`d63f0dd`](https://github.com/fhempy/fhempy/commit/d63f0dd1517d197ac56ead22007f2b439d304962))

### Unknown

* Merge branch &#39;development&#39; ([`06fa5b5`](https://github.com/fhempy/fhempy/commit/06fa5b57c921eff2dd3cb175bd24896902e973a4))


## v0.1.484 (2022-09-28)

### Chore

* chore: update controls ([`a1b08ab`](https://github.com/fhempy/fhempy/commit/a1b08aba7a458fcd83d770ce8b553d25614b65e9))

### Fix

* fix(tuya): fix translation for enum ([`31ddac2`](https://github.com/fhempy/fhempy/commit/31ddac209e2894c8b20809610337e697149d00a9))

### Unknown

* Merge branch &#39;development&#39; ([`1a9cff8`](https://github.com/fhempy/fhempy/commit/1a9cff88cf09aacca3c0322b04a437ed0a9ce768))


## v0.1.483 (2022-09-27)

### Chore

* chore: update controls ([`08e68f1`](https://github.com/fhempy/fhempy/commit/08e68f1c2a14f068058dd168d2c9bb0bf22d45c5))

### Fix

* fix(tuya): fix translation for enums ([`348e176`](https://github.com/fhempy/fhempy/commit/348e176c67360efcda6855305901a668f1afe850))

### Unknown

* Merge branch &#39;development&#39; ([`20f6e67`](https://github.com/fhempy/fhempy/commit/20f6e67533bf44e0cdb48a7c8cadbc617bd636e3))


## v0.1.482 (2022-09-27)

### Chore

* chore: update controls ([`f4f7cc5`](https://github.com/fhempy/fhempy/commit/f4f7cc5c2f8c8ac49b427d9bba4a0e739d0874a7))

* chore: add comment ([`ecb6074`](https://github.com/fhempy/fhempy/commit/ecb60748433d00bc5a937feae362301d805385c3))

### Fix

* fix(googlecast): update youtube_dl/spotipy ([`6d94d69`](https://github.com/fhempy/fhempy/commit/6d94d697e86d2448c45606e096116af274500b67))

* fix(spotify): update spotipy lib ([`bbd9ae8`](https://github.com/fhempy/fhempy/commit/bbd9ae82c8366e37792cab4e9c432d05d990c304))

### Unknown

* Merge branch &#39;development&#39; ([`ccb1608`](https://github.com/fhempy/fhempy/commit/ccb160883da8addb8241fef4f266d63af84304f5))


## v0.1.481 (2022-09-27)

### Chore

* chore: update controls ([`f4ea7ba`](https://github.com/fhempy/fhempy/commit/f4ea7baa6c0d974fd5a8a759fd5243870efcdfe6))

### Feature

* feat(tuya): add translation for kettle state ([`eafac0c`](https://github.com/fhempy/fhempy/commit/eafac0c06c4ff3e9a17decd2f4c3b9c52edd1596))

### Fix

* fix(tuya): use online reading for online/offline state ([`dd75bf3`](https://github.com/fhempy/fhempy/commit/dd75bf33a4e9bb9986ffe6009cde25d3e0d974c4))

### Unknown

* Merge branch &#39;development&#39; ([`d7b8d84`](https://github.com/fhempy/fhempy/commit/d7b8d8453e9cca15bae4feef11e9eacef7c1cc89))


## v0.1.480 (2022-09-27)

### Chore

* chore: update controls ([`9bbeb67`](https://github.com/fhempy/fhempy/commit/9bbeb67e377bc4b5edf5d5c3e4d4d8f442b76737))

* chore: remove space at end of line ([`a3d9ec3`](https://github.com/fhempy/fhempy/commit/a3d9ec39d54f3ad89c73d6c1e6322b853625b320))

### Fix

* fix(fhempy): support ws msgs up to 10MiB ([`87bfd3e`](https://github.com/fhempy/fhempy/commit/87bfd3e8baf6a6974ce6fe3caec617d7726877da))

* fix(blue_connect): keep BLE connection ([`7e89afd`](https://github.com/fhempy/fhempy/commit/7e89afd0f47132ed462e7e6d7c28b29b59106a92))

### Unknown

* Merge branch &#39;development&#39; ([`1d087c7`](https://github.com/fhempy/fhempy/commit/1d087c7bdf93d24fecba055abc2307f3f590a5cb))


## v0.1.479 (2022-09-26)

### Chore

* chore: update controls ([`cc5bbc9`](https://github.com/fhempy/fhempy/commit/cc5bbc97dd6df61e9b27b78918d02ae8e557814a))

### Fix

* fix(fhempy): make DevIo_IsOpen call more clear ([`2216284`](https://github.com/fhempy/fhempy/commit/2216284cfed0159cf991ebd06fab4d391e00b6ae))

* fix(fhempy): better connection closed handling ([`c59119f`](https://github.com/fhempy/fhempy/commit/c59119fec1dc26963898c93d2e9e7ee221b32c2e))

### Unknown

* Merge branch &#39;development&#39; ([`e33b9e5`](https://github.com/fhempy/fhempy/commit/e33b9e5701448949e94cbf3e3de72c3f290f7393))


## v0.1.478 (2022-09-26)

### Chore

* chore: update controls ([`89339e4`](https://github.com/fhempy/fhempy/commit/89339e45441a3c1eb35b6bc0e2d7f12867a124d8))

### Fix

* fix(fhempy): fix asyncio warnings for WebSocketServerProtocol.handler() ([`cf11e97`](https://github.com/fhempy/fhempy/commit/cf11e97054c43d701ad9a864e834540ab6236ff7))

### Unknown

* Merge branch &#39;development&#39; ([`cde5aa1`](https://github.com/fhempy/fhempy/commit/cde5aa10acaa71a4a1e242c063afbc3a1eac8cf5))


## v0.1.477 (2022-09-25)

### Chore

* chore: update controls ([`3fac186`](https://github.com/fhempy/fhempy/commit/3fac186c2a97679417ec10a14db5dedc0dc500ac))

* chore(tuya): add reference comment ([`65a24dd`](https://github.com/fhempy/fhempy/commit/65a24dd1fee9df94107fff390796a8dbfc2388fc))

### Feature

* feat(fhempy): add healthcheck possibility ([`11e2ef8`](https://github.com/fhempy/fhempy/commit/11e2ef8b700e5be56d0014bfb328c94948e3378f))

### Fix

* fix(tuya): do not rais exception on CancelledError ([`f9fe2f9`](https://github.com/fhempy/fhempy/commit/f9fe2f9a61c87d872c20a05254cc57f34489d937))

* fix(google_weather): use several user agent strings ([`7b0730c`](https://github.com/fhempy/fhempy/commit/7b0730c93ecff146a0df39d0a46c201e1303fef0))

* fix(fhempy): improve log message ([`47598df`](https://github.com/fhempy/fhempy/commit/47598df0563c069983c73b5543280df2610d9c4f))

* fix(blue_connect): try to connect 10 times every 10s on failure ([`2571ab1`](https://github.com/fhempy/fhempy/commit/2571ab175d6eb29814ebc4bbadbdab7aa1acd2b0))

### Unknown

* Merge branch &#39;development&#39; ([`e47f5c1`](https://github.com/fhempy/fhempy/commit/e47f5c1f14434e7669d82853a52173e19b3ac1bf))


## v0.1.476 (2022-09-24)

### Chore

* chore: update controls ([`56c5862`](https://github.com/fhempy/fhempy/commit/56c5862bcb5fe627f23dab9d139974dc390d8707))

### Feature

* feat(meross): support thermostat ([`842ad75`](https://github.com/fhempy/fhempy/commit/842ad750590a47b3a518b4c7e3f8d939af79f60b))

### Unknown

* Merge branch &#39;development&#39; ([`95f013d`](https://github.com/fhempy/fhempy/commit/95f013d8abdbb3570020e3ff20968296fb4104a0))


## v0.1.475 (2022-09-24)

### Chore

* chore: update controls ([`2336ce3`](https://github.com/fhempy/fhempy/commit/2336ce3c0d9901a90a44d42639d1001ae2a4e752))

### Fix

* fix(fhempy): fix max_payload_size websocket issues, add state info on first define ([`896ed11`](https://github.com/fhempy/fhempy/commit/896ed11ed34b1d6aed8db3522f06a5684c4937e0))

### Unknown

* Merge branch &#39;development&#39; ([`759462b`](https://github.com/fhempy/fhempy/commit/759462bf5024e30b0f90b83747d51175b7ea5fa9))


## v0.1.474 (2022-09-24)

### Chore

* chore: update controls ([`0f77aa9`](https://github.com/fhempy/fhempy/commit/0f77aa9fdde712339b61c331ec261b27064d064c))

### Fix

* fix(tuya): fix values wrong format ([`8c44946`](https://github.com/fhempy/fhempy/commit/8c44946b1aafbf7ffb96183794a4d0a4d8d9082d))

* fix(fhempy): recommend Python 3.8 or higher ([`1d44b53`](https://github.com/fhempy/fhempy/commit/1d44b538e79a2f01cca0e5ec96f66cc9ebe18aeb))

### Unknown

* Merge branch &#39;development&#39; ([`736cd88`](https://github.com/fhempy/fhempy/commit/736cd88abc7601000c256b5696f8b446ae81dbe2))


## v0.1.473 (2022-09-21)

### Chore

* chore: update controls ([`2ac2376`](https://github.com/fhempy/fhempy/commit/2ac2376f07da75b55bc57ea11635fa573d4e38a3))

### Feature

* feat(tuya): support productid utzgmksz7zj66als ([`af599ff`](https://github.com/fhempy/fhempy/commit/af599ffa664085f34ce29aeb86195763f6d7e840))

### Fix

* fix(tuya): fix readings for local mapping ([`5f557cc`](https://github.com/fhempy/fhempy/commit/5f557cc3a453be89103707487cc2d667a459ace8))

* fix(zigbee2mqtt): start z2m after update ([`f6687aa`](https://github.com/fhempy/fhempy/commit/f6687aa7a566b748469d88d4e62fbbbc42a4ee55))

* fix(fhempy): better log when advertising fhempy on local network ([`bdff568`](https://github.com/fhempy/fhempy/commit/bdff5686eb9402e18c74aa733dba9fe7ee8021ed))

### Unknown

* Merge branch &#39;development&#39; ([`1fdc7d3`](https://github.com/fhempy/fhempy/commit/1fdc7d337d4177b0bf338701a1a404c46a056819))


## v0.1.472 (2022-09-20)

### Chore

* chore: update controls ([`7ce24de`](https://github.com/fhempy/fhempy/commit/7ce24defb462e3a3b81b4513235dff3996ddfa6c))

### Fix

* fix(gfprobt): fix circular import ([`5b4670b`](https://github.com/fhempy/fhempy/commit/5b4670b7a06c1ff14f651eb0f1c142fceb3e6188))

### Unknown

* Merge branch &#39;development&#39; ([`3132b1f`](https://github.com/fhempy/fhempy/commit/3132b1f81732966d7f08d4be2da8a2708f6a2b24))


## v0.1.471 (2022-09-20)

### Chore

* chore: update controls ([`f8f1d52`](https://github.com/fhempy/fhempy/commit/f8f1d52d37bea675f8856f0d3818e5cd22316080))

### Fix

* fix(blue_connect): do not round battery reading ([`30cf035`](https://github.com/fhempy/fhempy/commit/30cf03544c4b10060ac90a1db1c4f3da1ff217c1))

### Unknown

* Merge branch &#39;development&#39; ([`ab74627`](https://github.com/fhempy/fhempy/commit/ab7462776f2d5e3067d19d72e2629518b002e02a))


## v0.1.470 (2022-09-20)

### Chore

* chore: update controls ([`099db5d`](https://github.com/fhempy/fhempy/commit/099db5daea1f5916db53ff7fa77c38ed356f5ba3))

### Fix

* fix(blue_connect): do not round battery reading ([`b7a5ccb`](https://github.com/fhempy/fhempy/commit/b7a5ccb3ef1d4043dea4d0c3f753a8ed713296d2))

### Unknown

* Merge branch &#39;development&#39; ([`1afc0d3`](https://github.com/fhempy/fhempy/commit/1afc0d346ac553d0fbb79ec7679cfafbd84379fd))


## v0.1.469 (2022-09-20)

### Chore

* chore: update controls ([`d23d3b6`](https://github.com/fhempy/fhempy/commit/d23d3b674e62ca8706734c87689e5cdd046fef58))

### Feature

* feat(blue_connect): support battery ([`f8d1360`](https://github.com/fhempy/fhempy/commit/f8d13603662a53ef6b19bf24fd0080c47c2a00ef))

### Fix

* fix(blue_connect): set readings 0 on errors ([`7d8d27c`](https://github.com/fhempy/fhempy/commit/7d8d27ccfd929b120e717b61176db9485f0ca496))

### Unknown

* Merge branch &#39;development&#39; ([`11d740a`](https://github.com/fhempy/fhempy/commit/11d740a7379dbca189488c70f2ca14946eaa9ac5))


## v0.1.468 (2022-09-19)

### Chore

* chore: update controls ([`ca03d1b`](https://github.com/fhempy/fhempy/commit/ca03d1b46cf9b38c972033b395cf9b977035bbe5))

### Feature

* feat(blue_connect): add raw data reading ([`2d6b32c`](https://github.com/fhempy/fhempy/commit/2d6b32cee3dcc735baf68b2f047c1ce4510b2389))

### Unknown

* Merge branch &#39;development&#39; ([`dfcfa51`](https://github.com/fhempy/fhempy/commit/dfcfa51f482d8da47fc5c33f19f0428e50e5afa9))


## v0.1.467 (2022-09-18)

### Chore

* chore: update controls ([`96fa113`](https://github.com/fhempy/fhempy/commit/96fa1138b030de2ceb86e89b57978249947a0217))

### Fix

* fix(blue_connect): fix retry ([`14e29d8`](https://github.com/fhempy/fhempy/commit/14e29d8fccaf97b4ea55ae9ab9bcc349a324aadd))

### Unknown

* Merge branch &#39;development&#39; ([`492aacc`](https://github.com/fhempy/fhempy/commit/492aacce50a43b1b18af395cfa110b72bd6c199e))


## v0.1.466 (2022-09-18)

### Chore

* chore: update controls ([`d69903c`](https://github.com/fhempy/fhempy/commit/d69903c0cead55542386412bcb88670ce5865934))

### Feature

* feat(esphome): update to 2022.8.3 ([`eb93ae9`](https://github.com/fhempy/fhempy/commit/eb93ae95cf9451fbb239f73ea399f5e70ec734f7))

### Unknown

* Merge branch &#39;development&#39; ([`2922fe2`](https://github.com/fhempy/fhempy/commit/2922fe2c8d3c9f7f631b863bf00187aef2c3ff9a))


## v0.1.465 (2022-09-18)

### Chore

* chore: update controls ([`a4a3029`](https://github.com/fhempy/fhempy/commit/a4a30296dfafd9297b397913ba06cb7daf0d2a7c))

### Feature

* feat(blue_connect): add state reading and ph/orp_state reading ([`fd682b8`](https://github.com/fhempy/fhempy/commit/fd682b865d40ccba5073120e528b6e91990cf2b3))

### Unknown

* Merge branch &#39;development&#39; ([`ff610af`](https://github.com/fhempy/fhempy/commit/ff610af22be214d9ed6968c6e38463d7a10a44ff))


## v0.1.464 (2022-09-18)

### Chore

* chore: update controls ([`9c08819`](https://github.com/fhempy/fhempy/commit/9c08819747f7f39eddb536704d3b5156290b7c6d))

### Fix

* fix(blue_connect): fix blue connect ([`63a0356`](https://github.com/fhempy/fhempy/commit/63a0356e36b242dad06c52cfca7f95a982d4aae2))

### Unknown

* Merge branch &#39;development&#39; ([`8d413ac`](https://github.com/fhempy/fhempy/commit/8d413acfc80e041d0cb0307a610117623c317405))


## v0.1.463 (2022-09-16)

### Chore

* chore: update controls ([`53761e6`](https://github.com/fhempy/fhempy/commit/53761e6097dc5ebd2c508a42a96579d3a5b4304d))

### Feature

* feat(blue_connect): initial version ([`fa0b3fd`](https://github.com/fhempy/fhempy/commit/fa0b3fd6a156bffab9a740d7016a5e167780c5e8))

* feat(fhempy): force version update ([`4ac7a31`](https://github.com/fhempy/fhempy/commit/4ac7a31dd5cf792d9ede472928b4c7f2a1d447a4))

### Fix

* fix(blue_connect): add retries ([`49a8833`](https://github.com/fhempy/fhempy/commit/49a88330c07754631c990d8b86c74f111629cdcc))

### Unknown

* Merge branch &#39;development&#39; ([`2b45cb1`](https://github.com/fhempy/fhempy/commit/2b45cb1ca2fd839d288537a5fae512c3fb01a434))


## v0.1.462 (2022-09-12)

### Chore

* chore: update controls ([`f600f2a`](https://github.com/fhempy/fhempy/commit/f600f2ab9e9e9f75b0823186dc9e6e2d09f580da))

### Fix

* fix(fhempy): fix docker installation? ([`31417aa`](https://github.com/fhempy/fhempy/commit/31417aa12d2dc4fa8ce71c069c0ca5064a14e433))

### Unknown

* Merge branch &#39;development&#39; ([`287b76f`](https://github.com/fhempy/fhempy/commit/287b76f2bbbc6c35175920bfaf7da4a526f9eb96))


## v0.1.461 (2022-09-09)

### Chore

* chore: update controls ([`5b8649d`](https://github.com/fhempy/fhempy/commit/5b8649d733fed33e707ae1703630c3fc9b076d1b))

### Fix

* fix(github_backup): only update file if sha1 sum changes ([`3cc7b7a`](https://github.com/fhempy/fhempy/commit/3cc7b7a2e9c68500ea556f5c51ea39aea134640c))

* fix(kia_hyundai): add pytz dependency ([`21eac89`](https://github.com/fhempy/fhempy/commit/21eac89b19f46af95e772b4925873cd78d813639))

### Unknown

* Merge branch &#39;development&#39; ([`cf00190`](https://github.com/fhempy/fhempy/commit/cf00190e833f1798e190b0db85dd10d08548c17a))


## v0.1.460 (2022-09-09)

### Chore

* chore: update controls ([`c7a47ef`](https://github.com/fhempy/fhempy/commit/c7a47ef6b2ed38b41847e3228962ce841c10ae50))

### Fix

* fix(kia_hyundai): fix name of dateutil ([`ad28c6b`](https://github.com/fhempy/fhempy/commit/ad28c6bd7195fe5c3c8a24fe0f62d954f933c166))

### Unknown

* Merge branch &#39;development&#39; ([`e66a5b4`](https://github.com/fhempy/fhempy/commit/e66a5b44fa7db5693966a6cfa8bb114007420234))


## v0.1.459 (2022-09-09)

### Chore

* chore: update controls ([`26b1ad7`](https://github.com/fhempy/fhempy/commit/26b1ad7a8b82007b831a9be5bb9e4604c2b986f1))

### Fix

* fix(kia_hyundai): add dateutil ([`da3d112`](https://github.com/fhempy/fhempy/commit/da3d1125d4da5963024b32a5fc3fb8ded5f88171))

### Unknown

* Merge branch &#39;development&#39; ([`c2b14aa`](https://github.com/fhempy/fhempy/commit/c2b14aa2a0329d61673068638a81e6e0ce306eec))


## v0.1.458 (2022-09-08)

### Chore

* chore: update controls ([`6aa59b9`](https://github.com/fhempy/fhempy/commit/6aa59b9abd03a34a70fe6ac503992e859422ab3d))

### Feature

* feat(github_backup): improve commit message ([`dfb29ed`](https://github.com/fhempy/fhempy/commit/dfb29ed138ad4631e907c20c7a88af47c9ce1eb2))

### Fix

* fix(skodaconnect): Update Base Lib (#88) ([`b2d2c8f`](https://github.com/fhempy/fhempy/commit/b2d2c8f14676cd3ab12374ef6981cd57942faa16))

### Unknown

* Merge branch &#39;development&#39; ([`b18fa85`](https://github.com/fhempy/fhempy/commit/b18fa8523a7b62fd856aad8f3e9e758146b6e74a))

* Merge branch &#39;development&#39; of https://github.com/dominikkarall/fhempy into development ([`15a0ad7`](https://github.com/fhempy/fhempy/commit/15a0ad7c4e439a182d7bb276dd8d72b18bd66043))


## v0.1.457 (2022-09-06)

### Chore

* chore: update controls ([`15f7b4d`](https://github.com/fhempy/fhempy/commit/15f7b4d78fc14863c64d4dce7198f2eb3cc6a200))

### Fix

* fix(fhempy): fix memory leak ([`45f8909`](https://github.com/fhempy/fhempy/commit/45f89092b95a7335322897f8d832970a875d9646))

### Unknown

* Merge branch &#39;development&#39; ([`a3b92d7`](https://github.com/fhempy/fhempy/commit/a3b92d7cbfbc89639a0cd7c9261b3c1d0ead4aa6))


## v0.1.456 (2022-09-05)

### Chore

* chore: update controls ([`24a1c91`](https://github.com/fhempy/fhempy/commit/24a1c91c4edc68bb2e04ddb4dfad9c04e240efed))

### Fix

* fix(tuya): fix json loads ([`5037a89`](https://github.com/fhempy/fhempy/commit/5037a89b300e2220c2a01b398101f345838c8552))

### Unknown

* Merge branch &#39;development&#39; ([`06281d5`](https://github.com/fhempy/fhempy/commit/06281d5f89c4f067a360ee891d487c016812247e))


## v0.1.455 (2022-09-05)

### Chore

* chore: update controls ([`707ce01`](https://github.com/fhempy/fhempy/commit/707ce016d09b449016e8af00a19089c9c95b2e5a))

* chore: fix newline ([`ad6d16b`](https://github.com/fhempy/fhempy/commit/ad6d16b64a098d05b97467418d56629f572c7949))

### Fix

* fix(tuya): fix translation again ([`754061d`](https://github.com/fhempy/fhempy/commit/754061dbd2ee2eba7c46eb4b0df13a38085077ed))

### Unknown

* Merge branch &#39;development&#39; ([`5aebc12`](https://github.com/fhempy/fhempy/commit/5aebc1275c8f9ae5896a09d54a9cd7b1f1eea5b8))


## v0.1.454 (2022-09-05)

### Chore

* chore: update controls ([`6fabe66`](https://github.com/fhempy/fhempy/commit/6fabe668bea945c8956842460d2d93623307e5bf))

### Feature

* feat(skodaconnect): update base lib ([`811efce`](https://github.com/fhempy/fhempy/commit/811efce3ff4e6c906b3b9de05c6beae4edd6ec55))

### Unknown

* Merge branch &#39;development&#39; ([`3b1e10f`](https://github.com/fhempy/fhempy/commit/3b1e10f1505c59bcf3aff625e07b42bc999f2e60))

* Merge branch &#39;development&#39; of https://github.com/dominikkarall/fhempy into development ([`a92c542`](https://github.com/fhempy/fhempy/commit/a92c5428bf16ec66f819bbdb49454de9f545d097))


## v0.1.453 (2022-09-05)

### Chore

* chore: update controls ([`1aa007b`](https://github.com/fhempy/fhempy/commit/1aa007b913a8eabb698a275d5017190fcfb02a7c))

### Fix

* fix(tuya): fix translation error for local devices ([`7fd5dcb`](https://github.com/fhempy/fhempy/commit/7fd5dcbca46f47f852dbeaae4122ad33356a527f))

### Unknown

* Merge branch &#39;development&#39; ([`09ee8ff`](https://github.com/fhempy/fhempy/commit/09ee8ff7c1b299f19f64b16de96ed444cde1bb88))


## v0.1.452 (2022-09-05)

### Chore

* chore: update controls ([`ebc36f2`](https://github.com/fhempy/fhempy/commit/ebc36f2c61a56633572458f24ec8836df1381be2))

### Fix

* fix(tuya): fix set translation ([`6aac36d`](https://github.com/fhempy/fhempy/commit/6aac36d1fb1cea1a11d6bb5128e15dbcdaefa779))

### Unknown

* Merge branch &#39;development&#39; ([`ff2c50b`](https://github.com/fhempy/fhempy/commit/ff2c50bc2dd016f7cba1b924c079db6655a9405e))


## v0.1.451 (2022-09-04)

### Chore

* chore: update controls ([`3c44579`](https://github.com/fhempy/fhempy/commit/3c4457970c5c517f5c55cf853205484ac0c63adc))

### Feature

* feat(tuya): support translation in mappings ([`2875c31`](https://github.com/fhempy/fhempy/commit/2875c31507712241f14e64af6da3d4aee499d85e))

### Unknown

* Merge branch &#39;development&#39; ([`397008b`](https://github.com/fhempy/fhempy/commit/397008ba166078a1f0195854ecd8bb03f1d1dd25))


## v0.1.450 (2022-09-04)

### Chore

* chore: update controls ([`8b01ded`](https://github.com/fhempy/fhempy/commit/8b01dedc5e1f1eb5b3841edd8ba4b0490b3e3030))

### Fix

* fix(fusionsolar): fix pv string current reading ([`1e94c42`](https://github.com/fhempy/fhempy/commit/1e94c428b7dcafdaea057d6a0f139530fecfc276))

* fix(github_backup): fix sha compare ([`96a7c07`](https://github.com/fhempy/fhempy/commit/96a7c072f0146bbe1bba3e3a859038a12734f10e))

### Unknown

* Merge branch &#39;development&#39; ([`f0d6f0a`](https://github.com/fhempy/fhempy/commit/f0d6f0a4946c92134fb783ca2c4b47c931b43b39))


## v0.1.449 (2022-09-03)

### Chore

* chore: update controls ([`42a17ae`](https://github.com/fhempy/fhempy/commit/42a17ae5fb7de8ee52a8dc7db1b41a93a5fec3da))

### Feature

* feat(tuya): add kettle support ([`92d5a09`](https://github.com/fhempy/fhempy/commit/92d5a09428946a43a957fd982d2ca1457973db87))

### Unknown

* Merge branch &#39;development&#39; ([`e09b3d7`](https://github.com/fhempy/fhempy/commit/e09b3d7bfa1bc3e03b9c1a8d70dcf8e461e2d661))


## v0.1.448 (2022-09-03)

### Chore

* chore: update controls ([`1e1243a`](https://github.com/fhempy/fhempy/commit/1e1243aacb7c88402c240e7df42a60b57b44faad))

### Feature

* feat(fusionsolar): add string voltage/current ([`f7d4b3d`](https://github.com/fhempy/fhempy/commit/f7d4b3da7703d460b45ec5403ddb8eb6b12dba8f))

### Unknown

* Merge branch &#39;development&#39; ([`6531b44`](https://github.com/fhempy/fhempy/commit/6531b446965a82a4c2ef4b9edfecae9b6cf6270f))


## v0.1.447 (2022-09-02)

### Chore

* chore: update controls ([`272493c`](https://github.com/fhempy/fhempy/commit/272493c260d729b93535eb84d5b72e65160dc58d))

### Feature

* feat(fusionsolar): correct ratio values when battery is used ([`6d190ba`](https://github.com/fhempy/fhempy/commit/6d190bad0579d4382fe09f70d3064a0088b6630a))

### Fix

* fix(fhempy): support function_param also without function parameter in set_conf ([`2c5bb67`](https://github.com/fhempy/fhempy/commit/2c5bb670b97721fb9b1a3093334d8d5b0e5fa8a3))

### Unknown

* Merge branch &#39;development&#39; ([`26e59b8`](https://github.com/fhempy/fhempy/commit/26e59b87d6d00aabd90440d70cb33ede41d637a5))


## v0.1.446 (2022-09-01)

### Chore

* chore: update controls ([`0477245`](https://github.com/fhempy/fhempy/commit/047724535fe45befed2bc1566e08fade25e8b98c))

### Fix

* fix(meross): fix on/off ([`fe931dc`](https://github.com/fhempy/fhempy/commit/fe931dca53ae4a520d3e617cae53103c328c98ca))

### Unknown

* Merge branch &#39;development&#39; ([`9843de5`](https://github.com/fhempy/fhempy/commit/9843de51a68d964d8c51ea7dd5e6d8714dbba49c))


## v0.1.445 (2022-08-31)

### Chore

* chore: update controls ([`f530782`](https://github.com/fhempy/fhempy/commit/f53078270c43b3862fa0e5b3175cb54c36b193b6))

### Fix

* fix(meross): fix channel handling again ([`c48c59e`](https://github.com/fhempy/fhempy/commit/c48c59efb130598dc2cf29b35edfc09adb2e3cf9))

### Unknown

* Merge branch &#39;development&#39; ([`51b6971`](https://github.com/fhempy/fhempy/commit/51b6971b6251ead68e4afae3c701e9b929dc6951))


## v0.1.444 (2022-08-30)

### Chore

* chore: update controls ([`46dc137`](https://github.com/fhempy/fhempy/commit/46dc137636271896c828a1e2d95dcf230b22e5ec))

* chore: disable Python 3.10 tests ([`4886469`](https://github.com/fhempy/fhempy/commit/4886469bc776e0b5c6f47214afdec9642e5c8da0))

### Fix

* fix(meross): fix channel support ([`a94020d`](https://github.com/fhempy/fhempy/commit/a94020db5358c84640297f6548dc02957ee705f9))

### Unknown

* Merge branch &#39;development&#39; ([`9a6f89d`](https://github.com/fhempy/fhempy/commit/9a6f89de67ad0a9fff526bb82fe8054fd7d9ca27))


## v0.1.443 (2022-08-29)

### Chore

* chore: update controls ([`345e90b`](https://github.com/fhempy/fhempy/commit/345e90bf15357592a4ed8b292eb4cbd84310e6c0))

### Feature

* feat(fhempy): report error when fhempy takes longer than 5s to send back answer to fhem ([`9825a67`](https://github.com/fhempy/fhempy/commit/9825a67608b33d2108295c23a7c026a748f8b1e8))

### Unknown

* Merge branch &#39;development&#39; ([`531bd4a`](https://github.com/fhempy/fhempy/commit/531bd4ae4babfca9150d7fad9fa1f4bfaf11bf47))


## v0.1.442 (2022-08-28)

### Chore

* chore: update controls ([`9f59743`](https://github.com/fhempy/fhempy/commit/9f5974324049dd99b36620cdd378177ab47d9eda))

### Feature

* feat(meross): support channels ([`7c89512`](https://github.com/fhempy/fhempy/commit/7c89512d10636da3f7e3f521120e31d6b6258828))

### Unknown

* Merge branch &#39;development&#39; ([`856f037`](https://github.com/fhempy/fhempy/commit/856f0370fd01469af3845417cff131b2abedf905))


## v0.1.441 (2022-08-24)

### Chore

* chore: update controls ([`20b8a76`](https://github.com/fhempy/fhempy/commit/20b8a765e7eacde77cbb03a9dd4b17d48b8cfe87))

### Fix

* fix(tuya): fix use API_KEY and API_SECRET reading ([`ad8db6c`](https://github.com/fhempy/fhempy/commit/ad8db6c5d34087c2ad10e3468f77f50b022ef5c6))

### Unknown

* Merge branch &#39;development&#39; ([`15e7d39`](https://github.com/fhempy/fhempy/commit/15e7d3920a1f6b6e8e020f8ead2a89f8caab9e9c))


## v0.1.440 (2022-08-22)

### Chore

* chore: update controls ([`de12c70`](https://github.com/fhempy/fhempy/commit/de12c7021bd38d3888dd58a408af8d8766927af4))

### Feature

* feat(fhempy): support time format in set/attr ([`ecc84a3`](https://github.com/fhempy/fhempy/commit/ecc84a303d35afc1edcc636c071f8e6867106491))

* feat(github_backup): new attr backup_time, support directories ([`2e26689`](https://github.com/fhempy/fhempy/commit/2e266895281081be544fe81ab5c8a2799e1d3d91))

### Unknown

* Merge branch &#39;development&#39; ([`df95c5e`](https://github.com/fhempy/fhempy/commit/df95c5e5de7e1b2216e163081fb3c46605db0694))


## v0.1.439 (2022-08-21)

### Chore

* chore: update controls ([`d87824a`](https://github.com/fhempy/fhempy/commit/d87824a73c8a31eaa827faeb23280f0bcee2433b))

### Feature

* feat(github_backup): support binary files ([`c94bb7f`](https://github.com/fhempy/fhempy/commit/c94bb7fbd1ad1e1a6f046a67a038de917b92ab37))

### Unknown

* Merge branch &#39;development&#39; ([`9ac1c15`](https://github.com/fhempy/fhempy/commit/9ac1c15032f29148eafc5e15ea49b28c0b331964))


## v0.1.438 (2022-08-21)

### Chore

* chore: update controls ([`23a8dfb`](https://github.com/fhempy/fhempy/commit/23a8dfb83109c021ca24f866aa8a871f97bb7741))

### Fix

* fix(github_backup): fix do_backup call ([`0a83c07`](https://github.com/fhempy/fhempy/commit/0a83c070aa99353543d17448978ce7923904e1c0))

### Unknown

* Merge branch &#39;development&#39; ([`8327c20`](https://github.com/fhempy/fhempy/commit/8327c2082b9fd785a591a2bc2882c4363b177769))


## v0.1.437 (2022-08-21)

### Chore

* chore: update controls ([`6f9ed08`](https://github.com/fhempy/fhempy/commit/6f9ed082224df57356fec01b267bd8574fd68a75))

### Fix

* fix(github_backup): fix set backup_now ([`e28e7af`](https://github.com/fhempy/fhempy/commit/e28e7afb8523ba6533b20afd3eca9ab54c5719a2))

### Unknown

* Merge branch &#39;development&#39; ([`5af3d99`](https://github.com/fhempy/fhempy/commit/5af3d99a5d9b77081749fa1daba54cfa4e35164d))


## v0.1.436 (2022-08-21)

### Chore

* chore: update controls ([`3c4eb06`](https://github.com/fhempy/fhempy/commit/3c4eb06d7e5e87564ae71c1da82f57c4aa00313e))

### Feature

* feat(github_backup): new github_backup module ([`6bff115`](https://github.com/fhempy/fhempy/commit/6bff115b9825aeecad6eab2af0ddf9eb0a192a83))

### Unknown

* Merge branch &#39;development&#39; ([`ea229b8`](https://github.com/fhempy/fhempy/commit/ea229b85c3729fc07909bfe89c30e14c7a389d4f))


## v0.1.435 (2022-08-20)

### Chore

* chore: update controls ([`6a9b3b2`](https://github.com/fhempy/fhempy/commit/6a9b3b21654f4791c1ab82346376b08c01de38be))

### Feature

* feat(ddnssde): add ddnssde ([`2c706ab`](https://github.com/fhempy/fhempy/commit/2c706ab5ecd73db20f110e0b472dcfa76245aefd))

### Fix

* fix(fhempy): fix log level which caused delays ([`0b26f20`](https://github.com/fhempy/fhempy/commit/0b26f209e275e51834ffb7e55d6ea30e02635f2d))

### Unknown

* Merge branch &#39;development&#39; ([`4ffbd43`](https://github.com/fhempy/fhempy/commit/4ffbd43493f2371266e6a665ab724185d85fe130))


## v0.1.434 (2022-08-20)

### Chore

* chore: update controls ([`cf6185d`](https://github.com/fhempy/fhempy/commit/cf6185d9715f3266457a27615e29402ece8c75b2))

### Fix

* fix(object_detection): fix import ([`a815b68`](https://github.com/fhempy/fhempy/commit/a815b6854e6ebffe04d1c8017d24cdba28d5ec18))

### Unknown

* Merge branch &#39;development&#39; ([`a0ad99f`](https://github.com/fhempy/fhempy/commit/a0ad99fdeb446825488fc0b92feb6ed71097c8b8))


## v0.1.433 (2022-08-20)

### Chore

* chore: update controls ([`d55ced9`](https://github.com/fhempy/fhempy/commit/d55ced92f7a3e3ed6b2ac6f636114d46ce0ebaa9))

### Fix

* fix(object_detection): fix import ([`7fc674e`](https://github.com/fhempy/fhempy/commit/7fc674e55a44302d3060e9f85d24ebdc91903c62))

### Unknown

* Merge branch &#39;development&#39; ([`46dc777`](https://github.com/fhempy/fhempy/commit/46dc777fc058c854b63d8e24bde30a08d60fe8ec))


## v0.1.432 (2022-08-20)

### Chore

* chore: update controls ([`109e94d`](https://github.com/fhempy/fhempy/commit/109e94d62afe226f6bba0039b3ae3f28980d00e7))

### Fix

* fix(ddnssde): fix ip_check_interval attr ([`5ebca91`](https://github.com/fhempy/fhempy/commit/5ebca91b068b857a1d0da5f5a47fdc562c513e6b))

### Unknown

* Merge branch &#39;development&#39; ([`db826c3`](https://github.com/fhempy/fhempy/commit/db826c3f2a613797e3451638606631b9465dcb7f))


## v0.1.431 (2022-08-20)

### Chore

* chore: update controls ([`5c67d07`](https://github.com/fhempy/fhempy/commit/5c67d073fcd8e8c0f0986750d359888ab7e2954d))

### Fix

* fix(object_detection): update opencv lib ([`192f91d`](https://github.com/fhempy/fhempy/commit/192f91dd70f3396be52f3ad3627bc8b9187ff7f9))

* fix(object_detection): update tflite-runtime ([`b2f5880`](https://github.com/fhempy/fhempy/commit/b2f588005d9257a1252bdadcfdef9591105a9aa7))

### Unknown

* Merge branch &#39;development&#39; ([`b2a41ad`](https://github.com/fhempy/fhempy/commit/b2a41adca56a3ba50ad70e637ea4eac6f77183a0))


## v0.1.430 (2022-08-20)

### Chore

* chore: update controls ([`ad76a82`](https://github.com/fhempy/fhempy/commit/ad76a8277e3e86513c39d727845b06f0b62d6cce))

### Fix

* fix(geizhals): add missing dependency ([`1bab5a8`](https://github.com/fhempy/fhempy/commit/1bab5a8c0cc77d00545ccd5f70001d4bfd9a3999))

### Unknown

* Merge branch &#39;development&#39; ([`5ae16bf`](https://github.com/fhempy/fhempy/commit/5ae16bf441f27f08b75b345dedf6571a109c4339))


## v0.1.429 (2022-08-20)

### Chore

* chore: update controls ([`1ed4b8f`](https://github.com/fhempy/fhempy/commit/1ed4b8f674391f8cf993d480f58ea966c023b245))

* chore: code style fixes ([`81f7b41`](https://github.com/fhempy/fhempy/commit/81f7b41450ccd65da2c7c8960e4ed1244b142da4))

* chore: add python 3.10 ([`55b06df`](https://github.com/fhempy/fhempy/commit/55b06df3b55d3050234147878a9a4a0d525eaa79))

* chore: fix python version ([`8df0f0a`](https://github.com/fhempy/fhempy/commit/8df0f0a36e4699ca4baaaf58510f4bf2cb0b0fa8))

* chore: update setup-python to v4 ([`7fe9f74`](https://github.com/fhempy/fhempy/commit/7fe9f74821b319dcdee6fd0d6e729f8967a34025))

* chore: fix tests ([`194f77f`](https://github.com/fhempy/fhempy/commit/194f77f3e83ee561ef345922d72c4c64ca662c2c))

### Unknown

* Merge branch &#39;development&#39; ([`8a3ecac`](https://github.com/fhempy/fhempy/commit/8a3ecacb0d72ce6b659f4018714cfc2d0a3a8589))

* Merge branch &#39;development&#39; ([`892ae3d`](https://github.com/fhempy/fhempy/commit/892ae3d04c5c004dc8c8ab7b94dc70246600429c))

* Merge branch &#39;development&#39; ([`0690ac1`](https://github.com/fhempy/fhempy/commit/0690ac1fc7fb4e4b8e297d0b5a6534f5771f3ebd))

* Merge branch &#39;development&#39; ([`d153ab4`](https://github.com/fhempy/fhempy/commit/d153ab4d03e0029dc4cf59a7162377a6336e99e2))


## v0.1.428 (2022-08-20)

### Chore

* chore: update controls ([`012d3df`](https://github.com/fhempy/fhempy/commit/012d3dfb1a0ad90c4d1cecd065b98fd7a9e7af8f))

### Unknown

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhempy ([`e8e55ac`](https://github.com/fhempy/fhempy/commit/e8e55ac0836326444776945d5395480143f40f47))


## v0.1.427 (2022-08-20)

### Chore

* chore: update controls ([`a9ffa57`](https://github.com/fhempy/fhempy/commit/a9ffa579da3d0e81a533fc1adb1c8688956faad1))

* chore: run tests on ubuntu-22.04 ([`77bb85d`](https://github.com/fhempy/fhempy/commit/77bb85d9eca8e6d1a619cff5f963a9cc95c8da6c))

### Unknown

* Merge branch &#39;development&#39; ([`9a22ff2`](https://github.com/fhempy/fhempy/commit/9a22ff20b2bd41f301414628f18cf835af8333fd))

* action: auto update controls ([`d90bad0`](https://github.com/fhempy/fhempy/commit/d90bad0b928270eb38c2a5b5f822e40cb7e414fe))


## v0.1.426 (2022-08-20)

### Chore

* chore: update controls ([`942db87`](https://github.com/fhempy/fhempy/commit/942db878bf1750894ded596ec8bd18cc4f265738))

* chore: run tests on ubuntu 22.04 ([`0ab5657`](https://github.com/fhempy/fhempy/commit/0ab5657ac69bbb20310dd0a5785832deef91ae85))

### Unknown

* Merge branch &#39;development&#39; ([`74a87af`](https://github.com/fhempy/fhempy/commit/74a87af8ca6be52b84250e1da7df5a7d9b502698))


## v0.1.425 (2022-08-20)

### Chore

* chore: update controls ([`f03ec5e`](https://github.com/fhempy/fhempy/commit/f03ec5e9932f749be6a906efb08233f8c49e17e0))

### Feature

* feat(ddnssde): add ddnss.de IP updater ([`5ec7e04`](https://github.com/fhempy/fhempy/commit/5ec7e0413af4aae2bc8e777ff86a5c3cc2fe81f8))

### Unknown

* Merge branch &#39;development&#39; ([`7e5b882`](https://github.com/fhempy/fhempy/commit/7e5b8828d306e5cc8d5d9d3f84423c5485d2d9b6))


## v0.1.424 (2022-08-13)

### Chore

* chore: update controls ([`bc288e1`](https://github.com/fhempy/fhempy/commit/bc288e1243dc778cc9f241d5c3ba61d8de82d0c2))

### Fix

* fix(fhempy): fix restart ([`4f7d452`](https://github.com/fhempy/fhempy/commit/4f7d45216fb967a69215d3b9ea20b0b9dcb62e69))

### Unknown

* Merge branch &#39;development&#39; ([`cfa1246`](https://github.com/fhempy/fhempy/commit/cfa1246ea61911c4785e4dbbeba5373cae549007))


## v0.1.423 (2022-08-13)

### Chore

* chore: update controls ([`c37afab`](https://github.com/fhempy/fhempy/commit/c37afab7ccea45747dd75ee53ed410a02eef3000))

### Fix

* fix(fhempy): stop sending msgs on shutdown ([`f1c9041`](https://github.com/fhempy/fhempy/commit/f1c90415e1af54b9dc07ed2ea303464f1abbf555))

### Unknown

* Merge branch &#39;development&#39; ([`1bf7c35`](https://github.com/fhempy/fhempy/commit/1bf7c3590e0d0dae6363e7744648416c55cca60b))


## v0.1.422 (2022-08-13)

### Chore

* chore: update controls ([`52f3b54`](https://github.com/fhempy/fhempy/commit/52f3b54221c64cd1df6f0bd8c4fc28bd06a9c3ac))

### Fix

* fix(fhempy): handle close frame ([`d8e5b44`](https://github.com/fhempy/fhempy/commit/d8e5b44e5a37dce52d1ae531bf8f289637e7a00b))

### Unknown

* Merge branch &#39;development&#39; ([`c72ba29`](https://github.com/fhempy/fhempy/commit/c72ba292cff0b70b8a1215a5f59a52b6f935244b))


## v0.1.421 (2022-08-13)

### Chore

* chore: update controls ([`8ce1297`](https://github.com/fhempy/fhempy/commit/8ce12971b518ed00319b108c5437e7dc24e7255d))

### Fix

* fix(fhempy): fix long running set on define ([`24f99f8`](https://github.com/fhempy/fhempy/commit/24f99f8a21bc38e0dab396f816d40dc650a46b01))

### Unknown

* Merge branch &#39;development&#39; ([`a112e4c`](https://github.com/fhempy/fhempy/commit/a112e4ccd9fa7f6782b88858fb2604c58e221259))


## v0.1.420 (2022-08-13)

### Chore

* chore: update controls ([`70d4a31`](https://github.com/fhempy/fhempy/commit/70d4a315955ffad134b379406a68970600b7dfe2))

### Fix

* fix(fhempy): add more details to readme ([`402735e`](https://github.com/fhempy/fhempy/commit/402735ec9274ecfd756eeecfc225dc705b3b8342))

### Unknown

* Merge branch &#39;development&#39; ([`ad1b75f`](https://github.com/fhempy/fhempy/commit/ad1b75f230dc123dddafbc9ea3ebc24ab88193f6))


## v0.1.419 (2022-08-13)

### Chore

* chore: update controls ([`0c7f81d`](https://github.com/fhempy/fhempy/commit/0c7f81d3c9a475d3b22bbc5b35bec79a866c7fb8))

### Fix

* fix(fhempy): logging seems to block fhempy ([`15872ee`](https://github.com/fhempy/fhempy/commit/15872eef3e5a3166d6d2c6982cab14cfc317a04e))

### Unknown

* Merge branch &#39;development&#39; ([`fae2b6a`](https://github.com/fhempy/fhempy/commit/fae2b6a7aa3fd53579fc0d3613c35d8d3dfcd343))


## v0.1.418 (2022-08-13)

### Chore

* chore: update controls ([`6dee8e2`](https://github.com/fhempy/fhempy/commit/6dee8e29ed8e67216edca46c48cfd1686fbc433b))

### Feature

* feat(fhempy): add long running log again ([`69ab9bc`](https://github.com/fhempy/fhempy/commit/69ab9bcb4c02f7fc5566a5dbdb7779c1d423b0e1))

### Fix

* fix(fhempy): reduce timeout, fix hangup ([`f90b516`](https://github.com/fhempy/fhempy/commit/f90b5165d7157558024fbced8459b4e908fc7fae))

### Unknown

* Merge branch &#39;development&#39; ([`d92d5fb`](https://github.com/fhempy/fhempy/commit/d92d5fbbc6e209dddfa10af82ed6575009e6baeb))


## v0.1.417 (2022-08-13)

### Chore

* chore: update controls ([`9f89cdf`](https://github.com/fhempy/fhempy/commit/9f89cdfb72f5077978902523f9ce2a7134f1244c))

### Fix

* fix(fhempy): fix hang on startup ([`d943ddd`](https://github.com/fhempy/fhempy/commit/d943ddd2ebf2fb542a06ba124a5ce409e841a17e))

### Unknown

* Merge branch &#39;development&#39; ([`a67b9ad`](https://github.com/fhempy/fhempy/commit/a67b9adf0b4792c413e5b6abcbc0d99986029a41))


## v0.1.416 (2022-08-13)

### Chore

* chore: update controls ([`5302d10`](https://github.com/fhempy/fhempy/commit/5302d103fd9af44c04b4848520b5ec1646625bec))

### Feature

* feat(fhempy): log error when fhempy takes over 100ms to reply to fhem ([`0649ec7`](https://github.com/fhempy/fhempy/commit/0649ec7c392da8b90dc5acecb8db864453fa4dd9))

### Unknown

* Merge branch &#39;development&#39; ([`64e36a2`](https://github.com/fhempy/fhempy/commit/64e36a2f9cb06e29a68d3caa9f368b095c12c863))


## v0.1.415 (2022-08-13)

### Chore

* chore: update controls ([`bed7c16`](https://github.com/fhempy/fhempy/commit/bed7c167b7e7b62bf8f2a1dfaf460ccd9eff5ca0))

### Feature

* feat(fhempy): log error if fhem took longer than 200ms to handle cmd ([`2767776`](https://github.com/fhempy/fhempy/commit/27677769cb7372055ebdff5255771ca31203fad5))

### Fix

* fix(xiaomi_tokens): fix logging ([`2859f1f`](https://github.com/fhempy/fhempy/commit/2859f1f0ac0c966401e21d3b482333d3975301d6))

### Unknown

* Merge branch &#39;development&#39; ([`7b03e36`](https://github.com/fhempy/fhempy/commit/7b03e36cf48d856784ec328374f8bc2ef898c6dd))


## v0.1.414 (2022-08-13)

### Chore

* chore: update controls ([`852eb95`](https://github.com/fhempy/fhempy/commit/852eb9564e87ed35716a35bb151a2aa09e8187a3))


## v0.1.413 (2022-08-13)

### Chore

* chore: update controls ([`21fae0a`](https://github.com/fhempy/fhempy/commit/21fae0a732e2e0fb27a26592f9662f3fdebde5a5))

* chore: touch BindingsIo insead of PythonModule ([`362c19f`](https://github.com/fhempy/fhempy/commit/362c19f3903c0481a7f93b1272f05cd133da9fb3))

### Fix

* fix(fhempy): better error handling for fhempy connection ([`a1fb108`](https://github.com/fhempy/fhempy/commit/a1fb10858b348f57fc6748af8e25ffc3b6444b53))

### Unknown

* Merge branch &#39;development&#39; ([`eb480c2`](https://github.com/fhempy/fhempy/commit/eb480c2228220edd50859bc2bb33a7d884ebfab4))


## v0.1.412 (2022-08-13)

### Chore

* chore: update controls ([`085a329`](https://github.com/fhempy/fhempy/commit/085a329f6afd09b58a532a59394e55f5adb65bdb))

### Feature

* feat(fhempy): add fhem log entry on update ([`dc89f94`](https://github.com/fhempy/fhempy/commit/dc89f9428dec62ab6d49a9ef002fa25dc995d63f))

### Fix

* fix(fhempy): better error handling ([`9331279`](https://github.com/fhempy/fhempy/commit/933127998e0f1c1ca69ff0d647f18631e786fb2e))

* fix(fhempy): deactivate MOV for controls file ([`4bb248b`](https://github.com/fhempy/fhempy/commit/4bb248bac3e7956dbefa7667d9403f4d788d75ca))

### Unknown

* Merge branch &#39;development&#39; ([`6e9ab0d`](https://github.com/fhempy/fhempy/commit/6e9ab0d0e5d61e2ec9ecee916965515a8cad99e9))


## v0.1.411 (2022-08-12)

### Chore

* chore: update controls ([`d7b3ab4`](https://github.com/fhempy/fhempy/commit/d7b3ab4bde4ace997a136c18e99dcd08404babc9))

### Feature

* feat(fhempy): receive all fhem events in fhempy ([`0aad85a`](https://github.com/fhempy/fhempy/commit/0aad85a1dccb1efb514fb2925175f7ee60199e67))

### Fix

* fix(fhempy): skip non-utf8 messages ([`c1abfd1`](https://github.com/fhempy/fhempy/commit/c1abfd1662af378e15c70e753fdbaf4b79336e4b))

* fix(fhempy): fix continue in some cases and fix devStateIcon ([`5c98ef5`](https://github.com/fhempy/fhempy/commit/5c98ef5c987c5076debf5324bd26f9ba4bb1e310))

* fix(fhempy): set devio log level to 5 ([`f5d9492`](https://github.com/fhempy/fhempy/commit/f5d94928e67a54c68c6348509505feb1b34ee9f9))

### Unknown

* Merge branch &#39;development&#39; ([`db4de9f`](https://github.com/fhempy/fhempy/commit/db4de9f1b7ca6b4492585918ae622f43025495ca))


## v0.1.410 (2022-08-12)

### Chore

* chore: update controls ([`a20c818`](https://github.com/fhempy/fhempy/commit/a20c8183ca29a44c7617ca80a7fa0fddf91d1228))

### Fix

* fix(xiaomi_tokens): fix newline from readings ([`4bba6f3`](https://github.com/fhempy/fhempy/commit/4bba6f3398d5b6e95e29c6be637c4b73aaa67ae9))

### Unknown

* Merge branch &#39;development&#39; ([`09aace2`](https://github.com/fhempy/fhempy/commit/09aace26b4ed9adcbd557bbf7f0c231190f30994))


## v0.1.409 (2022-08-12)

### Chore

* chore: update controls ([`6d1c1ad`](https://github.com/fhempy/fhempy/commit/6d1c1ad9712ac2433e8d6c61dc424e17ab8dc136))

### Fix

* fix(xiaomi_tokens): fix rstrip ([`9e5bc0d`](https://github.com/fhempy/fhempy/commit/9e5bc0dfc486b9815c5b1dd8c614c1d04f2d40a8))

### Unknown

* Merge branch &#39;development&#39; ([`7e4dfb8`](https://github.com/fhempy/fhempy/commit/7e4dfb8ccf8518f0c7a1544c9e70fb854bb52ff5))


## v0.1.408 (2022-08-12)

### Chore

* chore: update controls ([`d9a85c3`](https://github.com/fhempy/fhempy/commit/d9a85c3e09023b786527b244b9081591d2595f6c))

### Fix

* fix(fhempy): migrate to fhempyServer ([`710f79e`](https://github.com/fhempy/fhempy/commit/710f79e281b522eec6a1de3ffeaefc04f2bca429))

* fix(fhempy): migrate to fhempy ([`33ad82a`](https://github.com/fhempy/fhempy/commit/33ad82ae0c0f3f212af442d6075c2b05beb8ce8a))

* fix(xiaomi_tokens): remove newline from username, password ([`1e5ef64`](https://github.com/fhempy/fhempy/commit/1e5ef642e94df0d10e29fc118bbbc862b6332d97))

### Unknown

* Merge branch &#39;development&#39; ([`2a30bea`](https://github.com/fhempy/fhempy/commit/2a30bea124c9ba6969716642a171e63f5d417d71))


## v0.1.407 (2022-08-12)

### Chore

* chore: update controls ([`0da79ba`](https://github.com/fhempy/fhempy/commit/0da79ba09ff219c55dbefdc57cf8124b52279b7a))

### Fix

* fix(fhempy): log utf-8 decode error ([`5249cee`](https://github.com/fhempy/fhempy/commit/5249ceeb5b4fb966018be6815863cf918e4eedcd))

### Unknown

* Merge branch &#39;development&#39; ([`7c4e890`](https://github.com/fhempy/fhempy/commit/7c4e8903efffa22af0bbcd3725c929144085cf5a))


## v0.1.406 (2022-08-12)

### Chore

* chore: update controls ([`30bd1db`](https://github.com/fhempy/fhempy/commit/30bd1db13fe9ffab0be6e12c956691aa753ecfb0))

### Fix

* fix(fhempy): fix sendBackError without id ([`c32c271`](https://github.com/fhempy/fhempy/commit/c32c271fdc63b4d9303a250af8c32f150f80e118))

### Unknown

* Merge branch &#39;development&#39; ([`2d3aa43`](https://github.com/fhempy/fhempy/commit/2d3aa435e9410d4bc080dac680600cc27d97695f))


## v0.1.405 (2022-08-11)

### Chore

* chore: update controls ([`a83d482`](https://github.com/fhempy/fhempy/commit/a83d48249a32231f1794eb9fc6261a154a893f49))

### Fix

* fix(fhempy): send back error on json error ([`7d951d1`](https://github.com/fhempy/fhempy/commit/7d951d1dc87f4d8a879ffd0d785dc1440367e81e))

* fix(fhempy): send binary data via websocket ([`912f15f`](https://github.com/fhempy/fhempy/commit/912f15f06d08c9ced432ae2a6760d65c0d27ea80))

### Unknown

* Merge branch &#39;development&#39; ([`120bb42`](https://github.com/fhempy/fhempy/commit/120bb421b29e577756c00369994b6546c4c74bfe))


## v0.1.404 (2022-08-11)

### Chore

* chore: update controls ([`9b2de63`](https://github.com/fhempy/fhempy/commit/9b2de63a159c493e8bcbe8d27685b9889d2b0818))

### Fix

* fix(fhempy): fix message handling ([`6c3a835`](https://github.com/fhempy/fhempy/commit/6c3a8351ac1c6269d0208f4ea27a9d81c687a363))

### Unknown

* Merge branch &#39;development&#39; ([`9d18e72`](https://github.com/fhempy/fhempy/commit/9d18e722a48992ec807b7c48bffe115eaef1eb48))


## v0.1.403 (2022-08-11)

### Chore

* chore: update controls ([`b9ecef7`](https://github.com/fhempy/fhempy/commit/b9ecef78f9818f10882f792614c3399cf6844788))

### Feature

* feat(fhempy): support binary messages from fhem ([`63d8b92`](https://github.com/fhempy/fhempy/commit/63d8b92ecb6a0aa6eb08720eb6e20b9b43438176))

### Fix

* fix(esphome): update esphome lib ([`6cff272`](https://github.com/fhempy/fhempy/commit/6cff2724203a6ae50feaf909c59dce2dac7da3ad))

* fix(fhem_forum): fix state reading ([`6f42906`](https://github.com/fhempy/fhempy/commit/6f42906e7436303df50dd086d1cfb9e968b502aa))

### Unknown

* Merge branch &#39;development&#39; ([`1961d74`](https://github.com/fhempy/fhempy/commit/1961d74556ef0e6fe8205c5cafad290e21907ef8))


## v0.1.402 (2022-08-10)

### Chore

* chore: update controls ([`4dd2092`](https://github.com/fhempy/fhempy/commit/4dd209287af731871f0c5a6da3a2c6a95df3872d))

### Fix

* fix(fhempy): fix disconnected icon ([`05994b9`](https://github.com/fhempy/fhempy/commit/05994b970a69b032abf2b8a35e213f2fcc11eb8f))

### Unknown

* Merge branch &#39;development&#39; ([`a745123`](https://github.com/fhempy/fhempy/commit/a74512340f2dd7769e43717d35b816125e7acb20))


## v0.1.401 (2022-08-10)

### Chore

* chore: update controls ([`27f5849`](https://github.com/fhempy/fhempy/commit/27f584967a76883da6114af3834fbe24c4a4fcfc))

### Fix

* fix(fhempy): update available fhempy version every 12 hours ([`8af8092`](https://github.com/fhempy/fhempy/commit/8af8092ff0a76b39e3827b97a54223324967f441))

### Unknown

* Merge branch &#39;development&#39; ([`3c80ebb`](https://github.com/fhempy/fhempy/commit/3c80ebb7f3bcf2d99bf085fd54b92198213579e6))


## v0.1.400 (2022-08-10)

### Chore

* chore: update controls ([`ff3e06e`](https://github.com/fhempy/fhempy/commit/ff3e06e30c52b2421b1428fbf700ae2e4088c91d))

### Fix

* fix(fhempy): always show update icon in BindingsIo device ([`cb322da`](https://github.com/fhempy/fhempy/commit/cb322da3014d80f3f17686d81594eee54eaa4621))

### Unknown

* Merge branch &#39;development&#39; ([`4f70418`](https://github.com/fhempy/fhempy/commit/4f704184b72d012f605ac097af009cd9410f72dc))


## v0.1.399 (2022-08-10)

### Chore

* chore: update controls ([`6fe451c`](https://github.com/fhempy/fhempy/commit/6fe451c64be17fbfff673536d2f7b02063387a6c))

### Feature

* feat(fhempy): add info about available update ([`23fd613`](https://github.com/fhempy/fhempy/commit/23fd613b9f6430b85c8371e1edbcdb4dd3f2f0f3))

### Unknown

* Merge branch &#39;development&#39; ([`650ef78`](https://github.com/fhempy/fhempy/commit/650ef7843fbc7cc79cae075dac002598cef471b6))


## v0.1.398 (2022-08-10)

### Chore

* chore: update controls ([`a1f3b32`](https://github.com/fhempy/fhempy/commit/a1f3b32af2f04516732d4dd2d05e8abd194679e3))

### Fix

* fix(fhempy): fix README for blocking code ([`81e332f`](https://github.com/fhempy/fhempy/commit/81e332fcad42a8c00f8ab2a270d4c65bca3b7a5b))

* fix(fhem_forum): fix state reading ([`e0abe40`](https://github.com/fhempy/fhempy/commit/e0abe40e32ffe4b842e6f83252f00846c9159e8c))

### Unknown

* Merge branch &#39;development&#39; ([`f086a81`](https://github.com/fhempy/fhempy/commit/f086a813fb3ae49518fd49d8a6ea3ee9511357be))


## v0.1.397 (2022-08-10)

### Chore

* chore: update controls ([`a5910f2`](https://github.com/fhempy/fhempy/commit/a5910f26e63a816ef0f28f592db33ce3c8552dd3))

### Feature

* feat(miio): update python-miio lib ([`b5b65ac`](https://github.com/fhempy/fhempy/commit/b5b65acab2ceabeb25b25eeab190021ccbfc7e0a))

### Unknown

* Merge branch &#39;development&#39; ([`ba7b98e`](https://github.com/fhempy/fhempy/commit/ba7b98e37a2387af3a30fc38b72f69d63be1b2f7))


## v0.1.396 (2022-08-10)

### Chore

* chore: update controls ([`b608988`](https://github.com/fhempy/fhempy/commit/b60898869f7db0f09e16ddbfd9810f70973977f3))

### Feature

* feat(geizhals): add alias attr, best store reading and store availability ([`874d5c9`](https://github.com/fhempy/fhempy/commit/874d5c9b6c437b2128d0131c0135e9457b3bd363))

### Fix

* fix(fhempy): change timeout to 60s on shutdown/restart ([`0b87dbf`](https://github.com/fhempy/fhempy/commit/0b87dbfef46fcdc5b44ab7f9f6e44ccdbb297ba0))

* fix(fhem_forum): fix keyword handling and state reading ([`a6af955`](https://github.com/fhempy/fhempy/commit/a6af955e48fbed5457f18ceed794526856be6e23))

* fix(fhem_forum): fix state ([`7371bf4`](https://github.com/fhempy/fhempy/commit/7371bf40b6860ac585d606aa1812c1babc99668d))

### Unknown

* Merge branch &#39;development&#39; ([`8caa49f`](https://github.com/fhempy/fhempy/commit/8caa49f3c95fd965096ea50843a1028d99b7f4dd))


## v0.1.395 (2022-08-09)

### Chore

* chore: update controls ([`6cdffbe`](https://github.com/fhempy/fhempy/commit/6cdffbe5b2d2fe3e76f7b787d01a0b53dca79d90))

### Feature

* feat(fhem_forum): check FHEM forum for updates ([`4e843e0`](https://github.com/fhempy/fhempy/commit/4e843e024fb8cd7ad6f14a48f4c58b0929b9b33a))

### Unknown

* Merge branch &#39;development&#39; ([`9471e79`](https://github.com/fhempy/fhempy/commit/9471e790e0d5b63f7884d3cc125e98aadbdecb95))


## v0.1.394 (2022-08-09)

### Chore

* chore: update controls ([`f3d8c1b`](https://github.com/fhempy/fhempy/commit/f3d8c1bc39b11f8e1a3c9af5c969e8ee62164597))

### Fix

* fix(fhempy): fix restart/shutdown issues ([`8198930`](https://github.com/fhempy/fhempy/commit/8198930a92ca50c86db8c91e8e12a3466dd98447))

* fix(geizhals): change default update interval ([`e11770e`](https://github.com/fhempy/fhempy/commit/e11770e95aa05cb509db6604572ae8f9941360a6))

* fix(google_weather): add headers ([`5b0d423`](https://github.com/fhempy/fhempy/commit/5b0d4237cd37df7bbf71d963f5cd834273969d66))

### Unknown

* Merge branch &#39;development&#39; ([`44b835d`](https://github.com/fhempy/fhempy/commit/44b835d45557c0b02adc73e8d2559ac16fc5c5ae))


## v0.1.393 (2022-08-08)

### Chore

* chore: update controls ([`2115f4b`](https://github.com/fhempy/fhempy/commit/2115f4b54675486416f7ef2186eae967060b9fdf))

### Feature

* feat(geizhals): add link reading ([`fd9ee3a`](https://github.com/fhempy/fhempy/commit/fd9ee3a876fe624d2a6f8e14690b670521dd546c))

### Unknown

* Merge branch &#39;development&#39; ([`afa1ed7`](https://github.com/fhempy/fhempy/commit/afa1ed7cb83297c98e3de56c7daaae6360177f25))


## v0.1.392 (2022-08-07)

### Chore

* chore: update controls ([`369b14d`](https://github.com/fhempy/fhempy/commit/369b14d12743100f9d1fde1bdcfe0bbfca6db53b))

### Fix

* fix(tuya): correct current, power values ([`229d549`](https://github.com/fhempy/fhempy/commit/229d54968dd365662ccde90bc81207715a638991))

* fix(warema): add README ([`f836930`](https://github.com/fhempy/fhempy/commit/f8369301590ee560fa25beeeeecdc3ad79aac107))

### Unknown

* Merge branch &#39;development&#39; ([`2e9fe8a`](https://github.com/fhempy/fhempy/commit/2e9fe8a6beaf676a25f6b09d2572a54049eb02ae))


## v0.1.391 (2022-08-06)

### Chore

* chore: update controls ([`d5df523`](https://github.com/fhempy/fhempy/commit/d5df5235f4ce13682fdba6833bed0a88b135e172))

### Fix

* fix(tuya): fix dp readings when locally not detected ([`e4b5f92`](https://github.com/fhempy/fhempy/commit/e4b5f928d6dc9e8f61bd6ebd35200016f51aa0fc))

### Unknown

* Merge branch &#39;development&#39; ([`6d83724`](https://github.com/fhempy/fhempy/commit/6d8372400a2edb0c2293807e720e5046cd60de0c))


## v0.1.390 (2022-08-06)

### Chore

* chore: update controls ([`3066b47`](https://github.com/fhempy/fhempy/commit/3066b47172dd7ca578b2c8c6604471d708f533d7))

### Fix

* fix(tuya): add debug msgs ([`53732a9`](https://github.com/fhempy/fhempy/commit/53732a97581df0b4e55037d751ebc92677b5d236))

### Unknown

* Merge branch &#39;development&#39; ([`113d06d`](https://github.com/fhempy/fhempy/commit/113d06d31829ff5accce568295508da8ea01d410))


## v0.1.389 (2022-08-06)

### Chore

* chore: update controls ([`c10d115`](https://github.com/fhempy/fhempy/commit/c10d1156583cada247fcdb974a8d94a815710530))

### Feature

* feat(kia_hyundai): support commands ([`4fa92bf`](https://github.com/fhempy/fhempy/commit/4fa92bfc36fc030b24a8ec8d19ea9deae1611119))

### Unknown

* Merge branch &#39;development&#39; ([`f64ee7a`](https://github.com/fhempy/fhempy/commit/f64ee7aacdf094e0da459b330beda8d77a6eccb5))


## v0.1.388 (2022-08-06)

### Chore

* chore: update controls ([`52d10a5`](https://github.com/fhempy/fhempy/commit/52d10a5e9f29b102075776adab8dd361c8d63be7))

### Feature

* feat(kia_hyundai): initial release for Kia / Hyundai cars ([`08987cb`](https://github.com/fhempy/fhempy/commit/08987cbeedcf8ed235e952950a6f0d5cf13606eb))

### Unknown

* Merge branch &#39;development&#39; ([`7ca2706`](https://github.com/fhempy/fhempy/commit/7ca27069956089952abdaa94ab36e5c9cc59e38f))


## v0.1.387 (2022-08-06)

### Chore

* chore: update controls ([`95f07b7`](https://github.com/fhempy/fhempy/commit/95f07b7e2446cb25025d84c59e28b5b74f1acb26))

### Feature

* feat(tuya): support Json for category zndb devices ([`53209ff`](https://github.com/fhempy/fhempy/commit/53209ff361fabfe3d8b6dc4014753234cbbe0487))

### Unknown

* Merge branch &#39;development&#39; ([`9c98c72`](https://github.com/fhempy/fhempy/commit/9c98c72a36f33276a8c3b5048eb8c960f8e9ddde))


## v0.1.386 (2022-08-05)

### Chore

* chore: update controls ([`91e6682`](https://github.com/fhempy/fhempy/commit/91e66822952117e99431bf6ddd2a6edd56d46a72))

### Feature

* feat(tuya): split json into multiple readings ([`366d729`](https://github.com/fhempy/fhempy/commit/366d729267d27c9603bef1bbe1a929ef5cca9f97))

### Fix

* fix(fusionsolar): better error handling ([`03d67f3`](https://github.com/fhempy/fhempy/commit/03d67f3e0b191be42d8c08f7b2e3d949624bbb85))

* fix(fhempy): support string format for flatten_json ([`d7457a8`](https://github.com/fhempy/fhempy/commit/d7457a851d0374fc1fda76ece0fa775f7c3234f0))

### Unknown

* Merge branch &#39;development&#39; ([`a34c512`](https://github.com/fhempy/fhempy/commit/a34c512b07c8cdaa30461ad5623b03b4611e1d37))


## v0.1.385 (2022-08-04)

### Chore

* chore: update controls ([`7a80ba6`](https://github.com/fhempy/fhempy/commit/7a80ba640fe3a991846248801df29dc026eb7319))

### Feature

* feat(geizhals): add geizhals module ([`dda5f09`](https://github.com/fhempy/fhempy/commit/dda5f0989f2adb395c1ac9b3be9157f2a4421512))

### Unknown

* Merge branch &#39;development&#39; ([`75bc0e3`](https://github.com/fhempy/fhempy/commit/75bc0e3ee8710f900fe01497ce96bec92fd28808))


## v0.1.384 (2022-08-04)

### Chore

* chore: update controls ([`3f225b7`](https://github.com/fhempy/fhempy/commit/3f225b7c7592480fe99bdbd46b7c5850b1e3cffd))

### Feature

* feat(geizhals): retrieve best prices from geizhals ([`b6c935e`](https://github.com/fhempy/fhempy/commit/b6c935e75521d9432b18541aa9c2d55f86c19b6d))

### Fix

* fix(google_weather): fix replace command ([`311ee9c`](https://github.com/fhempy/fhempy/commit/311ee9c9adc10d481b89819be532d1b212c905ec))

### Unknown

* Merge branch &#39;development&#39; ([`246b382`](https://github.com/fhempy/fhempy/commit/246b382a7b5337f6fdea8c09d4cbdf087745e3b1))


## v0.1.383 (2022-08-04)

### Chore

* chore: update controls ([`07e723b`](https://github.com/fhempy/fhempy/commit/07e723b219b8342d6bc38b38c816b122726e69e6))

### Feature

* feat(google_weather): add hourly weather data ([`65101c3`](https://github.com/fhempy/fhempy/commit/65101c33101c5a8996d3ab07cbccd1728fff8580))

### Unknown

* Merge branch &#39;development&#39; ([`2cac292`](https://github.com/fhempy/fhempy/commit/2cac29227ff3daeb2920a8cbbe2b86119ac5f1c4))


## v0.1.382 (2022-08-03)

### Chore

* chore: update controls ([`60f37c9`](https://github.com/fhempy/fhempy/commit/60f37c98bf390c0ab39a975ab029bcc429f4195a))

### Unknown

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhempy ([`50f6972`](https://github.com/fhempy/fhempy/commit/50f6972370c3ce2ee67f68c834c61fc49cec5898))


## v0.1.381 (2022-08-03)

### Chore

* chore: update controls ([`f3d65ce`](https://github.com/fhempy/fhempy/commit/f3d65ce808aa12097c97a86391e230bfab4fe847))

* chore: update naming ([`e1aa1cc`](https://github.com/fhempy/fhempy/commit/e1aa1ccfcb32e72ea8195bc5212ef355dc73fb9b))

### Feature

* feat(google_weather): add google weather ([`6a45ff5`](https://github.com/fhempy/fhempy/commit/6a45ff5f23a2fc545075ee22186507d44e0cf3a6))

### Fix

* fix(zigbee2mqtt): fix restart ([`d872abd`](https://github.com/fhempy/fhempy/commit/d872abd0581c045a4beac6c5f11a4bcc1fcbf1bc))

* fix(gree_climate): update greeclimate lib ([`db874ed`](https://github.com/fhempy/fhempy/commit/db874ed9a002ecf6ba4906501a08fbf09ad4370c))

### Unknown

* Merge branch &#39;development&#39; ([`6cfa7aa`](https://github.com/fhempy/fhempy/commit/6cfa7aaaad11d633801b9d79d5b8959e095a307d))

* Create FUNDING.yml ([`a33fc46`](https://github.com/fhempy/fhempy/commit/a33fc469f20f428d6c7873519e07067c8fe7716d))


## v0.1.380 (2022-07-16)

### Chore

* chore: update controls ([`e09a9f2`](https://github.com/fhempy/fhempy/commit/e09a9f29abd3fe349f6c4157240dd3afea5462a7))

### Fix

* fix(fhempy): handle defmod/modify properly ([`c0e29df`](https://github.com/fhempy/fhempy/commit/c0e29df6ac8cb38c8c12bfe1185414bb3d85daf4))

### Unknown

* Merge branch &#39;development&#39; ([`c386e1d`](https://github.com/fhempy/fhempy/commit/c386e1d2194201d56e499b991baea5d74db44796))


## v0.1.379 (2022-07-15)

### Chore

* chore: update controls ([`43ec5aa`](https://github.com/fhempy/fhempy/commit/43ec5aaceef7a1b86bab6c66d963f02bf52002fb))

### Fix

* fix(gree_climate): retry to establish connection on startup ([`4a8141c`](https://github.com/fhempy/fhempy/commit/4a8141c47d4a6829ac50e700df59d3ab358d3df3))

### Unknown

* Merge branch &#39;development&#39; ([`f210ca0`](https://github.com/fhempy/fhempy/commit/f210ca0e5e31c4d8bd2986749980b7268809779e))


## v0.1.378 (2022-07-13)

### Chore

* chore: update controls ([`f639680`](https://github.com/fhempy/fhempy/commit/f63968072338b62ad397389b971dbc713879b6aa))

### Fix

* fix(fusionsolar): fix login procedure ([`a2387c1`](https://github.com/fhempy/fhempy/commit/a2387c12f9ba53a5ac1b6d79b5785f41441aaf98))

### Unknown

* Merge branch &#39;development&#39; ([`3c1a11f`](https://github.com/fhempy/fhempy/commit/3c1a11f4042e9014e2ba4ac0a64d17d4312e6d32))


## v0.1.377 (2022-07-13)

### Chore

* chore: update controls ([`36ee2ee`](https://github.com/fhempy/fhempy/commit/36ee2ee64c96b35d752f65817af7ba49ce9361a9))

### Fix

* fix(fusionsolar): add debug output ([`ba2c97f`](https://github.com/fhempy/fhempy/commit/ba2c97f52e0fded216cfb2231175a54bce1fe7c5))

### Unknown

* Merge branch &#39;development&#39; ([`e0804f1`](https://github.com/fhempy/fhempy/commit/e0804f16845742add4713181c069daf08021090a))


## v0.1.376 (2022-07-12)

### Chore

* chore: update controls ([`3d0e182`](https://github.com/fhempy/fhempy/commit/3d0e18280f1c5632a682c282e92766d03df387ee))

### Fix

* fix(fhempy): fix ssdp ([`95febe2`](https://github.com/fhempy/fhempy/commit/95febe2d1b9f79d0ab8d267d77d8e683d7adec19))

### Unknown

* Merge branch &#39;development&#39; ([`e48f491`](https://github.com/fhempy/fhempy/commit/e48f4913b291c5100bef589d3bcd43445ae2f7c4))


## v0.1.375 (2022-07-12)

### Chore

* chore: update controls ([`62bcdb2`](https://github.com/fhempy/fhempy/commit/62bcdb257969e45990b941ea0950d7a17b42e63d))

### Fix

* fix(fhempy): update cryptography, aiohttp, async-upnp-client ([`7d7f654`](https://github.com/fhempy/fhempy/commit/7d7f65438335d5efaee9a2cc1cd113486562bd5d))

### Unknown

* Merge branch &#39;development&#39; ([`8c48840`](https://github.com/fhempy/fhempy/commit/8c488400b810e5923ebf6e333bbf52b981bc9ab3))


## v0.1.374 (2022-07-12)

### Chore

* chore: update controls ([`8beda46`](https://github.com/fhempy/fhempy/commit/8beda4660122d67fd4089443ec9f7bd84d12127c))

### Fix

* fix(dlna_dmr): fix manifest ([`98a7f03`](https://github.com/fhempy/fhempy/commit/98a7f036650546c7fc55303e568398569918d960))

### Unknown

* Merge branch &#39;development&#39; ([`149d23d`](https://github.com/fhempy/fhempy/commit/149d23d22767936952778ac58f22325175681ae3))


## v0.1.373 (2022-07-12)

### Chore

* chore: update controls ([`258571b`](https://github.com/fhempy/fhempy/commit/258571b7c33977107954db1a50ef10e8d3f60287))

### Fix

* fix(wienerlinien): fix requirements ([`85679d4`](https://github.com/fhempy/fhempy/commit/85679d48a1c970f0824b7f0aaeaced057fc7a136))

### Unknown

* Merge branch &#39;development&#39; ([`de9b48a`](https://github.com/fhempy/fhempy/commit/de9b48aea9a3b9506102ae89c9b6c9144e905c42))


## v0.1.372 (2022-07-12)

### Chore

* chore: update controls ([`29107a4`](https://github.com/fhempy/fhempy/commit/29107a442be79f2474e3b821c6f328b0cf310b10))

### Fix

* fix(fhempy): fix aiohttp bug ([`2cd64fd`](https://github.com/fhempy/fhempy/commit/2cd64fd25819b47a749d6accd6741d1e22584625))

### Unknown

* Merge branch &#39;development&#39; ([`3e4ec68`](https://github.com/fhempy/fhempy/commit/3e4ec68a0c95874d60412f3a400805a400505831))


## v0.1.371 (2022-07-12)

### Chore

* chore: update controls ([`9c95ef9`](https://github.com/fhempy/fhempy/commit/9c95ef9bc03c8fdc4e2d6b2c28966c9c54f2fee6))

### Fix

* fix(fhempy): disable events because of utf-8 bug ([`3a3bf25`](https://github.com/fhempy/fhempy/commit/3a3bf25f2535ff2fadc490c7a917c40b9e11b94e))

### Unknown

* Merge branch &#39;development&#39; ([`7e1846e`](https://github.com/fhempy/fhempy/commit/7e1846e3f464870a37d1674e43f791802ca7e7b2))


## v0.1.370 (2022-07-10)

### Chore

* chore: update controls ([`923f781`](https://github.com/fhempy/fhempy/commit/923f781995a8a9048787c0fa694c20d442c4fcff))

### Feature

* feat(fusionsolar): BREAKING CHANGE, see README. Username/password support instead of sessionid. ([`0a3d94d`](https://github.com/fhempy/fhempy/commit/0a3d94de9fa15d854e28076684fbf033039f0c0c))

### Unknown

* Merge branch &#39;development&#39; ([`b7ff047`](https://github.com/fhempy/fhempy/commit/b7ff0473b5b6207c555c64cabdfca512032ecace))


## v0.1.369 (2022-07-09)

### Chore

* chore: update controls ([`e83bab5`](https://github.com/fhempy/fhempy/commit/e83bab50743074a05f2c57d19e2c376f594f7c83))

### Feature

* feat(volvo_software_update): new module which notifies about volvo software updates ([`aada589`](https://github.com/fhempy/fhempy/commit/aada58901979f5c79d2ddbc8640890cd21e6e957))

### Fix

* fix(fhempy): fix event handling ([`8649e04`](https://github.com/fhempy/fhempy/commit/8649e04cda8fde246a0ee4c187af1f74a4b3c79a))

* fix(tuya): prevent error when attr dp_xx is not available localy ([`30ebebf`](https://github.com/fhempy/fhempy/commit/30ebebff1af3aaede5a8ff01ad96642229c970a0))

* fix(fusionsolar): support new web api ([`31423a8`](https://github.com/fhempy/fhempy/commit/31423a8f1309eb4c46607c70e4608dbca13dab82))

* fix(googlecast): update pychromecast lib ([`d30c288`](https://github.com/fhempy/fhempy/commit/d30c288f020978b525ea2ef8d27f3d02b6afaa0c))

### Unknown

* Merge branch &#39;development&#39; ([`242cdcb`](https://github.com/fhempy/fhempy/commit/242cdcba6249cf97ed3fbf5142e03581cb0858a3))


## v0.1.368 (2022-06-20)

### Chore

* chore: update controls ([`3c714dc`](https://github.com/fhempy/fhempy/commit/3c714dcb3325b9614c2d6804365c4b763aa1999b))

### Fix

* fix(fhempy): fix ble disconnect failure ([`1142d94`](https://github.com/fhempy/fhempy/commit/1142d94de4a365449b531acdc71995045149fe35))

* fix(fhempy): fix naming ([`6b7ddc2`](https://github.com/fhempy/fhempy/commit/6b7ddc2dc71483d0b08bc3d9a38c354746ce4818))

* fix(fusionsolar): fix string energy ([`f015ac7`](https://github.com/fhempy/fhempy/commit/f015ac71d4b7c0908ecbaa74bc6f7ab29f020788))

### Unknown

* Merge branch &#39;development&#39; ([`15785ec`](https://github.com/fhempy/fhempy/commit/15785ec64d687b0f572589df0b6a58f994ff92a8))


## v0.1.367 (2022-06-17)

### Chore

* chore: update controls ([`5eaba85`](https://github.com/fhempy/fhempy/commit/5eaba855e445f587bb13b13289ff0a30f4ba1857))

### Fix

* fix(fusionsolar): fix string_output_power ([`4f83d8a`](https://github.com/fhempy/fhempy/commit/4f83d8ab6b3a04820ce7dc75b10a11d23f0a743c))

### Unknown

* Merge branch &#39;development&#39; ([`cea2b4c`](https://github.com/fhempy/fhempy/commit/cea2b4c651e1b21873ab584824cf2b3b738175d5))


## v0.1.366 (2022-06-16)

### Chore

* chore: update controls ([`e4ff7aa`](https://github.com/fhempy/fhempy/commit/e4ff7aa4b8eabb66bc1f54a7834e9e5bacbaebda))

### Fix

* fix(fusionsolar): fix NoneType exception ([`9cc40c3`](https://github.com/fhempy/fhempy/commit/9cc40c3bc188b8a4deb1ed7c2193828b7f0a7264))

### Unknown

* Merge branch &#39;development&#39; ([`33ea55e`](https://github.com/fhempy/fhempy/commit/33ea55e3dbb32ce458fd7c796a7b88bdeb199774))


## v0.1.365 (2022-06-15)

### Chore

* chore: update controls ([`44bf295`](https://github.com/fhempy/fhempy/commit/44bf295a8a2ff10070c4f905eaed59c41037a581))

### Fix

* fix(tuya): do not raise exception if decoding fails ([`1371ca4`](https://github.com/fhempy/fhempy/commit/1371ca4376c5365b940d94074363796286cf418e))

### Unknown

* Merge branch &#39;development&#39; ([`1c4ad68`](https://github.com/fhempy/fhempy/commit/1c4ad68e09c0e62e399d07173aa0d16881409a9b))


## v0.1.364 (2022-06-14)

### Chore

* chore: update controls ([`248d9d2`](https://github.com/fhempy/fhempy/commit/248d9d2e99473386c5bb6d9d2e0a9c860f73231e))

### Fix

* fix(tuya): add logging if payload decoding fails ([`79953c5`](https://github.com/fhempy/fhempy/commit/79953c5de67e1f1e950336cbec6d32903af8da67))

### Unknown

* Merge branch &#39;development&#39; ([`c8762ef`](https://github.com/fhempy/fhempy/commit/c8762efbcca77e0acad261d6b3d9ff681589be19))


## v0.1.363 (2022-06-13)

### Chore

* chore: update controls ([`fa43ebe`](https://github.com/fhempy/fhempy/commit/fa43ebe9ec7eb646800f11e993cadb61d59025c1))

### Fix

* fix(fusionsolar): prevent token to expire ([`9629bfb`](https://github.com/fhempy/fhempy/commit/9629bfb16133595248c6b5d3df856483c546e67b))

* fix(gfprobt): do not send parallel commands ([`3f1e504`](https://github.com/fhempy/fhempy/commit/3f1e504cf6992337abb0886d4f19316dd42c2915))

* fix(gfprobt): fix adjust ([`54427b2`](https://github.com/fhempy/fhempy/commit/54427b2e3f9aade0ba6400b58cbeea48574d1c95))

### Unknown

* Merge branch &#39;development&#39; ([`eb9c7dc`](https://github.com/fhempy/fhempy/commit/eb9c7dc94fd8da40b2cba8037bba11915d0e2e31))


## v0.1.362 (2022-06-10)

### Chore

* chore: update controls ([`3a1e82e`](https://github.com/fhempy/fhempy/commit/3a1e82ee5bb24ac5c2c8e1bc77d266072f0c0fb4))

### Feature

* feat(fusionsolar): add string_output_power ([`84bdaa1`](https://github.com/fhempy/fhempy/commit/84bdaa155871bd199c21a46e87af5e690c803484))

### Unknown

* Merge branch &#39;development&#39; ([`33cca51`](https://github.com/fhempy/fhempy/commit/33cca512bb01e6782d57937df8f22e6cc0ecb6f5))


## v0.1.361 (2022-06-10)

### Chore

* chore: update controls ([`d9319de`](https://github.com/fhempy/fhempy/commit/d9319deface61203b28ed17fca0734b88f313f51))

### Fix

* fix(fusionsolar): add idle call ([`987a88a`](https://github.com/fhempy/fhempy/commit/987a88ab4f91e68f96e745db2acebb0a59f3bc28))

* fix(fhempy): fix local restart ([`3842026`](https://github.com/fhempy/fhempy/commit/38420261e3176d6cc43b32f73c219833706efe50))

### Unknown

* Merge branch &#39;development&#39; ([`df3fcbc`](https://github.com/fhempy/fhempy/commit/df3fcbc0bf192539e62124dd03fed08829337964))


## v0.1.360 (2022-06-04)

### Chore

* chore: update controls ([`a978428`](https://github.com/fhempy/fhempy/commit/a97842866edda2d01650636f0561b1c0d35aa56a))

### Fix

* fix(googlecast): update lib and fix protobuf ([`bf73a18`](https://github.com/fhempy/fhempy/commit/bf73a182363dc39bcafc9570ec0b3579f484c814))

### Unknown

* Merge branch &#39;development&#39; ([`34fed50`](https://github.com/fhempy/fhempy/commit/34fed506d7c5c6d17067cab43da81a9a93fbbb80))


## v0.1.359 (2022-06-04)

### Chore

* chore: update controls ([`9b1ab09`](https://github.com/fhempy/fhempy/commit/9b1ab09ea3a698548585bf53e48336d971eace5d))

### Fix

* fix(tuya): improve state text when device couldn&#39;t be discovered ([`2db8add`](https://github.com/fhempy/fhempy/commit/2db8addc3bcd993f6294b8211c72a2b065a0eab4))

* fix(fusionsolar): fix division by zero exception ([`765982c`](https://github.com/fhempy/fhempy/commit/765982c9401c08aa1d400b23128888a3c4acaa19))

### Unknown

* Merge branch &#39;development&#39; ([`5ee2e74`](https://github.com/fhempy/fhempy/commit/5ee2e7447f483823d0bb0fa8852fdce464854bd4))


## v0.1.358 (2022-05-23)

### Chore

* chore: update controls ([`490f989`](https://github.com/fhempy/fhempy/commit/490f98974095cbc8cc0ac5dcfaf5e7f74f44411f))

### Fix

* fix(fhempy): downgrade libraries to working versions ([`8ba4662`](https://github.com/fhempy/fhempy/commit/8ba46629905c6233ef3a79ae204e0d7dc468fd8d))

### Unknown

* Merge branch &#39;development&#39; ([`d1451a0`](https://github.com/fhempy/fhempy/commit/d1451a055245cf42ceef0e8898fac4356dfe6896))


## v0.1.357 (2022-05-19)

### Chore

* chore: update controls ([`844fa03`](https://github.com/fhempy/fhempy/commit/844fa0321f51d4af9045c8d598bfe1d4b98a56b2))

### Fix

* fix(fhempy): revert aiohttp version ([`905dfe0`](https://github.com/fhempy/fhempy/commit/905dfe01af0aeb3a7894aa945b855370e2486ec5))

### Unknown

* Merge branch &#39;development&#39; ([`d5d8340`](https://github.com/fhempy/fhempy/commit/d5d83400b068ed5de5715156b20f536978a38a59))


## v0.1.356 (2022-05-19)

### Chore

* chore: update controls ([`ac89578`](https://github.com/fhempy/fhempy/commit/ac8957856330d068b8cae382a15261c2591c4bbc))

### Fix

* fix(fhempy): update libraries ([`20f40b8`](https://github.com/fhempy/fhempy/commit/20f40b86fbccc160f254cf2d184e301eccb8e8fe))

* fix(fhempy): cleanup imports ([`d66b01a`](https://github.com/fhempy/fhempy/commit/d66b01a6e0ff1d70feb6b34b12910066dd558a0b))

### Unknown

* Merge branch &#39;development&#39; ([`85a9d61`](https://github.com/fhempy/fhempy/commit/85a9d616b3c1e79230d0e36bae2afa4e20a7f4e9))


## v0.1.355 (2022-05-19)

### Chore

* chore: update controls ([`cdae011`](https://github.com/fhempy/fhempy/commit/cdae01102ea1eab807bac964132dda1b6df2283c))

### Fix

* fix(fhempy): update zeroconf to 0.38.6 ([`4f60df8`](https://github.com/fhempy/fhempy/commit/4f60df8a79f804b97016588aefb80d3575e7bb5f))

### Unknown

* Merge branch &#39;development&#39; ([`088f762`](https://github.com/fhempy/fhempy/commit/088f762de60868780d04383c3d58cb3603e2794f))


## v0.1.354 (2022-05-19)

### Chore

* chore: update controls ([`bd67ce2`](https://github.com/fhempy/fhempy/commit/bd67ce2a99d45a469b370441325328fa9ed90dfc))

### Fix

* fix(fhempy): deactivate events ([`40bd9a4`](https://github.com/fhempy/fhempy/commit/40bd9a44c42ea9081f9db00c8b0e785dd4fcb21d))

### Unknown

* Merge branch &#39;development&#39; ([`4812d5e`](https://github.com/fhempy/fhempy/commit/4812d5e796d124de0d5ea3dfed34b98056aaf63c))


## v0.1.353 (2022-05-19)

### Chore

* chore: update controls ([`296a0fe`](https://github.com/fhempy/fhempy/commit/296a0fe5c2d790aa520ffe648d2d3e992b9c136c))

### Fix

* fix(fhempy): revert event handling ([`f020c34`](https://github.com/fhempy/fhempy/commit/f020c34d1c790ce831bf50db86f1ddd950735d82))

### Unknown

* Merge branch &#39;development&#39; ([`1a52786`](https://github.com/fhempy/fhempy/commit/1a527861ca8d00bfa7fcf377277c7a90c1752cb5))


## v0.1.352 (2022-05-19)

### Chore

* chore: update controls ([`44d36a6`](https://github.com/fhempy/fhempy/commit/44d36a67efa8fb8ef7d8eb84bdf9dfe3f933a1c8))

### Fix

* fix(fhempy): fix event handling (?) ([`ba5e9c4`](https://github.com/fhempy/fhempy/commit/ba5e9c42f3a28ded54d31ec6d2fb2e8a8291ecfe))

### Unknown

* Merge branch &#39;development&#39; ([`ecc7b3a`](https://github.com/fhempy/fhempy/commit/ecc7b3a4ed81fbfaa26d1e4d1ea6273f232728c3))


## v0.1.351 (2022-05-18)

### Chore

* chore: update controls ([`dc66fdd`](https://github.com/fhempy/fhempy/commit/dc66fdde6ce9740c69b0b5974af0389c09b55056))

### Feature

* feat(fusionsolar): support battery values ([`f0a67cd`](https://github.com/fhempy/fhempy/commit/f0a67cd9362c324cf73cf413f2fa4a9a3b15fe5f))

### Unknown

* Merge branch &#39;development&#39; ([`5794d0d`](https://github.com/fhempy/fhempy/commit/5794d0df8a338b1f37b1fe2daa0ade7f57e0617c))


## v0.1.350 (2022-05-18)

### Chore

* chore: update controls ([`d0b02a8`](https://github.com/fhempy/fhempy/commit/d0b02a8ccaa65e2c17c3bebb5ebd6013059d6577))

### Fix

* fix(fusionsolar): fix if battery in use ([`ad7c12f`](https://github.com/fhempy/fhempy/commit/ad7c12f6970b92a49bab10999498ef11daed3847))

### Unknown

* Merge branch &#39;development&#39; ([`a90e895`](https://github.com/fhempy/fhempy/commit/a90e895b438205995e622ec164a442f1c34ebe25))


## v0.1.349 (2022-05-18)

### Chore

* chore: update controls ([`f38eef8`](https://github.com/fhempy/fhempy/commit/f38eef8822119638f391c654668f85c3f5ca1614))

### Fix

* fix(fusionsolar): fix region usage in define ([`d388160`](https://github.com/fhempy/fhempy/commit/d38816072464b140ef774f0d003820935c640b8a))

### Unknown

* Merge branch &#39;development&#39; ([`71c1ebc`](https://github.com/fhempy/fhempy/commit/71c1ebcc44927068f6d3798212318de230a47305))


## v0.1.348 (2022-05-16)

### Chore

* chore: update controls ([`1dceb73`](https://github.com/fhempy/fhempy/commit/1dceb736129efa97c46569953cc58dbd59b18271))

### Fix

* fix(fhempy): deactivate events as long as encoding issues are not fixed ([`55353e9`](https://github.com/fhempy/fhempy/commit/55353e922902a655d4efda95b9897e467bf56689))

* fix(fhempy): rename PyBinding class to fhempy ([`259507d`](https://github.com/fhempy/fhempy/commit/259507d668c101778f58a03bd22ba95632e05652))

### Unknown

* Merge branch &#39;development&#39; ([`92a2a7c`](https://github.com/fhempy/fhempy/commit/92a2a7cc31731bc3209ceb202c1accd1f295026d))


## v0.1.347 (2022-05-16)

### Chore

* chore: update controls ([`f5d5d42`](https://github.com/fhempy/fhempy/commit/f5d5d4219ad7f9545b36666e624ac37615e99905))

### Fix

* fix(fhempy): fix for non string events ([`fdccd1f`](https://github.com/fhempy/fhempy/commit/fdccd1f41a17ae0e41904bcff7dc7a7ec7466923))

### Unknown

* Merge branch &#39;development&#39; ([`4ba6983`](https://github.com/fhempy/fhempy/commit/4ba6983e6af851b3b4d22766c21817289b9c235e))


## v0.1.346 (2022-05-15)

### Chore

* chore: update controls ([`9180558`](https://github.com/fhempy/fhempy/commit/9180558b21491a7277baa294842eccb2e78d5f17))

### Fix

* fix(miio): set offline when no reply on status call ([`57c4908`](https://github.com/fhempy/fhempy/commit/57c49089e49119770b1ef673fcbbe30f2a98fef1))

### Unknown

* Merge branch &#39;development&#39; ([`ec7e5ab`](https://github.com/fhempy/fhempy/commit/ec7e5abeab0da518aade43841547e8ee6df32681))


## v0.1.345 (2022-05-15)

### Chore

* chore: update controls ([`61ee2c4`](https://github.com/fhempy/fhempy/commit/61ee2c408863615cb7536754828fd9527455f9a6))

### Feature

* feat(fhempy): support FHEM events (register_event_listener) ([`1c4e38b`](https://github.com/fhempy/fhempy/commit/1c4e38bc830b5a6bd9b3c2e05bd55ae7d041ff93))

### Fix

* fix(fhempy): add SIGINT handling ([`c2ab429`](https://github.com/fhempy/fhempy/commit/c2ab42979241cce82cd250a72046023855330427))

### Unknown

* Merge branch &#39;development&#39; ([`e4eb8a3`](https://github.com/fhempy/fhempy/commit/e4eb8a399dafab46c47b3c44f304ccdf64a7e9d7))


## v0.1.344 (2022-05-13)

### Chore

* chore: update controls ([`e112258`](https://github.com/fhempy/fhempy/commit/e112258216984638051ff02d4c511ff5557f0f8e))

### Fix

* fix(esphome): fix long running set functions ([`48fbf28`](https://github.com/fhempy/fhempy/commit/48fbf28f7b0b7bc38137d4ad13ea6604064d9587))

* fix(gfprobt): fix loop on asyncio cancel ([`7fc9075`](https://github.com/fhempy/fhempy/commit/7fc9075e9cea31cd4609ad7b77446579e8c1b0dd))

### Unknown

* Merge branch &#39;development&#39; ([`48d9059`](https://github.com/fhempy/fhempy/commit/48d90593b25dc765a1a0805ff005d25d70704ead))


## v0.1.343 (2022-05-13)

### Chore

* chore: update controls ([`3e942bc`](https://github.com/fhempy/fhempy/commit/3e942bc3d983356e0ef9348881b0db90736a43d0))

### Fix

* fix(zigbee2mqtt): fix function arguments ([`790b00a`](https://github.com/fhempy/fhempy/commit/790b00a646581eab4c1739814c2e6ee78fadca6b))

### Unknown

* Merge branch &#39;development&#39; ([`eb4b52f`](https://github.com/fhempy/fhempy/commit/eb4b52faccfe029c12fdf9b22d0b2d1eee23cbcd))


## v0.1.342 (2022-05-13)

### Chore

* chore: update controls ([`b610481`](https://github.com/fhempy/fhempy/commit/b610481c3af82873100c817e00caf6733291e744))

### Fix

* fix(fhempy): use os._exit again ([`9c64c08`](https://github.com/fhempy/fhempy/commit/9c64c081f52edfe957cbcabec115021313a98c22))

* fix(zigbee2mqtt): some restart fixes, z2m takes about 15s to shutdown correctly ([`20d6761`](https://github.com/fhempy/fhempy/commit/20d676147c21a241f1beb9e28a853978d607b28b))

### Unknown

* Merge branch &#39;development&#39; ([`99e5ef9`](https://github.com/fhempy/fhempy/commit/99e5ef95da0c876f662cc2e431ae886b0b6aa604))


## v0.1.341 (2022-05-13)

### Chore

* chore: update controls ([`647c4e5`](https://github.com/fhempy/fhempy/commit/647c4e58afe7fd2a1d7cd22bfd3d94f3b7169799))

### Fix

* fix(zigbee2mqtt): fix possible zombie process ([`bc8102b`](https://github.com/fhempy/fhempy/commit/bc8102b2768685494080a1329c83c54baca0b1ce))

* fix(esphome): fix possible zombie process ([`8140d62`](https://github.com/fhempy/fhempy/commit/8140d62cbb122e53f69770e9deffa64a1ec4cbd4))

### Unknown

* Merge branch &#39;development&#39; ([`46fb6ca`](https://github.com/fhempy/fhempy/commit/46fb6ca97c9116a01fc6b1dc5bdd835203ce42a6))


## v0.1.340 (2022-05-13)

### Chore

* chore: update controls ([`497cb2c`](https://github.com/fhempy/fhempy/commit/497cb2cbc0a0d7905bf58db653345966fb5ae0f1))

### Fix

* fix(zigbee2mqtt): wait longer for z2m to stop ([`7bab4d9`](https://github.com/fhempy/fhempy/commit/7bab4d97c208e18d637bb22b90c19e7ef1e2ea0f))

* fix(fhempy): use os._exit if undefine fails to ensure exit ([`c634917`](https://github.com/fhempy/fhempy/commit/c63491715c28d1ba0020e20bf961fc34b507e226))

### Unknown

* Merge branch &#39;development&#39; ([`da7699b`](https://github.com/fhempy/fhempy/commit/da7699b52b92fdfb8e95807b36a2f2222dfd5135))


## v0.1.339 (2022-05-13)

### Chore

* chore: update controls ([`b6c9776`](https://github.com/fhempy/fhempy/commit/b6c97762c47d1249e042d8083e3ad446676cd8f6))

### Fix

* fix(gfprobt): disconnect on Undefine ([`8ab7a81`](https://github.com/fhempy/fhempy/commit/8ab7a81f3ff80ed55a0d699171e92666b4abeac9))

### Unknown

* Merge branch &#39;development&#39; ([`c2eb031`](https://github.com/fhempy/fhempy/commit/c2eb0318539f7c4e68ead0ec65c9ce8cc7b76901))


## v0.1.338 (2022-05-13)

### Chore

* chore: update controls ([`014f312`](https://github.com/fhempy/fhempy/commit/014f312c4c119403a91edaaef78558403565f95f))

### Fix

* fix(fhempy): fix Undefine calls when stopped ([`2f62033`](https://github.com/fhempy/fhempy/commit/2f620330e70c28d77137db840fd0570b0c56adf5))

* fix(eq3bt): fix Undefine when not yet connected ([`ebdbe92`](https://github.com/fhempy/fhempy/commit/ebdbe92dcbbb1f3d5e57a6c311e8ef6a25b31900))

### Unknown

* Merge branch &#39;development&#39; ([`fa5126e`](https://github.com/fhempy/fhempy/commit/fa5126ed8d49718d80d3095cf975601c89517902))


## v0.1.337 (2022-05-13)

### Chore

* chore: update controls ([`29600bb`](https://github.com/fhempy/fhempy/commit/29600bbff1a1748468689679364a5cbb178162f9))

### Fix

* fix(eq3bt): disconnect on Undefine ([`bbd52d0`](https://github.com/fhempy/fhempy/commit/bbd52d0a3b91f0e0fe2088231e9a361fd152db86))

### Unknown

* Merge branch &#39;development&#39; ([`53ed6ec`](https://github.com/fhempy/fhempy/commit/53ed6ec2cd97969f34adb85e8ae88e61572c2444))


## v0.1.336 (2022-05-13)

### Chore

* chore: update controls ([`52a73b9`](https://github.com/fhempy/fhempy/commit/52a73b9ca53208eb203a230c51c0b3e218cdaa16))

### Fix

* fix(zigbee2mqtt): better stop process handling ([`46ac614`](https://github.com/fhempy/fhempy/commit/46ac6143c1c85cde01365eaa62ee1d34d5088ef3))

* fix(esphome): better stop process handling ([`8efa358`](https://github.com/fhempy/fhempy/commit/8efa3588f8565d1070054f439c4cfc17f0f14dfd))

* fix(zigbee2mqtt): code style improvement ([`39f6bca`](https://github.com/fhempy/fhempy/commit/39f6bcace4074195741973593e369c05737befbd))

### Unknown

* Merge branch &#39;development&#39; ([`7b707e8`](https://github.com/fhempy/fhempy/commit/7b707e8e2ba22a7c61ce6dfd6e7c329a5506e728))


## v0.1.335 (2022-05-10)

### Chore

* chore: update controls ([`5367e21`](https://github.com/fhempy/fhempy/commit/5367e21a980ab055506bf6654542d8b205d17c19))

### Feature

* feat(fhempy): support peer restart from FHEM ([`ce7803a`](https://github.com/fhempy/fhempy/commit/ce7803a9672f460e6599cec899b0d1787f69dfea))

### Fix

* fix(spotify): update spotipy to 2.19.0 ([`77d8ee2`](https://github.com/fhempy/fhempy/commit/77d8ee2589e14b32132a7458bad745c78118a829))

### Unknown

* Merge branch &#39;development&#39; ([`14b6504`](https://github.com/fhempy/fhempy/commit/14b6504e36a2b8e91b2be588ac2de3b6990c249f))


## v0.1.334 (2022-05-10)

### Chore

* chore: update controls ([`d1c2a49`](https://github.com/fhempy/fhempy/commit/d1c2a494555d53e5f434e71f03ca4f578b98c45a))

### Fix

* fix(fhempy): fix stash for release script ([`ef9fada`](https://github.com/fhempy/fhempy/commit/ef9fadad91908550ac7bac17d381266b67fa887e))

* fix(fhempy): add update info log ([`920d4c9`](https://github.com/fhempy/fhempy/commit/920d4c9fddd911a0fa0dc872d7bcd5b9ea61bb07))

* fix(fhempy): update websockets to 10.3 ([`b0313d0`](https://github.com/fhempy/fhempy/commit/b0313d03148f35e45858e8ffd7ee0a0c772dc4bc))

* fix(fhempy): close websockets on restart ([`729a65e`](https://github.com/fhempy/fhempy/commit/729a65e83f8d322ecaf05b2dbef1818fdfc96935))

* fix(zigbee2mqtt): stop task on restart ([`6fea8af`](https://github.com/fhempy/fhempy/commit/6fea8af00f58e2f83117ca1c8051ad06d155c4ad))

### Unknown

* Merge branch &#39;development&#39; ([`af4bd14`](https://github.com/fhempy/fhempy/commit/af4bd14a6cf277bd0efefb7e62513e04d5b45c06))


## v0.1.333 (2022-05-10)

### Chore

* chore: update controls ([`9353317`](https://github.com/fhempy/fhempy/commit/9353317fd7a7b3eb26ba398ce77d779fc0d4e751))

### Fix

* fix(zigbee2mqtt): fix stop zigbee2mqtt process ([`ab44052`](https://github.com/fhempy/fhempy/commit/ab44052bf25e64fa8d84685c152d43aeb877080a))

### Unknown

* Merge branch &#39;development&#39; ([`d13ea80`](https://github.com/fhempy/fhempy/commit/d13ea80ca9a932ca55cd82651f94ce64760bc0cd))


## v0.1.332 (2022-05-10)

### Chore

* chore: update controls ([`1933aa8`](https://github.com/fhempy/fhempy/commit/1933aa84c840ecb6b0d43031e199f9fc74e82a2e))

* chore: update controls ([`342aee0`](https://github.com/fhempy/fhempy/commit/342aee0ccb1cf53f1cccc6445ca7e1bc839b00c7))

### Fix

* fix(fhempy): log exit code ([`7dee7c8`](https://github.com/fhempy/fhempy/commit/7dee7c8914a420aab8c4c6185d395859c572a6d8))

* fix(fhempy): asyncio improvements ([`7d2e005`](https://github.com/fhempy/fhempy/commit/7d2e00579b1b3d85ce7004381c0055b1f2ef02b4))

* fix(tuya): fix usage without api key/secret ([`4e716d7`](https://github.com/fhempy/fhempy/commit/4e716d7163b216a1a1555612626fd6c5ee456a1f))

* fix(fhempy): code style improvements ([`1c6744c`](https://github.com/fhempy/fhempy/commit/1c6744c3220852f45cf0246492c774640fc9aa33))

* fix(discover_upnp): code style improvements ([`b0eb47b`](https://github.com/fhempy/fhempy/commit/b0eb47bc0a301581cbc03652366a0654d446df04))

* fix(fhempy): import cleanup ([`427f826`](https://github.com/fhempy/fhempy/commit/427f8267ae8dcd4a12e376c82e59d33cb5e8b154))

* fix(zigbee2mqtt): code style improvements ([`560d061`](https://github.com/fhempy/fhempy/commit/560d06133996aa34bd1cc50b1531845e90cf11b5))

### Unknown

* Merge branch &#39;development&#39; ([`7b7043b`](https://github.com/fhempy/fhempy/commit/7b7043bb8b8d4d9aba90277ae3aaf88c9a0caeef))

* Merge branch &#39;development&#39; ([`72f3271`](https://github.com/fhempy/fhempy/commit/72f32710970b14f1807925b266db3d212a230c68))


## v0.1.331 (2022-05-09)

### Chore

* chore: update controls ([`ba91a3a`](https://github.com/fhempy/fhempy/commit/ba91a3a0b70a08d022ab6453d54a17afbf63671b))

### Fix

* fix(zigbee2mqtt): kill instead of terminate ([`dbeeb36`](https://github.com/fhempy/fhempy/commit/dbeeb36a77981fe360f70149c97f7b619c0b0ba5))

* fix(esphome): kill instead of terminate ([`0040297`](https://github.com/fhempy/fhempy/commit/0040297d934398a3027059c090cac0a31cc908e9))

* fix(discover_upnp): delete unused variable ([`e30f2c6`](https://github.com/fhempy/fhempy/commit/e30f2c692496cc4980f9bd0995654a14f72a2c11))

### Unknown

* Merge branch &#39;development&#39; ([`71931d2`](https://github.com/fhempy/fhempy/commit/71931d2b358ed00bed23a9abb1e624dfe14f4161))


## v0.1.330 (2022-05-09)

### Chore

* chore: update controls ([`fc3a649`](https://github.com/fhempy/fhempy/commit/fc3a6498575f44bd55c30bda6cb52a192e0426e3))

### Fix

* fix(fhempy): better restart/shutdown handling ([`4e97c58`](https://github.com/fhempy/fhempy/commit/4e97c58b02573cdee0ee9dd11fee30667abb7ad8))

* fix(tuya): import only Cloud, deviceScan ([`3f92df2`](https://github.com/fhempy/fhempy/commit/3f92df2412409541f55a70e49d26b1fe0dbc5337))

* fix(tuya): remove unused attributes ([`1beab02`](https://github.com/fhempy/fhempy/commit/1beab02553dcee4c265cc49131e1afe93fe0c0b0))

* fix(miio): fix send_command, sort imports ([`737eeef`](https://github.com/fhempy/fhempy/commit/737eeefbbf37f9a263ea4527248834ef351cef3c))

* fix(tuya): sort imports ([`1a3acfd`](https://github.com/fhempy/fhempy/commit/1a3acfd020c853e08ad3f8a93915a7682c5b9844))

### Unknown

* Merge branch &#39;development&#39; ([`72fe983`](https://github.com/fhempy/fhempy/commit/72fe983bcc3c7df45cfd38d8359363a7b8359f64))


## v0.1.329 (2022-05-08)

### Chore

* chore: update controls ([`302ff77`](https://github.com/fhempy/fhempy/commit/302ff777d83f07c98c161e426961cd0aeb7a85d8))

### Fix

* fix(miio): fix tuple usage ([`d97751a`](https://github.com/fhempy/fhempy/commit/d97751ad8c7c0ca31fc2bce6f7991a14f4f3c6a3))

* fix(tuya): fix tests ([`dd9ce3c`](https://github.com/fhempy/fhempy/commit/dd9ce3cda1f98ed73c743051f2ea1abe72d62721))

### Unknown

* Merge branch &#39;development&#39; ([`0e50cb4`](https://github.com/fhempy/fhempy/commit/0e50cb4585d0876c1b83baa372863ba6ce587692))


## v0.1.328 (2022-05-08)

### Chore

* chore: update controls ([`c3287a0`](https://github.com/fhempy/fhempy/commit/c3287a0eb4c88759e1e748555fe6754467990333))

### Feature

* feat(fhempy): log version on startup ([`63ecc62`](https://github.com/fhempy/fhempy/commit/63ecc627966b3aaa8647f6eb06e2b6bf1dd51fda))

### Fix

* fix(fhempy): fix shutdown again ([`6e0e1f1`](https://github.com/fhempy/fhempy/commit/6e0e1f1a4cf13a30803087f2f337dfc3e46728a1))

### Unknown

* Merge branch &#39;development&#39; ([`4619ac8`](https://github.com/fhempy/fhempy/commit/4619ac82dc0d4d357b493bf5a1320f5c82c8325e))


## v0.1.327 (2022-05-08)

### Chore

* chore: update controls ([`f672002`](https://github.com/fhempy/fhempy/commit/f6720022a62e45f7f14fb9c92ba2b4d8a149aafe))

### Fix

* fix(fhempy): fix shutdown handler ([`d246ca8`](https://github.com/fhempy/fhempy/commit/d246ca8cdb7aa44c1a7e7c2b0f17e217b24836dc))

### Unknown

* Merge branch &#39;development&#39; ([`5e45955`](https://github.com/fhempy/fhempy/commit/5e4595570ca07fc9aa07766d6b157b67dc1af0af))


## v0.1.326 (2022-05-08)

### Chore

* chore: update controls ([`372e844`](https://github.com/fhempy/fhempy/commit/372e844e13736379a12f82dd1fd0f8259bf46978))

### Fix

* fix(fhempy): handle SIGTERM for graceful shutdown ([`35dff0a`](https://github.com/fhempy/fhempy/commit/35dff0aac289f97fceb15ceff3f7b51469b2e778))

* fix(zigbee2mqtt): call stop_process on Undefine ([`e3626e5`](https://github.com/fhempy/fhempy/commit/e3626e518b171b0610dd0d95f5356a9ac72e7a89))

* fix(esphome): call stop_process on Undefine ([`8402760`](https://github.com/fhempy/fhempy/commit/84027609c91ff675634165f8c0a25511b32541b1))

* fix(esphome): set proc None when terminated ([`81f10b0`](https://github.com/fhempy/fhempy/commit/81f10b0f8c68a0b3ad424201574aa9d2b50c0920))

* fix(zigbee2mqtt): fix blocking calls ([`a980bf3`](https://github.com/fhempy/fhempy/commit/a980bf3000341e43ffd83dec9c8b1b4784f971dc))

### Unknown

* Merge branch &#39;development&#39; ([`55c7db3`](https://github.com/fhempy/fhempy/commit/55c7db326f11121035a2b484c15b02282e11fa73))


## v0.1.325 (2022-05-08)

### Chore

* chore: update controls ([`8f73869`](https://github.com/fhempy/fhempy/commit/8f73869796888d17a65dfb08a11d34a511d70aff))

### Fix

* fix(tuya): always use cloud specs when APIKEY and APISECRET is provided ([`d9d3812`](https://github.com/fhempy/fhempy/commit/d9d381292fe731fccf4b04a11dcc06dfe0514d7c))

### Unknown

* Merge branch &#39;development&#39; ([`a233289`](https://github.com/fhempy/fhempy/commit/a2332897679fc62b938cf88bc0f0b41f715094f0))


## v0.1.324 (2022-05-08)

### Chore

* chore: update controls ([`704e41f`](https://github.com/fhempy/fhempy/commit/704e41f8bf6c62f561380c4cc12449408776993c))

### Fix

* fix(fusionsolar): update takes a bit longer, extend to full 5min + 30s ([`79cb26a`](https://github.com/fhempy/fhempy/commit/79cb26a08008f6b30c00598244e0117a39f2b4b6))

### Unknown

* Merge branch &#39;development&#39; ([`2d2df6d`](https://github.com/fhempy/fhempy/commit/2d2df6d50544fa1b1c0da4e3dbc54141ba1ed3d9))


## v0.1.323 (2022-05-08)

### Chore

* chore: update controls ([`5b6f315`](https://github.com/fhempy/fhempy/commit/5b6f31520e80e71c165ceb4fba8a80bb6a3ba7ec))

### Fix

* fix(tuya): fix local found counter ([`a8b708c`](https://github.com/fhempy/fhempy/commit/a8b708cfa13d6266966ce27b70cdc98216594dc1))

### Unknown

* Merge branch &#39;development&#39; ([`0441d6c`](https://github.com/fhempy/fhempy/commit/0441d6c10bb299d08ca804d6625013b51ca3eb27))


## v0.1.322 (2022-05-08)

### Chore

* chore: update controls ([`f610b05`](https://github.com/fhempy/fhempy/commit/f610b05ac2cfcda63f03b3354d1012cdffa4ad07))

### Fix

* fix(wienerlinien): code style improvements ([`c5207f4`](https://github.com/fhempy/fhempy/commit/c5207f47970d689a7b4ed5c0ee9fa8356072f6fe))

* fix(tuya_cloud): code style improvements ([`46c90ca`](https://github.com/fhempy/fhempy/commit/46c90ca41b62a2bd24d46dff20a333bb3ced5f00))

* fix(esphome): code style improvements ([`f8a091b`](https://github.com/fhempy/fhempy/commit/f8a091be9dd6505c4416217309e1307246b81abc))

* fix(fusionnsolar): code style improvements ([`dd01e29`](https://github.com/fhempy/fhempy/commit/dd01e29c433ab4593536060a9d8f829cb452c6d2))

* fix(tuya): code style improvements ([`b014060`](https://github.com/fhempy/fhempy/commit/b01406066a0b460ee0d63a011755f96423263a06))

* fix(fusionsolar): fix update interval ([`a33dc00`](https://github.com/fhempy/fhempy/commit/a33dc005daf44920d921c4283a824feb859b6eff))

### Unknown

* Merge branch &#39;development&#39; ([`fbfd429`](https://github.com/fhempy/fhempy/commit/fbfd429f8730d5f12e5abef24111b344a7b65706))


## v0.1.321 (2022-05-08)

### Chore

* chore: update controls ([`0d8404e`](https://github.com/fhempy/fhempy/commit/0d8404e1edaf41e84736b0f500fd8e1a0eb914fd))

### Feature

* feat(tuya): support wifi devices which are not online all the time (e.g. water leak sensor, smoke detector, ...) ([`035429c`](https://github.com/fhempy/fhempy/commit/035429ceab4508ba94c4e9e2253f2ba736e62bea))

* feat(fusionsolar): update on fusionsolar update (every full 5min) ([`b338277`](https://github.com/fhempy/fhempy/commit/b338277d1e42e93b681dd8e1344d72d13d97c032))

### Fix

* fix(fusionsolar): fix div/0 ([`57bbc51`](https://github.com/fhempy/fhempy/commit/57bbc51ad9e51637d70bbba57902aa73ddd3937f))

* fix(fusionsolar): delete unused file ([`45f7bb8`](https://github.com/fhempy/fhempy/commit/45f7bb8ad4d4ca2882d7c9b4cce0c13dd9a04ad9))

### Unknown

* Merge branch &#39;development&#39; ([`cf904ff`](https://github.com/fhempy/fhempy/commit/cf904ff7671c00238776b2fc7e450decac13b3d3))


## v0.1.320 (2022-05-07)

### Chore

* chore: update controls ([`41fa99b`](https://github.com/fhempy/fhempy/commit/41fa99b32c1f92ed0ecc26e0bb48da88ee4e3ee1))

### Fix

* fix(miio): fix tuple type ([`4282a99`](https://github.com/fhempy/fhempy/commit/4282a995425efc1940d4a27ca11cd1fd08dac692))

### Unknown

* Merge branch &#39;development&#39; ([`e9a3487`](https://github.com/fhempy/fhempy/commit/e9a3487a2634861db99ec1b1ebc6d468956bdeff))


## v0.1.319 (2022-05-07)

### Chore

* chore: update controls ([`74b2fe1`](https://github.com/fhempy/fhempy/commit/74b2fe17169b9d4eef51eed30fe2341a354b8e4c))

### Fix

* fix(fhempy): wait max 10s for restart ([`896d80b`](https://github.com/fhempy/fhempy/commit/896d80bd065e4f3670e0b66df706bc64ccd2fb32))

### Unknown

* Merge branch &#39;development&#39; ([`52be331`](https://github.com/fhempy/fhempy/commit/52be331a51f9eb0e8c0cf1096bbcc74d22a42959))


## v0.1.318 (2022-05-07)

### Chore

* chore: update controls ([`f338b0d`](https://github.com/fhempy/fhempy/commit/f338b0d24a20ca75db181d92c60416b5a68259b2))

### Feature

* feat(fusionsolar): add daily_self_use_solar_ratio reading ([`4abd020`](https://github.com/fhempy/fhempy/commit/4abd02016a99e319afcb04ab0c99fe3668a255ff))

### Unknown

* Merge branch &#39;development&#39; ([`ea96b67`](https://github.com/fhempy/fhempy/commit/ea96b670e0c77404dab5a673df516df3f64de57a))


## v0.1.317 (2022-05-07)

### Chore

* chore: update controls ([`29d4111`](https://github.com/fhempy/fhempy/commit/29d41115f85fdde1f92d5f3b7db8e77ba96f602d))

### Fix

* fix(fusionsolar): fix daily_self_use_ratio ([`84ea1e0`](https://github.com/fhempy/fhempy/commit/84ea1e0ab36a2a66a5e6caabe86c9aff92ed71d4))

### Unknown

* Merge branch &#39;development&#39; ([`82422e3`](https://github.com/fhempy/fhempy/commit/82422e3aa557cdb187427f790bd5a8f8ec0e6b7b))


## v0.1.316 (2022-05-07)

### Chore

* chore: update controls ([`3316a52`](https://github.com/fhempy/fhempy/commit/3316a52ca5b4a9bd3130a13d62592018928ec76f))

### Fix

* fix(fusionsolar): small fixes ([`cdbd06c`](https://github.com/fhempy/fhempy/commit/cdbd06ced4a2bcfedd43dd70fce916a4cab30ea9))

### Unknown

* Merge branch &#39;development&#39; ([`950832c`](https://github.com/fhempy/fhempy/commit/950832c9753b40d167a3743ee9eac083683535ab))


## v0.1.315 (2022-05-07)

### Chore

* chore: update controls ([`b2468af`](https://github.com/fhempy/fhempy/commit/b2468af3fdfac6941c0164b12578d676a2501cf4))

### Feature

* feat(fusionsolar): add further readings ([`f3432af`](https://github.com/fhempy/fhempy/commit/f3432af9b8bbfa9708747680b91adac1eaf6a0b7))

### Unknown

* Merge branch &#39;development&#39; ([`93ab795`](https://github.com/fhempy/fhempy/commit/93ab795185bdd1514b024a1558d9c4d769c0fbb4))


## v0.1.314 (2022-05-07)

### Chore

* chore: update controls ([`d01e584`](https://github.com/fhempy/fhempy/commit/d01e5842f464d148f066ab1d62f6ebb443967023))

### Fix

* fix(fusionsolar): fix define ([`f421b51`](https://github.com/fhempy/fhempy/commit/f421b51e741e7e042e4dd38906c515ad7fd56191))

### Unknown

* Merge branch &#39;development&#39; ([`9b81de9`](https://github.com/fhempy/fhempy/commit/9b81de96f4a8e8a6743a4636a86e6d13cd285d30))


## v0.1.313 (2022-05-07)

### Chore

* chore: update controls ([`4175ffa`](https://github.com/fhempy/fhempy/commit/4175ffa2d057522f970d5ac4d74909b8592eeefb))

### Feature

* feat(fusionsolar): BREAKING: no more kiosk mode, all values are taken from REST API. See README for details ([`221e88c`](https://github.com/fhempy/fhempy/commit/221e88c67bc6697c4a1f45144a321467b4ca7912))

### Unknown

* Merge branch &#39;development&#39; ([`54faeb5`](https://github.com/fhempy/fhempy/commit/54faeb5a6a238eb8530daa95276c9fe5ce414de7))


## v0.1.312 (2022-05-07)

### Chore

* chore: update controls ([`4288994`](https://github.com/fhempy/fhempy/commit/4288994918810fecd0dda043a461fe55b333cba6))

### Fix

* fix(fusionsolar): fix wrong default region ([`bea81bf`](https://github.com/fhempy/fhempy/commit/bea81bf0ea2f84871b34ee1af9aadad8321fc9a6))

### Unknown

* Merge branch &#39;development&#39; ([`8f3087f`](https://github.com/fhempy/fhempy/commit/8f3087f7a316a27cca83fc19a4bd2f35d6dc5d9a))


## v0.1.311 (2022-05-07)

### Chore

* chore: update controls ([`f0054d8`](https://github.com/fhempy/fhempy/commit/f0054d8f5f77bed9370fc34efe0519234a81de25))

### Fix

* fix(fusionsolar): fix from/to_grid_power ([`fe7bea1`](https://github.com/fhempy/fhempy/commit/fe7bea111b286e6c3cf8287cbe09f51c9c8ae456))

### Unknown

* Merge branch &#39;development&#39; ([`f43a209`](https://github.com/fhempy/fhempy/commit/f43a2098b43a9c6b1a656cc68a136d13580618e2))


## v0.1.310 (2022-05-07)

### Chore

* chore: update controls ([`ae754cc`](https://github.com/fhempy/fhempy/commit/ae754cc0378766fae37cad9fe14a570e8c4ac5ab))

### Feature

* feat(fusionsolar): support from/to_grid, electrical_load, grid_power and inverter_output_power ([`3c73b83`](https://github.com/fhempy/fhempy/commit/3c73b8312ae71d9fa74e23d7d9299e40ece61951))

### Unknown

* Merge branch &#39;development&#39; ([`8831d09`](https://github.com/fhempy/fhempy/commit/8831d09e54e939f2283b0c119b0a98f0ce2c4b3e))


## v0.1.309 (2022-05-06)

### Chore

* chore: update controls ([`0b68a64`](https://github.com/fhempy/fhempy/commit/0b68a64c14563fa1940623547f070f199fb9ad43))

### Fix

* fix(fhempy): fix task exception handling ([`81225c1`](https://github.com/fhempy/fhempy/commit/81225c12840754ea691b7d9624c1fd3446babd89))

### Unknown

* Merge branch &#39;development&#39; ([`74e3c9a`](https://github.com/fhempy/fhempy/commit/74e3c9aa9e73aa7fa42367b0eefdcecad12db599))


## v0.1.308 (2022-05-06)

### Chore

* chore: update controls ([`7ac1605`](https://github.com/fhempy/fhempy/commit/7ac160520d5e15db404180aabdb8a1984ca213f0))

### Fix

* fix(fhempy): handle exceptions in asyncio tasks ([`6708650`](https://github.com/fhempy/fhempy/commit/670865014807e9aceb636b03f81106fca466ba88))

* fix(tuya): remove unused function ([`3b8b785`](https://github.com/fhempy/fhempy/commit/3b8b785d459a815bc9890227a572f554857b8a3a))

### Unknown

* Merge branch &#39;development&#39; ([`3a072ee`](https://github.com/fhempy/fhempy/commit/3a072eec35405e64bebf7ffae95e24113b85ce28))


## v0.1.307 (2022-05-05)

### Chore

* chore: update controls ([`562b56d`](https://github.com/fhempy/fhempy/commit/562b56db31bf3fb6d3c4c9c2ae6527f96ad16e00))

### Fix

* fix(tuya): get info before connection setup ([`fd5edcc`](https://github.com/fhempy/fhempy/commit/fd5edcc20ff04ee7cf7c3f6523168cb7372b0453))

### Unknown

* Merge branch &#39;development&#39; ([`e38f185`](https://github.com/fhempy/fhempy/commit/e38f1855a756b169574e29494dc347cc7801a03a))


## v0.1.306 (2022-05-03)

### Chore

* chore: update controls ([`a4674e8`](https://github.com/fhempy/fhempy/commit/a4674e82c0cb1fa8b94bc2017395889e2268b8d5))

### Fix

* fix(tuya): handle exception ([`0b3c77b`](https://github.com/fhempy/fhempy/commit/0b3c77b29caf58aa18257e763664237cac9a36f8))

### Unknown

* Merge branch &#39;development&#39; ([`8cd709b`](https://github.com/fhempy/fhempy/commit/8cd709b23adffb8ca6f109181af6c2c2d243b8a2))


## v0.1.305 (2022-05-02)

### Chore

* chore: update controls ([`292edac`](https://github.com/fhempy/fhempy/commit/292edac97d9cf0846377f1ea1623b26bbd8fb261))

### Feature

* feat(tuya): try to support water leak sensor ([`b3229d6`](https://github.com/fhempy/fhempy/commit/b3229d6790cfcb73be963490d2f641c374bc02d0))

### Unknown

* Merge branch &#39;development&#39; ([`93b1ea1`](https://github.com/fhempy/fhempy/commit/93b1ea143dc957530662d7c6c09a36070ad04c93))


## v0.1.304 (2022-05-01)

### Chore

* chore: update controls ([`5a56457`](https://github.com/fhempy/fhempy/commit/5a56457b4f312ed87c9c036c7d021dd1462ad726))

### Fix

* fix(nespresso_ble): remove unused requirement ([`889e582`](https://github.com/fhempy/fhempy/commit/889e582813c225f481db4fbfc5110f263e57cbc3))

### Unknown

* Merge branch &#39;development&#39; ([`8d1f394`](https://github.com/fhempy/fhempy/commit/8d1f394f7f3ed54730d6aa2b2c2849cc1c3f1e30))


## v0.1.303 (2022-05-01)

### Chore

* chore: update controls ([`7a3007d`](https://github.com/fhempy/fhempy/commit/7a3007d44a8be7f6e8668efbbaf71e63f41b1603))

### Fix

* fix(fhempy): remove Python 3.7 test ([`d1c2b7b`](https://github.com/fhempy/fhempy/commit/d1c2b7b2438c4429d05b4c329d8c8c3440f48ad8))

### Unknown

* Merge branch &#39;development&#39; ([`a677c55`](https://github.com/fhempy/fhempy/commit/a677c55ad96ba3d4ef589398a05e420a56855b89))


## v0.1.302 (2022-05-01)

### Chore

* chore: update controls ([`0ce270c`](https://github.com/fhempy/fhempy/commit/0ce270ceefcc15ef775e4707f8f5d9104caf4924))

### Fix

* fix(rct_power): fix commands ([`4efb800`](https://github.com/fhempy/fhempy/commit/4efb8002ab923878c761aabf65e95263c7a44d77))

### Unknown

* Merge branch &#39;development&#39; ([`de6d4ba`](https://github.com/fhempy/fhempy/commit/de6d4bac8419f715899880f93795df624a9052c8))


## v0.1.301 (2022-05-01)

### Chore

* chore: update controls ([`15ec021`](https://github.com/fhempy/fhempy/commit/15ec021b1eb440f3b95072b5bee0c26a35c458e6))

### Fix

* fix(rct_power): fix commands ([`5753a35`](https://github.com/fhempy/fhempy/commit/5753a35bc2f67bcb58af0ae6cf8fd0dde570bc97))

### Unknown

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhempy ([`edb9691`](https://github.com/fhempy/fhempy/commit/edb9691a148cda728070629463122e4cf72c3d92))


## v0.1.300 (2022-05-01)

### Chore

* chore: update controls ([`9503134`](https://github.com/fhempy/fhempy/commit/950313473468826e1713464e78898730f04b36cf))

### Fix

* fix(rct_power): fix commands (#76) ([`bf88baa`](https://github.com/fhempy/fhempy/commit/bf88baaed7f13a63956baa3e68e7bf91e3e83c36))

* fix(rct_power): fix commands (#75)

Read/Write: Einen Fehler im Kommentar beseitigt, einen Slider angeglichen, Formatierungsänderung in den Kommentaren ([`4dbe2f7`](https://github.com/fhempy/fhempy/commit/4dbe2f765040f42e5056c0984b5b8175fb028c8c))

### Unknown

* Merge branch &#39;development&#39; ([`6dd9fa4`](https://github.com/fhempy/fhempy/commit/6dd9fa4f41a0e9e7168e8a2fa83c4a409bb257a8))


## v0.1.299 (2022-05-01)

### Chore

* chore: update controls ([`e9c1d92`](https://github.com/fhempy/fhempy/commit/e9c1d92c581aabaa0e412693523a46e824c797c9))

### Fix

* fix(tuya): optimize define runtime ([`2109d7a`](https://github.com/fhempy/fhempy/commit/2109d7a7273c1ba857b32ee50d5cf9b70b18a3fc))

* fix(gree_climate): fix missing off cmd ([`fdcb422`](https://github.com/fhempy/fhempy/commit/fdcb422e3c8e473596217ef5bd0656de7ec1521f))

### Unknown

* Merge branch &#39;development&#39; ([`d38d26f`](https://github.com/fhempy/fhempy/commit/d38d26fb41178b464098b0714c2e5f3b709dc149))


## v0.1.298 (2022-05-01)

### Chore

* chore: update controls ([`d95c829`](https://github.com/fhempy/fhempy/commit/d95c8292cc1321e92498979529ba7e3a417d3159))

* chore: update tuya readme ([`e88275a`](https://github.com/fhempy/fhempy/commit/e88275abdb5485f8ece48c5ca7fce6a8b93c9f24))

### Fix

* fix(tuya): update tuya cloud instructions ([`84dd50c`](https://github.com/fhempy/fhempy/commit/84dd50cce90cb990ac727459a5e263c74d26bd8b))

* fix(tuya_cloud): update README link ([`507ffb0`](https://github.com/fhempy/fhempy/commit/507ffb038daa1e033f2b80293a39dab40a5c8ddc))

### Unknown

* Merge branch &#39;development&#39; ([`1dcee83`](https://github.com/fhempy/fhempy/commit/1dcee831667d3da6130deb07f417e9d0a52dd5f4))


## v0.1.297 (2022-04-29)

### Chore

* chore: update controls ([`e6f2cff`](https://github.com/fhempy/fhempy/commit/e6f2cff51fa012435166c656f5c802f92e129ba0))

### Fix

* fix(gree_climate): fix usage ([`0023119`](https://github.com/fhempy/fhempy/commit/00231192441a53284e3789a9b540242c8753ee08))

### Unknown

* Merge branch &#39;development&#39; ([`0681770`](https://github.com/fhempy/fhempy/commit/06817702d0c06a5801cb4b2806e336a317d76646))


## v0.1.296 (2022-04-29)

### Chore

* chore: update controls ([`cdc18c6`](https://github.com/fhempy/fhempy/commit/cdc18c6366e18e6fce3aaed69c23fdb5a522fe84))

### Fix

* fix(gree_climate): fix set temperature ([`fcc825f`](https://github.com/fhempy/fhempy/commit/fcc825fe177f0bb35163d65473cb76ae32a7525d))

* fix(gree_climate): fix commands ([`1f2779a`](https://github.com/fhempy/fhempy/commit/1f2779a9e71954ddddfc53a75272398dcb5e91fd))

* fix(gree_climate): remove set cmds for scan device ([`45c2d2f`](https://github.com/fhempy/fhempy/commit/45c2d2fe1afa5953cb6d6eeb36c55e7cedb06240))

### Unknown

* Merge branch &#39;development&#39; ([`9644111`](https://github.com/fhempy/fhempy/commit/9644111da843e8d8778a8b9779d731b648e2c588))


## v0.1.295 (2022-04-29)

### Chore

* chore: update controls ([`3d79674`](https://github.com/fhempy/fhempy/commit/3d796746c01b7759242a3a06ba57a3a34b8c02c6))

### Fix

* fix(rct_power): remove slider (#74) ([`e45006d`](https://github.com/fhempy/fhempy/commit/e45006d7d04fce3768a90830a83492e316ab758e))

* fix(gree_climate): fix function call on error ([`0bcedbe`](https://github.com/fhempy/fhempy/commit/0bcedbe75c8b0ab4f062edd2c2448b689826a4c9))

### Unknown

* Merge branch &#39;development&#39; ([`be6df59`](https://github.com/fhempy/fhempy/commit/be6df595c22865860572843bb1cbd0c4ae4da13e))


## v0.1.294 (2022-04-29)

### Chore

* chore: update controls ([`6bee800`](https://github.com/fhempy/fhempy/commit/6bee8005a70e56feea11da3db104ce189734cf6a))

### Feature

* feat(gree_climate): add to readme ([`7ed6b1e`](https://github.com/fhempy/fhempy/commit/7ed6b1eae89690f2576115c396eb4e8fb8ac70da))

* feat(gree_climate): first release ([`c526e10`](https://github.com/fhempy/fhempy/commit/c526e10a6e38d07793ffc0d3584730c763528a1c))

* feat(rct_power): update help (#73) ([`b67e0a6`](https://github.com/fhempy/fhempy/commit/b67e0a606a8abaacf19ac1c529ee23def8746fbd))

### Unknown

* Merge branch &#39;development&#39; ([`6dc4a2d`](https://github.com/fhempy/fhempy/commit/6dc4a2de09c3e907920d8452fa4611d5f254ebae))

* Merge branch &#39;development&#39; of https://github.com/dominikkarall/fhempy into development ([`f302736`](https://github.com/fhempy/fhempy/commit/f30273659dce102a72472e640a4d167fc7e2c28c))


## v0.1.293 (2022-04-26)

### Chore

* chore: update controls ([`c1d7b7a`](https://github.com/fhempy/fhempy/commit/c1d7b7a37fa8cb771a0edbc799f2809c3bfe3bc9))

### Fix

* fix(tuya): fix create device ([`6b4c524`](https://github.com/fhempy/fhempy/commit/6b4c5247dd052ba42f766268b92253c9d1d49561))

### Unknown

* Merge branch &#39;development&#39; ([`9b00c8d`](https://github.com/fhempy/fhempy/commit/9b00c8d06d6438db1b936e2d1a7208da6e801493))


## v0.1.292 (2022-04-26)

### Chore

* chore: update controls ([`7b6c1ee`](https://github.com/fhempy/fhempy/commit/7b6c1ee1aecdeee2c29cb1ad1b520094bc9849e9))

### Fix

* fix(tuya): fix tests ([`fd7c390`](https://github.com/fhempy/fhempy/commit/fd7c390aece3c7477203c1e78d516a4680a7dbf4))

### Unknown

* Merge branch &#39;development&#39; ([`3b05d9d`](https://github.com/fhempy/fhempy/commit/3b05d9d758ad2a46752f62d4d4bf9751df6a0536))


## v0.1.291 (2022-04-26)

### Chore

* chore: update controls ([`f37f26c`](https://github.com/fhempy/fhempy/commit/f37f26cc885a686e7f3f187968443d7f0ea16cfa))

### Feature

* feat(tuya): add info readings ([`f1817ad`](https://github.com/fhempy/fhempy/commit/f1817ada60d07a83f1274b38f240694298d929b4))

### Unknown

* Merge branch &#39;development&#39; ([`70f1945`](https://github.com/fhempy/fhempy/commit/70f19456207c0d62b3e6dc4ad2e62cec4fb7bf34))


## v0.1.290 (2022-04-26)

### Chore

* chore: update controls ([`12e9f7c`](https://github.com/fhempy/fhempy/commit/12e9f7ce5985678c019490ab2fc5e0d585e37e65))

### Fix

* fix(tuya): fix local scan ([`6a850d4`](https://github.com/fhempy/fhempy/commit/6a850d4ced3cb3bf573943e9269383ce930ce728))

### Unknown

* Merge branch &#39;development&#39; ([`91b59b4`](https://github.com/fhempy/fhempy/commit/91b59b479e2038f40e05d6a7c352fa5c6d0c6191))


## v0.1.289 (2022-04-26)

### Chore

* chore: update controls ([`8cddfd7`](https://github.com/fhempy/fhempy/commit/8cddfd76ca714a8a047459e69728d623526a63d4))

### Fix

* fix(gfprobt): deactivate not working adjust values ([`73c5aae`](https://github.com/fhempy/fhempy/commit/73c5aae511e5e28a4c250e0d45c074e6597ee92c))

### Unknown

* Merge branch &#39;development&#39; ([`33de75d`](https://github.com/fhempy/fhempy/commit/33de75db52cd83c09e5a18cf41601c267279a6dd))


## v0.1.288 (2022-04-26)

### Chore

* chore: update controls ([`68ccd1a`](https://github.com/fhempy/fhempy/commit/68ccd1a2d87c0d6b9893a183382913ca89fa5e15))

### Fix

* fix(tuya): fix local scan ([`eed15a2`](https://github.com/fhempy/fhempy/commit/eed15a2198e9c856a95dd052323438e031b401bc))

### Unknown

* Merge branch &#39;development&#39; ([`e0da9dc`](https://github.com/fhempy/fhempy/commit/e0da9dc6c14799cd9dd37bee1174807ad10cb7b3))


## v0.1.287 (2022-04-26)

### Chore

* chore: update controls ([`3855ac0`](https://github.com/fhempy/fhempy/commit/3855ac0e5115be016d83e65da8a55a640f53b6e4))

### Fix

* fix(tuya): fix for existing mappings ([`1d5d301`](https://github.com/fhempy/fhempy/commit/1d5d301dd69d0cef8b7b84655d01dc325c161375))

### Unknown

* Merge branch &#39;development&#39; ([`5b14396`](https://github.com/fhempy/fhempy/commit/5b1439603fb91472d24a4bcc9e9c0af3ca948b1f))


## v0.1.286 (2022-04-26)

### Chore

* chore: update controls ([`09a7b48`](https://github.com/fhempy/fhempy/commit/09a7b485f0de373fbd762568582dc15e8e17c4c2))

### Feature

* feat(tuya): support tuya local real-time updates ([`9104867`](https://github.com/fhempy/fhempy/commit/9104867f51edb1a22ec3d8d34ff0dda4fbabfaf6))

### Unknown

* Merge branch &#39;development&#39; ([`72a2830`](https://github.com/fhempy/fhempy/commit/72a2830b1089a7ff6283d99325d98cd609eb2ca4))


## v0.1.285 (2022-04-25)

### Chore

* chore: update controls ([`36c3255`](https://github.com/fhempy/fhempy/commit/36c3255974b116e756924acffe0932cb2e31af4d))

* chore: update controls ([`20cf55d`](https://github.com/fhempy/fhempy/commit/20cf55daa5d9b650b05666622eec9e72b17c22f3))

### Feature

* feat(rct_power): further readings and commands (#72) ([`85981f4`](https://github.com/fhempy/fhempy/commit/85981f430b18c7d2821861ce1af014a231c9002d))

### Fix

* fix(ring): change update order ([`75016f6`](https://github.com/fhempy/fhempy/commit/75016f6e263420eb9fb24e58bf529d638d2a05a7))

* fix(miio): support Tuple data type ([`3b8dce5`](https://github.com/fhempy/fhempy/commit/3b8dce51f65a6c0b9f47ea9397ec7ee81162ef65))

* fix(ring): show errors in state ([`32d2a4b`](https://github.com/fhempy/fhempy/commit/32d2a4b39de821895407157352e6cfb2a79c8ddf))

### Unknown

* Merge branch &#39;development&#39; ([`ae003d7`](https://github.com/fhempy/fhempy/commit/ae003d7d1d9e4a6d218e88150a6941cb7a97ca8d))

* Merge branch &#39;development&#39; of https://github.com/dominikkarall/fhempy into development ([`f68b7e4`](https://github.com/fhempy/fhempy/commit/f68b7e4907a2ddf3b9c463f305a9b6a507e7db74))


## v0.1.284 (2022-04-20)

### Chore

* chore: update controls ([`c8f9d02`](https://github.com/fhempy/fhempy/commit/c8f9d02e541eed4d8c8ef07c95e02eaa27a3cbfa))

### Feature

* feat(esphome): update to 2022.4.0 ([`59683c2`](https://github.com/fhempy/fhempy/commit/59683c2f7c0bc125334320ae0dfa8ae198cbafa7))

### Unknown

* Merge branch &#39;development&#39; ([`e71ecdc`](https://github.com/fhempy/fhempy/commit/e71ecdce2491fc9877f0ceff0d6e7508fac00114))


## v0.1.283 (2022-04-20)

### Chore

* chore: update controls ([`7c9de04`](https://github.com/fhempy/fhempy/commit/7c9de04531b20dee3a6ee7b43aa0b9fbe38dfdba))


## v0.1.282 (2022-04-20)

### Chore

* chore: update controls ([`7f735b9`](https://github.com/fhempy/fhempy/commit/7f735b9ab5bd4a7d50a5a61a419f4ed6d5806ef7))


## v0.1.281 (2022-04-20)

### Chore

* chore: update controls ([`6245498`](https://github.com/fhempy/fhempy/commit/62454986110a25488ce4ab8fd5efe6db08a38c98))

### Fix

* fix(eq3bt): fix possible infinite loop ([`7c21c2a`](https://github.com/fhempy/fhempy/commit/7c21c2a49bb645a7071259799b22c4c85f96dae5))

* fix(discover_mdns): fix exception handling ([`f2bb640`](https://github.com/fhempy/fhempy/commit/f2bb6409005b3d7bac9ae6d2db05dbd3f9264ef3))

* fix(fhempy): fix exception handling ([`db7c74b`](https://github.com/fhempy/fhempy/commit/db7c74b9d9810d4ee3a9b9cdb0e2be4fb2318f59))

* fix(gfprobt): fix invalid type ([`93f2873`](https://github.com/fhempy/fhempy/commit/93f28736e577d69e489ce680904c0a596b7fe61f))

### Unknown

* Merge branch &#39;development&#39; ([`8a2a6c7`](https://github.com/fhempy/fhempy/commit/8a2a6c7cdfa713fdb127ee0b9f1fcd27357eca60))


## v0.1.280 (2022-04-20)

### Chore

* chore: update controls ([`6e14a4e`](https://github.com/fhempy/fhempy/commit/6e14a4e0925afeea9a3a9055ce5f72d29322ca50))

### Feature

* feat(rct_power): Update commands (#71)

-Update of address of battery soc limits. Old values were from a wrong module in the inverter
-Update of address of battery current limits. Old values were not writable ([`ee8ea0d`](https://github.com/fhempy/fhempy/commit/ee8ea0d5b8aa3622a9aec43f24090aef1fa48d27))

* feat(esphome): update to 2022.3.1 ([`3abba2f`](https://github.com/fhempy/fhempy/commit/3abba2f6b02c52a252b5705b6d0226a121c2e4cd))

* feat(gfprobt): prepare adjust ([`115fc60`](https://github.com/fhempy/fhempy/commit/115fc6060a78d3949dd2d5a022429b2dac0f1219))

### Fix

* fix(fhempy): code cleanup ([`9e123cf`](https://github.com/fhempy/fhempy/commit/9e123cfea795629f8e2c52a6e2e88a93bcb62c2b))

* fix(fhempy): code style fixes ([`23db77b`](https://github.com/fhempy/fhempy/commit/23db77bee65481d844c3fc6fcc66f8e43f1050c6))

* fix(helloworld): remove unused import ([`ebe9245`](https://github.com/fhempy/fhempy/commit/ebe92454e0658c8f420fa6f65c767a22486dc4cf))

* fix(gfprobt): prepare adjust ([`51cc4bb`](https://github.com/fhempy/fhempy/commit/51cc4bb5fd369d124a2a3c84ffe639b4a0bf5c8c))

* fix(nefit): fix Undefine ([`e9b0168`](https://github.com/fhempy/fhempy/commit/e9b016828cc5fb00254d538cc5a11fd2d9925c6d))

### Unknown

* Merge branch &#39;development&#39; ([`e9610ea`](https://github.com/fhempy/fhempy/commit/e9610eae20bd12f435757218606418c2576400e0))


## v0.1.279 (2022-04-11)

### Chore

* chore: update controls ([`80115e1`](https://github.com/fhempy/fhempy/commit/80115e1cdbd4e93378406c7fe2935f4be9cb86ec))

### Fix

* fix(fhempy): cryptography 3.4.8 ([`0bf5665`](https://github.com/fhempy/fhempy/commit/0bf56652a74ad231c4c3b9cbb9b281f68971c44d))

### Unknown

* Merge branch &#39;development&#39; ([`4124b11`](https://github.com/fhempy/fhempy/commit/4124b1198b5708f2ff27b8bf925697f8d0d66c1c))


## v0.1.278 (2022-04-10)

### Chore

* chore: update controls ([`23630d7`](https://github.com/fhempy/fhempy/commit/23630d75afe860fcebc513bc8bd657826c77eb6d))


## v0.1.277 (2022-04-10)

### Chore

* chore: update controls ([`45c7715`](https://github.com/fhempy/fhempy/commit/45c7715ec541b96993491d0b1c520dd7a0f4242d))

* chore: update test actions ([`4642379`](https://github.com/fhempy/fhempy/commit/4642379aae33613cd068117c581a69bc1d99bd4f))

### Unknown

* Merge branch &#39;development&#39; ([`752f739`](https://github.com/fhempy/fhempy/commit/752f7394c54c61d1c357c602f7e92b6e7e882243))


## v0.1.276 (2022-04-10)

### Chore

* chore: update controls ([`8a9c0b0`](https://github.com/fhempy/fhempy/commit/8a9c0b08d457dd38e39da65c70e4d09ed24bbfd7))

### Fix

* fix(ring): fix Undefine ([`56ceda2`](https://github.com/fhempy/fhempy/commit/56ceda2b38528f89bf63c649d7279e425ffa4b63))

* fix(ring): fix test ([`b637c09`](https://github.com/fhempy/fhempy/commit/b637c092e03f5b233f0b64c34d242c7d1729aa11))

* fix(fhempy): fix ssdp stop_search ([`5d998d6`](https://github.com/fhempy/fhempy/commit/5d998d65c39c7e262551255d88b67361e0ffb56e))

### Unknown

* Merge branch &#39;development&#39; ([`c9f4f56`](https://github.com/fhempy/fhempy/commit/c9f4f566a8ffcf1fb9229d443abbd95b0a0fb03b))


## v0.1.275 (2022-04-10)

### Chore

* chore: update controls ([`0058ee8`](https://github.com/fhempy/fhempy/commit/0058ee8064b516b4c38bf8bff2ffe02691799d32))

### Feature

* feat(erelax_vaillant): use vaillant-netatmo-api ([`f138b6b`](https://github.com/fhempy/fhempy/commit/f138b6b1a9e852a70ba545a1afb5a11224c8842c))

### Unknown

* Merge branch &#39;development&#39; ([`a1a2a5d`](https://github.com/fhempy/fhempy/commit/a1a2a5db4e28f9957ca3b227f6e255a48c9fac2d))


## v0.1.274 (2022-04-10)

### Chore

* chore: update controls ([`b4b58d7`](https://github.com/fhempy/fhempy/commit/b4b58d75d085992e889f0427ab4fb623eef505dd))

### Fix

* fix(fhempy): update cryptography ([`52afbf7`](https://github.com/fhempy/fhempy/commit/52afbf71510ad985d156d19941336319032c0fab))

### Unknown

* Merge branch &#39;development&#39; ([`d034506`](https://github.com/fhempy/fhempy/commit/d034506f2589258e21811ed01c773ca5bda42e7e))


## v0.1.273 (2022-04-10)

### Chore

* chore: update controls ([`a2ae209`](https://github.com/fhempy/fhempy/commit/a2ae2093eb099d059d5ce575f64d9906f33f05ac))

### Fix

* fix(ring): fix Undefine endless loop ([`e1ce34f`](https://github.com/fhempy/fhempy/commit/e1ce34fb1d20757ac4d4a4e4fe566ae0a20388fa))

### Unknown

* Merge branch &#39;development&#39; ([`313040c`](https://github.com/fhempy/fhempy/commit/313040c7d7c9cb4c66e9fc0df08a682d2b9e4190))


## v0.1.272 (2022-04-10)

### Chore

* chore: update controls ([`0f7c5fe`](https://github.com/fhempy/fhempy/commit/0f7c5fee1c0ccf25236e03fc11d7685df19b4f6f))

### Feature

* feat(xiaomi_gateway3): support ble smoke detector ([`3dee86f`](https://github.com/fhempy/fhempy/commit/3dee86f38fd2550fc0f30b88cccfbe8c79cfc832))

* feat(fhempy): support git+https requirements ([`7987489`](https://github.com/fhempy/fhempy/commit/7987489abbaf31cfc9b8bd2305609e4e460f39c7))

### Unknown

* Merge branch &#39;development&#39; ([`158eb75`](https://github.com/fhempy/fhempy/commit/158eb75f2d4ac605f59002cad9b88eb14e2df92d))


## v0.1.271 (2022-04-10)

### Chore

* chore: update controls ([`c66a753`](https://github.com/fhempy/fhempy/commit/c66a75336f61eef939ca8ee1dcb1740dae31fd59))

### Fix

* fix(esphome): fix esphome start ([`e4c1697`](https://github.com/fhempy/fhempy/commit/e4c1697cc62aa4734c2ca5879a35207889e641e7))

### Unknown

* Merge branch &#39;development&#39; ([`6c7924a`](https://github.com/fhempy/fhempy/commit/6c7924af020a16823ad65bf3289cdee5096a480c))


## v0.1.270 (2022-03-09)

### Chore

* chore: update controls ([`5bcea05`](https://github.com/fhempy/fhempy/commit/5bcea052d3b34dfb64fb51d265682d762b98bad5))

### Fix

* fix(fhempy): downgrade requests to fix errors ([`82a5eb5`](https://github.com/fhempy/fhempy/commit/82a5eb566601a1e18118914cf8c65fb5ab596027))

### Unknown

* Merge branch &#39;development&#39; ([`d17f578`](https://github.com/fhempy/fhempy/commit/d17f5785e86382e98ad340cf67fb59e10a520042))


## v0.1.269 (2022-03-09)

### Chore

* chore: update controls ([`e856946`](https://github.com/fhempy/fhempy/commit/e856946361f1e05eab094a718ce24f3e29b91dcb))

### Fix

* fix(tuya_cloud): try to fix circular import ([`7187a88`](https://github.com/fhempy/fhempy/commit/7187a88bf401c531419cda3bbe2251f66ff783fa))

### Unknown

* Merge branch &#39;development&#39; ([`836eb3a`](https://github.com/fhempy/fhempy/commit/836eb3a67aff5758c091e2473f7c77b6147c4309))


## v0.1.268 (2022-03-07)

### Chore

* chore: update controls ([`1604526`](https://github.com/fhempy/fhempy/commit/16045267987db64506ae2fff7de62aa02e1850d2))

### Fix

* fix(tuya_cloud): try to fix circular import ([`d5cf08f`](https://github.com/fhempy/fhempy/commit/d5cf08faeabee835432fec80c6eb2a4406caf8d3))

### Unknown

* Merge branch &#39;development&#39; ([`16fbd84`](https://github.com/fhempy/fhempy/commit/16fbd84e10fa3bdf1566319f904612905d5d858d))


## v0.1.267 (2022-03-06)

### Chore

* chore: update controls ([`3813297`](https://github.com/fhempy/fhempy/commit/3813297d3f33d1c0a3b3a7f8edb1ab6cfd433fd0))

### Fix

* fix(tuya_cloud): fix circular import ([`48b0d5d`](https://github.com/fhempy/fhempy/commit/48b0d5dfe7a48219af74d0379e1ce4d553b57523))

### Unknown

* Merge branch &#39;development&#39; ([`122c316`](https://github.com/fhempy/fhempy/commit/122c316061441b458a24b63a69ca756b9873e0f6))


## v0.1.266 (2022-03-06)

### Chore

* chore: update controls ([`42dfeba`](https://github.com/fhempy/fhempy/commit/42dfeba959af473babb24d607223c6cf31ea93cd))

### Feature

* feat(fhempy): add more info about peer ([`54c320d`](https://github.com/fhempy/fhempy/commit/54c320d050cb2ce200b39a405ac413350d28603c))

### Unknown

* Merge branch &#39;development&#39; ([`2d4bc12`](https://github.com/fhempy/fhempy/commit/2d4bc12aef4d7c3a76c6bcebb1175be888e92abd))


## v0.1.265 (2022-03-06)

### Chore

* chore: update controls ([`7ef5be9`](https://github.com/fhempy/fhempy/commit/7ef5be9755fd624b1835672e2ad3d0980a139f9b))

### Fix

* fix(fhempy): fix restart ([`04ac131`](https://github.com/fhempy/fhempy/commit/04ac13107deda0eb044daba1dbf98ad2960b8dba))

### Unknown

* Merge branch &#39;development&#39; ([`257539e`](https://github.com/fhempy/fhempy/commit/257539e4e7f8a42f7455a6d800bc84e7ec446d04))


## v0.1.264 (2022-03-05)

### Chore

* chore: update controls ([`fe0f1be`](https://github.com/fhempy/fhempy/commit/fe0f1befe1c6b42a741b007289a1cce4fbf88fda))

### Fix

* fix(fhempy): fix IODev missing when disconnected ([`9244dd3`](https://github.com/fhempy/fhempy/commit/9244dd366b137cb5270fe24eadf44b49b21b20a3))

* fix(fhempy): use fhempy instead of PythonModule ([`8d8abb4`](https://github.com/fhempy/fhempy/commit/8d8abb485286945156d60b77f6ee6f128ee0e46d))

### Unknown

* Merge branch &#39;development&#39; ([`c931a66`](https://github.com/fhempy/fhempy/commit/c931a664cd11f452ac44e6c28a356fd1f68da49c))


## v0.1.263 (2022-03-05)

### Chore

* chore: update controls ([`bb1815f`](https://github.com/fhempy/fhempy/commit/bb1815f400ee08580f7176d4050f0b4d33b82521))

### Fix

* fix(fhempy): keep disconnected state for bindings ([`4f6621c`](https://github.com/fhempy/fhempy/commit/4f6621c2b38eeb5572bddb4cbf96549f4cbd8c8b))

### Unknown

* Merge branch &#39;development&#39; ([`ec770b3`](https://github.com/fhempy/fhempy/commit/ec770b3ae7e4a387e75f80c8964c854eb0a7241a))


## v0.1.262 (2022-03-05)

### Chore

* chore: update controls ([`bf19bdb`](https://github.com/fhempy/fhempy/commit/bf19bdbce049e252ab6d55d7792fc5eb5521d276))

### Fix

* fix(fhempy): python reading font correction ([`3284f3c`](https://github.com/fhempy/fhempy/commit/3284f3c332bef010dd00dad409fe69c00e09a80e))

### Unknown

* Merge branch &#39;development&#39; ([`854cf91`](https://github.com/fhempy/fhempy/commit/854cf912f99c6fe450fcdd51b4bcda2f3062de65))


## v0.1.261 (2022-03-05)

### Chore

* chore: update controls ([`cd80ef1`](https://github.com/fhempy/fhempy/commit/cd80ef19d24ca5b5601350e686175455b5315fa8))

### Fix

* fix(fhempy): fix startup ([`2145a4d`](https://github.com/fhempy/fhempy/commit/2145a4d5fc6fbc4731025625d1b081f389735842))

### Unknown

* Merge branch &#39;development&#39; ([`9c2200a`](https://github.com/fhempy/fhempy/commit/9c2200ad6162b24d321a39daefbfba747b37d75a))


## v0.1.260 (2022-03-04)

### Chore

* chore: update controls ([`dd3b8f0`](https://github.com/fhempy/fhempy/commit/dd3b8f0e76c0c5e105b43300a7e2a0c4f9c4d5cd))

### Fix

* fix(fhempy): fix sartup ([`5d23162`](https://github.com/fhempy/fhempy/commit/5d2316218912c8e51cbd970a0f3de3c13d85e255))

### Unknown

* Merge branch &#39;development&#39; ([`f706b63`](https://github.com/fhempy/fhempy/commit/f706b637dea7db8dbfe580d4f72923981cb94f32))


## v0.1.259 (2022-03-04)

### Chore

* chore: update controls ([`550e949`](https://github.com/fhempy/fhempy/commit/550e949173ac187b434df40929ed85c2cb25d1c7))

### Fix

* fix(fhempy): fix reading ([`5bbba76`](https://github.com/fhempy/fhempy/commit/5bbba76743abe5ec6089fc603ed134001b4d8841))

### Unknown

* Merge branch &#39;development&#39; ([`ea5ad03`](https://github.com/fhempy/fhempy/commit/ea5ad0397785f0656029332c4f0297ae7633608c))


## v0.1.258 (2022-03-04)

### Chore

* chore: update controls ([`07861d4`](https://github.com/fhempy/fhempy/commit/07861d4bb8241da30769a8e511ce6412adcaea48))

### Fix

* fix(fhempy): add python version check to perl code ([`2452f37`](https://github.com/fhempy/fhempy/commit/2452f37fa7a0312fb480d8b078dd06b22d6b1b02))

### Unknown

* Merge branch &#39;development&#39; ([`3e0b2ef`](https://github.com/fhempy/fhempy/commit/3e0b2ef001c927ae8a89ce938276b9ffd528041c))


## v0.1.257 (2022-03-04)

### Chore

* chore: update controls ([`48bd50d`](https://github.com/fhempy/fhempy/commit/48bd50d9cc63bcb770e1e4444c41c73f11d237aa))

### Fix

* fix(fhempy): fix installation errors ([`b3dfa34`](https://github.com/fhempy/fhempy/commit/b3dfa3446dceb2cce4d7be5a9c3c06d564f1b19e))

### Unknown

* Merge branch &#39;development&#39; ([`71539be`](https://github.com/fhempy/fhempy/commit/71539bef4970ec6058f2058f898b7622a674d03a))


## v0.1.256 (2022-03-03)

### Chore

* chore: update controls ([`bd512d9`](https://github.com/fhempy/fhempy/commit/bd512d97238e38ea1be01a425c6aab70ff98fcd8))

### Feature

* feat(rct_power): support ext_power_reduction ([`3d72be9`](https://github.com/fhempy/fhempy/commit/3d72be98c9d6348413f32086aeea2c184b8516dc))

### Unknown

* Merge branch &#39;development&#39; ([`8818f8a`](https://github.com/fhempy/fhempy/commit/8818f8af1f5c1a4ed89495633bfd5d79e897fcee))


## v0.1.255 (2022-03-03)

### Chore

* chore: update controls ([`484dcde`](https://github.com/fhempy/fhempy/commit/484dcde9d56da4d47e4786e21aec72f7d0b81982))

### Fix

* fix(fhempy): fix python version error handling ([`f9c1d89`](https://github.com/fhempy/fhempy/commit/f9c1d899ac312d3e70a5c4d3dffa21124f91d407))

### Unknown

* Merge branch &#39;development&#39; ([`72d7ca6`](https://github.com/fhempy/fhempy/commit/72d7ca6caff442188479a0af09ff1350f451afb1))


## v0.1.254 (2022-03-02)

### Chore

* chore: update controls ([`bf86f4f`](https://github.com/fhempy/fhempy/commit/bf86f4f21ee88c54f0a9c6cfb59cd988cc2589d7))

### Fix

* fix(tuya_cloud): fix logging ([`f384975`](https://github.com/fhempy/fhempy/commit/f38497553e662633c139b7825fe3c047b0bf932f))

### Unknown

* Merge branch &#39;development&#39; ([`c53de9e`](https://github.com/fhempy/fhempy/commit/c53de9ee2e7a83fb27728ca5ef4c2123805c6290))


## v0.1.253 (2022-03-02)

### Chore

* chore: update controls ([`d14642f`](https://github.com/fhempy/fhempy/commit/d14642f87bc78118d42f299bdc627ce321d91acc))

### Feature

* feat(fhempy): support datetime for   readings ([`3a9cf74`](https://github.com/fhempy/fhempy/commit/3a9cf740b946d80bf9673a04d98c3ed21301bf03))

### Unknown

* Merge branch &#39;development&#39; ([`7f7848e`](https://github.com/fhempy/fhempy/commit/7f7848e386416ebe31c74407dd02b2c671b9c7ba))

* fix(tuya_cloud):support verbose 5 ([`4e18818`](https://github.com/fhempy/fhempy/commit/4e18818d38105842362db29aaa0b242af51717e2))


## v0.1.252 (2022-02-23)

### Chore

* chore: update controls ([`2edc20b`](https://github.com/fhempy/fhempy/commit/2edc20bdb57117c82258bfe595e1d864fc3d495e))

### Fix

* fix(miio): fix error when no helptext available ([`e22c55c`](https://github.com/fhempy/fhempy/commit/e22c55cf8654791895f6b220b349f1044a9c008b))

### Unknown

* Merge branch &#39;development&#39; ([`ecde017`](https://github.com/fhempy/fhempy/commit/ecde017bf1ef4db81c594e2fcc9f56cd23cc5824))


## v0.1.251 (2022-02-22)

### Chore

* chore: update controls ([`7163851`](https://github.com/fhempy/fhempy/commit/7163851d879a6803830589019facf7d6a2ca837a))

### Fix

* fix(ble_monitor): fix possible unregister error ([`264f1fb`](https://github.com/fhempy/fhempy/commit/264f1fb50f55fa0296d9aeca1fe45c385d952a11))

### Unknown

* Merge branch &#39;development&#39; ([`c5c081b`](https://github.com/fhempy/fhempy/commit/c5c081b8a9ee9abc5df436031f3766cde7f66309))


## v0.1.250 (2022-02-21)

### Chore

* chore: update controls ([`4aea9eb`](https://github.com/fhempy/fhempy/commit/4aea9eb1f85e0a8029e34b74188ebc07411b5a13))

### Feature

* feat(meross): support mod100 ([`6c0b7e2`](https://github.com/fhempy/fhempy/commit/6c0b7e2a94e29299d54104592d11acdad6c8fbcd))

### Unknown

* Merge branch &#39;development&#39; ([`aaa566d`](https://github.com/fhempy/fhempy/commit/aaa566d1772d020a874dd70c00bcf7ef94f4ffa6))


## v0.1.249 (2022-02-21)

### Chore

* chore: update controls ([`499ca45`](https://github.com/fhempy/fhempy/commit/499ca459df244e3e607bf8129beb85d21c6c06fe))

### Fix

* fix(zigbee2mqtt): fix restart ([`54545c2`](https://github.com/fhempy/fhempy/commit/54545c2b1935c7cc7f14ec9961188101fe540846))

### Unknown

* Merge branch &#39;development&#39; ([`b6c1ba7`](https://github.com/fhempy/fhempy/commit/b6c1ba7db69412b69dd5f923f9b863e54752dda9))


## v0.1.248 (2022-02-20)

### Chore

* chore: update controls ([`0c969af`](https://github.com/fhempy/fhempy/commit/0c969af3fbacaabbdaa97b3091c8a410878f30aa))

### Fix

* fix(fhempy): replace \n in help text ([`7a02515`](https://github.com/fhempy/fhempy/commit/7a02515a1f73b8a6e4aaca23baa05d08090b59a5))

* fix(miio): fixes for new library ([`edeab1f`](https://github.com/fhempy/fhempy/commit/edeab1f7ecc437fc017e474fb4304cf0f889d488))

### Unknown

* Merge branch &#39;development&#39; ([`6925048`](https://github.com/fhempy/fhempy/commit/69250486d5c4759e38788fdab89bae2b73c81c99))


## v0.1.247 (2022-02-20)

### Chore

* chore: update controls ([`0258fe0`](https://github.com/fhempy/fhempy/commit/0258fe0ceee0a8a555409dfe854393e1d53f793f))

### Fix

* fix(miscale): fix missing method ([`dbb4c3a`](https://github.com/fhempy/fhempy/commit/dbb4c3a29b6faccf9466ed261e0a913bdef0f574))

### Unknown

* Merge branch &#39;development&#39; ([`b4d3478`](https://github.com/fhempy/fhempy/commit/b4d3478d95d5cf2fba384e9cd2dc0f4c855cf3be))


## v0.1.246 (2022-02-19)

### Chore

* chore: update controls ([`1161c59`](https://github.com/fhempy/fhempy/commit/1161c5970ab790b15348ec9d2d2adc83c04280a3))

### Feature

* feat(rct_power): add min_soc_maint_charge ([`7695d8e`](https://github.com/fhempy/fhempy/commit/7695d8eb1129d0fe0ca505c62f9b28b79cdbf1f0))

* feat(ble_monitor): support encryption key attr ([`cdd1521`](https://github.com/fhempy/fhempy/commit/cdd1521c5fe0d6d23792c7b7283d2ecff0c1fdd9))

### Unknown

* Merge branch &#39;development&#39; ([`b6ad977`](https://github.com/fhempy/fhempy/commit/b6ad977100b120b2215f60f5e2fc2c932e86ed90))


## v0.1.245 (2022-02-18)

### Chore

* chore: update controls ([`562fd61`](https://github.com/fhempy/fhempy/commit/562fd61b29559287cfe1a8666db636d044f71bcc))

### Fix

* fix(zigbee2mqtt): fix weblink ([`ca6c105`](https://github.com/fhempy/fhempy/commit/ca6c105ed6140a7d308a69c5f98cf29abd0996ec))

### Unknown

* Merge branch &#39;development&#39; ([`1057293`](https://github.com/fhempy/fhempy/commit/1057293f4ea546e8bb7a8925bac840eb7f1a5aeb))


## v0.1.244 (2022-02-18)

### Chore

* chore: update controls ([`1d4c65c`](https://github.com/fhempy/fhempy/commit/1d4c65c4973c29e3834e689386d1ff2aa9bb9ffa))

### Feature

* feat(zigbee2mqtt): first working release ([`8f9d26a`](https://github.com/fhempy/fhempy/commit/8f9d26a503966edef49950d62c2b26e3350fc531))

### Fix

* fix(seatconnect): Fix Seatconnect Login (#67) ([`d67cce0`](https://github.com/fhempy/fhempy/commit/d67cce057f73e6e91f731fc2196abc14d0e8feef))

* fix(zigbee2mqtt): fix restart ([`d36bea4`](https://github.com/fhempy/fhempy/commit/d36bea4249350ea493757406328602f1b8e7a400))

### Unknown

* Merge branch &#39;development&#39; ([`acdc247`](https://github.com/fhempy/fhempy/commit/acdc247a20cf4198f804742634615a2f34282ba6))


## v0.1.243 (2022-02-18)

### Chore

* chore: update controls ([`8712f8b`](https://github.com/fhempy/fhempy/commit/8712f8b2e39f4218188db6781cc8d1229c3dae15))

### Feature

* feat(zigbee2mqtt): first release ([`ac1cd73`](https://github.com/fhempy/fhempy/commit/ac1cd73555f2edf0b0d34baa68e77a545377aa42))

* feat(miio): update lib ([`828bcec`](https://github.com/fhempy/fhempy/commit/828bcec59e385d242cf1cf4c0c69c7e5dabcf44a))

* feat(zigbee2mqtt): prepare zigbee2mqtt ([`9810678`](https://github.com/fhempy/fhempy/commit/98106780b9699a7be17ba713b79e188402d94c55))

### Fix

* fix(ring): fix Undefine? ([`c6d9d6a`](https://github.com/fhempy/fhempy/commit/c6d9d6af60297eba29800ccb8ce1df5e6114b5b1))

### Unknown

* Merge branch &#39;development&#39; ([`cca9ac7`](https://github.com/fhempy/fhempy/commit/cca9ac775a4948b33b740af001d0bf8e0e151489))


## v0.1.242 (2022-02-16)

### Chore

* chore: update controls ([`4f2d4e9`](https://github.com/fhempy/fhempy/commit/4f2d4e95ea066c01c5db9e0385f01b0a54a7531f))

### Fix

* fix(xiaomi_gateway3): fix disable ([`16830d1`](https://github.com/fhempy/fhempy/commit/16830d1ae68a1da82cb1a7454d9bef6beb4c3947))

### Unknown

* Merge branch &#39;development&#39; ([`9f5eec5`](https://github.com/fhempy/fhempy/commit/9f5eec5fba5fc0a4199cbadab5fdc6a3e1255599))


## v0.1.241 (2022-02-16)

### Chore

* chore: update controls ([`ef42630`](https://github.com/fhempy/fhempy/commit/ef4263012a3f9fafa04c81f1765b418b6edf0820))

### Fix

* fix(xiaomi_gateway3): fix disable ([`591612d`](https://github.com/fhempy/fhempy/commit/591612de340b4ed7e0162e441dddbc817dcb7086))

### Unknown

* Merge branch &#39;development&#39; ([`84d8796`](https://github.com/fhempy/fhempy/commit/84d8796186bcc3fedb600ae18525f430a9363561))


## v0.1.240 (2022-02-16)

### Chore

* chore: update controls ([`d992cb8`](https://github.com/fhempy/fhempy/commit/d992cb89fedfec31105d19b787114442992fb84a))

### Fix

* fix(xiaomi_gateway3): support disable ([`1b2a59c`](https://github.com/fhempy/fhempy/commit/1b2a59c7488c7c3e0047e8a3b3a2433c94e81f16))

### Unknown

* Merge branch &#39;development&#39; ([`e9b8535`](https://github.com/fhempy/fhempy/commit/e9b853533e461c9b79b30276ff9e7db5580b3aa6))


## v0.1.239 (2022-02-15)

### Chore

* chore: update controls ([`5a2309c`](https://github.com/fhempy/fhempy/commit/5a2309c25e8af0f41e0c4761d75433e0b543d70e))

### Feature

* feat(fhempy): add ble_monitor, miscale ([`819e678`](https://github.com/fhempy/fhempy/commit/819e6789a2d141287daa6f6a10b865013f27c5ce))

* feat(miscale): support miscale ([`b9dc4d6`](https://github.com/fhempy/fhempy/commit/b9dc4d698d9df2dc88e7fb888df3157ffd9d6509))

### Fix

* fix(miscale): working version ([`e30988a`](https://github.com/fhempy/fhempy/commit/e30988adc9e2e488617f93b2441bd9e3cfd38abe))

* fix(ble_monitor): working again ([`5399399`](https://github.com/fhempy/fhempy/commit/5399399b8ad45350d83a52dc74ef8343f6bbeba1))

* fix(miscale): fix usage ([`2492790`](https://github.com/fhempy/fhempy/commit/2492790f803f5455403048dd3cfa89e6a2deb1d5))

* fix(fhempy): fix readme processing ([`df9d48d`](https://github.com/fhempy/fhempy/commit/df9d48d1055562627c2492335ce28bba73abcad3))

* fix(ble_monitor): update readme ([`dc82d3d`](https://github.com/fhempy/fhempy/commit/dc82d3d9d9e88ec1286cdbb4ba1d4ad0ae6be025))

* fix(ble_monitor): remove unneeded function ([`206d62e`](https://github.com/fhempy/fhempy/commit/206d62ec888b15564750908b029ca52ac426cbc4))

* fix(ble_monitor): support more devs with same mac ([`2c18861`](https://github.com/fhempy/fhempy/commit/2c18861934fa83908bbefae0901922a98899ffe5))

* fix(ble_monitor): make it working ([`dec3186`](https://github.com/fhempy/fhempy/commit/dec31860d40b545cb3b6ad328c08e0344e858d44))

* fix(ble_monitor): code structure changes ([`aa6e14f`](https://github.com/fhempy/fhempy/commit/aa6e14f4b673d98b998df761678e3cfa995eb0da))

### Unknown

* Merge branch &#39;development&#39; ([`1585ed9`](https://github.com/fhempy/fhempy/commit/1585ed9b3b03ceca5c01117f75b55771e98e20d4))


## v0.1.238 (2022-02-14)

### Chore

* chore: update controls ([`98f3b02`](https://github.com/fhempy/fhempy/commit/98f3b02c44c394114d866c2ae3fa0d9f546cd698))

### Feature

* feat(ble_monitor): first working release ([`24eb78e`](https://github.com/fhempy/fhempy/commit/24eb78e3328bea123a1c17c75d404373ef526a9a))

* feat(rct_power): support max_power_ac ([`f4f6d8c`](https://github.com/fhempy/fhempy/commit/f4f6d8c89792ed3c4e8e2b84a0dc4d92f0a1081f))

### Fix

* fix(ble_monitor): fix codestyle ([`9c8e691`](https://github.com/fhempy/fhempy/commit/9c8e6919fbbe8e8aa0e811ca28d160e9ba4a664c))

* fix(fhempy): do not call set_attr on define ([`f32f12f`](https://github.com/fhempy/fhempy/commit/f32f12ff173b410492c4184b48085373046163e1))

* fix(fhempy): fix port parameter ([`1f55020`](https://github.com/fhempy/fhempy/commit/1f5502006678b2161fd6ee7393541bd5a3f91a88))

* fix(fhempy): fix quotes ([`934a344`](https://github.com/fhempy/fhempy/commit/934a344d5cfc10479799e73434bf6bf8440be466))

### Unknown

* Merge branch &#39;development&#39; ([`6813ee2`](https://github.com/fhempy/fhempy/commit/6813ee2fb18740192273feb39d814df60790575e))


## v0.1.237 (2022-02-13)

### Chore

* chore: update controls ([`8d21d47`](https://github.com/fhempy/fhempy/commit/8d21d474408b01e0bf119faf7dc4aef7987a6a8e))

### Feature

* feat(ble_monitor): prepare ble_monitor ([`c6098fa`](https://github.com/fhempy/fhempy/commit/c6098faf16fe140631c470a1e72d3def6eeae07d))

### Unknown

* Merge branch &#39;development&#39; ([`5215ab7`](https://github.com/fhempy/fhempy/commit/5215ab79bc59191973a9d6c16bd0da5321185c59))


## v0.1.236 (2022-02-13)

### Chore

* chore: update controls ([`ea99be2`](https://github.com/fhempy/fhempy/commit/ea99be24e8a4683162705dc77ab6265776623578))

### Fix

* fix(fusionsolar): fix usage ([`76e4858`](https://github.com/fhempy/fhempy/commit/76e485828b35179dd5bd8de11700c7e2e3e806c0))

### Unknown

* Merge branch &#39;development&#39; ([`5186e5c`](https://github.com/fhempy/fhempy/commit/5186e5c39137a25d6858686658f3bb77776d8402))


## v0.1.235 (2022-02-13)

### Chore

* chore: update controls ([`4dc5dee`](https://github.com/fhempy/fhempy/commit/4dc5deebd33245ca2f1d15e65b373bb117962146))

* chore: fix version ([`0e741bc`](https://github.com/fhempy/fhempy/commit/0e741bcaf70dd640df1021299ffdfd3ad0129738))

* chore: update controls ([`b64397a`](https://github.com/fhempy/fhempy/commit/b64397a9a2d41288ee680370d74cb2268c4d0f80))

* chore: update controls ([`e68b55f`](https://github.com/fhempy/fhempy/commit/e68b55f0a4b2b0fa0c026a80f50b6c532b675e0f))

* chore: update controls ([`edbb47c`](https://github.com/fhempy/fhempy/commit/edbb47c8ee58bf3c90befc84a26d44f220b1aea0))

### Feature

* feat(fhempy): add fusionsolar ([`a449c5e`](https://github.com/fhempy/fhempy/commit/a449c5e22b632f8a486a9d17a7e5dc8c7707cda6))

* feat(rct_power): support max_(dis)charge_current ([`0612cae`](https://github.com/fhempy/fhempy/commit/0612cae475e10e54da7f428cd14f104fcc267e47))

* feat(fusionsolar): get data from fusionsolar kiosk ([`85f1a1f`](https://github.com/fhempy/fhempy/commit/85f1a1fc3dc98c21ecaca66a70ef5950531b8266))

* feat(fhempy): no more BETA ([`bac69fc`](https://github.com/fhempy/fhempy/commit/bac69fc659dbcc5224d907d867bc5d7424eae278))

### Unknown

* Merge branch &#39;development&#39; ([`e276a94`](https://github.com/fhempy/fhempy/commit/e276a94327e6f8ecd3051373e9b2aa3fdb22c75d))


## v0.1.234 (2022-02-13)

### Chore

* chore: update controls ([`fb4d1fa`](https://github.com/fhempy/fhempy/commit/fb4d1fa5d68b622a38123b4c032f3563f1b286b4))

### Fix

* fix(rct_power): use textfield for set *_soc_target ([`ba9a923`](https://github.com/fhempy/fhempy/commit/ba9a92370159b35c33f87778c977173a5915f941))

### Unknown

* Merge branch &#39;development&#39; ([`eeb3960`](https://github.com/fhempy/fhempy/commit/eeb3960e1db2d8233d7f140edb2c65749aac74bb))


## v0.1.233 (2022-02-13)

### Chore

* chore: update controls ([`dae639b`](https://github.com/fhempy/fhempy/commit/dae639b7c875a774f5158a31ae76b521a271543d))

### Feature

* feat(rct_power): support disable/update_readings ([`f511879`](https://github.com/fhempy/fhempy/commit/f51187962b5357406e97fabe24e7203d85faaa2f))

### Unknown

* Merge branch &#39;development&#39; ([`4db9b0d`](https://github.com/fhempy/fhempy/commit/4db9b0d3fc8bd2f91de51ac915cfb397fb25c94b))


## v0.1.232 (2022-02-12)

### Chore

* chore: update controls ([`35ecf0b`](https://github.com/fhempy/fhempy/commit/35ecf0b55ad4c86b9c4d2295a9ff13ca793fe6d6))

### Fix

* fix(rct_power): fix set *_soc_target ([`f867b78`](https://github.com/fhempy/fhempy/commit/f867b7882ea37441e91ee0ace3760e3f74720946))

* fix(meross): remove stopped state ([`450fbf4`](https://github.com/fhempy/fhempy/commit/450fbf4ec7d412a08e86c8173ce0933212fdd945))

### Unknown

* Merge branch &#39;development&#39; ([`b461fb2`](https://github.com/fhempy/fhempy/commit/b461fb2e043ef6e13fbd6309d430d3ec4722f407))


## v0.1.231 (2022-02-12)

### Chore

* chore: update controls ([`36e20d2`](https://github.com/fhempy/fhempy/commit/36e20d2ebceb3abbb09025fa890f7b5a1ed86e77))

### Feature

* feat(rct_power): further set functions ([`27812d0`](https://github.com/fhempy/fhempy/commit/27812d066ee58689aab681b066180705f5805b5d))

### Unknown

* Merge branch &#39;development&#39; ([`60bce62`](https://github.com/fhempy/fhempy/commit/60bce621cc3de2f2a6e342aaade249e01d2dc33a))


## v0.1.230 (2022-02-12)

### Chore

* chore: update controls ([`cc19d33`](https://github.com/fhempy/fhempy/commit/cc19d334b5871f23409d00e6d171a0c9b78f260e))

### Fix

* fix(skodaconnect): fix login ([`d3a92df`](https://github.com/fhempy/fhempy/commit/d3a92df885c40d5a500bfc640cef191c5e2a6124))

### Unknown

* Merge branch &#39;development&#39; ([`a9b9a4c`](https://github.com/fhempy/fhempy/commit/a9b9a4c566bed4143c068125ca0078042c784c07))


## v0.1.229 (2022-02-12)

### Chore

* chore: update controls ([`8ddea26`](https://github.com/fhempy/fhempy/commit/8ddea265e7de1a462973e30c7d4a9985a3e0dc69))

### Fix

* fix(rct_power): fix display_brightness ([`89c8d92`](https://github.com/fhempy/fhempy/commit/89c8d92b3ce3e1db89cd909d1a97fc3b6a918e1d))

### Unknown

* Merge branch &#39;development&#39; ([`ba5a6a0`](https://github.com/fhempy/fhempy/commit/ba5a6a01824514c8fb5abd7e01cf79480f8515c5))


## v0.1.228 (2022-02-12)

### Chore

* chore: update controls ([`dd802c4`](https://github.com/fhempy/fhempy/commit/dd802c480e9cc0b385bdd79bd9c1916eb18a4fc5))

### Fix

* fix(rct_power): fix function call ([`995c6ba`](https://github.com/fhempy/fhempy/commit/995c6ba5d9ab78c906ff2c7d320e46ea122f1b73))

### Unknown

* Merge branch &#39;development&#39; ([`9394964`](https://github.com/fhempy/fhempy/commit/93949647ceb23adb4ef35ea2234d82fa93e16e52))


## v0.1.227 (2022-02-12)

### Chore

* chore: update controls ([`37bf694`](https://github.com/fhempy/fhempy/commit/37bf6949c9edae15a7bb15765747af4e7ef08a2e))

### Feature

* feat(rct_power): support display brightness ([`533954a`](https://github.com/fhempy/fhempy/commit/533954ac61b9fa84ce07a1edc692c712ff3d2a70))

### Unknown

* Merge branch &#39;development&#39; ([`50fd14e`](https://github.com/fhempy/fhempy/commit/50fd14e14aa5c35dc0afdb2ace2eb28266b55a77))


## v0.1.226 (2022-02-11)

### Chore

* chore: update controls ([`df4b634`](https://github.com/fhempy/fhempy/commit/df4b6343c4f78a327248c512e34190cc4d0939cf))

### Feature

* feat(rct_power): attr error_reading, default_... ([`584e849`](https://github.com/fhempy/fhempy/commit/584e8495ae323e4f71d2d4db9e4ac4af98bc000a))

* feat(rct_power): add format, add error reading ([`0772e76`](https://github.com/fhempy/fhempy/commit/0772e7693cefb66f84bc90b9a633b8cd11f22f56))

### Fix

* fix(fhempy): fix naming ([`b9c9cf1`](https://github.com/fhempy/fhempy/commit/b9c9cf1fa3562fe24d8c4601a9520c565f1bb09c))

### Unknown

* Merge branch &#39;development&#39; ([`2925b58`](https://github.com/fhempy/fhempy/commit/2925b584da74a5c4438469e410e6ed5d4602f198))


## v0.1.225 (2022-02-11)

### Chore

* chore: update controls ([`6e5a9b9`](https://github.com/fhempy/fhempy/commit/6e5a9b9e95ee224be3923b4bc6c35c92a0c70857))

### Fix

* fix(rct_power): support json/array format ([`c282ac9`](https://github.com/fhempy/fhempy/commit/c282ac979ee79e53a08593b169619b046b86f362))

### Unknown

* Merge branch &#39;development&#39; ([`301b64d`](https://github.com/fhempy/fhempy/commit/301b64dfbd4089f53dcf2d0dbb2ed691559c8fb6))


## v0.1.224 (2022-02-10)

### Chore

* chore: update controls ([`493e2d8`](https://github.com/fhempy/fhempy/commit/493e2d827ff4ae50900481860615eec7b318a777))

### Feature

* feat(rct_power): new attributes ([`0651dc5`](https://github.com/fhempy/fhempy/commit/0651dc5dbe48e3ecaf8454a20ad357ecac61be35))

### Unknown

* Merge branch &#39;development&#39; ([`ee5bffe`](https://github.com/fhempy/fhempy/commit/ee5bffe6f844537684f33773107ba48862f81c60))


## v0.1.223 (2022-02-10)

### Chore

* chore: update controls ([`816dc07`](https://github.com/fhempy/fhempy/commit/816dc0712d22f6fc765f86ce20504930e1f69e6e))

### Fix

* fix(rct_power): change interval to 10s, fix state ([`72dced8`](https://github.com/fhempy/fhempy/commit/72dced8eb70b4082a317254b9be6eac35d608c2e))

### Unknown

* Merge branch &#39;development&#39; ([`92493b4`](https://github.com/fhempy/fhempy/commit/92493b440463c9b15bb748330eaa257a10d08d1e))


## v0.1.222 (2022-02-09)

### Chore

* chore: update controls ([`9597c3a`](https://github.com/fhempy/fhempy/commit/9597c3a57c6b44ac5d86c3fb7c5f647912a6f6b6))

### Feature

* feat(rct_power): support RCT Power inverter ([`76f316f`](https://github.com/fhempy/fhempy/commit/76f316fd280a3209c44e0f6fc91a21bb8f206079))

### Unknown

* Merge branch &#39;development&#39; ([`f8800dc`](https://github.com/fhempy/fhempy/commit/f8800dc660a47e7bd02d514f5410a72099e3056b))


## v0.1.221 (2022-02-09)

### Chore

* chore: update controls ([`5b15569`](https://github.com/fhempy/fhempy/commit/5b155690b3eb82e8bdd879bcba7b6756c949c6df))

### Fix

* fix(tuya_cloud): add pulsar activation error msg ([`faab929`](https://github.com/fhempy/fhempy/commit/faab92932949a2eea85414704397d50aa8270e4b))

### Unknown

* Merge branch &#39;development&#39; ([`a82f8f8`](https://github.com/fhempy/fhempy/commit/a82f8f8541c4afbc4ff5988db2d2946d1aa9ce22))


## v0.1.220 (2022-02-08)

### Chore

* chore: update controls ([`9248eb4`](https://github.com/fhempy/fhempy/commit/9248eb4407a10c0264e05941a4e951dfbab752e3))

### Fix

* fix(skodaconnect): Update Base Lib (#65)

Fixed timestamps for requests in Base Lib ([`7ef4a13`](https://github.com/fhempy/fhempy/commit/7ef4a13358312ef14f764d5f81e754fc47732dcf))

### Unknown

* Merge branch &#39;development&#39; ([`8f76ae4`](https://github.com/fhempy/fhempy/commit/8f76ae4128c93311bc3626315d4d31a20943393b))


## v0.1.219 (2022-02-08)

### Chore

* chore: update controls ([`69ffec3`](https://github.com/fhempy/fhempy/commit/69ffec33eada0a4831ec3f28409fef92e6ede725))

### Feature

* feat(tuya_cloud): add tuya open pulsar messaging ([`2c49000`](https://github.com/fhempy/fhempy/commit/2c4900090738a80113512877a3a65172246514cb))

### Fix

* fix(xiaomi_gateway3): fix dict changed during iter ([`8c5bd74`](https://github.com/fhempy/fhempy/commit/8c5bd74e3262d60b9afbe3af472c1b3944c92d54))

* fix(fhempy): fix utf8 issues ([`36383c5`](https://github.com/fhempy/fhempy/commit/36383c5141a7ed48e386c73dfac9074bb1b3d28d))

### Unknown

* Merge branch &#39;development&#39; ([`1934598`](https://github.com/fhempy/fhempy/commit/19345980d152bd63424b0ccc5c65581eeddedc87))


## v0.1.218 (2022-02-07)

### Chore

* chore: update controls ([`c6bf93a`](https://github.com/fhempy/fhempy/commit/c6bf93a875d06df34872faf900b5a46ff1462a72))

### Fix

* fix(xiaomi_gateway3): fix BT devices ([`81f8aea`](https://github.com/fhempy/fhempy/commit/81f8aea5ffc16f55a239a3579c15ca5b1fc9b547))

* fix(ring): fix circular import? ([`a061667`](https://github.com/fhempy/fhempy/commit/a061667c55ec1e58d57ef0bd2ed6452a2acf0c0c))

* fix(meross): fix stop ([`b22b7a0`](https://github.com/fhempy/fhempy/commit/b22b7a0d232b0312aeb8eb62974f0dfdcd020fe6))

* fix(helloworld): add README ([`7f12567`](https://github.com/fhempy/fhempy/commit/7f12567ab7a5e84adeab4dfb5395e76bdc38011f))

### Unknown

* Merge branch &#39;development&#39; ([`4aa2bfc`](https://github.com/fhempy/fhempy/commit/4aa2bfcb1c1186502999e715769edc7b3ffab456))


## v0.1.217 (2022-02-06)

### Chore

* chore: update controls ([`e14160b`](https://github.com/fhempy/fhempy/commit/e14160bb6defd3fe988128dccf936b0acd351010))

### Fix

* fix(xiaomi_gateway3): fix BT devices ([`be7b30d`](https://github.com/fhempy/fhempy/commit/be7b30d6117c77b0c8e9d6fcfce995d7a619bfca))

### Unknown

* Merge branch &#39;development&#39; ([`72dcd4c`](https://github.com/fhempy/fhempy/commit/72dcd4cd05063a26ca41fa9e2f99535b34c38d83))


## v0.1.216 (2022-02-06)

### Chore

* chore: update controls ([`3b2b538`](https://github.com/fhempy/fhempy/commit/3b2b538a44f8e0bc3c5b79a84e76aff6757ee150))

### Feature

* feat(xiaomi_gateway3): support BT smoke alarm ([`983fe78`](https://github.com/fhempy/fhempy/commit/983fe78877eefa9232091273276a127776bd143b))

### Unknown

* Merge branch &#39;development&#39; ([`212efba`](https://github.com/fhempy/fhempy/commit/212efba409da0394771f1a976ff6e35c65c21a08))


## v0.1.215 (2022-02-06)

### Chore

* chore: update controls ([`0d85cfa`](https://github.com/fhempy/fhempy/commit/0d85cfa08d64928c2f637a142960bbf80b3c4244))

* chore: readme fixes ([`ecd1c81`](https://github.com/fhempy/fhempy/commit/ecd1c81da95287d49c650d00f103d2e6b1773555))

### Feature

* feat(xiaomi_gateway3): support 1371 sensor ([`3c04477`](https://github.com/fhempy/fhempy/commit/3c044779f1ccf3d7fafcd7fcdc238425169c90f1))

### Fix

* fix(fhempy): change fhempy_remote to _peer ([`570afc8`](https://github.com/fhempy/fhempy/commit/570afc8d469e2e498b1320928f359fa52628d2db))

### Unknown

* Merge branch &#39;development&#39; ([`ad5e426`](https://github.com/fhempy/fhempy/commit/ad5e426447500dfc6ef59ac3f460065b447525d3))


## v0.1.214 (2022-02-06)

### Chore

* chore: update controls ([`0171c2a`](https://github.com/fhempy/fhempy/commit/0171c2ada8471e86fc18566b0c2849ab8ef9a71b))

### Feature

* feat(meross): support roller shutter ([`eba7e27`](https://github.com/fhempy/fhempy/commit/eba7e2744e80549dd2efd5c733f17222481527b1))

### Unknown

* Merge branch &#39;development&#39; ([`5e10c0b`](https://github.com/fhempy/fhempy/commit/5e10c0ba08fb0d1b42a38f4a8971b811c53aca10))


## v0.1.213 (2022-02-06)

### Chore

* chore: update controls ([`8a5f332`](https://github.com/fhempy/fhempy/commit/8a5f332b18c97dc92f45727b882ac54c21bc55af))

### Fix

* fix(xiaomi_gateway3): fix ble devices ([`3c100d9`](https://github.com/fhempy/fhempy/commit/3c100d990ae16ddd2af94508c89545dd735414a7))

* fix(fhempy): fix fhempy_log error msg ([`da0f71c`](https://github.com/fhempy/fhempy/commit/da0f71c9d1230c4cc83980711797f42a6d84a3ae))

### Unknown

* Merge branch &#39;development&#39; ([`1e762f6`](https://github.com/fhempy/fhempy/commit/1e762f69db1b378edb30376b2b55583977fe0df5))


## v0.1.212 (2022-02-06)

### Chore

* chore: update controls ([`6976d94`](https://github.com/fhempy/fhempy/commit/6976d94d75a7fd746cd7ca1346b6d644753c919a))

### Feature

* feat(eq3bt): support max_retries attr ([`b483878`](https://github.com/fhempy/fhempy/commit/b483878b89e05fe78df9db4df4cbe2498468799c))

### Unknown

* Merge branch &#39;development&#39; ([`c733d85`](https://github.com/fhempy/fhempy/commit/c733d85a520602a0b399cd6355663536cd2598c2))


## v0.1.211 (2022-02-04)

### Chore

* chore: update controls ([`4a5f0c3`](https://github.com/fhempy/fhempy/commit/4a5f0c3dfa595a2ee431ef430ae39d65295fa9ff))

### Fix

* fix(nefit): change default interval to 900s ([`48a69e8`](https://github.com/fhempy/fhempy/commit/48a69e8cd819fe443a7e5ff2ef5e432e8972827f))

* fix(skodaconnect): Update Base Lib (#64) ([`c1eefd4`](https://github.com/fhempy/fhempy/commit/c1eefd4dd91c5563453b14469b2a41777208afda))

### Unknown

* Merge branch &#39;development&#39; ([`a1a7b01`](https://github.com/fhempy/fhempy/commit/a1a7b0176bedf802e6e14ae9e1355cf9ca83d4df))


## v0.1.210 (2022-02-01)

### Chore

* chore: update controls ([`d29fb65`](https://github.com/fhempy/fhempy/commit/d29fb65d75ad436b7b702d2d8af438ed1d263ef2))

### Feature

* feat(pyit600): additional attributes added (#59) ([`1753761`](https://github.com/fhempy/fhempy/commit/1753761290a41ba11e8959e6010a879554e8b0c9))

### Fix

* fix(nefit): fix system_pressure ([`1804780`](https://github.com/fhempy/fhempy/commit/1804780e585ca796277346d57da87810f9ec1349))

* fix(skodaconnect): Update manifest.json (#60)

Update Base-Lib to 1.1.14 due to change of login form ([`df00380`](https://github.com/fhempy/fhempy/commit/df0038006fece2eee2ff176255d1113a09037633))

### Unknown

* Merge branch &#39;development&#39; ([`dbb5bb0`](https://github.com/fhempy/fhempy/commit/dbb5bb0658e1fa18af4e2d741713174085497db5))


## v0.1.209 (2022-01-23)

### Chore

* chore: update controls ([`e275794`](https://github.com/fhempy/fhempy/commit/e275794bcdc94b6162ff0fbec6a75ef9c50de0b5))

### Feature

* feat(nefit): support system pressure ([`c90669e`](https://github.com/fhempy/fhempy/commit/c90669e3e1a053691eca2356c22fac30bc7a1ce6))

### Unknown

* Merge branch &#39;development&#39; ([`809ec84`](https://github.com/fhempy/fhempy/commit/809ec841da41a01c873e42b6a69d1d1cafcd0c70))


## v0.1.208 (2022-01-23)

### Chore

* chore: update controls ([`310695a`](https://github.com/fhempy/fhempy/commit/310695aba0e1f1b8e46f877f334079eb951be2c1))

### Fix

* fix(nefit): update dayassunday readings asap ([`9f55182`](https://github.com/fhempy/fhempy/commit/9f55182cd8231bf397d824b43cfeff0b36ab6111))

### Unknown

* Merge branch &#39;development&#39; ([`298a600`](https://github.com/fhempy/fhempy/commit/298a6008c2e9438c44dcfafba665b6e8d136b62a))


## v0.1.207 (2022-01-23)

### Chore

* chore: update controls ([`f527d60`](https://github.com/fhempy/fhempy/commit/f527d6019f107645dc0e29883ad8664fb2fcbe2a))

### Fix

* fix(nefit): fix again tomorrow/todayAsSunday ([`6449ad2`](https://github.com/fhempy/fhempy/commit/6449ad21485ce005e34d88853b2b71c44192d28e))

### Unknown

* Merge branch &#39;development&#39; ([`a14e3fc`](https://github.com/fhempy/fhempy/commit/a14e3fc21c4cec745c4051bdfff53c85ed8b7e0f))


## v0.1.206 (2022-01-23)

### Chore

* chore: update controls ([`429b3d8`](https://github.com/fhempy/fhempy/commit/429b3d84bb895e46afe76878938c6cf345c3776a))

### Fix

* fix(nefit): fix today/tomorrowAsSunday ([`ff11294`](https://github.com/fhempy/fhempy/commit/ff1129413f761ee9d9badff2d5080ac525c8e469))

### Unknown

* Merge branch &#39;development&#39; ([`60b99e9`](https://github.com/fhempy/fhempy/commit/60b99e9a2755da70a5c4676e7652ca89922b1430))


## v0.1.205 (2022-01-23)

### Chore

* chore: update controls ([`5f28193`](https://github.com/fhempy/fhempy/commit/5f2819320d2cc76c242e043271ee79fbffc4ee7d))

### Feature

* feat(nefit): support dayassunday set functions ([`0ed99f2`](https://github.com/fhempy/fhempy/commit/0ed99f2ddb49d03bf1112efa50684d01c6e2afea))

### Fix

* fix(fhempy): remove sentry as I&#39;m not using it ([`0fefcf0`](https://github.com/fhempy/fhempy/commit/0fefcf0dfd67d94f20678cf50dee8f9847233b86))

### Unknown

* Merge branch &#39;development&#39; ([`2a22538`](https://github.com/fhempy/fhempy/commit/2a22538ccafb4d965ec430c74bd4caa8f464035d))


## v0.1.204 (2022-01-22)

### Chore

* chore: update controls ([`ba6c953`](https://github.com/fhempy/fhempy/commit/ba6c95394eeb4b9f8b5804223501bc8cf9f076c8))

### Fix

* fix(nefit): fix retrieve dayassunday ([`c78e836`](https://github.com/fhempy/fhempy/commit/c78e836598aabf7289213200ce12aad3843e2423))

### Unknown

* Merge branch &#39;development&#39; ([`9918f12`](https://github.com/fhempy/fhempy/commit/9918f12556bf91841f77d3eccff5aad43e9c0fa9))


## v0.1.203 (2022-01-22)

### Chore

* chore: update controls ([`83cada6`](https://github.com/fhempy/fhempy/commit/83cada6effb60f1180eaed6d70debba5e52cd73c))

### Feature

* feat(nefit): retrieve dayassunday ([`8462ba4`](https://github.com/fhempy/fhempy/commit/8462ba421fc30c793b178d4f7b0ea7509f794dbf))

### Fix

* fix(nefix): readme fixes ([`7f698e8`](https://github.com/fhempy/fhempy/commit/7f698e898a7281f3a789ac54284c44261c86fb9f))

### Unknown

* Merge branch &#39;development&#39; ([`f4352a4`](https://github.com/fhempy/fhempy/commit/f4352a425504b61ebbf4d2e472d13aaf3422816f))


## v0.1.202 (2022-01-22)

### Chore

* chore: update controls ([`a75062b`](https://github.com/fhempy/fhempy/commit/a75062bc302f7ed0bec517fdf20320c0fa0e0d46))

### Fix

* fix(fhempy): use markdown2 instead of markdown ([`f2403e6`](https://github.com/fhempy/fhempy/commit/f2403e6457e860afc4b69485e48caf90a0a8c24a))

### Unknown

* Merge branch &#39;development&#39; ([`188f50c`](https://github.com/fhempy/fhempy/commit/188f50c3f241ed26993aa3575d759bc3cef62e59))


## v0.1.201 (2022-01-22)

### Chore

* chore: update controls ([`5d92283`](https://github.com/fhempy/fhempy/commit/5d9228324bb764710a4e12c9912ac3eea0d424eb))

### Fix

* fix(nefit): fix umlaut issue ([`76710bf`](https://github.com/fhempy/fhempy/commit/76710bf279eef26303edff96f7cce3de968c5983))

### Unknown

* Merge branch &#39;development&#39; ([`a91566a`](https://github.com/fhempy/fhempy/commit/a91566ad7ae86241e0a0179854b9c12dfc897cc7))


## v0.1.200 (2022-01-22)

### Chore

* chore: update controls ([`47869ac`](https://github.com/fhempy/fhempy/commit/47869ac31202bc7ab3ce34791b3868027f94598f))

### Fix

* fix(nefit): fix consumption again ([`def458c`](https://github.com/fhempy/fhempy/commit/def458c970e5deae0e60b237a973e3cdcfb93338))

### Unknown

* Merge branch &#39;development&#39; ([`5b16094`](https://github.com/fhempy/fhempy/commit/5b16094e4a1c2e16e9499e844e45697a302d1af0))


## v0.1.199 (2022-01-22)

### Chore

* chore: update controls ([`4184693`](https://github.com/fhempy/fhempy/commit/418469335f3aed21ee3da46fe869b2adf5c0d937))

### Fix

* fix(nefit): fix consumption ([`11ce422`](https://github.com/fhempy/fhempy/commit/11ce4222a7c9ddbf214eca26a5fdec6b03bea882))

### Unknown

* Merge branch &#39;development&#39; ([`168de6c`](https://github.com/fhempy/fhempy/commit/168de6c092b2589dacb10d7e8259d5411062db26))


## v0.1.198 (2022-01-22)

### Chore

* chore: update controls ([`7a37281`](https://github.com/fhempy/fhempy/commit/7a37281d77c0a2fd5edabdfe2fc0d81a8e67e740))

### Fix

* fix(nefit): fix some readings ([`e4613f9`](https://github.com/fhempy/fhempy/commit/e4613f909156015c190d2d39603f241e4d2769b3))

* fix(pyit600): usage description updated (#58) ([`9ce8405`](https://github.com/fhempy/fhempy/commit/9ce84058d648878e06cb720d1abdfc505124d388))

### Unknown

* Merge branch &#39;development&#39; ([`0746182`](https://github.com/fhempy/fhempy/commit/074618200ba646673c72401c90d514ba64fcf331))


## v0.1.197 (2022-01-15)

### Chore

* chore: update controls ([`0bc615a`](https://github.com/fhempy/fhempy/commit/0bc615ad8c0ecf7b1fb688f7442ef7bbe0d66035))

### Unknown

* Merge branch &#39;development&#39; ([`6539a94`](https://github.com/fhempy/fhempy/commit/6539a9499cb087be836a09ed0bae27703e74486c))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhempy ([`b7b8fa6`](https://github.com/fhempy/fhempy/commit/b7b8fa6a33b807b15b051e9247d626e05ebf57ed))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhempy into development ([`6ca23b3`](https://github.com/fhempy/fhempy/commit/6ca23b302e2b7d909bda6667c405930bf034f659))


## v0.1.196 (2022-01-15)

### Chore

* chore: update controls ([`6ec971d`](https://github.com/fhempy/fhempy/commit/6ec971dae7734d12e1e0c6039e50f6644b32fac2))

### Feature

* feat(nefit): add outdoor temperature ([`ecaadb1`](https://github.com/fhempy/fhempy/commit/ecaadb159dad75b96ea13d1149ca893b588af922))

### Fix

* fix(nefit): fix reconnect, rename readings ([`0705e8d`](https://github.com/fhempy/fhempy/commit/0705e8d44ab84743cb99b05ca8252a5a2e0e31e4))

* fix(pyit600): minor fixes (#56) ([`3bdbaff`](https://github.com/fhempy/fhempy/commit/3bdbaff9f374b4ab7b5fae250b76921b8ea2a98a))

### Unknown

* Merge branch &#39;development&#39; ([`c80dca1`](https://github.com/fhempy/fhempy/commit/c80dca1fefa1f140d06618c55340dfd872341552))


## v0.1.195 (2022-01-08)

### Chore

* chore: update controls ([`d8090e5`](https://github.com/fhempy/fhempy/commit/d8090e537d64044041139ba0aad662d388eb7069))

### Feature

* feat(nefit): support nefit devices ([`ea41aa8`](https://github.com/fhempy/fhempy/commit/ea41aa8d608e19a11c61fafae0c708f9fb7df140))

### Unknown

* Merge branch &#39;development&#39; ([`7df857a`](https://github.com/fhempy/fhempy/commit/7df857a12721fef9828b836161b3baac71949e82))


## v0.1.194 (2022-01-08)

### Chore

* chore: update controls ([`c7f17ce`](https://github.com/fhempy/fhempy/commit/c7f17ce64b9e4c240f92cdd044b2515365a7c96f))

### Unknown

* Merge branch &#39;development&#39; ([`31363b1`](https://github.com/fhempy/fhempy/commit/31363b1eff44bde0b9db1070abb62daa2727eae7))

* (feat): Add new heating device (#53) ([`54bd055`](https://github.com/fhempy/fhempy/commit/54bd0551f2746dd5904aeb40a8a508928f7a5394))


## v0.1.193 (2022-01-07)

### Chore

* chore: update controls ([`bb837c0`](https://github.com/fhempy/fhempy/commit/bb837c03fc5d407c5a4d50b2dc1d40c2c161c2d0))

* chore: add pyit600 to readme ([`80c28db`](https://github.com/fhempy/fhempy/commit/80c28db765d742ba0e8393bdf2106169918eec6e))

### Unknown

* Merge branch &#39;development&#39; ([`c9b454d`](https://github.com/fhempy/fhempy/commit/c9b454d4af8ee7e866f72184984160196475e5c4))

* (feat): Support Salus iT600 based on module pyit600 (#52)

Supports VS20WRF ([`3e250b5`](https://github.com/fhempy/fhempy/commit/3e250b5fec1b99554e173b7b84d1a81d65e589a0))


## v0.1.192 (2022-01-03)

### Chore

* chore: update controls ([`0bc3efa`](https://github.com/fhempy/fhempy/commit/0bc3efa064042e973b8bea2d64aef6cd0163288c))

### Fix

* fix(tuya_cloud): restart mqtt loop deactivated ([`3cbad93`](https://github.com/fhempy/fhempy/commit/3cbad9381002299d3b64f51887838e92dc9fb4fd))

### Unknown

* Merge branch &#39;development&#39; ([`3affdb1`](https://github.com/fhempy/fhempy/commit/3affdb18fd5656c63c71dafa4d898603e984bd11))


## v0.1.191 (2022-01-03)

### Chore

* chore: update controls ([`bb49b66`](https://github.com/fhempy/fhempy/commit/bb49b663ce3e6230ac5763beab46dd159bb66d0c))

### Fix

* fix(xiaomi_tokens): fix for de server ([`63c6c4b`](https://github.com/fhempy/fhempy/commit/63c6c4b458f2432cef97dade4d490f2cc0be7369))

### Unknown

* Merge branch &#39;development&#39; ([`44a17a7`](https://github.com/fhempy/fhempy/commit/44a17a7610326c3cb3718d46a715f63b5c88d7a4))


## v0.1.190 (2021-12-26)

### Chore

* chore: update controls ([`bf282e5`](https://github.com/fhempy/fhempy/commit/bf282e5cdeffee690284bbc0d3c8bb98b76058ca))

### Fix

* fix(tuya_cloud): fix lib usage ([`9b2dccf`](https://github.com/fhempy/fhempy/commit/9b2dccfc4469b0f186d3097b2f4aa1a3898ff058))

### Unknown

* Merge branch &#39;development&#39; ([`17fda1e`](https://github.com/fhempy/fhempy/commit/17fda1eb84991327a87d26a07600192e700cd139))


## v0.1.189 (2021-12-26)

### Chore

* chore: update controls ([`ac19ade`](https://github.com/fhempy/fhempy/commit/ac19ade79e56e4b29ebd16d3672e374727321617))

### Fix

* fix(tuya_cloud): update lib, python&gt;3.7 required!! ([`ea69096`](https://github.com/fhempy/fhempy/commit/ea690962be90d0c8713b503008ea52d8d4fe338d))

### Unknown

* Merge branch &#39;development&#39; ([`3f50d87`](https://github.com/fhempy/fhempy/commit/3f50d87ab13f82ddc20d6614d35c6b1351f46157))


## v0.1.188 (2021-12-19)

### Chore

* chore: update controls ([`b348a81`](https://github.com/fhempy/fhempy/commit/b348a8147e7362c287270fbe138d696842d8e337))

### Feature

* feat(esphome): attr port_dashboard ([`c52fa7a`](https://github.com/fhempy/fhempy/commit/c52fa7aa7f50bf195803c4b81435832c391c9d7c))

### Fix

* fix(fhempy): remove temporary for log ([`957a14b`](https://github.com/fhempy/fhempy/commit/957a14b92368af0b8a329bb2fc601eff98518a38))

### Unknown

* Merge branch &#39;development&#39; ([`91076cb`](https://github.com/fhempy/fhempy/commit/91076cb96dd30a2a386dd3792b4fe5bfcccd6e28))


## v0.1.187 (2021-12-05)

### Chore

* chore: update controls ([`1b6f060`](https://github.com/fhempy/fhempy/commit/1b6f060c832f6d380258d4afbf0c607378cafc84))

### Fix

* fix(fhempy): fix CoProcess error ([`397edde`](https://github.com/fhempy/fhempy/commit/397edde0b39d52b0175454c2fd071b5ce8b2e973))

### Unknown

* Merge branch &#39;development&#39; ([`9f6bf00`](https://github.com/fhempy/fhempy/commit/9f6bf003fa15d629489ea3e226ba94df7df4e398))


## v0.1.186 (2021-12-05)

### Chore

* chore: update controls ([`c96979b`](https://github.com/fhempy/fhempy/commit/c96979b931abbee09ba3b555a6b0d7f9df2ec80b))

### Feature

* feat(fhempy): support &#34;all&#34; notification in ble ([`ea1f5eb`](https://github.com/fhempy/fhempy/commit/ea1f5ebb0d40f5b3efdde39e04d38fd1350a8302))

### Fix

* fix(mitemp2): try to fix mitemp2 ([`ba558c0`](https://github.com/fhempy/fhempy/commit/ba558c07a56841c998166709447902e6fb671fa7))

### Unknown

* Merge branch &#39;development&#39; ([`0643d70`](https://github.com/fhempy/fhempy/commit/0643d70122214a25bd8d73ba82817be75db6c448))


## v0.1.185 (2021-12-03)

### Chore

* chore: update controls ([`35278ff`](https://github.com/fhempy/fhempy/commit/35278ff0aac1b5169adaf27af498dcaad391e23c))

### Fix

* fix(eq3bt): windowOpenTemp starts at 5 degrees ([`3ef7e36`](https://github.com/fhempy/fhempy/commit/3ef7e36bdfe2b90cd5f9780ac390decb5d0a3775))

### Unknown

* Merge branch &#39;development&#39; ([`a91520f`](https://github.com/fhempy/fhempy/commit/a91520f5e86a6c386da8959b81ba3d669e055464))


## v0.1.184 (2021-12-01)

### Chore

* chore: update controls ([`efe8030`](https://github.com/fhempy/fhempy/commit/efe8030c9424ca89c96187d81007cc3162c9224f))

### Fix

* fix(eq3bt): fix windowOpenTime/Temp ([`47ad1d2`](https://github.com/fhempy/fhempy/commit/47ad1d2c24fb50dba7f1f1ed09041eb4375ac56e))

### Unknown

* Merge branch &#39;development&#39; ([`507f0f5`](https://github.com/fhempy/fhempy/commit/507f0f5af9aa17e5b79fa916f64f7223abed352e))


## v0.1.183 (2021-11-30)

### Chore

* chore: update controls ([`929d536`](https://github.com/fhempy/fhempy/commit/929d536164930eee659cec387c7dbd2763a37af8))

### Fix

* fix(tuya_cloud): fix AuthType ([`777edc0`](https://github.com/fhempy/fhempy/commit/777edc0327b71e424864f9478e0fbc2564ac51f2))

### Unknown

* Merge branch &#39;development&#39; ([`0fb4521`](https://github.com/fhempy/fhempy/commit/0fb4521d11098d2f7ccc9912e15e8407b7d75cc0))


## v0.1.182 (2021-11-30)

### Chore

* chore: update controls ([`832bc6e`](https://github.com/fhempy/fhempy/commit/832bc6ebacca6dc2b5282ca938f9251468467b58))

### Fix

* fix(tuya_cloud): support python 3.7 again ([`b54b5b8`](https://github.com/fhempy/fhempy/commit/b54b5b82683d177691df0a7c0c3bb85ab9670f38))

* fix(fhempy): clarify peer installation ([`9d9a5d3`](https://github.com/fhempy/fhempy/commit/9d9a5d3415afd500948f4043ae02847245998d8f))

### Unknown

* Merge branch &#39;development&#39; ([`833cec2`](https://github.com/fhempy/fhempy/commit/833cec2de42da2e35ebc98e613fec2832c7b3fe1))


## v0.1.181 (2021-11-29)

### Chore

* chore: update controls ([`0262d7c`](https://github.com/fhempy/fhempy/commit/0262d7cc8a27bbe149cb6a8bdae79c21b94e12a0))

### Fix

* fix(tuya_cloud): remove update API calls ([`2aac25c`](https://github.com/fhempy/fhempy/commit/2aac25c2426850ee0fa3d419b5eff9e4474b150a))

* fix(googlecast): update lib to 10.1.1 ([`334d171`](https://github.com/fhempy/fhempy/commit/334d171f3ead33f6b108bd519d0e5d01a2577779))

### Unknown

* Merge branch &#39;development&#39; ([`3744062`](https://github.com/fhempy/fhempy/commit/37440623fb9bb418f3389afd64e1b6900294aff9))


## v0.1.180 (2021-11-28)

### Chore

* chore: update controls ([`5fb112d`](https://github.com/fhempy/fhempy/commit/5fb112d732356c546bccd88525c93d76307cd496))

### Fix

* fix(esphome): fix esphome_installer device ([`7b0d925`](https://github.com/fhempy/fhempy/commit/7b0d92581d0700e295164e125a909687f97dfd2f))

* fix(fhempy): link to github releases ([`7e3f326`](https://github.com/fhempy/fhempy/commit/7e3f326b3f8cf34728510ada4d2bffc07b6408a4))

### Unknown

* Merge branch &#39;development&#39; ([`443e591`](https://github.com/fhempy/fhempy/commit/443e59167313d3462e4d7893323bc4e07aa1cbb0))


## v0.1.179 (2021-11-28)

### Chore

* chore: update controls ([`15e9c53`](https://github.com/fhempy/fhempy/commit/15e9c53e88d778b82ffcd6cfdd77f7996cffc749))

### Fix

* fix(tuya_cloud): fix typo ([`e7b8b62`](https://github.com/fhempy/fhempy/commit/e7b8b62c1acf7cc65de83c8cd8688e4c0808fa05))

* fix(tuya_cloud): retrieve status every 900s ([`c085381`](https://github.com/fhempy/fhempy/commit/c085381fe00d1087feba2afd1a44dea88b0b5e3b))

* fix(tuya_cloud): better error handling ([`0d94229`](https://github.com/fhempy/fhempy/commit/0d94229f70039e7b650462101fd3940c8cb26e95))

### Unknown

* Merge branch &#39;development&#39; ([`e092a2d`](https://github.com/fhempy/fhempy/commit/e092a2da66828df124be86c67959279686ef00d5))

* Update base-lib to v1.1.12 (#44)

some envaq issues solved ([`9a8537d`](https://github.com/fhempy/fhempy/commit/9a8537daf5a55bd55b0f6bdc430e801cedb85a5b))


## v0.1.178 (2021-11-27)

### Chore

* chore: update controls ([`962df60`](https://github.com/fhempy/fhempy/commit/962df601d9d4a57bf900bbd1015a336b550d1cdc))

### Fix

* fix(tuya_cloud): update lib to 0.6.3 (python&gt;=3.8) ([`d2448d7`](https://github.com/fhempy/fhempy/commit/d2448d764ece18b4387420216e86b83f15adb495))

### Unknown

* Merge branch &#39;development&#39; ([`7e2af55`](https://github.com/fhempy/fhempy/commit/7e2af558efd04d363fc6de114cd591eb16506c57))


## v0.1.177 (2021-11-26)

### Chore

* chore: update controls ([`d01a9b8`](https://github.com/fhempy/fhempy/commit/d01a9b8c874a2aab2ddb59321e382e657b66dcdb))

### Fix

* fix(esphome): fix checkIfDeviceExists ([`2b67d7d`](https://github.com/fhempy/fhempy/commit/2b67d7d6dbfc14e1e800dcdd957f5d7a0355bfbd))

* fix(fhempy): fix dbus dependency ([`09c5717`](https://github.com/fhempy/fhempy/commit/09c5717cee2fd8aa13c911ca5466d1a50dba7f6d))

### Unknown

* Merge branch &#39;development&#39; ([`068bc12`](https://github.com/fhempy/fhempy/commit/068bc12a060c5ff40ef0248a9b0cf7c875d4a605))


## v0.1.176 (2021-11-26)

### Chore

* chore: update controls ([`7ca1a09`](https://github.com/fhempy/fhempy/commit/7ca1a0975bd0c4713f01738b0dac2ec20f247994))

### Fix

* fix(esphome): fix attr sortby on restart ([`a605adf`](https://github.com/fhempy/fhempy/commit/a605adfe0c0704f3e04db94fbb4d59697a4bef3f))

* fix(tuya_cloud): change lib to 0.4.1 ([`8ef2e9f`](https://github.com/fhempy/fhempy/commit/8ef2e9f03c64bb0ef69ab6e14aaddd73806251b0))

### Unknown

* Merge branch &#39;development&#39; ([`20bf32e`](https://github.com/fhempy/fhempy/commit/20bf32ea95247213dd2efb3a3bf4e28f23ebaa90))


## v0.1.175 (2021-11-21)

### Chore

* chore: update controls ([`11cf452`](https://github.com/fhempy/fhempy/commit/11cf45276fbaf06b02c5115e6539a0c8f3b6598c))

### Fix

* fix(googlecast): update lib and change discovery ([`13f02e1`](https://github.com/fhempy/fhempy/commit/13f02e1eeba09a4f6f61452727b5a4f3825c64fd))

### Unknown

* Merge branch &#39;development&#39; ([`26ec625`](https://github.com/fhempy/fhempy/commit/26ec625d3fbdcc848afc689aeef022a6e9133df4))


## v0.1.174 (2021-11-15)

### Chore

* chore: update controls ([`725f580`](https://github.com/fhempy/fhempy/commit/725f580c404375fd02262b97ffb833c085faf8c7))


## v0.1.173 (2021-11-15)

### Chore

* chore: update controls ([`1b463bf`](https://github.com/fhempy/fhempy/commit/1b463bf0ef572e8635211476bc5c2cf9bef0633c))

### Fix

* fix(tuya_cloud): fix colour_data ([`d2fd1ac`](https://github.com/fhempy/fhempy/commit/d2fd1ac0b56540ff589c234489416e95f1973fc4))

* fix(fhempy): update zeroconf 0.36.12 ([`768df9e`](https://github.com/fhempy/fhempy/commit/768df9e8a27d0ac06b1f8e7ccd95ff01a7ec34f5))

* fix(googlecast): update lib to 9.4.0 ([`82a1d6b`](https://github.com/fhempy/fhempy/commit/82a1d6b8431343d4d5ed1a1c9dd8c07de2ac2e28))

* fix(tuya_cloud): fix pow() bug ([`275ef99`](https://github.com/fhempy/fhempy/commit/275ef996e953cf65224af85d606d517db07cc8b3))

### Unknown

* Merge branch &#39;development&#39; ([`57a316f`](https://github.com/fhempy/fhempy/commit/57a316f88d489348197ce7a59f5b714c9b0e9302))


## v0.1.172 (2021-11-05)

### Chore

* chore: update controls ([`e28ae40`](https://github.com/fhempy/fhempy/commit/e28ae40aab04f5318d7e1f1d99c16a18160d120b))

### Fix

* fix(googlecast): fix speak ([`5a37d57`](https://github.com/fhempy/fhempy/commit/5a37d57ac0ce598827598918dbe3c50d261f9cf7))

* fix(skodaconnect): update lib to 1.1.10 ([`eb19421`](https://github.com/fhempy/fhempy/commit/eb19421b9ddc7c17cddb84847503fa1f5f608fcb))

### Unknown

* Merge branch &#39;development&#39; ([`167494b`](https://github.com/fhempy/fhempy/commit/167494bcba7780fb21245a80158c9075d236284f))


## v0.1.171 (2021-11-05)

### Chore

* chore: update controls ([`1be3fc0`](https://github.com/fhempy/fhempy/commit/1be3fc0f145ca812585813b7f26c9b81f16c4fc3))

### Fix

* fix(xiaomi_gateway3): fix z2m mode ([`14f3f5b`](https://github.com/fhempy/fhempy/commit/14f3f5b305e7a76bb61092819c5dc404f66e6206))

### Unknown

* Merge branch &#39;development&#39; ([`ca13e8f`](https://github.com/fhempy/fhempy/commit/ca13e8fa4cd705e37c6906975bedd236cd8cf98b))


## v0.1.170 (2021-11-05)

### Chore

* chore: update controls ([`17fad34`](https://github.com/fhempy/fhempy/commit/17fad34f9398c35a944199c52674f6c0e55d514f))

### Fix

* fix(xiaomi_gateway3): fix connected state ([`08005c0`](https://github.com/fhempy/fhempy/commit/08005c0634846aa21e9b56b977b41d24497bc288))

### Unknown

* Merge branch &#39;development&#39; ([`f1d1ef9`](https://github.com/fhempy/fhempy/commit/f1d1ef9dd10bcd99963c2be864fb5c7f1be82c7d))


## v0.1.169 (2021-11-05)

### Chore

* chore: update controls ([`3d5f8eb`](https://github.com/fhempy/fhempy/commit/3d5f8ebcda4022895f72d6e5c1e7431e00494c02))

### Feature

* feat(xiaomi_gateway3): update to 1.6.0rc2 xgw3 lib ([`bcf7f8d`](https://github.com/fhempy/fhempy/commit/bcf7f8d9d303efadafc5f33c0166b5d38fa575c0))

### Fix

* fix(esphome): fix weblinks device ([`9e93ef0`](https://github.com/fhempy/fhempy/commit/9e93ef00a44e15845906196536651dd858fab87a))

### Unknown

* Merge branch &#39;development&#39; ([`b7746fc`](https://github.com/fhempy/fhempy/commit/b7746fcc55194b430390531cf9a15e2a3d9af4be))


## v0.1.168 (2021-10-30)

### Chore

* chore: update controls ([`5de3350`](https://github.com/fhempy/fhempy/commit/5de33500bd4245629f0615df30ce0083dc042f12))

### Fix

* fix(tuya_cloud): fix python 3.7 ([`b28cf4e`](https://github.com/fhempy/fhempy/commit/b28cf4e0213e9ee802c8aec94b40d1840d92ba3f))

### Unknown

* Merge branch &#39;development&#39; ([`2a0e4de`](https://github.com/fhempy/fhempy/commit/2a0e4dec4174564d6a214c6e4476ab0b0e3be9bd))


## v0.1.167 (2021-10-30)

### Chore

* chore: update controls ([`10ca462`](https://github.com/fhempy/fhempy/commit/10ca462df34df0d271dc080b60801b5b05d634d3))

### Fix

* fix(tuya_cloud): update tuya iot lib ([`3ef9f5b`](https://github.com/fhempy/fhempy/commit/3ef9f5bbddf53aa03d07044b881fedf069733f91))

* fix(esphome): fix create weblinks ([`e4ec22f`](https://github.com/fhempy/fhempy/commit/e4ec22f6597ee96307bc1ea5de6a4d2c22f67264))

### Unknown

* Merge branch &#39;development&#39; ([`cd47ec4`](https://github.com/fhempy/fhempy/commit/cd47ec4109896ace3c75889bcd811944cdb94fdf))


## v0.1.166 (2021-10-28)

### Chore

* chore: update controls ([`2252342`](https://github.com/fhempy/fhempy/commit/22523425d024d920676128432e0d848601efa2c4))

### Fix

* fix(ring): update test ([`cef1d64`](https://github.com/fhempy/fhempy/commit/cef1d643813884af75ff54e24296d56fe79aa422))

* fix(ring): correctly stop update thread ([`cec6b74`](https://github.com/fhempy/fhempy/commit/cec6b746886a8991cacb95a10ec361b6f0d7085b))

* fix(googlecast): do not stop zeroconf ([`720b007`](https://github.com/fhempy/fhempy/commit/720b007c81f3ff41da84485feedd7a0660e5fc5e))

* fix(fhempy): add sentry requirement ([`0df8c52`](https://github.com/fhempy/fhempy/commit/0df8c522e369b225878d656a291cf22714e66157))

### Unknown

* Merge branch &#39;development&#39; ([`f8db81b`](https://github.com/fhempy/fhempy/commit/f8db81b82dc04064bdf2a1269a22675ef1a14a95))


## v0.1.165 (2021-10-27)

### Chore

* chore: update controls ([`ca2938d`](https://github.com/fhempy/fhempy/commit/ca2938dafbb73256af8d0230bf399e2a97610ad6))

### Fix

* fix(xiaomi_gateway3): fix zigbee2mqtt ([`fd10b93`](https://github.com/fhempy/fhempy/commit/fd10b93e9719626add8604b913743a5bcba41694))

### Unknown

* Merge branch &#39;development&#39; ([`889c880`](https://github.com/fhempy/fhempy/commit/889c880c766f99f524b1952fd8f4479839959aef))


## v0.1.164 (2021-10-27)

### Chore

* chore: update controls ([`e3c76f4`](https://github.com/fhempy/fhempy/commit/e3c76f44b10936d097dc1e2e0fcb02bccd0e8b00))

### Fix

* fix(xiaomi_gateway3): fix pairing ([`26848db`](https://github.com/fhempy/fhempy/commit/26848db865253f70a95851fa44621adc0e783b51))

### Unknown

* Merge branch &#39;development&#39; ([`38b40e6`](https://github.com/fhempy/fhempy/commit/38b40e6107a6426bb7da79f18f762ce510b243a2))


## v0.1.163 (2021-10-27)

### Chore

* chore: update controls ([`a772c14`](https://github.com/fhempy/fhempy/commit/a772c14ea08151ca04c66cdc9814f3cf1d6c164f))

### Feature

* feat(xiaomi_gateway3): support zigbee2mqtt ([`3829860`](https://github.com/fhempy/fhempy/commit/3829860d8cdf9ace4b181b3769579874d62eee43))

* feat(xiaomi_gateway3): support non xiaomi zigbee ([`be74c22`](https://github.com/fhempy/fhempy/commit/be74c22428b890bf30650f0031eba02bd7507bc9))

### Unknown

* Merge branch &#39;development&#39; ([`dd9ef8d`](https://github.com/fhempy/fhempy/commit/dd9ef8d073048b2f3383ae4c4ba5f98e6e8be458))


## v0.1.162 (2021-10-25)

### Chore

* chore: update controls ([`0e7c318`](https://github.com/fhempy/fhempy/commit/0e7c318eb8c6b178d0eee7c6a308341222abf236))

### Fix

* fix(fhempy): wait max60s for fhem reply ([`1dbcf1e`](https://github.com/fhempy/fhempy/commit/1dbcf1e5e929815864f2791dc6407c3415b30688))

### Unknown

* Merge branch &#39;development&#39; ([`3aa205c`](https://github.com/fhempy/fhempy/commit/3aa205ceb427911b07204ff114f158663193f838))


## v0.1.161 (2021-10-25)

### Chore

* chore: update controls ([`ebd668b`](https://github.com/fhempy/fhempy/commit/ebd668bb9f7158148158774653471cd7041db0b3))

* chore: fix git ([`0b37201`](https://github.com/fhempy/fhempy/commit/0b37201a93357761c4a8f40d588f31f72118b3fc))

### Fix

* fix(googlecast): update lib/zeroconf ([`cab72a7`](https://github.com/fhempy/fhempy/commit/cab72a71694f9754af29d8ccdb64050697717dea))

* fix(fhempy): fix timeout again ([`6f920cb`](https://github.com/fhempy/fhempy/commit/6f920cbc79fb1ebfe4394ae147fa908213555d2a))

* fix(fhempy): update zeroconf ([`650f7ad`](https://github.com/fhempy/fhempy/commit/650f7ad6176d0d89a54fa638b12da75e50619740))

### Unknown

* Merge branch &#39;development&#39; ([`0a238af`](https://github.com/fhempy/fhempy/commit/0a238af7f00e9a0e01387582bf8820281760838c))

* Merge branch &#39;development&#39; ([`a2a2934`](https://github.com/fhempy/fhempy/commit/a2a29345be8a65833503f13d2bd08fbc12d3d6db))


## v0.1.160 (2021-10-25)

### Chore

* chore: update controls ([`d5835a7`](https://github.com/fhempy/fhempy/commit/d5835a76a3da70035797393864d95a104bc39bfb))

### Fix

* fix(tuya): remove error when offline ([`91cfa6c`](https://github.com/fhempy/fhempy/commit/91cfa6cf58df2dd789d9675c420849a7c1a04a35))

### Unknown

* Merge branch &#39;development&#39; ([`d12eb1c`](https://github.com/fhempy/fhempy/commit/d12eb1c83bfac2121df1c2d7db5b2035b52f03d1))


## v0.1.159 (2021-10-24)

### Chore

* chore: update controls ([`bb0f4cc`](https://github.com/fhempy/fhempy/commit/bb0f4cc2d29a7a823da3cf621ba537f364211d9d))

### Fix

* fix(fhempy): remove perf sentry ([`cc5d4f8`](https://github.com/fhempy/fhempy/commit/cc5d4f8985ecd3c904f5c9bac78f50170f6da830))

* fix(googlecast): fix endless loop on undefine ([`655e3ad`](https://github.com/fhempy/fhempy/commit/655e3adc13a4d7d79036055a2595893f6b98ad60))

### Unknown

* Merge branch &#39;development&#39; ([`b8667ee`](https://github.com/fhempy/fhempy/commit/b8667eecbcc2575b34382e6203c2c9905c3c9db7))


## v0.1.158 (2021-10-24)

### Chore

* chore: update controls ([`b070894`](https://github.com/fhempy/fhempy/commit/b070894f583c0e6ec7fec05df095fe1088abedec))

### Fix

* fix(ring): ding poll in separate thread ([`7fc27a6`](https://github.com/fhempy/fhempy/commit/7fc27a683177ce84b2aaac7eac541c66b6bde574))

### Unknown

* Merge branch &#39;development&#39; ([`dee4e5c`](https://github.com/fhempy/fhempy/commit/dee4e5cfefc121253294d12287062af73b261421))


## v0.1.157 (2021-10-24)

### Chore

* chore: update controls ([`9f86a91`](https://github.com/fhempy/fhempy/commit/9f86a91718935eed54bf7bfac7decc8c39862d89))

### Fix

* fix(fhempy): change sentry sample rate ([`3a0d3e5`](https://github.com/fhempy/fhempy/commit/3a0d3e5b4d617cc73f4107801ad4237d4e596672))

* fix(googlecast): report token errors to user ([`a65c64e`](https://github.com/fhempy/fhempy/commit/a65c64ea956e415afa0a2e52dce7e293ba8b5d65))

* fix(fhempy): hopefully fixed a timeout bug ([`1c4f6be`](https://github.com/fhempy/fhempy/commit/1c4f6be11f7c8d06b57094bfffafb5ec9fda6ecc))

### Unknown

* Merge branch &#39;development&#39; ([`c63bfc3`](https://github.com/fhempy/fhempy/commit/c63bfc3d4d3cce63a0fde52d24a0f1a2b3e44dc8))


## v0.1.156 (2021-10-23)

### Chore

* chore: update controls ([`ff44704`](https://github.com/fhempy/fhempy/commit/ff447044d08e731a06292e2dfb7ed0e49b2d82f7))

### Feature

* feat(fhempy): add sentry logging ([`4d3cab6`](https://github.com/fhempy/fhempy/commit/4d3cab6a833d21fcb87136550e00b5bd96fffdb6))

### Fix

* fix(fhempy): iodev selection fix ([`495e41d`](https://github.com/fhempy/fhempy/commit/495e41da6c4b6054ffa8de5b0cde2ca2e297141c))

### Unknown

* Merge branch &#39;development&#39; ([`6cd3915`](https://github.com/fhempy/fhempy/commit/6cd391564ef16738670adefd5b7fd30afc97c4ff))


## v0.1.155 (2021-10-23)

### Chore

* chore: update controls ([`9d0964b`](https://github.com/fhempy/fhempy/commit/9d0964b56601c82098fcd629fa0180b73506242d))

### Fix

* fix(meross): fix typo ([`08f332e`](https://github.com/fhempy/fhempy/commit/08f332e8c2f08e70429b2f54b40988c37654c01f))

### Unknown

* Merge branch &#39;development&#39; ([`ce24029`](https://github.com/fhempy/fhempy/commit/ce24029fb5dfa1e8b803c571d7441c11f1d0d3fc))


## v0.1.154 (2021-10-23)

### Chore

* chore: update controls ([`c89bb9c`](https://github.com/fhempy/fhempy/commit/c89bb9c1ccc3c856a1f98f97d2ff1e5195dcf855))

### Feature

* feat(meross): support rgb,bri,ct ([`a23f34d`](https://github.com/fhempy/fhempy/commit/a23f34ddb496feba162f51542a6c1f66af26b62b))

* feat(fhempy): support iodev select in attr ([`3f64c63`](https://github.com/fhempy/fhempy/commit/3f64c633721cee69d9d4042e6a941ae6f97a8895))

### Unknown

* Merge branch &#39;development&#39; ([`3329d66`](https://github.com/fhempy/fhempy/commit/3329d66160e701bde5d0b7169050e883ad77a9f4))


## v0.1.153 (2021-10-23)

### Chore

* chore: update controls ([`7b8532e`](https://github.com/fhempy/fhempy/commit/7b8532e4926c960dc96203a6dba6b6a38a377032))

### Fix

* fix(fhempy): better logging ([`d35fff7`](https://github.com/fhempy/fhempy/commit/d35fff7c6bf35197ddb0e0323d10e9029dd0fab7))

### Unknown

* Merge branch &#39;development&#39; ([`bef1ce4`](https://github.com/fhempy/fhempy/commit/bef1ce44f50e74bcea871223d2d81a4af1372fd4))


## v0.1.152 (2021-10-22)

### Chore

* chore: update controls ([`cd92aa5`](https://github.com/fhempy/fhempy/commit/cd92aa54dd0255fc70003e4b494c262712d87f33))

### Fix

* fix(meross): fix garage readings ([`b65e004`](https://github.com/fhempy/fhempy/commit/b65e004ad9942063cc6d24eefcec6e4292a1e7ea))

### Unknown

* Merge branch &#39;development&#39; ([`9e5668c`](https://github.com/fhempy/fhempy/commit/9e5668c977cbd328a21cb12997fce47df4ba2f5a))


## v0.1.151 (2021-10-21)

### Chore

* chore: update controls ([`5465581`](https://github.com/fhempy/fhempy/commit/5465581ff9bef8af7f751e08c6e0107450601085))

### Fix

* fix(esphome): fix weblink creation (2) ([`3df3ec0`](https://github.com/fhempy/fhempy/commit/3df3ec013400939ce17a6ba1883ef8eff256a964))

### Unknown

* Merge branch &#39;development&#39; ([`5abe89a`](https://github.com/fhempy/fhempy/commit/5abe89a4bc1ee7f4048b9d2141222597d24d32ff))


## v0.1.150 (2021-10-21)

### Chore

* chore: update controls ([`10df7d2`](https://github.com/fhempy/fhempy/commit/10df7d2a67e4726640c272b012757652cfc7825d))

### Fix

* fix(meross): fix open/close ([`63e25bd`](https://github.com/fhempy/fhempy/commit/63e25bdda3adcb54ee75109601a52e0fee3219b4))

* fix(esphome): fix weblink creation ([`60ebbcf`](https://github.com/fhempy/fhempy/commit/60ebbcf2896802410dd5b1f8c2b6d96cef2bddae))

### Unknown

* Merge branch &#39;development&#39; ([`391973b`](https://github.com/fhempy/fhempy/commit/391973b36edc0b52a6cb656c83541c61976acc13))


## v0.1.149 (2021-10-21)

### Chore

* chore: update controls ([`772c654`](https://github.com/fhempy/fhempy/commit/772c654a5c24a97f5f272f1f7509c5d9426aba38))

### Feature

* feat(erelax_vaillant): add duration for temp ([`d96f897`](https://github.com/fhempy/fhempy/commit/d96f897a18b29bb03af3838869b710aa996968ae))

* feat(esphome): add install link ([`6a22557`](https://github.com/fhempy/fhempy/commit/6a225570b39d201f670061cbe96b288ad0fdd99b))

* feat(meross): support garage opener ([`dd4136e`](https://github.com/fhempy/fhempy/commit/dd4136e3ded61788242771ddd70fe37cfaff2e8e))

### Fix

* fix(fhempy): make installation easier on debian 11 ([`6857d47`](https://github.com/fhempy/fhempy/commit/6857d475dd67cba27fdf074949e87741fadcc4e2))

### Unknown

* Merge branch &#39;development&#39; ([`725d06f`](https://github.com/fhempy/fhempy/commit/725d06fbde4a2cbb541b94530346ff38fea8f2d9))


## v0.1.148 (2021-10-17)

### Chore

* chore: update controls ([`7636dc2`](https://github.com/fhempy/fhempy/commit/7636dc2b30b759867958aa7ee20b46ac9d71d7f7))

### Fix

* fix(esphome): fix path again ([`d35b0af`](https://github.com/fhempy/fhempy/commit/d35b0af64b8a2603385f9bc499c40fd549d18c89))

### Unknown

* Merge branch &#39;development&#39; ([`5cfda1b`](https://github.com/fhempy/fhempy/commit/5cfda1b934771ce66f461ccc2610ed0a1487cf09))


## v0.1.147 (2021-10-16)

### Chore

* chore: update controls ([`9a95963`](https://github.com/fhempy/fhempy/commit/9a9596356caac7fbb5a614b4c9c6d173326f5725))

### Fix

* fix(esphome): revert path change ([`7452ebb`](https://github.com/fhempy/fhempy/commit/7452ebb20fa012bda4a6a52bc955e20cf7dd24b1))

### Unknown

* Merge branch &#39;development&#39; ([`5cdc924`](https://github.com/fhempy/fhempy/commit/5cdc9246513708a5e26d3cbd06e31b7049af970f))


## v0.1.146 (2021-10-16)

### Chore

* chore: update controls ([`4d8be12`](https://github.com/fhempy/fhempy/commit/4d8be12a366332383a06bb09c599d7c3d10d58df))

### Fix

* fix(googlecast): fix circular import ([`6d705de`](https://github.com/fhempy/fhempy/commit/6d705def909adef171a8d461d10ea5cbf9a44a8a))

* fix(esphome): update library ([`56af685`](https://github.com/fhempy/fhempy/commit/56af685dba0cf25c362a3dd320acc8ae795695e4))

* fix(esphome): set path for esphome ([`5b80c65`](https://github.com/fhempy/fhempy/commit/5b80c65b4ffcb3acbeca3dff2725f980b2cfa34d))

### Unknown

* Merge branch &#39;development&#39; ([`b9b3f80`](https://github.com/fhempy/fhempy/commit/b9b3f8015854a953c172eaa4c46cac28c921b121))


## v0.1.145 (2021-10-13)

### Chore

* chore: update controls ([`7647557`](https://github.com/fhempy/fhempy/commit/764755777c26bc5161bd535ca8c236acfe88f84d))

### Fix

* fix(fhempy): fix circular imports ([`6feb2e9`](https://github.com/fhempy/fhempy/commit/6feb2e9641f0122402f6840030fc1b0a41d7b1ef))

### Unknown

* Merge branch &#39;development&#39; ([`f6f8991`](https://github.com/fhempy/fhempy/commit/f6f899181d0113e08bc4b1f7614442660c05d0bd))


## v0.1.144 (2021-10-13)

### Chore

* chore: update controls ([`249c4c0`](https://github.com/fhempy/fhempy/commit/249c4c0e3b005f5800f0accd62a7b2dca0df0525))

### Fix

* fix(tuya_cloud): change info to debug ([`55b5ed5`](https://github.com/fhempy/fhempy/commit/55b5ed5aea41c94fc97ab5ac6edd6692c98415bf))

### Unknown

* Merge branch &#39;development&#39; ([`91ccf74`](https://github.com/fhempy/fhempy/commit/91ccf7487eb93d090059e8d023bab07441a36074))


## v0.1.143 (2021-10-13)

### Chore

* chore: update controls ([`eb6d5aa`](https://github.com/fhempy/fhempy/commit/eb6d5aa61185320dce534e9cfc51d111daf8085d))

### Fix

* fix(fhempy): better logging ([`38337ea`](https://github.com/fhempy/fhempy/commit/38337ea15575c56cc3cb3d4edad2e6050e1413f3))

* fix(fhempy): fix fhempyServer module ([`c969a27`](https://github.com/fhempy/fhempy/commit/c969a279c2ee1ba0b60afac96091695d72d9a243))

* fix(fhempy): fix fhem help ([`220bf15`](https://github.com/fhempy/fhempy/commit/220bf1544dee7103dc40b5afdc6bd0f93d945ee0))

### Unknown

* Merge branch &#39;development&#39; ([`e6036cc`](https://github.com/fhempy/fhempy/commit/e6036cc5ff3ae9553402e6c5be70220810c52d0f))


## v0.1.142 (2021-10-13)

### Chore

* chore: update controls ([`9b6a2df`](https://github.com/fhempy/fhempy/commit/9b6a2dfe95e5fb052bcae95debebaa410d0a722f))

### Fix

* fix(fhempy): revert websockets change ([`4c4bf7e`](https://github.com/fhempy/fhempy/commit/4c4bf7e27f286cf1f794a0b4c41f142b7de95612))

### Unknown

* Merge branch &#39;development&#39; ([`8c879d7`](https://github.com/fhempy/fhempy/commit/8c879d7fa7f66f1d9d352480b90322fed3b7285d))


## v0.1.141 (2021-10-13)

### Chore

* chore: update controls ([`e42e8e3`](https://github.com/fhempy/fhempy/commit/e42e8e38c44cfdbe69fdc8e15fd635783291b438))

### Fix

* fix(eq3bt): fix circular import ([`0ffe738`](https://github.com/fhempy/fhempy/commit/0ffe7383c645ceecfa7d4411437a8f009245e9a9))

### Unknown

* Merge branch &#39;development&#39; ([`499302a`](https://github.com/fhempy/fhempy/commit/499302ae907f94ea6b397ae9d06e75746db799c5))


## v0.1.140 (2021-10-13)

### Chore

* chore: update controls ([`fe7303d`](https://github.com/fhempy/fhempy/commit/fe7303df768fa542c04470a551fa26d4d5ca2650))

### Fix

* fix(fhempy): do not use legacy websockets ([`c5ea3c1`](https://github.com/fhempy/fhempy/commit/c5ea3c1e1969058a03f71314598491477c5f4b79))

### Unknown

* Merge branch &#39;development&#39; ([`c38bbba`](https://github.com/fhempy/fhempy/commit/c38bbbabc851f8caa9c25e56c2321d678d350664))


## v0.1.139 (2021-10-13)

### Chore

* chore: update controls ([`841f3ce`](https://github.com/fhempy/fhempy/commit/841f3ce04a7fda8444b4869dfd48b5534256a741))

* chore: add markdown ([`58a0e45`](https://github.com/fhempy/fhempy/commit/58a0e455e4d5baa754a66ff20f8eb7f1ca11739c))

### Fix

* fix(xiaomi_gateway3): update readme ([`541d941`](https://github.com/fhempy/fhempy/commit/541d941f5f0a08b9c5e5f04e2bd3dba4e41e3a6f))

* fix(fhempy): reducing &gt;100ms &#34;blocking&#34; ([`a4d2799`](https://github.com/fhempy/fhempy/commit/a4d27996c83ae197145b5ebd1dbcace3f90b2471))

### Unknown

* Merge branch &#39;development&#39; ([`b373a10`](https://github.com/fhempy/fhempy/commit/b373a107b613c5bb923118ef74f3633239f2ab8e))


## v0.1.138 (2021-10-13)

### Chore

* chore: update controls ([`493f86d`](https://github.com/fhempy/fhempy/commit/493f86dc2788a4a94317e4bb9387a381656d94d4))

### Feature

* feat(fhempy): use readme as help in fhem ([`faf245f`](https://github.com/fhempy/fhempy/commit/faf245f403af6da5d752a2ebce248bb2d3d0c212))

### Fix

* fix(xiaomi_gateway3): fix circular import ([`d9402b9`](https://github.com/fhempy/fhempy/commit/d9402b9e4d3554ac15532351e15b684f081f42ca))

### Unknown

* Merge branch &#39;development&#39; ([`f103773`](https://github.com/fhempy/fhempy/commit/f1037736ee6adc03a197bd41c723d065755d5a0b))


## v0.1.137 (2021-10-12)

### Chore

* chore: update controls ([`c041fb9`](https://github.com/fhempy/fhempy/commit/c041fb9df4ba93aa36f49c3cfda01ab3053d8372))

### Fix

* fix(fhempy): fix no response ([`a2656a0`](https://github.com/fhempy/fhempy/commit/a2656a0e0c00260e299e0593751fd22f503d67bc))

### Unknown

* Merge branch &#39;development&#39; ([`b19c271`](https://github.com/fhempy/fhempy/commit/b19c2715f1eb77d5aee5fa24d7e08d9f15101a38))


## v0.1.136 (2021-10-11)

### Chore

* chore: update controls ([`5ddb39d`](https://github.com/fhempy/fhempy/commit/5ddb39d89832deb1ef0048074f9bb07a973adcb6))

### Fix

* fix(fhempy): fix tests ([`8cd8c71`](https://github.com/fhempy/fhempy/commit/8cd8c7116eab1c0e53f55413c4e82bacb7eaa324))

### Unknown

* Merge branch &#39;development&#39; ([`f164388`](https://github.com/fhempy/fhempy/commit/f164388867dfaf9b41bf04f59e389a12ceb1e9a7))


## v0.1.135 (2021-10-11)

### Chore

* chore: update controls ([`af1f4ee`](https://github.com/fhempy/fhempy/commit/af1f4ee466e069b9db2b1bdb9cb630018792a7f2))

### Fix

* fix(fhempy): fix tests for 3.7 ([`c620d09`](https://github.com/fhempy/fhempy/commit/c620d0992acd3e94b309b9bda493e92775abf30f))

### Unknown

* Merge branch &#39;development&#39; ([`5c066b4`](https://github.com/fhempy/fhempy/commit/5c066b49ce52cd2bb735ec27226622a0eb11fc74))


## v0.1.134 (2021-10-11)

### Chore

* chore: update controls ([`ee0068a`](https://github.com/fhempy/fhempy/commit/ee0068ad00bc176470559b00aec80540310b2078))

* chore: update controls ([`27c2b9e`](https://github.com/fhempy/fhempy/commit/27c2b9e26b96cb2cd02810cbb02b908cca42c75d))

* chore: update controls ([`55c98f7`](https://github.com/fhempy/fhempy/commit/55c98f7409fef5f8961d67d7812415a6b15618cb))

### Fix

* fix(fhempy): fix version ([`ed0159d`](https://github.com/fhempy/fhempy/commit/ed0159da60a40da8077cee4cf77855965084062a))

* fix(fhempy): add 3.8,3.9 tests ([`d06989d`](https://github.com/fhempy/fhempy/commit/d06989d3bd9aa713cb8eea87c163aa9471be0ae0))

* fix(fhempy): update requirements ([`3dd10df`](https://github.com/fhempy/fhempy/commit/3dd10dfa1e86c88c3b68aa1b8a3d89f15aaf553b))

* fix(fhempy): fix tests ([`b1e68a8`](https://github.com/fhempy/fhempy/commit/b1e68a88ff25565a63c89b45a9a550fd45434d26))

* fix(fhempy): fix pythontype handling ([`8c43843`](https://github.com/fhempy/fhempy/commit/8c4384324501b03fdbeb712bacf0ca1fa773800f))

* fix(object_detection): update lib ([`8273a31`](https://github.com/fhempy/fhempy/commit/8273a314ed001c7b54ff324f3831be389bc09e1d))

### Unknown

* Merge branch &#39;development&#39; ([`60f0d70`](https://github.com/fhempy/fhempy/commit/60f0d7029b4015f6ae7f8dceb0413fe2104d96e9))


## v0.1.133 (2021-10-11)

### Chore

* chore: update controls ([`8a57e41`](https://github.com/fhempy/fhempy/commit/8a57e4165d2dd0700054121b4eb37c93f655ffa3))

### Fix

* fix(fhempy): rename to fhempy ([`3ee719c`](https://github.com/fhempy/fhempy/commit/3ee719c336ba7ddb834ecd236e4e66961c6cb7d7))

* fix(fhempy): rename to fhempy ([`74442ea`](https://github.com/fhempy/fhempy/commit/74442ea9c4c03e748e4734df95ae6c4c93ef72ce))

### Unknown

* Merge branch &#39;development&#39; ([`83aa2c5`](https://github.com/fhempy/fhempy/commit/83aa2c513589138927b8724b353587150d6cee33))


## v0.1.132 (2021-10-11)

### Chore

* chore: update controls ([`1cac9ea`](https://github.com/fhempy/fhempy/commit/1cac9ea509bacb31a9cfb6a600edd11c3d6d4adc))

### Fix

* fix(fhempy): rename to fhempy ([`53c68c0`](https://github.com/fhempy/fhempy/commit/53c68c0f95b584ade1d6283a8208295f8e5038be))

* fix(fhempy): rename to fhempy ([`7aac6cb`](https://github.com/fhempy/fhempy/commit/7aac6cb07e8195835c5b28b5227caeaa8b7fa81d))

* fix(fhempy): rename to fhempy ([`058ba5f`](https://github.com/fhempy/fhempy/commit/058ba5f385c90a6ae79a27f575fcd90390af4448))

* fix(fhempy): rename to fhempy ([`11e8f99`](https://github.com/fhempy/fhempy/commit/11e8f99f033481a4bd44e58007831d9036d823f2))

* fix(miio): update miio lib ([`32cbc78`](https://github.com/fhempy/fhempy/commit/32cbc78d21326edc760425c32727ddea5f7a380b))

* fix(fhempy): update zeroconf lib ([`40eefeb`](https://github.com/fhempy/fhempy/commit/40eefebec873f5ebba506bbd0aa9bb47f73db44c))

### Unknown

* Merge branch &#39;development&#39; ([`0ca9155`](https://github.com/fhempy/fhempy/commit/0ca9155ee02e651957d7c898afe9b6a02c8b3ae1))


## v0.1.131 (2021-10-10)

### Chore

* chore: update controls ([`b633b62`](https://github.com/fhempy/fhempy/commit/b633b622c527cef70e6078ecfc2325fa4ea5d189))

### Feature

* feat(seatconnect): Bugfixing (#39) ([`a5996f5`](https://github.com/fhempy/fhempy/commit/a5996f557c12ce4a7390faee31d0cbaeb05dbe71))

* feat(fhempy): add new devices to room/group ([`c197110`](https://github.com/fhempy/fhempy/commit/c197110a26df50acea79ae9abdac7832ac0182f6))

### Fix

* fix(tuya_cloud): better error handling ([`056ab5c`](https://github.com/fhempy/fhempy/commit/056ab5c4c5583f490c17b7d007b347f1d08ca2a4))

* fix(xiaomi_gateway3): fix attr usage ([`eb1f4b1`](https://github.com/fhempy/fhempy/commit/eb1f4b180944d28697fd49a0c4b7be5730d9e326))

* fix(fhempy): flake8 fixes ([`519658c`](https://github.com/fhempy/fhempy/commit/519658ccbad6ebc9c8eb27f4dc9025913f7fdb4f))

### Unknown

* Merge branch &#39;development&#39; ([`4b5652b`](https://github.com/fhempy/fhempy/commit/4b5652b770f257c9436838d10d43734aecf30a8c))


## v0.1.130 (2021-10-08)

### Chore

* chore: update controls ([`006eaac`](https://github.com/fhempy/fhempy/commit/006eaac232342f179c2b4c4a1b0746970a74af80))

### Unknown

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhempy ([`87a16ad`](https://github.com/fhempy/fhempy/commit/87a16ad3c49f9e7d670980ccc2287785edc53d7c))


## v0.1.129 (2021-10-08)

### Chore

* chore: update controls ([`c16b02d`](https://github.com/fhempy/fhempy/commit/c16b02d240638078ce1a846b0efc053e229bf6ab))

### Feature

* feat(seatconnect): Integration of Timer Schedule for Climatisation (#38)

* First Version of seatconnect

* Bug Climatisation and first integration of Timer

* seprated schedule timer

* added climatisation description

* timer configuration formated

* climatisation temp from int to float ([`f3a130d`](https://github.com/fhempy/fhempy/commit/f3a130d92948ce9eaa5cb65c61ce7e68c7049251))

### Fix

* fix(xiaomi_gateway3): small fixes ([`d96bbc8`](https://github.com/fhempy/fhempy/commit/d96bbc849c24fb275e8bc3e3f3b0095f81464ccc))

### Unknown

* Merge branch &#39;development&#39; ([`7987439`](https://github.com/fhempy/fhempy/commit/798743949816ec13cc65e707f3644bd63db3cae9))


## v0.1.128 (2021-10-07)

### Chore

* chore: update controls ([`71e280d`](https://github.com/fhempy/fhempy/commit/71e280dacebc377218dacb715bf05c0eb60a851a))

### Fix

* fix(xiaomi_gateway3): fix gateway device ([`24f0b13`](https://github.com/fhempy/fhempy/commit/24f0b13aa29f557ec3ccee32e78c18fc03a619ef))

### Unknown

* Merge branch &#39;development&#39; ([`ff13cce`](https://github.com/fhempy/fhempy/commit/ff13ccee1cc4d6cdc69da8770fafcbd3d6786e60))


## v0.1.127 (2021-10-07)

### Chore

* chore: update controls ([`f051427`](https://github.com/fhempy/fhempy/commit/f0514276d6b13b26b12e810cbf75685cd5cfcef4))

### Feature

* feat(xiaomi_gateway3): update xg3 library ([`62352da`](https://github.com/fhempy/fhempy/commit/62352da7581f1f338d34078ebfc2822fd38e217a))

### Fix

* fix(fhempy): better error handling ([`5910b6a`](https://github.com/fhempy/fhempy/commit/5910b6ae1fe3a6ea2e2cb97cdcf45ba782a25024))

### Unknown

* Merge branch &#39;development&#39; ([`ae267c7`](https://github.com/fhempy/fhempy/commit/ae267c72e58cc152307ba570badc5b8cf928ddea))


## v0.1.126 (2021-09-30)

### Chore

* chore: update controls ([`b96b783`](https://github.com/fhempy/fhempy/commit/b96b783e3b5a2f5bcfe125c1c992e5f85aad2248))

### Fix

* fix(fhempy): update requirements ([`f327a5a`](https://github.com/fhempy/fhempy/commit/f327a5a5e5abd3393c336743a376618d5136176a))

### Unknown

* Merge branch &#39;development&#39; ([`c2f5ae6`](https://github.com/fhempy/fhempy/commit/c2f5ae6a776dd006048275122e09844ca8330a31))


## v0.1.125 (2021-09-30)

### Chore

* chore: update controls ([`ae0d620`](https://github.com/fhempy/fhempy/commit/ae0d6205e3becbfbc3f089f3ef05cf22e44817d9))

### Fix

* fix(tuya_cloud): fix rgb readings ([`5257ff2`](https://github.com/fhempy/fhempy/commit/5257ff2428219e75767b4f756734d7dbf1982bbf))

* fix(meross): add usage ([`ccd7a4c`](https://github.com/fhempy/fhempy/commit/ccd7a4cd9b84573fbc472a024c0e1854fb509038))

### Unknown

* Merge branch &#39;development&#39; ([`e7c3f50`](https://github.com/fhempy/fhempy/commit/e7c3f507e5d5275822cbf2331eabec42d4c4d7b8))


## v0.1.124 (2021-09-29)

### Chore

* chore: update controls ([`b1da53f`](https://github.com/fhempy/fhempy/commit/b1da53fa2a253da511bc1289dc8e6e5044cacc95))

* chore: add tuya_cloud recommandation ([`cc8dfb8`](https://github.com/fhempy/fhempy/commit/cc8dfb85a08e052d240ba20cfe8424af42dca529))

### Feature

* feat(meross): support meross on/off ([`d08c927`](https://github.com/fhempy/fhempy/commit/d08c927361771164d8dc7665e0687fdc3420e777))

* feat(fhempy): add gen_fhemdev_name fct ([`6cf9829`](https://github.com/fhempy/fhempy/commit/6cf9829124d6c3f759360b176be34510b319b7c7))

### Fix

* fix(fhempy): add exception handling ([`bcaaf97`](https://github.com/fhempy/fhempy/commit/bcaaf970f4b0f2e239bba52fe7c136f92c95218c))

* fix(tuya_cloud): handle stop() exceptions ([`8bb081a`](https://github.com/fhempy/fhempy/commit/8bb081aa46f55a98a3900fc062b77fdd8369c16f))

### Unknown

* Merge branch &#39;development&#39; ([`569d066`](https://github.com/fhempy/fhempy/commit/569d0661734791ca4e97e53a8aa323e894d07998))


## v0.1.123 (2021-09-28)

### Chore

* chore: update controls ([`0c970ec`](https://github.com/fhempy/fhempy/commit/0c970ec0ac5af4a86b649f91753e048559834bae))

### Fix

* fix(tuya_cloud): fix devnames with dashes ([`54e2f7c`](https://github.com/fhempy/fhempy/commit/54e2f7cb1de5f8bc844eb18f4332fbbbb8c7151d))

### Unknown

* Merge branch &#39;development&#39; ([`827a5cb`](https://github.com/fhempy/fhempy/commit/827a5cbaf2d4e7b4e213b7cb20e66a275f35ef9b))


## v0.1.122 (2021-09-28)

### Chore

* chore: update controls ([`909cfe4`](https://github.com/fhempy/fhempy/commit/909cfe4e0d2fbaf40c420bc4024ba97bfe9f0702))

### Unknown

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhempy ([`1ef0785`](https://github.com/fhempy/fhempy/commit/1ef07859ba58dc8daf789196b3eae9a453819985))


## v0.1.121 (2021-09-28)

### Chore

* chore: update controls ([`07ceb34`](https://github.com/fhempy/fhempy/commit/07ceb34f90f46a54e5f8577cd5eaee3fa8440d4a))

### Feature

* feat(seatconnect): First Version of seatconnect (#35) ([`124f715`](https://github.com/fhempy/fhempy/commit/124f71588f3bd54e20118baf37029760809cdfe8))


## v0.1.120 (2021-09-22)

### Chore

* chore: update controls ([`a889cf8`](https://github.com/fhempy/fhempy/commit/a889cf818495a33f19b40888bbd792e5b92e4c0c))

### Fix

* fix(fhempy): handle zeroconf exceptions ([`eebf78f`](https://github.com/fhempy/fhempy/commit/eebf78f761909ded5228cb0e32e99a89bd7cbeab))

### Unknown

* Merge branch &#39;development&#39; ([`5c8ea32`](https://github.com/fhempy/fhempy/commit/5c8ea32486755dcf5c5996aab73136b2fc6e9867))


## v0.1.119 (2021-09-20)

### Chore

* chore: update controls ([`3cf277c`](https://github.com/fhempy/fhempy/commit/3cf277c3027e510192d0080954e75d45ca4ce662))

### Fix

* fix(fhempy): add debug output ([`3b09a35`](https://github.com/fhempy/fhempy/commit/3b09a351db8851dfc5b34b684768d093e1a8ba45))

### Unknown

* Merge branch &#39;development&#39; ([`427bc50`](https://github.com/fhempy/fhempy/commit/427bc50b76e058b52b2363c39ad687460839af2e))


## v0.1.118 (2021-09-19)

### Chore

* chore: update controls ([`3e66626`](https://github.com/fhempy/fhempy/commit/3e666267244babe388ab8c68da724ebd6b312560))

### Fix

* fix(tuya_cloud): support devices with umlauts ([`df937dc`](https://github.com/fhempy/fhempy/commit/df937dc0c9298ac0dea0a795510ea14330b0b2d9))

* fix(discover_mdns): use async zeroconf ([`6ad6445`](https://github.com/fhempy/fhempy/commit/6ad6445e202e5cbe0a486b2701a775b6b32d599d))

### Unknown

* Merge branch &#39;development&#39; ([`13ac65e`](https://github.com/fhempy/fhempy/commit/13ac65e626745c05698c48ba380009f095628b84))


## v0.1.117 (2021-09-08)

### Chore

* chore: update controls ([`df3c3f7`](https://github.com/fhempy/fhempy/commit/df3c3f76be35524603e55ab1865cdba87ba79ee3))

### Fix

* fix(fhempy): fix release script ([`de82f89`](https://github.com/fhempy/fhempy/commit/de82f891c300feda26bc35168119293a520991f6))

### Unknown

* Merge branch &#39;development&#39; ([`412e267`](https://github.com/fhempy/fhempy/commit/412e267dfccff34ebeace361b99e61ad28dd102c))


## v0.1.116 (2021-09-07)

### Chore

* chore: update controls ([`a140b77`](https://github.com/fhempy/fhempy/commit/a140b77dafe0a1544fa3f7f82029437091cac710))

### Feature

* feat(skodaconnect): add honk and flash support ([`623c3d3`](https://github.com/fhempy/fhempy/commit/623c3d3bef608edfa0ed5c00f157e8f90fcc908d))

### Fix

* fix(skodaconnect): update lib to 1.1.4

update to latest lib with fix honkandflash and turn pheater off ([`192c4f3`](https://github.com/fhempy/fhempy/commit/192c4f3ac70b1b2ee33298f8d23d3aba7b025e79))

* fix(skodaconnect): update lib to 1.1.3 ([`ae47357`](https://github.com/fhempy/fhempy/commit/ae4735782c9d15a7a408de965b27bcdb422c1d23))

### Unknown

* Merge branch &#39;development&#39; ([`62c9277`](https://github.com/fhempy/fhempy/commit/62c9277517cc79331e06a83ba5d10efd2b224a7c))


## v0.1.115 (2021-09-05)

### Chore

* chore: update controls ([`2b47dd1`](https://github.com/fhempy/fhempy/commit/2b47dd1bf94babba90b31a680268db0ed4de139c))

* chore(admin): checkout development after release ([`75ae44a`](https://github.com/fhempy/fhempy/commit/75ae44a9edb6189c796173ac5f5720e3dd7d77f8))

### Fix

* fix(skodaconnect): update lib to 1.1.2 ([`a012022`](https://github.com/fhempy/fhempy/commit/a012022ae7ccb7c746df448d0b99975251fa25ce))

### Unknown

* Merge branch &#39;development&#39; ([`c5e3d3c`](https://github.com/fhempy/fhempy/commit/c5e3d3cbd4539fd0b075c7d30670baefeb05d484))


## v0.1.114 (2021-09-05)

### Chore

* chore: update controls ([`00fb5b1`](https://github.com/fhempy/fhempy/commit/00fb5b1a637895c8f6f7eec0526f2b03b3bed638))

### Fix

* fix(erelax_vaillant): set endtime 0 if not active ([`9103634`](https://github.com/fhempy/fhempy/commit/91036349b24ded901051833a79aecf920af23f0f))

### Unknown

* Merge branch &#39;development&#39; ([`4443173`](https://github.com/fhempy/fhempy/commit/44431735ad59344247aeff13d450e3aabca1fdc9))


## v0.1.113 (2021-09-05)

### Chore

* chore: update controls ([`a7feb25`](https://github.com/fhempy/fhempy/commit/a7feb25a961402c212dfef5235b410e8514689f7))

### Fix

* fix(erelax_vaillant): fix readings again ([`4fcb9d2`](https://github.com/fhempy/fhempy/commit/4fcb9d24c6deadbc1b622dc7dd9df4d26a6be645))

### Unknown

* Merge branch &#39;development&#39; ([`407dcd1`](https://github.com/fhempy/fhempy/commit/407dcd18eb7feed25efb1c81787027ce50c5fc2a))


## v0.1.112 (2021-09-05)

### Chore

* chore: update controls ([`29d0eaf`](https://github.com/fhempy/fhempy/commit/29d0eaf2c69244c6c6b5e76387183d3e73481555))

### Fix

* fix(erelax_vaillant): fix away/manual readings ([`ab0cc0c`](https://github.com/fhempy/fhempy/commit/ab0cc0ca69a24b66dbef4ff7343f11297588425f))

### Unknown

* Merge branch &#39;development&#39; ([`01e9b3b`](https://github.com/fhempy/fhempy/commit/01e9b3ba39e05a738ca63498c7a40417a086920c))


## v0.1.111 (2021-09-05)

### Chore

* chore: update controls ([`328c5d1`](https://github.com/fhempy/fhempy/commit/328c5d1643b8bb3e88282952c46a85f2b5f31550))

* chore(admin): update release script ([`02288bd`](https://github.com/fhempy/fhempy/commit/02288bd332219ffd6ae08613edd9f6b8dc95a7ab))

### Fix

* fix(erelax_vaillant): fix away/manual readings ([`31dfb46`](https://github.com/fhempy/fhempy/commit/31dfb464fc2a79121cbe0ea89a2e890954244f5c))

### Unknown

* Merge branch &#39;development&#39; ([`2b26625`](https://github.com/fhempy/fhempy/commit/2b266257060f098caaeb98de1d99ade7d2e775e7))


## v0.1.110 (2021-09-05)

### Chore

* chore: update controls ([`71d37e8`](https://github.com/fhempy/fhempy/commit/71d37e8de15ccdb46e68627982e2e1403703d8ad))

### Feature

* feat(erelax_vaillant): add away, manual readings ([`2e49418`](https://github.com/fhempy/fhempy/commit/2e494188b5e5c84603e2994bf4cb977b33b4c586))

### Unknown

* Merge branch &#39;development&#39; ([`26b42ec`](https://github.com/fhempy/fhempy/commit/26b42ece062d22e7bd828cee5e687cc0f518bdcc))


## v0.1.109 (2021-08-31)

### Chore

* chore: update controls ([`587a6e3`](https://github.com/fhempy/fhempy/commit/587a6e3fafff63c0a4fc5795e2f0e781c6888c74))

### Fix

* fix(tuya_cloud): fix reading updates ([`572c088`](https://github.com/fhempy/fhempy/commit/572c0880747a8535f9092f87cc12ee91e0910f6c))

### Unknown

* Merge branch &#39;development&#39; ([`3dae86d`](https://github.com/fhempy/fhempy/commit/3dae86dded554fb3f8ad10e7e9f004967e25a87f))


## v0.1.108 (2021-08-30)

### Chore

* chore: update controls ([`8f04a40`](https://github.com/fhempy/fhempy/commit/8f04a407cb87c273085b4ba9ae79dbd81234cb45))

### Fix

* fix(tuya_cloud): fix startup issues ([`a9c2e99`](https://github.com/fhempy/fhempy/commit/a9c2e99db2fd0730b95bb3a1dab5e8f853753ec1))

* fix(fhempy): fix github sec alert ([`6be1403`](https://github.com/fhempy/fhempy/commit/6be14039106babb653faa048336827e1719533bb))

### Unknown

* Merge branch &#39;development&#39; ([`8ad63a8`](https://github.com/fhempy/fhempy/commit/8ad63a80df63c5c3220a86a7b6c151aedb884e3c))


## v0.1.107 (2021-08-30)

### Chore

* chore: update controls ([`26c764e`](https://github.com/fhempy/fhempy/commit/26c764e3c382a81705806f1193bf8569f7e09d14))

### Fix

* fix(fhempy): update aiohttp library ([`f00540a`](https://github.com/fhempy/fhempy/commit/f00540abbc6daf6c8b8ba81772c3bef6769499fd))

* fix(skodaconnect): update library to 1.0.52 ([`f14583e`](https://github.com/fhempy/fhempy/commit/f14583ef3b6beb5032064aeb016fe0966238cbe8))

* fix(dlna_dmr): fix get_local_ip ([`e12f602`](https://github.com/fhempy/fhempy/commit/e12f60233cb5bd703d091a47bc21a3261d926331))

### Unknown

* Merge branch &#39;development&#39; ([`813e835`](https://github.com/fhempy/fhempy/commit/813e835a6249a6462fafd327edf039bbc864fc0e))


## v0.1.106 (2021-08-29)

### Chore

* chore: update controls ([`a05fe81`](https://github.com/fhempy/fhempy/commit/a05fe81fdf10b48b4e067aa9282e2109f9c482ad))

### Fix

* fix(tests): fix ring test ([`9098245`](https://github.com/fhempy/fhempy/commit/90982456484aec502ceeefe08c3a4be9e0ff9db4))

### Unknown

* Merge branch &#39;development&#39; ([`218cab6`](https://github.com/fhempy/fhempy/commit/218cab6af632a073bfda71eda3a29049c0ccfbda))


## v0.1.105 (2021-08-29)

### Chore

* chore: update controls ([`ba92c55`](https://github.com/fhempy/fhempy/commit/ba92c5557d0982d3712e4c24cca634ee6ae3a82e))

### Feature

* feat(upnp): update upnp library ([`f2c5120`](https://github.com/fhempy/fhempy/commit/f2c512079c665e8dd84c1efa288b08873cc98fed))

### Fix

* fix(fhempy): fix zeroconf exception ([`7ad2e73`](https://github.com/fhempy/fhempy/commit/7ad2e73c4140fa99ccac5a9a28fcc094fa890a61))

### Unknown

* Merge branch &#39;development&#39; ([`b35c24b`](https://github.com/fhempy/fhempy/commit/b35c24b5f734d5d397826aa6bf537f684616d042))


## v0.1.104 (2021-08-28)

### Chore

* chore: update controls ([`021610c`](https://github.com/fhempy/fhempy/commit/021610cfe8fa38a141db350d623c347d51e3af74))

### Feature

* feat(googlecast): update libraries (#25)

working with pychromecast==9.2.0 and youtube_dl&gt;=2021.06.06 tested. if spotify should work a modification must be made in base library controller spotify.py as followed:
```
&#34;&#34;&#34;
Controller to interface with Spotify.
&#34;&#34;&#34;
import logging
import threading
import requests
import json

from . import BaseController
from ..config import APP_SPOTIFY
from ..error import LaunchError

APP_NAMESPACE = &#34;urn:x-cast:com.spotify.chromecast.secure.v1&#34;
TYPE_GET_INFO = &#34;getInfo&#34;
TYPE_GET_INFO_RESPONSE = &#34;getInfoResponse&#34;
#TYPE_SET_CREDENTIALS = &#34;setCredentials&#34;
#TYPE_SET_CREDENTIALS_ERROR = &#34;setCredentialsError&#34;
#TYPE_SET_CREDENTIALS_RESPONSE = &#34;setCredentialsResponse&#34;
TYPE_ADD_USER = &#34;addUser&#34;
TYPE_ADD_USER_RESPONSE = &#34;addUserResponse&#34;
TYPE_ADD_USER_ERROR = &#34;addUserError&#34;

# pylint: disable=too-many-instance-attributes
class SpotifyController(BaseController):
    &#34;&#34;&#34;Controller to interact with Spotify namespace.&#34;&#34;&#34;

    def __init__(self, access_token=None, expires=None):
        super().__init__(APP_NAMESPACE, APP_SPOTIFY)

        self.logger = logging.getLogger(__name__)
        self.session_started = False
        self.access_token = access_token
        self.expires = expires
        self.is_launched = False
        self.device = None
        self.credential_error = False
        self.waiting = threading.Event()

    def receive_message(self, _message, data: dict):
        &#34;&#34;&#34;
        Handle the auth flow and active player selection.

        Called when a message is received.
        &#34;&#34;&#34;
        if data[&#34;type&#34;] == TYPE_GET_INFO_RESPONSE:
            self.device = data[&#34;payload&#34;][&#34;deviceID&#34;]
            self.client = data[&#34;payload&#34;][&#34;clientID&#34;]
            headers = {
                &#39;authority&#39;: &#39;spclient.wg.spotify.com&#39;,
                &#39;authorization&#39;: &#39;Bearer {}&#39;.format(self.access_token),
                &#39;content-type&#39;: &#39;text/plain;charset=UTF-8&#39;
            }

            request_body = json.dumps({&#39;clientId&#39;: self.client, &#39;deviceId&#39;: self.device})

            response = requests.post(&#39;https://spclient.wg.spotify.com/device-auth/v1/refresh&#39;, headers=headers, data=request_body)
            json_resp = response.json()
            self.send_message({
                &#34;type&#34;: TYPE_ADD_USER,
                &#34;payload&#34;: {
                    &#34;blob&#34;: json_resp[&#34;accessToken&#34;],
                    &#34;tokenType&#34;: &#34;accesstoken&#34;
                }
            })
        if data[&#34;type&#34;] == TYPE_ADD_USER_RESPONSE:
            self.is_launched = True
            self.waiting.set()

        if data[&#34;type&#34;] == TYPE_ADD_USER_ERROR:
            self.device = None
            self.credential_error = True
            self.waiting.set()
        return True

    def launch_app(self, timeout=10):
        &#34;&#34;&#34;
        Launch Spotify application.

        Will raise a LaunchError exception if there is no response from the
        Spotify app within timeout seconds.
        &#34;&#34;&#34;

        if self.access_token is None or self.expires is None:
            raise ValueError(&#34;access_token and expires cannot be empty&#34;)

        def callback():
            &#34;&#34;&#34;Callback function&#34;&#34;&#34;
            self.send_message({&#34;type&#34;: TYPE_GET_INFO, &#34;payload&#34;: {}})
            
        self.device = None
        self.credential_error = False
        self.waiting.clear()
        self.launch(callback_function=callback)

        counter = 0
        while counter &lt; (timeout + 1):
            if self.is_launched:
                return
            self.waiting.wait(1)
            counter += 1

        if not self.is_launched:
            raise LaunchError(
                &#34;Timeout when waiting for status response from Spotify app&#34;
            )

    # pylint: disable=too-many-locals
    def quick_play(self, **kwargs):
        &#34;&#34;&#34;
        Launches the spotify controller and returns when it&#39;s ready.
        To actually play media, another application using spotify connect is required.
        &#34;&#34;&#34;
        self.access_token = kwargs[&#34;access_token&#34;]
        self.expires = kwargs[&#34;expires&#34;]

        self.launch_app(timeout=20)
``` ([`856eeac`](https://github.com/fhempy/fhempy/commit/856eeac940659974458b323c6aa2d266a576040d))

* feat(ring): update library to 0.7.1 (#24)

Version 0.7.1 tested since release and workin with fhempy ([`9aa2360`](https://github.com/fhempy/fhempy/commit/9aa236079a81f483294be41e0a84a167b2ae5bed))

### Unknown

* Merge branch &#39;development&#39; ([`2f8eda6`](https://github.com/fhempy/fhempy/commit/2f8eda636206a87e2c0cc9774d181d8abd10ed0c))


## v0.1.103 (2021-08-28)

### Chore

* chore: update controls ([`94e39c5`](https://github.com/fhempy/fhempy/commit/94e39c5f318ed495bf60c31eb8674746c0541e74))

### Fix

* fix(fhempy): update requirements ([`02de53d`](https://github.com/fhempy/fhempy/commit/02de53de90b910c9a00a16267961869e5848ee41))

### Unknown

* Merge branch &#39;development&#39; ([`297ab4e`](https://github.com/fhempy/fhempy/commit/297ab4ef1f977973b01a423f20c69ad517737c03))


## v0.1.102 (2021-08-28)

### Chore

* chore: update controls ([`1f0f97e`](https://github.com/fhempy/fhempy/commit/1f0f97e2c1f2f554ed5c57da8d6ade1e1415db27))

### Feature

* feat(fhempy): update to asynczeroconf ([`7b319e3`](https://github.com/fhempy/fhempy/commit/7b319e347601634894c458c7ac2b3782b99dee5e))

### Fix

* fix(fhempy): better error handling ([`e4f2ba2`](https://github.com/fhempy/fhempy/commit/e4f2ba2a2d1c46b9bc767119ff4f4519e61ce724))

* fix(fhempy): rename to fhempy ([`38121ce`](https://github.com/fhempy/fhempy/commit/38121ce24260cf4dfd8291901c760008d6ee48e8))

### Unknown

* Merge branch &#39;development&#39; ([`dd20a3c`](https://github.com/fhempy/fhempy/commit/dd20a3ce0ee8b03328c9d314caffc0c3bac96643))


## v0.1.101 (2021-08-27)

### Chore

* chore: update controls ([`f0ca2cd`](https://github.com/fhempy/fhempy/commit/f0ca2cdb1284a09e9efe13436576a5c4ea742c9e))

### Fix

* fix(esphome): fix deprecation warning ([`49af229`](https://github.com/fhempy/fhempy/commit/49af2290a0527370857292c23bc51b9a9a522b2f))

* fix(fhempy): fix NO RESPONSE msgs ([`3413202`](https://github.com/fhempy/fhempy/commit/341320259b85f2d545c62cf898c060025181db5a))

* fix(fhempy): fix log ([`d3d11c4`](https://github.com/fhempy/fhempy/commit/d3d11c440c107fa21a871e331c7834add1e820ad))

### Unknown

* Merge branch &#39;development&#39; ([`d3f8e17`](https://github.com/fhempy/fhempy/commit/d3f8e17d1775733f8d01f520c411068afdfe9c75))


## v0.1.100 (2021-08-27)

### Chore

* chore: update controls ([`ae63614`](https://github.com/fhempy/fhempy/commit/ae636142b92b2a767c5070f905c57dda3e48c0ac))

### Fix

* fix(skodaconnect): update library ([`dc2035b`](https://github.com/fhempy/fhempy/commit/dc2035bb80810343eae441279ce52d1d1eddbbea))

* fix(tuya_cloud): update tuya lib ([`8059a68`](https://github.com/fhempy/fhempy/commit/8059a68023c693e0035bd163cdb6a393a53a63d4))

### Unknown

* Merge branch &#39;development&#39; ([`67a6de8`](https://github.com/fhempy/fhempy/commit/67a6de854dcdd646ed4ee459890a5c19735c1e18))


## v0.1.99 (2021-08-27)

### Chore

* chore: update controls ([`2dca780`](https://github.com/fhempy/fhempy/commit/2dca780fa40ef16163aad22c39029dbd2570c9f9))

### Fix

* fix(tuya_cloud): fix colour_data again ([`fd37524`](https://github.com/fhempy/fhempy/commit/fd37524f94bc30667b75849b1933e223d92df361))

### Unknown

* Merge branch &#39;development&#39; ([`ca0291e`](https://github.com/fhempy/fhempy/commit/ca0291ea3c02e99da1bdd1d938b4508c91c1ed27))


## v0.1.98 (2021-08-27)

### Chore

* chore: update controls ([`c4d1321`](https://github.com/fhempy/fhempy/commit/c4d1321d2c4a7f29f8b16a09e8237d784f38f19e))

### Fix

* fix(tuya_cloud): fix again colour_data ([`82998c7`](https://github.com/fhempy/fhempy/commit/82998c757357c9c9aee4fbc0b7c83ac8d9170cfb))

### Unknown

* Merge branch &#39;development&#39; ([`9530d6f`](https://github.com/fhempy/fhempy/commit/9530d6f4dfecf23ae15c1f1636f4fdbbf3479ac4))


## v0.1.97 (2021-08-26)

### Chore

* chore: update controls ([`c68b93c`](https://github.com/fhempy/fhempy/commit/c68b93c947910e7ef2216d0206efceb0d956591f))

* chore(googlecast): update play command ([`3a03191`](https://github.com/fhempy/fhempy/commit/3a031910a626d76d41ea91ea9da29122c61b59e7))

### Fix

* fix(tuya_cloud): handle exception on mqtt stop ([`de40876`](https://github.com/fhempy/fhempy/commit/de4087678f95429e9c86bf4ee3cd767f6836a326))

* fix(tuya_cloud): fix colour_data ([`c87c985`](https://github.com/fhempy/fhempy/commit/c87c9857c67b164cca75f87f5ff2b28fc284b5ac))

* fix(fhempy): add use Color ([`89c8264`](https://github.com/fhempy/fhempy/commit/89c8264adab1a2d788d73c0e1caaa438aa7af850))

### Unknown

* Merge branch &#39;development&#39; ([`fe4d2cf`](https://github.com/fhempy/fhempy/commit/fe4d2cf02b6a1a9b27772b44b4520ca328fcb08b))


## v0.1.96 (2021-08-26)

### Chore

* chore: update controls ([`554f5c2`](https://github.com/fhempy/fhempy/commit/554f5c225333f0566540a40e7efefb41b5f6beb7))

### Fix

* fix(tuya_cloud): fix colour_data ([`b46189c`](https://github.com/fhempy/fhempy/commit/b46189c60d0f0e58797b2dd0e8024ddfd97a66f8))

### Unknown

* Merge branch &#39;development&#39; ([`e44c9ad`](https://github.com/fhempy/fhempy/commit/e44c9ad3b62df3ae90712d74462ba01d3547c422))


## v0.1.95 (2021-08-26)

### Chore

* chore: update controls ([`3f4ef0f`](https://github.com/fhempy/fhempy/commit/3f4ef0f90f8251830297709dc98f5817fb6e677d))

### Feature

* feat(tuya_cloud): support colorpicker ([`fbef95d`](https://github.com/fhempy/fhempy/commit/fbef95d49466342270833adb428b466312ef372c))

### Unknown

* Merge branch &#39;development&#39; ([`99d68e6`](https://github.com/fhempy/fhempy/commit/99d68e653ee96972f4f90bd14cfc154b7e9dd6c8))


## v0.1.94 (2021-08-25)

### Chore

* chore: update controls ([`6f7a40f`](https://github.com/fhempy/fhempy/commit/6f7a40f6ab34eabc9e452bb5db351099c2d60e2d))

### Fix

* fix(mitemp): latest mitemp lib not working ([`9e2dcfc`](https://github.com/fhempy/fhempy/commit/9e2dcfc092d9102248bc8b4ef28c340505d5fc46))

### Unknown

* Merge branch &#39;development&#39; ([`2e07c88`](https://github.com/fhempy/fhempy/commit/2e07c8825cecc3e8e391ee423e59f343e262fca4))


## v0.1.93 (2021-08-25)

### Chore

* chore: update controls ([`0f84541`](https://github.com/fhempy/fhempy/commit/0f84541d908494afb67cedd1681f888e6c65d855))

### Fix

* fix(tuya_cloud): fix reset_reading ([`48410ec`](https://github.com/fhempy/fhempy/commit/48410ecfbe89b1c0310e83c4676c9407900551ad))

* fix(mitemp): update library ([`6919917`](https://github.com/fhempy/fhempy/commit/691991759cbc9909ede6aa44b23c030d9350d234))

### Unknown

* Merge branch &#39;development&#39; ([`e79a62d`](https://github.com/fhempy/fhempy/commit/e79a62d71b97efc6c98490310ea25d4e8246c292))


## v0.1.92 (2021-08-25)

### Chore

* chore: update controls ([`fe4c0d5`](https://github.com/fhempy/fhempy/commit/fe4c0d54efdc04cfa0ffb820cdbb652f7a96870c))

* chore(fhempy): show downloads per month ([`5173340`](https://github.com/fhempy/fhempy/commit/5173340eead9c680e59ee267a404997971819b1d))

### Feature

* feat(tuya_cloud): set state for some devices ([`de4f07a`](https://github.com/fhempy/fhempy/commit/de4f07a9d47c19c536464670081ef5f80f3789cf))

* feat(miflora): change conductivity to fertility ([`6d27f47`](https://github.com/fhempy/fhempy/commit/6d27f47f196c889c0c80cbaf0f5fcf2af0c2ae51))

* feat(tuya_cloud): use switch_led for state ([`a5f7e65`](https://github.com/fhempy/fhempy/commit/a5f7e659af1ba32ae9f15567f061122a6312c22c))

### Fix

* fix(fhempy): fix room for fhempy log ([`9662148`](https://github.com/fhempy/fhempy/commit/966214849c577e085dd3e796bb4ba71a7367a721))

### Unknown

* Merge branch &#39;development&#39; ([`b8989bf`](https://github.com/fhempy/fhempy/commit/b8989bf26106fdd6e7a7ddf6a6161471c3f52517))


## v0.1.91 (2021-08-23)

### Chore

* chore: update controls ([`3b3a7fa`](https://github.com/fhempy/fhempy/commit/3b3a7faea979ded5d2afcdfeabeb3a6e2a1ad487))

### Fix

* fix(tuya_cloud): fix set_json ([`246584f`](https://github.com/fhempy/fhempy/commit/246584fc1fd7adc6d4743e6dc9be9c43c8a28498))

* fix(skodaconnect): fix climater with new library ([`bdc8058`](https://github.com/fhempy/fhempy/commit/bdc8058c2d759454e6919b16d04aa36238de1d2e))

### Unknown

* Merge branch &#39;development&#39; ([`07e1063`](https://github.com/fhempy/fhempy/commit/07e1063cd048ea27e2b7d69e2e77ea557ff948a5))


## v0.1.90 (2021-08-23)

### Chore

* chore: update controls ([`d2fe795`](https://github.com/fhempy/fhempy/commit/d2fe7951c73e356f3134cb1a147c02a73715d1e3))

* chore: fix namings ([`e6f986b`](https://github.com/fhempy/fhempy/commit/e6f986b38e5f2471b95a2eaeb4ead6646342ea45))

### Unknown

* Merge branch &#39;development&#39; ([`ace14b4`](https://github.com/fhempy/fhempy/commit/ace14b4fb03de95ee6381298399c8896888c490b))


## v0.1.89 (2021-08-23)

### Chore

* chore: update controls ([`551440b`](https://github.com/fhempy/fhempy/commit/551440bc5f61724584865a6e89505386a491ce58))

### Feature

* feat(tuya_cloud): support json commands ([`fdc9170`](https://github.com/fhempy/fhempy/commit/fdc9170129fb0d45298eb9d3d323169fdba857a0))

### Fix

* fix(skodaconnect): fix climatisation ([`1870427`](https://github.com/fhempy/fhempy/commit/18704278f393203e487899b79ca6fe2b7b065745))

### Unknown

* Merge branch &#39;development&#39; ([`8c855c9`](https://github.com/fhempy/fhempy/commit/8c855c9d8be2f8a3cfcb7ad5d0340c01a8206a0b))


## v0.1.88 (2021-08-22)

### Chore

* chore: update controls ([`0d7594f`](https://github.com/fhempy/fhempy/commit/0d7594f2e5a94df737357144c79b7043719f59ad))

* chore: add git to apt installation ([`7139cea`](https://github.com/fhempy/fhempy/commit/7139cea69debcfe74bb06b1b8879169ac363e51b))

### Fix

* fix(skodaconnect): fix climatisation ([`527214f`](https://github.com/fhempy/fhempy/commit/527214fa5be15a7ba52b726472f1900b43262f61))

### Unknown

* Merge branch &#39;development&#39; ([`afb7912`](https://github.com/fhempy/fhempy/commit/afb79128b3858cd8ba189b3b4b66a2b47480aeba))


## v0.1.87 (2021-08-17)

### Chore

* chore: update controls ([`10f2b37`](https://github.com/fhempy/fhempy/commit/10f2b37e99ab35a901a3afeaf8473a99aa346c0d))

### Fix

* fix(xiaomi_gateway3): fix reading updates ([`d8a7ff0`](https://github.com/fhempy/fhempy/commit/d8a7ff04545b8411c0692df3f5d42cf44f14bec8))

### Unknown

* Merge branch &#39;development&#39; ([`a822427`](https://github.com/fhempy/fhempy/commit/a8224271372699fcc5318e0a2219a43f5009b3cb))


## v0.1.86 (2021-08-16)

### Chore

* chore: update controls ([`171d05f`](https://github.com/fhempy/fhempy/commit/171d05fecdc1000a865aabde9b7b940714d5139c))

### Fix

* fix(tuya_cloud): fix reading updates ([`54a1259`](https://github.com/fhempy/fhempy/commit/54a12595ec52bb6bb13a6619a77e26d16b161654))

### Unknown

* Merge branch &#39;development&#39; ([`363380c`](https://github.com/fhempy/fhempy/commit/363380c0bbfb0aeeeb0c400b32be0b717c62be21))


## v0.1.85 (2021-08-16)

### Chore

* chore: update controls ([`d87c1e7`](https://github.com/fhempy/fhempy/commit/d87c1e7d5f0f7f4d9a26166253bcf01c73b86300))

### Fix

* fix(skodaconnect): fix update readings (#21)

Fix Error:
Traceback (most recent call last):
  File &#34;/opt/fhem/.local/lib/python3.7/site-packages/fhempy/lib/skodaconnect/skodaconnect.py&#34;, line 243, in update_readings_once
    if self._update_readings == &#34;always&#34;:
AttributeError: &#39;skodaconnect&#39; object has no attribute &#39;_update_readings&#39; ([`cd0aef9`](https://github.com/fhempy/fhempy/commit/cd0aef9dec0350570b9b6667e356db53216e631e))

### Unknown

* Merge branch &#39;development&#39; ([`edb2c48`](https://github.com/fhempy/fhempy/commit/edb2c48dadbf008599aaced1c5364ac30fc58121))


## v0.1.84 (2021-08-15)

### Chore

* chore: update controls ([`dd1e430`](https://github.com/fhempy/fhempy/commit/dd1e430cb1c3b9eb6b03594c055231171fa572e7))

### Fix

* fix(tuya_cloud): fix switch ([`d1d1e03`](https://github.com/fhempy/fhempy/commit/d1d1e03f629985175a0bae88f797f5cc49ab1b0d))

### Unknown

* Merge branch &#39;development&#39; ([`5af2d94`](https://github.com/fhempy/fhempy/commit/5af2d941fa9f1626333d603ba094ea47c9b49d2d))


## v0.1.83 (2021-08-13)

### Chore

* chore: update controls ([`3d30eed`](https://github.com/fhempy/fhempy/commit/3d30eed4c5e5b3fd2d597164300857a45e690ae2))

### Fix

* fix(tuya_cloud): fix default code for state ([`deedac5`](https://github.com/fhempy/fhempy/commit/deedac5f4853c92d3d79b6848b89542134dfdaf0))

### Unknown

* Merge branch &#39;development&#39; ([`5b9a5a7`](https://github.com/fhempy/fhempy/commit/5b9a5a7f436a4ac7a4fd54d347b93a5789e9f218))


## v0.1.82 (2021-08-08)

### Chore

* chore: update controls ([`c7ab798`](https://github.com/fhempy/fhempy/commit/c7ab79878365b3908cf1b58a2dc1168a04656b78))

### Fix

* fix(tuya_cloud): fix tuya lib version ([`9cb101e`](https://github.com/fhempy/fhempy/commit/9cb101e9ba9812e5060039eebb105e4f95855385))

### Unknown

* Merge branch &#39;development&#39; ([`f516b78`](https://github.com/fhempy/fhempy/commit/f516b7849ef92b26dbf7c5a92075ead41600d400))


## v0.1.81 (2021-08-07)

### Chore

* chore: update controls ([`fc9ede4`](https://github.com/fhempy/fhempy/commit/fc9ede4690e71d8f6e8734e72fb1381d974e12af))

### Fix

* fix(skodaconnect): fix typo auxiliary ([`9455fc2`](https://github.com/fhempy/fhempy/commit/9455fc2b8fd66c329f4eb3e30b67e9fabd31cee6))

### Unknown

* Merge branch &#39;development&#39; ([`5854fee`](https://github.com/fhempy/fhempy/commit/5854fee63b18fb6f6871c3a58feb9ee8bca28fbd))


## v0.1.80 (2021-08-07)

### Chore

* chore: update controls ([`6b2e046`](https://github.com/fhempy/fhempy/commit/6b2e04674a071b9d78365050368139cc6172548a))

### Fix

* fix(skodaconnect): fix update_interval/_readings ([`8ee0686`](https://github.com/fhempy/fhempy/commit/8ee0686595e22337b0f5bf8c17720ec09a3a33a8))

### Unknown

* Merge branch &#39;development&#39; ([`cee2717`](https://github.com/fhempy/fhempy/commit/cee2717ad1955f5594176f83ba031e0dc16e3eed))


## v0.1.79 (2021-08-06)

### Chore

* chore: update controls ([`fdccf32`](https://github.com/fhempy/fhempy/commit/fdccf32c0addb463ac868180ac4e42e4cb659aa2))

### Fix

* fix(fhempy): fix zeroconf ([`bf048e3`](https://github.com/fhempy/fhempy/commit/bf048e322a58949eef11f305ecf09435b24ebda9))

### Unknown

* Merge branch &#39;development&#39; ([`5148f27`](https://github.com/fhempy/fhempy/commit/5148f27bc1d7215529d1b6d0817a748bac68cbf7))


## v0.1.78 (2021-08-06)

### Chore

* chore: update controls ([`e2afb0b`](https://github.com/fhempy/fhempy/commit/e2afb0b5b32f896b55122f04a9a37123350bd9df))

### Fix

* fix(skodaconnect): climatisation fix ([`8f2bc7d`](https://github.com/fhempy/fhempy/commit/8f2bc7da3d0767897d31269a5fba91e2c3854f0c))

### Unknown

* Merge branch &#39;development&#39; ([`a8ef46e`](https://github.com/fhempy/fhempy/commit/a8ef46ebce692c5a8e58df574deabd72b2468202))


## v0.1.77 (2021-08-02)

### Chore

* chore: update controls ([`e7539eb`](https://github.com/fhempy/fhempy/commit/e7539eb94b90d3962945ff50ec528797ca664236))

### Fix

* fix(tests): fix update test ([`b170df1`](https://github.com/fhempy/fhempy/commit/b170df1cfb06185c83aad5aa8a8c05aa183d89c9))

* fix(fhempy): log successfull update ([`2a3e37f`](https://github.com/fhempy/fhempy/commit/2a3e37f75db9b7277344e8fe0e255f31f1a59f9f))

### Unknown

* Merge branch &#39;development&#39; ([`6f37816`](https://github.com/fhempy/fhempy/commit/6f3781607c05674eca2f648693df9b90fbd96755))


## v0.1.76 (2021-08-02)

### Chore

* chore: update controls ([`5fa5261`](https://github.com/fhempy/fhempy/commit/5fa5261ef3eacc356199f99f98f93f2f33653aad))

### Fix

* fix(fhempy): fix shutdown after update ([`3d7d556`](https://github.com/fhempy/fhempy/commit/3d7d5569ee5416e08ed793791a55b5d3e15531d8))

### Unknown

* Merge branch &#39;development&#39; ([`29ef4e1`](https://github.com/fhempy/fhempy/commit/29ef4e19acb5a60c16b3799cd22ccc3654461189))


## v0.1.75 (2021-08-02)

### Chore

* chore: update controls ([`e07e1eb`](https://github.com/fhempy/fhempy/commit/e07e1ebd306294566af0e1d5d0fbd5592ba22f72))

* chore(tuya_cloud): clarify readme ([`2c9b282`](https://github.com/fhempy/fhempy/commit/2c9b282a89bbe4414a855aef4e97bef5f89d30de))

### Fix

* fix(tuya_cloud): one more fix ([`4a8dc19`](https://github.com/fhempy/fhempy/commit/4a8dc199c0fbb5ea99105e7ee47e0c83a0acbc96))

### Unknown

* Merge branch &#39;development&#39; ([`5c41684`](https://github.com/fhempy/fhempy/commit/5c41684ecf1e4668e2c1365d92610f34a38b6061))


## v0.1.74 (2021-08-02)

### Chore

* chore: update controls ([`1fa7794`](https://github.com/fhempy/fhempy/commit/1fa77942fb22cfce9fcc8a7a2be5e72dca06262b))

* chore(tuya_cloud): update readme ([`263da1a`](https://github.com/fhempy/fhempy/commit/263da1aa090d231a265d9318cfb5823e4e50dba5))

### Fix

* fix(tuya_cloud): some fixes ([`357ddf1`](https://github.com/fhempy/fhempy/commit/357ddf1299a123e28c3b18571b64ced5da2aeac4))

### Unknown

* Merge branch &#39;development&#39; ([`e200fe0`](https://github.com/fhempy/fhempy/commit/e200fe0f9479f8427268287fb1a8372aed5e7e5c))


## v0.1.73 (2021-08-02)

### Chore

* chore: update controls ([`553f64e`](https://github.com/fhempy/fhempy/commit/553f64e96c3c052256d7f16d54f9b4de64b11201))

* chore: update readme to specify supported devices ([`bc1ca28`](https://github.com/fhempy/fhempy/commit/bc1ca28fc3c277dadd050a088f3bccf5d3f4a006))

### Fix

* fix(tuya_cloud): fix readings for unsupported devs ([`8dea541`](https://github.com/fhempy/fhempy/commit/8dea541efce093b80eb187a051d00fc1051f55a0))

### Unknown

* Merge branch &#39;development&#39; ([`c5cada3`](https://github.com/fhempy/fhempy/commit/c5cada3f434250a5f0dcf1dbaae59ee17eacae5c))


## v0.1.72 (2021-08-01)

### Chore

* chore: update controls ([`f4fc5f4`](https://github.com/fhempy/fhempy/commit/f4fc5f49fade9fa80acb988f738df9e1198e9526))

### Fix

* fix(tuya_cloud): handle unsupported devices ([`0c224bd`](https://github.com/fhempy/fhempy/commit/0c224bd5d05825c6da004890574640442df6566c))

### Unknown

* Merge branch &#39;development&#39; ([`24f36bd`](https://github.com/fhempy/fhempy/commit/24f36bd061702df14eebe2b27994e75a5226639a))


## v0.1.71 (2021-07-31)

### Chore

* chore: update controls ([`2ff9d21`](https://github.com/fhempy/fhempy/commit/2ff9d21905986eef4604da0cea3c27afd1d304a5))

* chore: change to tuya cloud ([`4416307`](https://github.com/fhempy/fhempy/commit/4416307d60801b46fa8f6f938d85de242fab65db))

* chore: add skodaconnect ([`65077a3`](https://github.com/fhempy/fhempy/commit/65077a30a4ab466ad2ae2ff0318bcdccd693dbc2))

* chore: add warema ([`9ed5a7b`](https://github.com/fhempy/fhempy/commit/9ed5a7b9d049eb9aadd6c75e9d804c37b58760de))

* chore: add tuya_cloud ([`b79ce33`](https://github.com/fhempy/fhempy/commit/b79ce33e81877e4a7d4ca80d0d612b15b5af9b76))

### Fix

* fix(tuya_cloud): fix autocreation of new devices ([`80607f2`](https://github.com/fhempy/fhempy/commit/80607f2c566e6cf548e3eee786cc00df516e50ec))

* fix(xiaomi_gateway3): fix temp symbol ([`b033d42`](https://github.com/fhempy/fhempy/commit/b033d421c0634375fda99512b91e99b5dcb9e27c))

### Unknown

* Merge branch &#39;development&#39; ([`984da4e`](https://github.com/fhempy/fhempy/commit/984da4eb1fe56e479f9150a64ee68d31813b9f37))

* Merge branch development ([`eafa609`](https://github.com/fhempy/fhempy/commit/eafa60900c58655cf35a7435f9d8f86a23dd52de))


## v0.1.70 (2021-07-30)

### Chore

* chore: update controls ([`254443f`](https://github.com/fhempy/fhempy/commit/254443f16c7198238c4eb8ebe3ae704b31bfe2c8))

* chore: add relax_vaillant ([`5c649c9`](https://github.com/fhempy/fhempy/commit/5c649c9fae3a8bf7ab1466976e9a716079712491))

### Feature

* feat(tuya_cloud): support all tuya devices ([`ddceb85`](https://github.com/fhempy/fhempy/commit/ddceb855fe6758d5884346ea93a6e84a06625c34))

* feat(fhempy): use fhempy room instead of hidden ([`ae2ffdc`](https://github.com/fhempy/fhempy/commit/ae2ffdc9672e467d0ae68294acb6b79b559c8a04))

* feat(fhempy): support init_done ([`c807582`](https://github.com/fhempy/fhempy/commit/c80758235165e50f9256cc060db2930a5b97b738))

* feat(erelax_vaillant): support home/away ([`b29edde`](https://github.com/fhempy/fhempy/commit/b29eddeb16eb50c86f22eceb7cd8b2277e87f718))

### Fix

* fix(tuya): fix attributes ([`1bd998e`](https://github.com/fhempy/fhempy/commit/1bd998e478ff6e278b889169baeb89d0493031cb))

### Unknown

* Merge branch &#39;development&#39; ([`d9242ca`](https://github.com/fhempy/fhempy/commit/d9242ca376d6053932214c98b2cd1b6aa3af52b4))


## v0.1.69 (2021-07-27)

### Chore

* chore: update controls ([`cea6119`](https://github.com/fhempy/fhempy/commit/cea6119897f83899144b8bd7f4dc5c70ee64c2a0))

### Feature

* feat(erelax_vaillant): support erelax vaillant ([`0c7f12c`](https://github.com/fhempy/fhempy/commit/0c7f12c7f8709687cdf2d477b055c03bb3c6e38a))

### Unknown

* Merge branch &#39;development&#39; ([`75e4d6f`](https://github.com/fhempy/fhempy/commit/75e4d6fc7bd337708c0fab83a1d9529a2908ee86))


## v0.1.68 (2021-07-13)

### Chore

* chore: update controls ([`2aa48be`](https://github.com/fhempy/fhempy/commit/2aa48be75108d6f5b47e5a711ee705c1661cc68a))

### Feature

* feat(tuya): support unknown tuya devices ([`d42d30d`](https://github.com/fhempy/fhempy/commit/d42d30d2f91b4266eabf13a8e0985a24dee10f32))

### Unknown

* Merge branch &#39;development&#39; ([`3af15c2`](https://github.com/fhempy/fhempy/commit/3af15c267a1faf8b49fe953fee03aeb309c05190))


## v0.1.67 (2021-07-13)

### Chore

* chore: update controls ([`b09ccef`](https://github.com/fhempy/fhempy/commit/b09ccef0c03f44c2230f0c551d08b7f0aa7c5377))

### Fix

* fix(tuya): create unknown devices ([`3a57f5b`](https://github.com/fhempy/fhempy/commit/3a57f5bb5bbd3697ad19e8d58a0cff5da9267ad2))

* fix(ring): fix ring auth ([`ebc454d`](https://github.com/fhempy/fhempy/commit/ebc454d5302b3f9356b9d54efab6d76f833c5d35))

### Unknown

* Merge branch &#39;development&#39; ([`96f7cdb`](https://github.com/fhempy/fhempy/commit/96f7cdb290d6502f7d206f51a0512916cc456f5a))


## v0.1.66 (2021-07-04)

### Chore

* chore: update controls ([`a3f2dac`](https://github.com/fhempy/fhempy/commit/a3f2dacbe4757113817c9532859438b2484be935))

### Unknown

* Merge branch &#39;development&#39; ([`81603ed`](https://github.com/fhempy/fhempy/commit/81603ed6dfa2c074465e449da75adf91b0090aa3))

* Merge pull request #19 from jfmennedy/patch-2

Update manifest.json ([`5a4c527`](https://github.com/fhempy/fhempy/commit/5a4c5272ef20f0990ffe0234522d7a2aa87eb296))

* Update manifest.json ([`05db3bd`](https://github.com/fhempy/fhempy/commit/05db3bd3ce3c25920fe6e6f9106aadf8163e34c1))

* add apt update ([`f61fed9`](https://github.com/fhempy/fhempy/commit/f61fed9492e2d171ef41a2c55b0b1f6394c01f7b))


## v0.1.65 (2021-06-25)

### Chore

* chore: update controls ([`030e102`](https://github.com/fhempy/fhempy/commit/030e1021748f8bca186b590063f9566286ad9b6c))

* chore: minor code style changes ([`2204f05`](https://github.com/fhempy/fhempy/commit/2204f0575ea3e8f097b2ee70762b9cc5161a794e))

### Feature

* feat(skodaconnect): change vehicle.update() to connection.update(), add UpdateInterval, add UpdateReading, add ForceUpdate, add missing set_ commands, ([`1de20c3`](https://github.com/fhempy/fhempy/commit/1de20c34fe61541d42a1628a05b6b526aa439698))

### Unknown

* Merge branch &#39;development&#39; ([`1d54a57`](https://github.com/fhempy/fhempy/commit/1d54a579c6ff6ec8f6581d7fdcfab642331ee76f))

* Merge pull request #18 from jfmennedy/patch-1

feat(skodaconnect): fix update and add commands ([`a15c858`](https://github.com/fhempy/fhempy/commit/a15c8583aacde0c7ec38733ab62b6f0e9f722623))


## v0.1.64 (2021-06-23)

### Chore

* chore: update controls ([`6c035b7`](https://github.com/fhempy/fhempy/commit/6c035b758ac97092f264c33dd84b7d4ede7c42de))

### Feature

* feat(skodaconnect): add skoda connect support ([`ab507e8`](https://github.com/fhempy/fhempy/commit/ab507e872293014fedad786bf5d85c4e82eb36a4))

### Unknown

* Merge branch &#39;development&#39; ([`959b179`](https://github.com/fhempy/fhempy/commit/959b17993a81fbbd9ac22de0ae91b1ef5ea95d86))


## v0.1.63 (2021-06-01)

### Chore

* chore: update controls ([`276f594`](https://github.com/fhempy/fhempy/commit/276f5947ee63ddab1b43670fa6bf3ce0bb6ccd74))

### Unknown

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhempy ([`28d274e`](https://github.com/fhempy/fhempy/commit/28d274e484d70e34aa5bf221961f70ab2736f356))


## v0.1.62 (2021-06-01)

### Chore

* chore: update controls ([`b0bd831`](https://github.com/fhempy/fhempy/commit/b0bd8319543ef5c27cd495595a43b9f1e7708f08))

### Unknown

* Merge pull request #15 from hubecker/master

add warema module (@hubecker) ([`7becc40`](https://github.com/fhempy/fhempy/commit/7becc4032332b38a48d6f0991cfa69e9f63f0b27))

* fix interval update ([`eebad96`](https://github.com/fhempy/fhempy/commit/eebad96193e214645d0a869243c87f35078ce82d))

* Update warema.py

fixed bug ([`6fd157c`](https://github.com/fhempy/fhempy/commit/6fd157c824b744ab382999e1c2b95d5f89993c97))

* add warema module ([`bdd5b1b`](https://github.com/fhempy/fhempy/commit/bdd5b1bf3a228bba87c3c61eaa63c3140fb1a203))


## v0.1.61 (2021-05-23)

### Chore

* chore: update controls ([`d139e2f`](https://github.com/fhempy/fhempy/commit/d139e2fb19de73ba0ece4d7b75015a83ce734c0d))

### Fix

* fix(miflora): fix deadlocks ([`21810f8`](https://github.com/fhempy/fhempy/commit/21810f8f6680186b329db31e5a6de8fc0010b0aa))

* fix(BindingsIo): fix possible 100% cpu bug ([`947a90e`](https://github.com/fhempy/fhempy/commit/947a90e472034186656128676ba7d16f728950b3))

### Unknown

* Merge branch &#39;development&#39; ([`596ebe9`](https://github.com/fhempy/fhempy/commit/596ebe96bd0b2a35bf923090b11eae6a39df1e06))


## v0.1.60 (2021-05-04)

### Chore

* chore: update controls ([`3e4fb25`](https://github.com/fhempy/fhempy/commit/3e4fb25a4d6f8856139975c3e60c19c84e17140c))

### Feature

* feat(mitemp2): test version of mitemp2 ([`31e17a4`](https://github.com/fhempy/fhempy/commit/31e17a4e439ab92463659c20c0e494cd33f85947))

### Fix

* fix(spotify): change auth url ([`63319ba`](https://github.com/fhempy/fhempy/commit/63319bad78301caae4b0273745e459969fcf308f))

* fix(googlecast): fix spotify play ([`08ea929`](https://github.com/fhempy/fhempy/commit/08ea929003d6966c587aed433f6fefbe70e13cdf))

* fix(spotify): fix deprecation warning ([`a852b75`](https://github.com/fhempy/fhempy/commit/a852b75cd13a06ae90ad8b004225fb04014b0b45))

* fix(spotify_connect_player): fix deprecation warn ([`e9bc04b`](https://github.com/fhempy/fhempy/commit/e9bc04bc61cf439b12e6ad4b5101ca57f1bab2e6))

* fix(googlecast): fix spotify, add speak_lang attr ([`6a81f15`](https://github.com/fhempy/fhempy/commit/6a81f15dbce5d2b57489b1c0cffec88fe5653c53))

### Unknown

* Merge branch &#39;development&#39; ([`f5fe091`](https://github.com/fhempy/fhempy/commit/f5fe0916c6a4788f4c6a6b73e7ef91d98d9d2792))


## v0.1.59 (2021-04-18)

### Chore

* chore: update controls ([`b43d8de`](https://github.com/fhempy/fhempy/commit/b43d8deb274ac4e32854f375664c44ab25fde808))

### Fix

* fix(ring): fix update_health_data ([`747a129`](https://github.com/fhempy/fhempy/commit/747a12996a9b2552256fe0492086150c94586e5d))

### Unknown

* Merge branch &#39;development&#39; ([`b731edd`](https://github.com/fhempy/fhempy/commit/b731edd1474544fcd5697b3059505e0bca7a5dff))


## v0.1.58 (2021-04-18)

### Chore

* chore: update controls ([`ab3baa1`](https://github.com/fhempy/fhempy/commit/ab3baa187c55b8eddc215646bfe2893eaa2923ff))

### Feature

* feat(tuya): support miio lib 0.5.5.2 ([`88fb98b`](https://github.com/fhempy/fhempy/commit/88fb98bdd7e9f73bff231e64236832685e12f47b))

### Unknown

* Merge branch &#39;development&#39; ([`7721f95`](https://github.com/fhempy/fhempy/commit/7721f95affa8f318d73bbf840b8884300d574829))


## v0.1.57 (2021-03-09)

### Chore

* chore: update controls ([`a3427e6`](https://github.com/fhempy/fhempy/commit/a3427e61dec6a8161d62beb4c7d0e5ad62c0a731))

### Fix

* fix(fhempy): fix possible crash on reconnect ([`d68d60b`](https://github.com/fhempy/fhempy/commit/d68d60bcf9f52c145ad6be221fb6a7fe7388ee03))

* fix(ring): fix battery/volume updates ([`936cc49`](https://github.com/fhempy/fhempy/commit/936cc495c86040d13fc34e11668daf6d32967aa1))

### Unknown

* Merge branch &#39;development&#39; ([`d49454e`](https://github.com/fhempy/fhempy/commit/d49454ea987d02ef6c29f1ad9f0d1a6285dc670a))


## v0.1.56 (2021-03-08)

### Chore

* chore: update controls ([`df19a35`](https://github.com/fhempy/fhempy/commit/df19a35a3a2d9333a2673fe820ca09da941ab9eb))

### Feature

* feat(googlecast): update to pychromecast 9.1.1 ([`fdaab50`](https://github.com/fhempy/fhempy/commit/fdaab50f99006806464603a2ecfd2f4adf137967))

### Fix

* fix(ring): revert ring_doorbell lib to 0.6.2 ([`71b9511`](https://github.com/fhempy/fhempy/commit/71b9511e47751eb93e2365f0861918aabfe738cd))

### Unknown

* Merge branch &#39;development&#39; ([`6c9a4ff`](https://github.com/fhempy/fhempy/commit/6c9a4ff50b2fd65d675445d68df260d05fba5e65))


## v0.1.55 (2021-03-01)

### Chore

* chore: update controls ([`f18ff8a`](https://github.com/fhempy/fhempy/commit/f18ff8adab923f2cfd5faaf4b548d527a149146e))

* chore: fix requirements for dev ([`60a6bea`](https://github.com/fhempy/fhempy/commit/60a6beabcdb125e7872dcd1bcad735de9a0756bd))

### Unknown

* Merge branch &#39;development&#39; ([`55d4d86`](https://github.com/fhempy/fhempy/commit/55d4d86dac4934b7532a6e13b1ca53aef2ddbba6))


## v0.1.54 (2021-03-01)

### Chore

* chore: update controls ([`fb01f45`](https://github.com/fhempy/fhempy/commit/fb01f45d01657d90b73ddf22e11c948e44b5c7d2))


## v0.1.53 (2021-03-01)


## v0.1.52 (2021-03-01)

### Chore

* chore: update controls ([`4cd400e`](https://github.com/fhempy/fhempy/commit/4cd400e1bb574febb9e110445cdee90d7145d59d))

### Feature

* feat(ring): update to latest ring_doorbell lib ([`a7295ca`](https://github.com/fhempy/fhempy/commit/a7295ca3fcfb3e6f62cdcc969556b79f8198f468))

* feat(tuya): update to latest tinytuya lib ([`0edc476`](https://github.com/fhempy/fhempy/commit/0edc476557bf54da6c7775b0101b68eb35894115))

### Unknown

* Merge branch &#39;development&#39; ([`0a37583`](https://github.com/fhempy/fhempy/commit/0a37583b22ef0df2b56c8a2686defdd22bee766a))


## v0.1.51 (2021-02-17)

### Chore

* chore: update controls ([`b79dcf2`](https://github.com/fhempy/fhempy/commit/b79dcf215c29fa7b8a0e031593c2ea5b391befb6))

### Fix

* fix(fhempy): update cryptography ([`b154eb6`](https://github.com/fhempy/fhempy/commit/b154eb6b592cb672dbaabefc45b37e11ef304bce))

### Unknown

* Merge branch &#39;development&#39; ([`69e052b`](https://github.com/fhempy/fhempy/commit/69e052bbb1024aaf721dcc58ef25b61cc6125323))


## v0.1.50 (2021-02-17)

### Chore

* chore: update controls ([`4fb08ec`](https://github.com/fhempy/fhempy/commit/4fb08ecd1506e20de15c60ae200597af8c6da870))

### Fix

* fix(fhempy): fix cryptography installation ([`a7b4b6e`](https://github.com/fhempy/fhempy/commit/a7b4b6e5a5357f6b409656f4f79d99ce1b6154a3))

### Unknown

* Merge branch &#39;development&#39; ([`1f21d9a`](https://github.com/fhempy/fhempy/commit/1f21d9a359555598844bf2fcbc0d1337a2527cb9))


## v0.1.49 (2021-02-14)

### Chore

* chore: update controls ([`67dfc23`](https://github.com/fhempy/fhempy/commit/67dfc2344c47bb4ad62ecb9d311eb364963cc87a))

* chore: add xiaomi_gateway3 tests ([`46e9e62`](https://github.com/fhempy/fhempy/commit/46e9e62172ab6405130400c617536a9a43d20458))

### Feature

* feat(xiaomi_gateway3): update to latest version ([`9643837`](https://github.com/fhempy/fhempy/commit/96438373925c4c583dfbe4a9d8433fbc98aa678a))

### Fix

* fix(xiaomi_tokens): fix create miio device ([`f8e4352`](https://github.com/fhempy/fhempy/commit/f8e43525f62f00939f60d0ee30349246203682db))

### Unknown

* Merge branch &#39;development&#39; ([`9df191d`](https://github.com/fhempy/fhempy/commit/9df191d47c0a5c5a32665d1ffe00acc806c6b037))


## v0.1.48 (2021-02-02)

### Chore

* chore: update controls ([`d1c4502`](https://github.com/fhempy/fhempy/commit/d1c4502ba1a0a45c2e2bc3658670ea87944474a2))

### Fix

* fix(xiaomi_tokens): fix device creation ([`ebbc3bb`](https://github.com/fhempy/fhempy/commit/ebbc3bb61f20fba4ff8d1eadd1af61017abe956e))

### Unknown

* Merge branch &#39;development&#39; ([`b0bad66`](https://github.com/fhempy/fhempy/commit/b0bad66f74554348f4b7a38d0c5fb6c15fb3af25))


## v0.1.47 (2021-02-01)

### Chore

* chore: update controls ([`ab7643c`](https://github.com/fhempy/fhempy/commit/ab7643c2060b80d1110a3ab1a2e62bd228552e6d))

### Fix

* fix(xiaomi_tokens): make readings country specific ([`efe1b7a`](https://github.com/fhempy/fhempy/commit/efe1b7a4f37d3530b2f92a906e45f202d67e6d21))

### Unknown

* Merge branch &#39;development&#39; ([`342d194`](https://github.com/fhempy/fhempy/commit/342d194983cee1200d6faca5e1262440fbdaf72d))


## v0.1.46 (2021-02-01)

### Chore

* chore: update controls ([`5727798`](https://github.com/fhempy/fhempy/commit/57277988b360b9d7b0ebe6854e0bd0f981e6b93c))

* chore: add update test ([`6870fc7`](https://github.com/fhempy/fhempy/commit/6870fc78f2424d24cc8f37c97666745793b80eb9))

### Fix

* fix(fhempy): raise error if pkg install fails ([`8b15dcd`](https://github.com/fhempy/fhempy/commit/8b15dcd19180451b45f3de4aa420938334f951d2))

### Refactor

* refactor(*): sort imports ([`ed84897`](https://github.com/fhempy/fhempy/commit/ed84897fca897f01b6fc87a3ec5b25a9bb9eeef8))

### Unknown

* Merge branch &#39;development&#39; ([`0eb0861`](https://github.com/fhempy/fhempy/commit/0eb086198cab2e859747c6da60444873019af2ae))


## v0.1.45 (2021-01-31)

### Chore

* chore: update controls ([`a3758fa`](https://github.com/fhempy/fhempy/commit/a3758facffb5d145d051c4166ad554bb71036695))

* chore: fix readme for pypi ([`34c8587`](https://github.com/fhempy/fhempy/commit/34c8587fc278b29cdcbd6c042c9d605755a6eedf))

### Fix

* fix(xiaomi_gateway3): sort imports ([`89c14bc`](https://github.com/fhempy/fhempy/commit/89c14bc1477a91be51c86a80666f12e94430cb04))

* fix(googlecast): remove spotify_token dependency ([`ab8f872`](https://github.com/fhempy/fhempy/commit/ab8f8726158eb7037a62e98517a61b2760fbc47f))

* fix(xiaomi_gateway3): fix motion sensor reset ([`37222fc`](https://github.com/fhempy/fhempy/commit/37222fcd1d52c09cb97ba5943d939436c40d56a8))

### Unknown

* Merge branch &#39;development&#39; ([`eac8e0c`](https://github.com/fhempy/fhempy/commit/eac8e0c11d28cb483fb4472cb401aef4a38a1688))


## v0.1.44 (2021-01-30)

### Chore

* chore: update controls ([`597ca03`](https://github.com/fhempy/fhempy/commit/597ca037b44cf446d4b23bb0967a7f0ae191a332))

### Fix

* fix(fhempy): change logfile name to fhempy ([`2dc88df`](https://github.com/fhempy/fhempy/commit/2dc88df1177c69990926d5e55852656ee365f666))

* fix(xiaomi_gateway3): remove added_device reading ([`700e361`](https://github.com/fhempy/fhempy/commit/700e361417c9fc4ea634874b2f447396657c85fc))

* fix(fhempy): change log name to fhempy ([`ce8fac5`](https://github.com/fhempy/fhempy/commit/ce8fac5e3faa8fa8db360d787dc481288ba045f0))


## v0.1.43 (2021-01-30)

### Chore

* chore: update controls ([`62a8054`](https://github.com/fhempy/fhempy/commit/62a8054516f582383bc65857067455c60d808d73))


## v0.1.42 (2021-01-30)

### Chore

* chore: update controls ([`89b7e07`](https://github.com/fhempy/fhempy/commit/89b7e0788a3ba591022ce4ea079889f5aad093e3))

### Feature

* feat(eq3bt): support wndOpnTime/Temp, eco/cmftTemp ([`107805f`](https://github.com/fhempy/fhempy/commit/107805fd5d85fde76a49e2fabe1994943d27a169))

### Unknown

* Merge branch &#39;eq3bt_fix&#39; ([`3db4e20`](https://github.com/fhempy/fhempy/commit/3db4e20d04546279ada6b805e17983dd6e8c510a))


## v0.1.41 (2021-01-30)

### Chore

* chore: update controls ([`069587b`](https://github.com/fhempy/fhempy/commit/069587b327a16ae8c556e069d798a2ba1399ae9c))


## v0.1.40 (2021-01-30)

### Chore

* chore: update controls ([`d9cb6a6`](https://github.com/fhempy/fhempy/commit/d9cb6a61a6e75f966573d10bae6c3bb234903cd6))

* chore: remove return ([`f62078e`](https://github.com/fhempy/fhempy/commit/f62078e3091b1bfe4401d950c92a9a232ebb9b7c))

* chore: fix staticmethod annotation ([`02b11ab`](https://github.com/fhempy/fhempy/commit/02b11abc0fe63d22169e48b9fc3ccb39dd3d9804))

* chore: run tests only for python 3.7 ([`a73d685`](https://github.com/fhempy/fhempy/commit/a73d685ccc296d355877bf0abbf04ce5473fa5c0))

* chore: add tox-gh-actions ([`d0072a3`](https://github.com/fhempy/fhempy/commit/d0072a3fbb6415ffc8f3d5da2ca8ee4641dfe562))

* chore: fix gh actions ([`1da180e`](https://github.com/fhempy/fhempy/commit/1da180eeca798da27f8f4369315a54daab61abfc))

* chore: install apt deps ([`ba7cb89`](https://github.com/fhempy/fhempy/commit/ba7cb89b748647e4e741fd936186716f520f7d61))

* chore: rename ([`81af60c`](https://github.com/fhempy/fhempy/commit/81af60cdefec262cccb1e7d50d7409b600f4155e))

* chore: gh actions tests ([`9d80155`](https://github.com/fhempy/fhempy/commit/9d801556a90a5ea609b0de80907f64a89dbbdd35))

### Feature

* feat(xiaomi_gateway3): support sensor_wleak.aq1 ([`bc8cf61`](https://github.com/fhempy/fhempy/commit/bc8cf6183bb4568b5f47b98e07669e3e8cda4f4e))

### Fix

* fix(fhempy): fix update ([`6f381c1`](https://github.com/fhempy/fhempy/commit/6f381c1be050f3ee26d4cbd236b2e2da447c581f))

* fix(object_detection): fix image detection ([`cc5c8de`](https://github.com/fhempy/fhempy/commit/cc5c8defa3457d5a60d812c062623654ed3b0e9e))

* fix(esphome): fix restart ([`be47a72`](https://github.com/fhempy/fhempy/commit/be47a7221fc1814c091992393652c4c767a8b203))


## v0.1.39 (2021-01-29)

### Chore

* chore: update controls ([`f3474b4`](https://github.com/fhempy/fhempy/commit/f3474b46234c0525d23804f6e870ed54e81c2864))

### Feature

* feat(xiaomi_gateway3): support motion sensor ([`478db7a`](https://github.com/fhempy/fhempy/commit/478db7ad578ae6fef5a18066b2a4058fe561f745))

* feat(tuya): support another heating device ([`8843138`](https://github.com/fhempy/fhempy/commit/884313823231407a2155518cc01d04930246313c))

### Unknown

* Merge branch &#39;development&#39; ([`4707864`](https://github.com/fhempy/fhempy/commit/4707864eeb46442db7d8b42e977b87ade45f630d))


## v0.1.38 (2021-01-28)

### Chore

* chore: update controls ([`e3b801c`](https://github.com/fhempy/fhempy/commit/e3b801ce9bdc27dcd551bf329b59e73131c157b9))

### Fix

* fix(eq3bt): fix set temperatureOffset ([`429afcd`](https://github.com/fhempy/fhempy/commit/429afcd4f61f17b248dce60161d7418ec5770a54))

### Unknown

* Merge branch &#39;development&#39; ([`c60b601`](https://github.com/fhempy/fhempy/commit/c60b601de9712f0ea21e288a0494b336f86cab0b))


## v0.1.37 (2021-01-28)

### Chore

* chore: update controls ([`0536e1a`](https://github.com/fhempy/fhempy/commit/0536e1aebd81ce0b8424d23a0c7dc81626035ca0))

### Documentation

* docs: remove useless stuff ([`7401907`](https://github.com/fhempy/fhempy/commit/74019075190fb53b2cc7fdf6e4721360a698974e))

### Fix

* fix(xiaomi_gateway3): add missing imports ([`b54aa4a`](https://github.com/fhempy/fhempy/commit/b54aa4a2529f1c7c23c3bfbb457c05790dcc0014))

* fix(fhempy): set IODev after CommandDefine ([`b1a1299`](https://github.com/fhempy/fhempy/commit/b1a12993b76cebe3949f510add7a7e1857b91869))


## v0.1.36 (2021-01-27)

### Chore

* chore: update controls ([`e4ab8ac`](https://github.com/fhempy/fhempy/commit/e4ab8ac071fb82e42fe7257c7010eb4adc2b36ee))

### Fix

* fix(admin): another try ([`e592500`](https://github.com/fhempy/fhempy/commit/e592500ba431e5bd112e594f38b9a96f2bb0e65d))


## v0.1.35 (2021-01-27)

### Chore

* chore: update controls ([`a792112`](https://github.com/fhempy/fhempy/commit/a792112f5f8f5e39eae7cd3f00f57337c797e1a5))

### Fix

* fix(setup): fix excludes in manifest ([`9c3b255`](https://github.com/fhempy/fhempy/commit/9c3b255e90fbc8c8f0ab11a85531795c6239fd84))


## v0.1.34 (2021-01-27)

### Chore

* chore: update controls ([`7c905ff`](https://github.com/fhempy/fhempy/commit/7c905ff0913e39083c65674f3681e549f08b3734))

### Fix

* fix(readme): another fix ([`fc11bc4`](https://github.com/fhempy/fhempy/commit/fc11bc4426023161c219b2ea7b3daedf9f9696a6))


## v0.1.33 (2021-01-27)

### Chore

* chore: update controls ([`a60d32a`](https://github.com/fhempy/fhempy/commit/a60d32a21fb599b5b4913c3f2595984c071b49df))

### Fix

* fix(release): one more try to get gh token working ([`f7f0f04`](https://github.com/fhempy/fhempy/commit/f7f0f04443b9b2a05d05dbb8bd76cc46132a8f70))


## v0.1.32 (2021-01-27)

### Chore

* chore: update controls ([`d8db6b2`](https://github.com/fhempy/fhempy/commit/d8db6b298ec78ac1c03722f30cf62c941aa188bc))

### Fix

* fix(release): hopefully fix release script ([`cea2a16`](https://github.com/fhempy/fhempy/commit/cea2a165abd64ac7410ecb387dbf1d36f50cb468))


## v0.1.31 (2021-01-27)

### Chore

* chore: update controls ([`3c8a3d4`](https://github.com/fhempy/fhempy/commit/3c8a3d442734e5d064b638252226e7be77cafede))

### Feature

* feat(tuya): add keep_connected attr ([`b2c1ca4`](https://github.com/fhempy/fhempy/commit/b2c1ca47cf1b7adda9eb86731f21e0f755cf3dcd))

### Unknown

* Merge branch &#39;development&#39; ([`2a18460`](https://github.com/fhempy/fhempy/commit/2a184602aca7363f3c6cbfe30cd36d39afeb57d1))


## v0.1.30 (2021-01-27)

### Chore

* chore: update controls ([`7fbf8cb`](https://github.com/fhempy/fhempy/commit/7fbf8cbd3dabc56374993a5ab8b7add46e899c86))

### Fix

* fix(xiaomi_gateway3): remove unused imports ([`1758909`](https://github.com/fhempy/fhempy/commit/175890932f4efeeedba79ae6b2d1dfe81839abcc))

### Unknown

* Merge branch &#39;development&#39; ([`1af6b52`](https://github.com/fhempy/fhempy/commit/1af6b52c477f64a2b5e0d11e5ee396a41ec42ad6))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`76ff451`](https://github.com/fhempy/fhempy/commit/76ff451b49c9b71703f47aefce0532a2785ce102))


## v0.1.29 (2021-01-27)

### Chore

* chore: update controls ([`01e5c16`](https://github.com/fhempy/fhempy/commit/01e5c16e703aef16c436eeefa3662c14103a6640))

* chore: add controls update script ([`a08d81e`](https://github.com/fhempy/fhempy/commit/a08d81e4258ec907ce723f43d81ec61445e5af00))

* chore: add info for .env ([`531e4b8`](https://github.com/fhempy/fhempy/commit/531e4b8e952c1135ec34977ce9ad594ca03e52a8))

* chore: use patch level for rls, fix .env usage ([`57389f1`](https://github.com/fhempy/fhempy/commit/57389f18cd813636768c6620fcae3bb61458efc3))

### Fix

* fix(xiaomi_gateway3): add import time ([`7ef7a9e`](https://github.com/fhempy/fhempy/commit/7ef7a9ecabb2e8f765f6e1223bcaaaed365c6644))

* fix(xiaomi_gateway3): set last_update on update ([`146487d`](https://github.com/fhempy/fhempy/commit/146487daf69f9ed5219043c444fdfbac9f90021c))

### Unknown

* Merge branch &#39;development&#39; ([`f7ebf8f`](https://github.com/fhempy/fhempy/commit/f7ebf8f828b8ac707c0e5a330e68803b4893cf60))

* remove from release hook ([`ba41458`](https://github.com/fhempy/fhempy/commit/ba41458e6c29aedfdb0ef3315bffa185d6f9fbea))


## v0.1.28 (2021-01-27)

### Chore

* chore: add message to git merge ([`37dc281`](https://github.com/fhempy/fhempy/commit/37dc281e9f16c55ec6ad511686dd56277756a20d))

### Feature

* feat: new reading pairing on/off ([`ee42b9c`](https://github.com/fhempy/fhempy/commit/ee42b9c1dc822993ee882e94be056b311f87bd8e))

### Unknown

* Merge branch &#39;development&#39; ([`7ec29d8`](https://github.com/fhempy/fhempy/commit/7ec29d898f006e1d4abf1f99b6f05a01ee6c060e))

* action: auto update controls ([`3383182`](https://github.com/fhempy/fhempy/commit/33831829f53e07244f1813f2875415097d0b4c2f))


## v0.1.27 (2021-01-27)

### Chore

* chore: prepare release scripts ([`ba3e51f`](https://github.com/fhempy/fhempy/commit/ba3e51fca7e549bbd4d632488aa753a49bdb8859))

### Fix

* fix: pychromecast min version ([`8a58a53`](https://github.com/fhempy/fhempy/commit/8a58a5374c25ffcaf1f3c9a9f37b5ebb83272d96))

### Unknown

* Merge branch &#39;development&#39; ([`8f0595a`](https://github.com/fhempy/fhempy/commit/8f0595a6ced148229aa33edefcda3d4d41e5dadf))

* Merge branch &#39;development&#39; of https://github.com/dominikkarall/fhem_pythonbinding into development ([`7c0adb9`](https://github.com/fhempy/fhempy/commit/7c0adb9506db94f8f924b8a9b61e70b05e9672a9))

* fix pychromecast min version ([`d0eb9f5`](https://github.com/fhempy/fhempy/commit/d0eb9f5baa51b7cca9efc405e6fb7202556e8e5d))

* action: auto update controls ([`739a702`](https://github.com/fhempy/fhempy/commit/739a702ef5077fa9324b66c41842e7e5603fe879))

* Merge branch &#39;development&#39; ([`7918e93`](https://github.com/fhempy/fhempy/commit/7918e93d67b320bbd8a44534aafb8783397c4e17))

* version bump ([`4796a72`](https://github.com/fhempy/fhempy/commit/4796a7295b25c45ef7fe274afc991ea8e1c6f5b6))

* fix possible bug ([`fb60ede`](https://github.com/fhempy/fhempy/commit/fb60ede9dc0041f4121a891ba7128b2edb6090d6))

* action: auto update controls ([`49533bd`](https://github.com/fhempy/fhempy/commit/49533bdb266a33fe9492e6e94f2c6cbcf6b451de))


## v0.1.26 (2021-01-26)

### Unknown

* Merge branch &#39;development&#39; ([`497743d`](https://github.com/fhempy/fhempy/commit/497743dff4b1d861c21d5977a34e3994b12733c4))

* support lumi.weather.v1
support block firmware updates ([`28cab12`](https://github.com/fhempy/fhempy/commit/28cab120b2de10e004ddba3da2bc0b42a05edcc6))

* add temperature offset ([`557df9f`](https://github.com/fhempy/fhempy/commit/557df9f90fd328ab19ac5b23c2293d9669da4d6e))

* add pairing function for gateway
refactor device types ([`31f4b0d`](https://github.com/fhempy/fhempy/commit/31f4b0d90b76cd41643ad667dfb2db4193d19b01))

* fix volume ([`7d99fe2`](https://github.com/fhempy/fhempy/commit/7d99fe26866d2ba2c2ca874dd51fcf43eb6b0e48))

* keep asyncio debug slow coroutine 0.1s ([`5209d32`](https://github.com/fhempy/fhempy/commit/5209d32cf97c2aea43ee4c042c914b9a8474371c))

* stop zeroconf when connected ([`173521a`](https://github.com/fhempy/fhempy/commit/173521a2992be60aef24ac859f8aeb718f96dafc))

* add update info
small fixes ([`d35aa1f`](https://github.com/fhempy/fhempy/commit/d35aa1f161f8748a09edd5136f859be44883bdab))

* fix blocking fct call ([`54a907b`](https://github.com/fhempy/fhempy/commit/54a907b4aec1b8f0c3fd2f5af7dba7f03ee28a1d))

* support BubbleUpnp player ([`5a01c73`](https://github.com/fhempy/fhempy/commit/5a01c73d0eb4d853865db719b02c318f8ddddcd4))

* action: auto update controls ([`6f306fc`](https://github.com/fhempy/fhempy/commit/6f306fcd29abbcb105fc6f93f81d49f2afc996f2))


## v0.1.25 (2021-01-22)

### Unknown

* Merge branch &#39;development&#39; ([`4e72010`](https://github.com/fhempy/fhempy/commit/4e72010e62042e53446f5ae49931f605c3a44836))

* version bump ([`e51565a`](https://github.com/fhempy/fhempy/commit/e51565a032978bb5d2ddf58c1026e199518d1ae6))

* do not destroy schema after creation ([`4e7385d`](https://github.com/fhempy/fhempy/commit/4e7385d91e1ad92f5170f8fef36de619ad218328))

* add tuya tests ([`5adf61c`](https://github.com/fhempy/fhempy/commit/5adf61c2dd9a3f40b757c6db9b4bf91a24dbf74b))

* fix readings update ([`585c263`](https://github.com/fhempy/fhempy/commit/585c2632eb01d3bd35210b9a13de6ac74dbb2f09))

* add info reading ([`a487363`](https://github.com/fhempy/fhempy/commit/a4873632a990ec8ed1cadbd17d4d688894c51bee))

* support args: local, ip, port ([`7cc6815`](https://github.com/fhempy/fhempy/commit/7cc6815f17d9861a7a81db8eca2bc7236eb14401))

* fix state value, now online/offline ([`76bd506`](https://github.com/fhempy/fhempy/commit/76bd5067b4074ae41020c89bbc14233717002407))

* handle commands with optional parameters ([`4ef423b`](https://github.com/fhempy/fhempy/commit/4ef423b5742c7780f0370396a2156c4ad41817c8))

* not used, therefore deleted ([`c59592f`](https://github.com/fhempy/fhempy/commit/c59592f87abf2fb4bd5996eb0d4fa3c85d87eced))

* action: auto update controls ([`f2345d0`](https://github.com/fhempy/fhempy/commit/f2345d01ded00d94c5b61457ffde6a954b576733))


## v0.1.24 (2021-01-20)

### Unknown

* Merge branch &#39;development&#39; ([`71195dd`](https://github.com/fhempy/fhempy/commit/71195dd0e93c88b1a4c7fca13c79933bc2dee565))

* version bump ([`82f358c`](https://github.com/fhempy/fhempy/commit/82f358c64849f74c94a2584ffd91182b36396d22))

* fix automatic device creation ([`933ccd0`](https://github.com/fhempy/fhempy/commit/933ccd0b97398cd2ea11a980ab8b2c16b42d0dc6))

* add heater ([`2adb8a5`](https://github.com/fhempy/fhempy/commit/2adb8a51c1bb2313895ea2e4e83360e4cdd6c26e))

* action: auto update controls ([`8860b3c`](https://github.com/fhempy/fhempy/commit/8860b3c8f426b0bd84d8079dee62da3373b83ff3))


## v0.1.23 (2021-01-20)

### Unknown

* Merge branch &#39;development&#39; ([`1426b01`](https://github.com/fhempy/fhempy/commit/1426b0132bf888b372d1a6fefab1baaa467132fa))

* version bump ([`dd61b91`](https://github.com/fhempy/fhempy/commit/dd61b91079822f722540c87d59d11129ff544392))

* add exception handling ([`366d4c5`](https://github.com/fhempy/fhempy/commit/366d4c54a222747135e302714aa9897af8528b98))

* fix ble_presence ([`71898d5`](https://github.com/fhempy/fhempy/commit/71898d5552edb1358259700327655942a5fc29cd))

* support enum, integer, string, boolean datapoints ([`d283eea`](https://github.com/fhempy/fhempy/commit/d283eeaa4edf7e06dc7ee67efe090385e60aa6af))

* add getDeviceHashName ([`2f5b3a6`](https://github.com/fhempy/fhempy/commit/2f5b3a6f6db38370a61adcb5f09ac3ed1d9a9b66))

* fix long running imports ([`40c1309`](https://github.com/fhempy/fhempy/commit/40c130916e3f0bef13549490ef1b52549009dd2a))

* add tests for 3.7,3.8,3.9 ([`29ac454`](https://github.com/fhempy/fhempy/commit/29ac454c3a7305cb12273b246409b6de0d413c82))

* add python version badge ([`069b445`](https://github.com/fhempy/fhempy/commit/069b445a41e71637d6202d19d66876848056cfe7))

* add python install script ([`0f7b797`](https://github.com/fhempy/fhempy/commit/0f7b7979b3741b115f848b74158c973572170bcb))

* restructure tests ([`434dd19`](https://github.com/fhempy/fhempy/commit/434dd19623e741a67b32215e082f1a6635160153))

* action: auto update controls ([`cd41cde`](https://github.com/fhempy/fhempy/commit/cd41cdeaa23e29ef672ddd485f064843248867f6))


## v0.1.22 (2021-01-10)

### Unknown

* Merge branch &#39;development&#39; ([`06ef3a5`](https://github.com/fhempy/fhempy/commit/06ef3a5649980a74f0d75f638072cc4f81f6bc73))

* version bump ([`8ee5141`](https://github.com/fhempy/fhempy/commit/8ee51413bde1b5584edd0bbd7ffbbb3c451ffcbd))

* fix tox ([`edec153`](https://github.com/fhempy/fhempy/commit/edec1530d05614a9e224d7b34af09f38330de347))

* add mappings, currently not in use ([`111b631`](https://github.com/fhempy/fhempy/commit/111b631792f3e27be1e1496e64d495bfb449092e))

* add info if localkey is present ([`beef7e3`](https://github.com/fhempy/fhempy/commit/beef7e3bddfdfd7ce50e66668c37ddd195ff473c))

* fix Python 3.8 ([`c343f17`](https://github.com/fhempy/fhempy/commit/c343f1752f6dcb3c78941d0a9af5550891536397))

* action: auto update controls ([`27bca68`](https://github.com/fhempy/fhempy/commit/27bca68852ec6ff26190329e148080d7f361dd29))


## v0.1.21 (2021-01-09)

### Unknown

* Merge branch &#39;development&#39; ([`b91fca2`](https://github.com/fhempy/fhempy/commit/b91fca284a5403f5b7cf69a80bae8a06f98f80a4))

* version bump ([`37d30f2`](https://github.com/fhempy/fhempy/commit/37d30f2875fda3a10196784a62cbb010dcccf54f))

* add ring tests
update others ([`62592dd`](https://github.com/fhempy/fhempy/commit/62592dd73b7e87dd73726865bb8610a9edf185f6))

* test update ([`d9717ce`](https://github.com/fhempy/fhempy/commit/d9717ce68b4f3e9be1bee4c1268d7325f6d299f0))

* add test requirements ([`dbfb736`](https://github.com/fhempy/fhempy/commit/dbfb736591f567c1cf9dc5973c5ab548885b9ea6))

* set ip offline when not found in setup ([`e7476a9`](https://github.com/fhempy/fhempy/commit/e7476a94fefd0ceaa572dff80d264bee1da44787))

* better debugging ([`d21cf2f`](https://github.com/fhempy/fhempy/commit/d21cf2fd357bdc1a2eb3b0455d461b9084bc9f95))

* report login failed ([`1306d36`](https://github.com/fhempy/fhempy/commit/1306d36f463d5c6d10e4a8b4bc2c087f9c3f3a79))

* action: auto update controls ([`0917056`](https://github.com/fhempy/fhempy/commit/0917056ea4df7a9901d613b9253bd6657152804a))


## v0.1.20 (2021-01-08)

### Unknown

* Merge branch &#39;development&#39; ([`fb5b99b`](https://github.com/fhempy/fhempy/commit/fb5b99b292124f455be8ce63c65d7da5ccf56fe2))

* version bump ([`3f54468`](https://github.com/fhempy/fhempy/commit/3f54468574a653eecc85dd61b0d55993f7370ce7))

* Merge branch &#39;development&#39; ([`bf7ec82`](https://github.com/fhempy/fhempy/commit/bf7ec82a158e0a5ed3086c11cf4ca15523c52f58))

* add version reading ([`930acb0`](https://github.com/fhempy/fhempy/commit/930acb05d10439e6fb3dce1977e16b78c2f9dc64))

* better state messages ([`837eefa`](https://github.com/fhempy/fhempy/commit/837eefab95ea572b2e9f230e0006230fa9de3113))

* fix name ([`5226e57`](https://github.com/fhempy/fhempy/commit/5226e57de461af82c1ebfeacc878d041b7f2e4cc))

* fix attr handling ([`37c8e38`](https://github.com/fhempy/fhempy/commit/37c8e388e37dbca1fc85a9a3eab0e9103450490d))

* action: auto update controls ([`c2f7914`](https://github.com/fhempy/fhempy/commit/c2f7914126deb014d1d0e6fa8eaeedb38a389eeb))


## v0.1.19 (2021-01-08)

### Unknown

* Merge branch &#39;development&#39; ([`e7d1833`](https://github.com/fhempy/fhempy/commit/e7d18332685968758631667a49d81eec3b72b182))

* version bump ([`2eb6976`](https://github.com/fhempy/fhempy/commit/2eb697644f42eb2992cd8c38937eb13686b26bb7))

* prep ring tests ([`27901c2`](https://github.com/fhempy/fhempy/commit/27901c243bc0b8dfc67f33f74b87e856d31e4f9a))

* add tuya ([`dbfd124`](https://github.com/fhempy/fhempy/commit/dbfd12417e8a5987120bdc3f22e6aa5dd7e58266))

* initial release of tuya module ([`3bf784c`](https://github.com/fhempy/fhempy/commit/3bf784c3f96d2c63935e82489afd3d714671ad72))

* add flake8 complexity, linelength ([`7f2200a`](https://github.com/fhempy/fhempy/commit/7f2200a96a8dfa25e0bf119775d8f4d3251da94d))

* add timeout disconnect ([`4ed7456`](https://github.com/fhempy/fhempy/commit/4ed74562cbd81f4892c81d637cd97e3b9aa0cd12))

* add possibility to add a function_param ([`dc33d62`](https://github.com/fhempy/fhempy/commit/dc33d622659d48e7e9be8ce531622e16e22329c2))

* add launch.json ([`02aa986`](https://github.com/fhempy/fhempy/commit/02aa986fda936ade83303d0f1b8011dae992d568))

* remove reconnect timers ([`819ec3b`](https://github.com/fhempy/fhempy/commit/819ec3bc83db835b2d5b777d98bda937fa3e7335))

* action: auto update controls ([`c127ce8`](https://github.com/fhempy/fhempy/commit/c127ce83d74f93e7165744d1decd4585a0c15c7d))


## v0.1.18 (2021-01-05)

### Unknown

* Merge branch &#39;development&#39; ([`e8fcfde`](https://github.com/fhempy/fhempy/commit/e8fcfde0799c62a1ee2506e8ace8d681780cec38))

* bump version ([`457ef1f`](https://github.com/fhempy/fhempy/commit/457ef1fc78371040d0b5c6a11c104d3ff943d568))

* fix ring alerts ([`039a31f`](https://github.com/fhempy/fhempy/commit/039a31f5b9efb6835ed0c58988bf39fa8e9612db))

* fix typo ([`df4ef29`](https://github.com/fhempy/fhempy/commit/df4ef290daa6a06de28508d0f882f7304b0aad07))

* action: auto update controls ([`d2a6a5d`](https://github.com/fhempy/fhempy/commit/d2a6a5d113af0f7e52fd69bc331fda503d7b9f0a))


## v0.1.17 (2021-01-05)

### Unknown

* Merge branch &#39;development&#39; ([`e85520d`](https://github.com/fhempy/fhempy/commit/e85520d38d78860ebfdafb6b32e0b3ade3da1874))

* version bump ([`b0e3e58`](https://github.com/fhempy/fhempy/commit/b0e3e5866195585d2d58c7efe1cc82c59f629d54))

* fix handle_attr test ([`7739cce`](https://github.com/fhempy/fhempy/commit/7739ccef4d78d7c25cc0c83ff1e3952a96f0e58e))

* enable flake8 ([`b455863`](https://github.com/fhempy/fhempy/commit/b4558632d6fb19a8593cdd3b5ffc6e8092c321fc))

* update python-miio 0.5.4 ([`c91daaf`](https://github.com/fhempy/fhempy/commit/c91daaf85451e89730920109d6ddd6cc65ea53ad))

* fix startup ([`46be779`](https://github.com/fhempy/fhempy/commit/46be7796534211cf39ee05c9d86b71243292c850))

* fix update readings ([`5f9cd2a`](https://github.com/fhempy/fhempy/commit/5f9cd2a17f096c63ac4b8aba97dc8f04d41ed93c))

* action: auto update controls ([`f88519a`](https://github.com/fhempy/fhempy/commit/f88519ace87163d8f5e0a78c9a1782e9fec384c3))


## v0.1.16 (2021-01-05)

### Unknown

* Merge branch &#39;development&#39; ([`418c13a`](https://github.com/fhempy/fhempy/commit/418c13a14c8b2ae9c9295796096fcfd580a79d26))

* bump version ([`d24c02d`](https://github.com/fhempy/fhempy/commit/d24c02dbd95b2a9cac11d8770a453b7101ea312e))

* fix ring commands ([`e0b10d2`](https://github.com/fhempy/fhempy/commit/e0b10d2d34358582e06c2d0057111d5c95e1f8e2))

* action: auto update controls ([`8f5ea8f`](https://github.com/fhempy/fhempy/commit/8f5ea8febceb8283312d6261839c3b5d332a2e6d))


## v0.1.15 (2021-01-05)

### Unknown

* Merge branch &#39;development&#39; ([`5bf23b3`](https://github.com/fhempy/fhempy/commit/5bf23b30385854a01cdde4602d2ef405b184034d))

* bump version ([`aa3dc8c`](https://github.com/fhempy/fhempy/commit/aa3dc8c2f7a870ac9179eef6fa6755eeaafe6e5a))

* fix attribute handling ([`e105e3a`](https://github.com/fhempy/fhempy/commit/e105e3a289ca055c4f075efd3769d8cab9393d75))

* action: auto update controls ([`4784a5d`](https://github.com/fhempy/fhempy/commit/4784a5d029f8f64ffeb0118a76861eb814ea2cbc))


## v0.1.14 (2021-01-05)

### Unknown

* update controls ([`9f2b709`](https://github.com/fhempy/fhempy/commit/9f2b709da0b6cdfae33582ffd9b1c655dbb42a59))

* Merge branch &#39;development&#39; ([`17fd227`](https://github.com/fhempy/fhempy/commit/17fd227d023f00fc904e8db92def0b671e86b9df))

* version bump ([`44988cb`](https://github.com/fhempy/fhempy/commit/44988cb6830d2c7729f9982d1019f29c41db8733))

* remove assert False ([`42f560d`](https://github.com/fhempy/fhempy/commit/42f560d1e7cbe7e863b28f9067815d275a9df6cb))

* add googlecast tests ([`4e583bc`](https://github.com/fhempy/fhempy/commit/4e583bc8e88e9fe1f0ef10db7059c43e434a84e4))

* add run_blocking parameter check ([`d4cc4b8`](https://github.com/fhempy/fhempy/commit/d4cc4b8421dded925c54bdf60f4af468a22af5c5))

* fix Spotify issues ([`97767d0`](https://github.com/fhempy/fhempy/commit/97767d080839b9c8686a39a42b177c060465cd30))

* prepare for better testing ([`e022e45`](https://github.com/fhempy/fhempy/commit/e022e456ffb422f619f168841865ae580d7cad60))

* fix attribute handling ([`eee6f1b`](https://github.com/fhempy/fhempy/commit/eee6f1b9cb2526b125fa1f64cfa3c233633d855b))

* update tests ([`a7de12f`](https://github.com/fhempy/fhempy/commit/a7de12f94231de2d581db0711852dafdcfa0b527))

* close aiohttp session
add spotify
fix await ([`214dd78`](https://github.com/fhempy/fhempy/commit/214dd7889842516efcde6781157ab606e75f1b53))

* better define test handling ([`9ccb6e9`](https://github.com/fhempy/fhempy/commit/9ccb6e9e2cf8f46fc054ca308f73d671cc5d2a65))

* add more tests ([`09c9e4e`](https://github.com/fhempy/fhempy/commit/09c9e4e82d5c2c3a843d0fc614664938a839f77e))

* add vscode settings ([`c86c1e1`](https://github.com/fhempy/fhempy/commit/c86c1e1fd1164f59ca487e18bb265d882cfe4a37))

* add more libraries to be prepared for bluetooth ([`b3a5609`](https://github.com/fhempy/fhempy/commit/b3a5609a9ca34b33b6d4a3eac149b078b4481df3))

* add requirements for testing ([`906169a`](https://github.com/fhempy/fhempy/commit/906169a532bc70c66b8ed1c6dcd73fe57c9eaaea))

* add readingFnAttributes ([`25355f8`](https://github.com/fhempy/fhempy/commit/25355f84454caf293483ca24950e4bfb26867ff0))

* better info msgs ([`0ab7474`](https://github.com/fhempy/fhempy/commit/0ab7474e4a192bae7118f591e126bc6bed22ee90))

* fix Usage ([`e366274`](https://github.com/fhempy/fhempy/commit/e3662743048b2c4749f05099ca574e0baf1e9802))

* move ssdp to core ([`cfcbf30`](https://github.com/fhempy/fhempy/commit/cfcbf3018acf7d0245a59c15fbc8ee4fe96ba0db))

* use FhemModule ([`df96521`](https://github.com/fhempy/fhempy/commit/df965218189cd1d26e395e174d7fb5e5eeed1f2c))

* support object_detection on x86_64 and rpi ([`b816c75`](https://github.com/fhempy/fhempy/commit/b816c7526c28087b585bac93f5b65f45f89c543a))

* include .pm files ([`f5755ec`](https://github.com/fhempy/fhempy/commit/f5755ec52d3ee6f296d0e34fdd11b81fbbc6a172))

* fix install packages ([`76784c5`](https://github.com/fhempy/fhempy/commit/76784c5df81e576198f85d3238c7c69d4f22cb2e))

* ring only on 1 device ([`6967b4e`](https://github.com/fhempy/fhempy/commit/6967b4ef3a25a29a1e9e11e2024c7eadceb17cc6))

* add test_utils pytest ([`f2c1429`](https://github.com/fhempy/fhempy/commit/f2c14294ce8c40745bd62a834c9e57a36a8e80a4))

* use set_... params for all set_... functions ([`70b6b5c`](https://github.com/fhempy/fhempy/commit/70b6b5c2f008c04d9b31bc073ce961f1c55607cf))

* add spotify_connect_player (in dev, not working) ([`e85b355`](https://github.com/fhempy/fhempy/commit/e85b355638166308f2c2c59ee664cc21b8980c4b))

* update ([`def5a8e`](https://github.com/fhempy/fhempy/commit/def5a8e0dbc69ed0f580c6c6015a13711058230b))

* move to pip and therefore only bin/fhempy needed ([`ea89448`](https://github.com/fhempy/fhempy/commit/ea8944807fba148c91d8abc57444e3cf703efc35))

* typo ([`5c0a05d`](https://github.com/fhempy/fhempy/commit/5c0a05d2dd17146414031e1b25f130f39ffe4cc5))

* fix update ([`d2c9f3c`](https://github.com/fhempy/fhempy/commit/d2c9f3cc855c7e446d6ca72371c15366445b7126))

* action: auto update controls ([`5d5d3c6`](https://github.com/fhempy/fhempy/commit/5d5d3c65030de969bacc5de87de446bbfb6ab614))


## v0.1.13 (2020-12-31)

### Unknown

* Merge branch &#39;development&#39; ([`c22e818`](https://github.com/fhempy/fhempy/commit/c22e8183eb320fced0d689fc2939636414e3c757))

* version bump ([`030b9fd`](https://github.com/fhempy/fhempy/commit/030b9fd4e16f23a2bad845468c6a896f8936be39))

* Merge branch &#39;development&#39; ([`9dbd16e`](https://github.com/fhempy/fhempy/commit/9dbd16e1f7bdcda7691e2d5bee4c1b58486b146b))

* install requirements via pip ([`e87ed0b`](https://github.com/fhempy/fhempy/commit/e87ed0b5fa5570ce9dcee0a1b92a80e3ecc8dfab))

* allow update for local fhempy ([`9c230b3`](https://github.com/fhempy/fhempy/commit/9c230b3d54f8913230ccaff877e679fbef43370e))

* fix 127.0.1.1 issue ([`fac9fe4`](https://github.com/fhempy/fhempy/commit/fac9fe49f78a14175929e7dceee0c4d01e73cf2c))

* fix shuffle, volume ([`d5203b2`](https://github.com/fhempy/fhempy/commit/d5203b2fa775eb3cf4969d5372a25779e782c6b0))

* fix volume ([`c58d30f`](https://github.com/fhempy/fhempy/commit/c58d30f12811d3793a9b35e3447c75b279261102))

* store only needed data in javascript ([`6590a6e`](https://github.com/fhempy/fhempy/commit/6590a6e8923e5a29df791e7435f835956d30ff3b))

* delete old readings on startup ([`002091c`](https://github.com/fhempy/fhempy/commit/002091c47f61b6c6367e8bd3543f3ae0a81b8fd4))

* action: auto update controls ([`5f1b1d3`](https://github.com/fhempy/fhempy/commit/5f1b1d3674264a5a2e002146d7ff62c7ba94fe83))


## v0.1.12 (2020-12-30)

### Unknown

* update controls ([`f23282e`](https://github.com/fhempy/fhempy/commit/f23282e5e4fe842614d7cddf1f76e4395d9af94d))

* Merge branch &#39;development&#39; ([`626987f`](https://github.com/fhempy/fhempy/commit/626987fab0d197a8b7e08d53ffffed4b58953030))

* version bump ([`dad8d46`](https://github.com/fhempy/fhempy/commit/dad8d462da0452f2cd3009779fe66ada932fdf51))

* fix ([`d02e609`](https://github.com/fhempy/fhempy/commit/d02e609f819199e2afc33fcd6572a1709216c678))

* fix ([`1924ea8`](https://github.com/fhempy/fhempy/commit/1924ea8835a64fc7756f4dff1a3d601126595207))

* update controls ([`b0ef79d`](https://github.com/fhempy/fhempy/commit/b0ef79dad964be533eb811132d9d7e2bd049dcb5))

* Merge branch &#39;development&#39; ([`b810716`](https://github.com/fhempy/fhempy/commit/b8107166c094a8709a5fc47812b2c03b44e3ca3e))

* fix play favorites again ([`e96762f`](https://github.com/fhempy/fhempy/commit/e96762f455cd01310bdfd1b0041c5f7bdac96d52))

* action: auto update controls ([`d93202d`](https://github.com/fhempy/fhempy/commit/d93202d5c92ed9de6fb46fe7458a656c4352ee1b))


## v0.1.11 (2020-12-30)

### Unknown

* fix controls ([`ddf6e9a`](https://github.com/fhempy/fhempy/commit/ddf6e9a8642cc930e656f0ff1ea5418a68cc4192))

* update controls ([`6993d8d`](https://github.com/fhempy/fhempy/commit/6993d8d8ad8243f52102f6df0703b510f7f7c29f))

* Merge branch &#39;development&#39; ([`56b595a`](https://github.com/fhempy/fhempy/commit/56b595a77e1b8fe2513fc999a403016e9a05f713))

* bump version ([`da3205b`](https://github.com/fhempy/fhempy/commit/da3205bc241779c3b829555eca79b2f6607e1d29))

* fix bug for some attributes ([`21bde3c`](https://github.com/fhempy/fhempy/commit/21bde3cc687d2557d1a8d7a124f82e326804816f))

* fix possible bug if ip is not available ([`b83e6b0`](https://github.com/fhempy/fhempy/commit/b83e6b062d68fae3fe086dd5d0c38ec860f8b23e))

* support shuffle, volume, transfer_playback ([`09f54f4`](https://github.com/fhempy/fhempy/commit/09f54f4b0e8f7d85bc699f9fef136c407606abb1))

* fix messages ([`474d811`](https://github.com/fhempy/fhempy/commit/474d811f39cbaa88512c894ae86ef7c131ed5424))

* fix pause,next,prev,stop ([`a8c214c`](https://github.com/fhempy/fhempy/commit/a8c214c8a9a61aea9e359d3c911ebaf341d0ee74))

* fix play favorite ([`7aa7b26`](https://github.com/fhempy/fhempy/commit/7aa7b26878057f86847296b729c2fc8686598008))

* rename to fhempy ([`9d9d1a3`](https://github.com/fhempy/fhempy/commit/9d9d1a3725e2b23ff4d39e879e314d0fa096b821))

* change days 60=&gt;40 ([`aaa9087`](https://github.com/fhempy/fhempy/commit/aaa9087cd5e735cee6bbf3a93965e75994452010))

* action: auto update controls ([`6d4b4f5`](https://github.com/fhempy/fhempy/commit/6d4b4f58e3c9fb5342e0e9abdedefc9ea50d7adf))


## v0.1.10 (2020-12-29)

### Unknown

* update controls ([`6cf5a89`](https://github.com/fhempy/fhempy/commit/6cf5a897a07c5395e8b6d8964361a8b3d591d743))

* Merge branch &#39;development&#39; ([`380d932`](https://github.com/fhempy/fhempy/commit/380d93242f32c5467e685206ff1b96b12e91063d))

* bump version ([`3ce34d7`](https://github.com/fhempy/fhempy/commit/3ce34d7d051100e80f12aa92e159a111d3361801))

* update controls ([`0891d43`](https://github.com/fhempy/fhempy/commit/0891d436559dbf4f7d08904f28029c87f96bb4fd))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`3c24157`](https://github.com/fhempy/fhempy/commit/3c241570067861e94c6c47e5528822af1765387a))

* Merge branch &#39;development&#39; ([`5d396ac`](https://github.com/fhempy/fhempy/commit/5d396ac9375e6920ffffd32f25ec6697ff8cea32))

* add spotify connect incl. web player ([`cfe01b4`](https://github.com/fhempy/fhempy/commit/cfe01b4bd9b54d9ee8d136f4979e3c086d0e055e))

* fix table for pypi ([`de584b0`](https://github.com/fhempy/fhempy/commit/de584b0980ac3887ad5f06b6d8b3945621a32a63))

* action: auto update controls ([`5e82c56`](https://github.com/fhempy/fhempy/commit/5e82c560293f95b46d5867025d566f9a552e8ada))


## v0.1.9 (2020-12-28)

### Unknown

* update controls ([`c72b206`](https://github.com/fhempy/fhempy/commit/c72b206b49ffdca1913ef7f65f46a0d0d9b3ff35))

* Merge branch &#39;development&#39; ([`2948fdb`](https://github.com/fhempy/fhempy/commit/2948fdb9003d184612d74415a60df30e286aaad8))

* bump version ([`57af469`](https://github.com/fhempy/fhempy/commit/57af4691d8e0ad990b3c4365947838eaf2bb429e))

* Merge branch &#39;development&#39; ([`c7e4f0c`](https://github.com/fhempy/fhempy/commit/c7e4f0c06c038d168de4aec6a0a181953bfabcb3))

* add startSpotify ([`fb88766`](https://github.com/fhempy/fhempy/commit/fb887663d8a8fa67bad977928e1c27ca807529f6))

* fix play ([`0f2c137`](https://github.com/fhempy/fhempy/commit/0f2c137ab75eece44f423d26f43d756815ee0a6c))

* action: auto update controls ([`2abbdc9`](https://github.com/fhempy/fhempy/commit/2abbdc9f7d954c7c1e05a986c9761ae87a7a3d84))


## v0.1.8 (2020-12-25)

### Unknown

* version bump ([`c7bd925`](https://github.com/fhempy/fhempy/commit/c7bd925713dd29ba48443a52ad3460ff09260296))

* Merge branch &#39;development&#39; ([`b25e179`](https://github.com/fhempy/fhempy/commit/b25e17979a48dc46c0b776e3c034d0494d5e8984))

* version bump ([`3cde499`](https://github.com/fhempy/fhempy/commit/3cde4999395020de214c5026b391827aae658f59))

* update controls ([`e779e20`](https://github.com/fhempy/fhempy/commit/e779e206ae8b4f702fecd6c49c90be80a35623bf))

* Merge branch &#39;development&#39; ([`f845eef`](https://github.com/fhempy/fhempy/commit/f845eefd3ae037d6fb6b23d00d4386849471e0ef))

* add more info ([`fbd74df`](https://github.com/fhempy/fhempy/commit/fbd74df3eba51f51296d5d472955352067291159))

* add coffee link ([`9d528d0`](https://github.com/fhempy/fhempy/commit/9d528d04f7cf82c93101281805960e4c0bbb47f5))

* add spotify usage ([`1c86894`](https://github.com/fhempy/fhempy/commit/1c8689475ca90b5ecf321e3de0c62912be030600))

* add Spotify info ([`077b705`](https://github.com/fhempy/fhempy/commit/077b705672ce7a58925f0e28d06adc8a4975642d))

* bugfix: missing do_trigger ([`b4babfb`](https://github.com/fhempy/fhempy/commit/b4babfbf02296b23edfb8b754d6ea3c631d7033e))

* fix some threading bugs ([`6ed00ed`](https://github.com/fhempy/fhempy/commit/6ed00edbb0fd3913cdd87926d0aa64ec8843f7fb))

* support Spotify
use FhemModule ([`d63491a`](https://github.com/fhempy/fhempy/commit/d63491a3d9430434b790ccc6597821c3d11ac49e))

* support function in attr_conf ([`80012a7`](https://github.com/fhempy/fhempy/commit/80012a7e544d528a7302fad3d5ca9e279657f29a))

* add self.loop
set hash before handle_define_attr ([`0f85d1b`](https://github.com/fhempy/fhempy/commit/0f85d1b601ad4298cbb7989ce37d08a53296352f))

* fix prepare script ([`6d0e072`](https://github.com/fhempy/fhempy/commit/6d0e0723e85be0cf7e1afc1403ad4c54af4f668d))

* fix controls ([`1034978`](https://github.com/fhempy/fhempy/commit/10349780e74df46eedcb2ec2a0ebdd7654bf8a0c))

* update controls ([`43265fe`](https://github.com/fhempy/fhempy/commit/43265fe8318a062561d6284c5a57e043f80f6797))

* Merge branch &#39;development&#39; ([`2510c57`](https://github.com/fhempy/fhempy/commit/2510c57717282e51f83b3b332c8e1b9eb2a43284))

* fix FHEM update ([`e2d14c9`](https://github.com/fhempy/fhempy/commit/e2d14c9f0847023c4005ad64e53be57f2ae9aef5))

* action: auto update controls ([`0ed2b2c`](https://github.com/fhempy/fhempy/commit/0ed2b2c3b5151f4d97af1b72ff99c50542ee65ca))


## v0.1.7 (2020-12-22)

### Unknown

* update controls ([`81544f5`](https://github.com/fhempy/fhempy/commit/81544f53337c275a26c12b21b2e73e859596d01c))

* Merge branch &#39;development&#39; ([`2674c52`](https://github.com/fhempy/fhempy/commit/2674c52403fc91c0bf679a9dd3ad95da39ebdf31))

* version bump ([`75e0104`](https://github.com/fhempy/fhempy/commit/75e01042b9f8c67ad996f6dbb3aad1f137e7bec4))

* Merge branch &#39;development&#39; ([`91a4e9c`](https://github.com/fhempy/fhempy/commit/91a4e9c5e1af559746d6ae2ed7609b475f443de6))

* update readme ([`1e0d57f`](https://github.com/fhempy/fhempy/commit/1e0d57fdf95a50a920a58af91548bb82fc8aff9c))

* update controls ([`5e181f7`](https://github.com/fhempy/fhempy/commit/5e181f762e2d2ae01032862c505fdd9926c96848))

* Merge branch &#39;development&#39; ([`9179c30`](https://github.com/fhempy/fhempy/commit/9179c308b3773543de720c99ee0cb808746ff633))

* add MOV fhempy to avoid issues with older versions ([`c1890de`](https://github.com/fhempy/fhempy/commit/c1890de4484349cd64186572ff88d1302d2a2c7b))

* fix shields ([`405b0d0`](https://github.com/fhempy/fhempy/commit/405b0d093490f29985e255d86e6e596d8b72a75f))

* update readme ([`b2bd0ee`](https://github.com/fhempy/fhempy/commit/b2bd0ee4ce47397331d5c55a5b3a1f100f8ba68c))

* fix help text ([`c691e79`](https://github.com/fhempy/fhempy/commit/c691e7978ed6c785cfcb48102dd4e16806f14eca))

* update changed ([`2ed04f9`](https://github.com/fhempy/fhempy/commit/2ed04f904cee104f7a6b21c28f7b1c3e0e5bcee4))

* support create device out of xiaomi_token ([`bc2dcc9`](https://github.com/fhempy/fhempy/commit/bc2dcc9b5b623ad132ed16e75315be9b21172ed8))

* one line import ([`ab3cfd6`](https://github.com/fhempy/fhempy/commit/ab3cfd63d413a305836fb7273c0179261693159a))

* save username/password encrypted
always retrieve de,cn,sg servers ([`91a3f4c`](https://github.com/fhempy/fhempy/commit/91a3f4cba47e3c62c0f2b1445329e445fee8c503))

* fix python version detection ([`69708ae`](https://github.com/fhempy/fhempy/commit/69708aef964f73c439ef3e1fb8c47952cf8c353d))

* fix issues for attr_conf without default ([`c3bc585`](https://github.com/fhempy/fhempy/commit/c3bc5852d7e883e5f8b2f467e9cad115d0838647))

* avoid too many log messages on auto restart ([`7257fff`](https://github.com/fhempy/fhempy/commit/7257fffdc4010c855139deabb02fe8888ae916af))

* remove try/except from run_blocking ([`d1178b6`](https://github.com/fhempy/fhempy/commit/d1178b6ba7ba2ead343b00ba1d584cfa4e08c45e))

* use state instead of presence ([`1d73b0c`](https://github.com/fhempy/fhempy/commit/1d73b0cf2397fb694dcbb986b2b65aa2596fb52c))

* change error log to debug ([`3f09be3`](https://github.com/fhempy/fhempy/commit/3f09be344ab9addfd9402a1c94a250ffaf1d2a6f))

* fix possible deadlock ([`d011605`](https://github.com/fhempy/fhempy/commit/d011605785dac49633a6260fa19890b1400a4b7c))

* handle stats ([`c955ee4`](https://github.com/fhempy/fhempy/commit/c955ee47c9ba50c160fbf46689ac619bf3167857))

* support BLE
use latest AlexxIT code ([`c7e7560`](https://github.com/fhempy/fhempy/commit/c7e75603b39ef25979a0a8018863e58d061ba6ed))

* use relative import ([`39b3f1f`](https://github.com/fhempy/fhempy/commit/39b3f1f7712312b8b0b66b970e74f6a565d153e6))

* add ip addr ([`d4e412c`](https://github.com/fhempy/fhempy/commit/d4e412c27219c2f0bd7e3ec72a039512277919f2))

* initial working version, just on/off ([`01452d3`](https://github.com/fhempy/fhempy/commit/01452d37f7c2c3181108262094aa53a5a47baa4e))

* create ble library to be used by modules ([`165a79b`](https://github.com/fhempy/fhempy/commit/165a79bb1a2f414bae51d72a81cfac0d08970b36))

* add xiaomi_gateway3 readme ([`de88bd5`](https://github.com/fhempy/fhempy/commit/de88bd5b6f1493d9d48aaa8019ca1565baa304f0))

* update readme ([`d06e9a8`](https://github.com/fhempy/fhempy/commit/d06e9a8e9131b4b635286ade83e288e24524a7bd))

* hint for new firmware ([`e20f7c9`](https://github.com/fhempy/fhempy/commit/e20f7c9a66af10eb6080c05ddb2a151e05d9d132))

* better readme ([`74cb0b8`](https://github.com/fhempy/fhempy/commit/74cb0b8deb062f84934209ba872452c0e3d1ca44))

* fix &#34;too many params&#34; ([`2c7ff8a`](https://github.com/fhempy/fhempy/commit/2c7ff8a9bf2b0b00ea5cfc89db318e708e6f9434))

* add more infos ([`593b304`](https://github.com/fhempy/fhempy/commit/593b3042cc13d878841429cc239f82110292bfeb))

* fix cmdIcon, webCmd ([`5508629`](https://github.com/fhempy/fhempy/commit/5508629b27de6494d7439f9633be7a8e8ca896da))

* handle to many arguments in set ([`d3c17f9`](https://github.com/fhempy/fhempy/commit/d3c17f90be25811ba7c7ff5f6eb99e007d93f145))

* use relative import ([`b670e28`](https://github.com/fhempy/fhempy/commit/b670e28468d9fcdb8b426434c7fb0c44a1c6036e))

* fix version check ([`d594305`](https://github.com/fhempy/fhempy/commit/d594305bf1c35e0122d2f6484060c49e9d495cba))

* reload page hint ([`817f64d`](https://github.com/fhempy/fhempy/commit/817f64d9919bd44de24f389e19f390fb916bc708))

* fix warning of uninitialized value ([`e544dde`](https://github.com/fhempy/fhempy/commit/e544ddef2e0464603d822c99e78c3b3d4bcea09c))

* add exception log ([`2f5beba`](https://github.com/fhempy/fhempy/commit/2f5bebae4116f61d907a6c2f81d94f316323f3b8))

* move fhempy file away ([`3453a1a`](https://github.com/fhempy/fhempy/commit/3453a1af840d6e4a4ac5325ce551fa22b54fe172))

* fix controls ([`3d69a21`](https://github.com/fhempy/fhempy/commit/3d69a21f1f9214966aee8b6e70c3e414fc452988))

* fix prepare ([`f2546c4`](https://github.com/fhempy/fhempy/commit/f2546c4021ace1a3002683cad966d85809705c6d))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`1187135`](https://github.com/fhempy/fhempy/commit/118713548ac9ea6cad8f51c787e99d666478e5d9))

* Merge branch &#39;development&#39; ([`6ab28d2`](https://github.com/fhempy/fhempy/commit/6ab28d212ba452e117157a3745bda47b620d1465))

* fix readme links ([`c1a42d9`](https://github.com/fhempy/fhempy/commit/c1a42d94429b298c8c678538b9964be5f07f95a6))

* action: auto update controls ([`ee30e0a`](https://github.com/fhempy/fhempy/commit/ee30e0a41be38b31e6669297f67703192efb5922))

* Merge branch &#39;development&#39; ([`8b689ab`](https://github.com/fhempy/fhempy/commit/8b689ab530bc73ec7f8e31a0dca03821deaf215f))

* bump version ([`cda83fd`](https://github.com/fhempy/fhempy/commit/cda83fdc5ab624b7b81f2939324124fdcc137cb7))


## v0.1.6 (2020-12-09)

### Unknown

* Merge branch &#39;development&#39; ([`9843d6d`](https://github.com/fhempy/fhempy/commit/9843d6d3dd602242aa8c226db9b73354984e1411))

* add newline at eof ([`2600844`](https://github.com/fhempy/fhempy/commit/260084427acb00374a74130c4b55ecd3bbce126b))

* restructure for proper pip package ([`8ea1d07`](https://github.com/fhempy/fhempy/commit/8ea1d07618aebd3fd51d7bcd39004e49e76cc8c7))

* typo ([`ef0f77b`](https://github.com/fhempy/fhempy/commit/ef0f77b4f99fe0496f1c1fb2e488c037ba9f559a))

* update readme with autodiscovery ([`498bd68`](https://github.com/fhempy/fhempy/commit/498bd687cd032e8d85e63377dbd0dfcf1b40166e))

* fix possible bug if devhash not defined ([`f01500e`](https://github.com/fhempy/fhempy/commit/f01500e5420b9d3161a008fcb1679dfbd2f77bf1))

* internal zeroconf usage ([`42d9bc5`](https://github.com/fhempy/fhempy/commit/42d9bc58aba505bd8b537b53576a9022b8ba3291))

* fix error ([`99dc90d`](https://github.com/fhempy/fhempy/commit/99dc90d61ef0e67d29e704f72f519a8b05a4eae2))

* use internal zeroconf ([`73909ce`](https://github.com/fhempy/fhempy/commit/73909ce9982a78c925d4a4068ef311fed8a4c4e8))

* internal zeroconf module ([`a197342`](https://github.com/fhempy/fhempy/commit/a19734238270c3c3491848bc4cc9cbdb10251ae0))

* add upgrade ([`48c2f08`](https://github.com/fhempy/fhempy/commit/48c2f08d9e122a8c81c9db72d66aa4324a552b0e))

* add wait before status request ([`242dfc3`](https://github.com/fhempy/fhempy/commit/242dfc349d5317106ff716c166655e643fae6137))

* fix autodiscover of peers via mdns ([`5cbb05f`](https://github.com/fhempy/fhempy/commit/5cbb05f917bea153963e3822d3110238bccdb5ea))

* fix lungo typo ([`639caf5`](https://github.com/fhempy/fhempy/commit/639caf5cbcbae85d89bec24058cc5fab523537b4))

* Merge branch &#39;development&#39; ([`e42694b`](https://github.com/fhempy/fhempy/commit/e42694bb18e5bff8e2b55ed94046ec5712ed9c97))

* use fhempy by user pi ([`014e907`](https://github.com/fhempy/fhempy/commit/014e907bbefa0c0f6eda2a471786d63e7e83d147))

* try to fix controls commit ([`6986324`](https://github.com/fhempy/fhempy/commit/698632469bccd0ae405fc93ae3815c08b51cd22b))

* action: auto update controls ([`05c3e5a`](https://github.com/fhempy/fhempy/commit/05c3e5a0274d318f2c312f1fcc77a4c82424bc23))


## v0.1.5 (2020-12-07)

### Unknown

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`c287f0f`](https://github.com/fhempy/fhempy/commit/c287f0fe8120f61caa825b242c29bba24701385e))

* Merge branch &#39;development&#39; ([`f1d4699`](https://github.com/fhempy/fhempy/commit/f1d4699b8f71dd6b4bde971644e6703abf875daf))

* version bump ([`efe6fcb`](https://github.com/fhempy/fhempy/commit/efe6fcbec74e80a0eee8545f35417d1e13075733))

* action: auto update controls ([`5eef54b`](https://github.com/fhempy/fhempy/commit/5eef54b99f65756d65973903b75869c5ba5a3479))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`04aade7`](https://github.com/fhempy/fhempy/commit/04aade78f40d63dd92b86a91eef611d714731776))

* Merge branch &#39;development&#39; ([`9bca24e`](https://github.com/fhempy/fhempy/commit/9bca24e57047143deb61470cd4827cdeef15047a))

* fix zeroconf remote peer ([`2116824`](https://github.com/fhempy/fhempy/commit/2116824287d9cd81611c8e19bb36c41acae52139))

* action: auto update controls ([`16d7cae`](https://github.com/fhempy/fhempy/commit/16d7cae9a7ce6369106acff245bd6c2e243d8b8a))


## v0.1.4 (2020-12-07)

### Unknown

* Merge branch &#39;development&#39; ([`f81e2eb`](https://github.com/fhempy/fhempy/commit/f81e2eb8de7ccde36fc5cec58e175c96be9cdf4a))

* version bump ([`2d581a4`](https://github.com/fhempy/fhempy/commit/2d581a4e73ec2a2257ffa33fbd6bce48af743c86))

* clearify change msg ([`69deced`](https://github.com/fhempy/fhempy/commit/69deced9b8fb0435ed8b09cee8139c604a0b5a7a))

* autodiscover remote peers ([`a8758db`](https://github.com/fhempy/fhempy/commit/a8758db1d9e636c9e20afdc3ff3953bfd292f7cf))

* black formatting ([`094ae6d`](https://github.com/fhempy/fhempy/commit/094ae6d2d1445d4a4382a5ada664419c9dbe36c2))

* core zeroconf service ([`397be93`](https://github.com/fhempy/fhempy/commit/397be93fca015d271c4d33f631ea085613ea3f64))

* fix status loop
fix bug when no reply ([`cab3f08`](https://github.com/fhempy/fhempy/commit/cab3f0885b216962a97ec3870eeeab142004f7f6))

* use setDevAttrList ([`7718346`](https://github.com/fhempy/fhempy/commit/77183464ccc018b3b73407cad9c2b92d5a25de7c))

* remove update for local bindings ([`f7f0458`](https://github.com/fhempy/fhempy/commit/f7f045821b40e8b79c44f81202aac89d1d192013))

* action: auto update controls ([`f51a447`](https://github.com/fhempy/fhempy/commit/f51a44765d5822f19e5e9afba1aabbe6817e4ca3))

* fix checkout ([`e6ef2a1`](https://github.com/fhempy/fhempy/commit/e6ef2a11377b5e86bfb3e0b87f324cdf88c2a99b))


## v0.1.3 (2020-12-05)

### Unknown

* Merge branch &#39;development&#39; ([`12ae023`](https://github.com/fhempy/fhempy/commit/12ae023499231c44b67fc6e02b7e4f3f55885ccb))

* bugfix ([`a480e2a`](https://github.com/fhempy/fhempy/commit/a480e2abbec68c4d51443abe0e64b256ffc0cc4d))

* black code formatting ([`0fd8e32`](https://github.com/fhempy/fhempy/commit/0fd8e322c875bd468cf8fbb8db222f0b457d9523))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`6f9a73b`](https://github.com/fhempy/fhempy/commit/6f9a73bdb7e43560f6d5356ec3ae3ecc3a0c2336))

* fix release ([`f9630b5`](https://github.com/fhempy/fhempy/commit/f9630b5c38ba1bcad547656a40e58a582e511289))

* action: auto update controls ([`08e5622`](https://github.com/fhempy/fhempy/commit/08e56228bfcb19e5f30ccd2e2a2771456bf8c96a))


## v0.1.2 (2020-12-05)

### Fix

* fix: need module ([`de7c2fa`](https://github.com/fhempy/fhempy/commit/de7c2fac248ec45ae1bb21e188cc86d251aab741))

* fix: loop ([`b968e3d`](https://github.com/fhempy/fhempy/commit/b968e3d97485a7d3b216edaaad772236052bc28a))

* fix: param is optional ([`6112d9a`](https://github.com/fhempy/fhempy/commit/6112d9a7da98dff9ce14dad6b14218296a917e05))

* fix: str concat int ([`c693afb`](https://github.com/fhempy/fhempy/commit/c693afbc131e4f53db0f6a8efa8aba436c670a20))

### Unknown

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`764ae49`](https://github.com/fhempy/fhempy/commit/764ae4903f29132b91fd7321d334cfe1f6c18a57))

* Merge branch &#39;development&#39; ([`69acff5`](https://github.com/fhempy/fhempy/commit/69acff5bb4614ebb20d12541225d8fd23940dbe6))

* bump version to 0.1.2 ([`6a9162e`](https://github.com/fhempy/fhempy/commit/6a9162ea9f6753b8f56d68a921dab44b81313bd5))

* Delete python-publish.yml ([`6207761`](https://github.com/fhempy/fhempy/commit/62077617ce7b1e4848a788105f9003a496684dcd))

* add pip package creation ([`29a9487`](https://github.com/fhempy/fhempy/commit/29a948790f387723d1c6c939327a5a21586fcdb9))

* action: auto update controls ([`3e14629`](https://github.com/fhempy/fhempy/commit/3e14629d05d4e67dbaf642ffcbac084529d4b046))

* fix ([`c4430d0`](https://github.com/fhempy/fhempy/commit/c4430d08de679b9094bea37b86360796aadbc7bd))

* update ([`e73f88a`](https://github.com/fhempy/fhempy/commit/e73f88a6503197a887781d8465671561dcf418cb))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`3310201`](https://github.com/fhempy/fhempy/commit/33102013fd6f8a80f1b6731da157829704041f0e))

* update controls ([`0ff04a3`](https://github.com/fhempy/fhempy/commit/0ff04a33ee839909d865f97c585a71b03d7344e6))

* Merge branch &#39;development&#39; ([`dc1ae8e`](https://github.com/fhempy/fhempy/commit/dc1ae8e1e443c5b6bb38569a7d436b1a75fadc7d))

* fix prepare
remove release and use actions ([`b5acaec`](https://github.com/fhempy/fhempy/commit/b5acaec4989ef87d02f31d0e4dc88eaf35b49fe4))

* prepare auto controls update ([`375c2b6`](https://github.com/fhempy/fhempy/commit/375c2b613fbc7671f6f63e86824317856187f304))

* update remote peers on update ([`fdde17b`](https://github.com/fhempy/fhempy/commit/fdde17b21cf2e7f83dd3b4006e15cea4310f63dd))

* rename to fhempy ([`f17cea8`](https://github.com/fhempy/fhempy/commit/f17cea8e6c8ead62487955ebb1f68b01ab284ff1))

* Merge branch &#39;development&#39; ([`ddb652d`](https://github.com/fhempy/fhempy/commit/ddb652dc709640cf1741978ba77457c4caee2ef4))

* update readme links ([`9d86dc9`](https://github.com/fhempy/fhempy/commit/9d86dc9e4421faf1838a4d224ce6feeb103ddd95))

* update controls ([`452057c`](https://github.com/fhempy/fhempy/commit/452057c14d8e7f62876b027cc3e8bc8a459389a6))

* Merge branch &#39;development&#39; ([`6ee3a26`](https://github.com/fhempy/fhempy/commit/6ee3a26184b8b030f3a03a80e1da44091627e990))

* update readme ([`250ea93`](https://github.com/fhempy/fhempy/commit/250ea936880c8f7bee5c7dad6f02f45c5c4654d0))

* Merge branch &#39;development&#39; ([`9471fbf`](https://github.com/fhempy/fhempy/commit/9471fbfc354e3caac9bfd1cca97d471944021065))

* use FhemModule ([`382fc10`](https://github.com/fhempy/fhempy/commit/382fc10e793acab888ece208a7cc3066e9a331e3))

* save self.hash ([`cc951bd`](https://github.com/fhempy/fhempy/commit/cc951bd3a18071830eb311717b70c043a361d74f))

* fix ([`99590eb`](https://github.com/fhempy/fhempy/commit/99590eb08a1f8358a56c99fe873275c0d81b3c6e))

* remove links ([`ecaf384`](https://github.com/fhempy/fhempy/commit/ecaf384ea11f7176481c935ae6053455f90ea272))

* some more shields ([`2bb1c57`](https://github.com/fhempy/fhempy/commit/2bb1c57a009f07de189a94dc1e9f306a06600b74))

* add downloads badget ([`8bbd293`](https://github.com/fhempy/fhempy/commit/8bbd2938f698ca88d1e2db148df183a936451efc))

* create stale workflow ([`52bed33`](https://github.com/fhempy/fhempy/commit/52bed339839e66a1e283ac9b70db99350953fb83))

* create publish package workflow ([`20919f5`](https://github.com/fhempy/fhempy/commit/20919f5d7ce6df1b28b8c61aa7bc2694f28cc116))

* update controls ([`0310f2a`](https://github.com/fhempy/fhempy/commit/0310f2acfb7eecb342342cee22303136bb2019ab))

* Merge branch &#39;development&#39; ([`5b5348e`](https://github.com/fhempy/fhempy/commit/5b5348e92ba8d01c0bc2a8b8ef1c98e87526a28f))

* update version ([`dc69031`](https://github.com/fhempy/fhempy/commit/dc690319c5280b5078eb928ecbb11b706b32e5aa))

* fix path ([`4739523`](https://github.com/fhempy/fhempy/commit/4739523016c1ab3a899be11b8fbda4c6e684a324))

* rename to fhempy
update remote peer infos ([`0f29602`](https://github.com/fhempy/fhempy/commit/0f29602333cfd071141b5dd7a2ffcc215dc40cbe))

* add release script ([`55becb2`](https://github.com/fhempy/fhempy/commit/55becb286a942d3eb9166cf7f43da4db4448629d))

* add installation script for systemd ([`99c029f`](https://github.com/fhempy/fhempy/commit/99c029fc15121ac6b7e5927fc4aab76a54b8eeb3))

* fix restart after update ([`fd525ac`](https://github.com/fhempy/fhempy/commit/fd525ac2f8666a0a2e593f76073b6efcf693cd05))

* prepare pip package ([`d6ed9a9`](https://github.com/fhempy/fhempy/commit/d6ed9a90f0f64b6acf0cf161ca76d51c7d5fac57))

* support remote update
add version reading ([`5bce14a`](https://github.com/fhempy/fhempy/commit/5bce14a6f49a6ae9902089d02bb121c88bc09fe9))

* add license ([`199f731`](https://github.com/fhempy/fhempy/commit/199f731eaa674df61d642ca09e81946649336a09))

* update changed ([`b96d280`](https://github.com/fhempy/fhempy/commit/b96d2801f4d4738da474f5b516f9181c19e07de0))

* support FW_detailFn ([`5bd3b98`](https://github.com/fhempy/fhempy/commit/5bd3b981b1bf184fb907eaf619b1eb220ddf20d7))

* change to fhempy ([`e62211b`](https://github.com/fhempy/fhempy/commit/e62211bb83cd28a1cae224bdc6929029bedc034c))

* change to fhempy ([`10b26bc`](https://github.com/fhempy/fhempy/commit/10b26bc67b96fa955528379b4c9beac7e3a453ec))

* rename fhem_pythonbinding to fhempy ([`69c104c`](https://github.com/fhempy/fhempy/commit/69c104cf45c70059c4ea926b3c799f80aa473245))

* add min version for ring_doorbell ([`30b8d3d`](https://github.com/fhempy/fhempy/commit/30b8d3d169e2dcbd6d8ec119a387782cabc005fb))

* use FhemModule and help ([`9abe2e3`](https://github.com/fhempy/fhempy/commit/9abe2e38f0deaf58238317d46b1b9236c0c74923))

* use FhemModule ([`75b565d`](https://github.com/fhempy/fhempy/commit/75b565d7ef83f3986a7a4ab58437a8426eaf9e07))

* use FhemModule and help ([`bbd2797`](https://github.com/fhempy/fhempy/commit/bbd27977b96e9006995ba325306f880de9c4b65d))

* add FhemModule base class ([`f2958a2`](https://github.com/fhempy/fhempy/commit/f2958a24cb13efaf64af65631663f22b251336a2))

* update controls ([`459e613`](https://github.com/fhempy/fhempy/commit/459e6136fc774c66bff00b45ff5c366de1ac7f6d))

* Merge branch &#39;development&#39; ([`2b748d3`](https://github.com/fhempy/fhempy/commit/2b748d3afa67a148dee4a8fc5d014ff91c8d93c8))

* better readings ([`3776c7a`](https://github.com/fhempy/fhempy/commit/3776c7a5098138a98bcc1f6531df0fbdc3d53d48))

* update controls ([`5eb72ea`](https://github.com/fhempy/fhempy/commit/5eb72eaa18c4291ad60a7a881af1498ea1c84e2b))

* Merge branch &#39;development&#39; ([`6d3126c`](https://github.com/fhempy/fhempy/commit/6d3126c1562348176c642cc6ded1b1bd0a087245))

* fix update_functions ([`ba262f8`](https://github.com/fhempy/fhempy/commit/ba262f8208cbf9c910700f6bd76829526ad688c8))

* Merge branch &#39;development&#39; ([`021c8a3`](https://github.com/fhempy/fhempy/commit/021c8a3abd723e1ca9b331d6fed308b9c3145f13))

* fix IODev attribute ([`571e051`](https://github.com/fhempy/fhempy/commit/571e051b4a05a3458f8a3f58a4033d8fc06ce6e5))

* update controls ([`cb67e50`](https://github.com/fhempy/fhempy/commit/cb67e50157a8f105c32a4456236bbf3f1e15e78a))

* Merge branch &#39;development&#39; ([`ed64fa3`](https://github.com/fhempy/fhempy/commit/ed64fa37026020c1d0f88f09f763054d78a58099))

* support update_functions attr ([`0f3a7a7`](https://github.com/fhempy/fhempy/commit/0f3a7a7099a9fd22ec960bf280f6a0ec5715d4a7))

* try to fix reconnect issues ([`257039e`](https://github.com/fhempy/fhempy/commit/257039e07736ead319010a15d1423c5585d2ffc6))

* fix stop_process ([`a3c84ab`](https://github.com/fhempy/fhempy/commit/a3c84abf40ae62f80e0e469f165e541b6cf55988))

* add logfile,nrarchive ([`139cee4`](https://github.com/fhempy/fhempy/commit/139cee4384d4444a155a873ef7c67118d6f1e78b))

* use setDevAttrList instead of userattr ([`29ebf04`](https://github.com/fhempy/fhempy/commit/29ebf0468551efde4dab4fbdadf5e8eb2b7a7fb2))

* fix multiple connects ([`0af9844`](https://github.com/fhempy/fhempy/commit/0af984458c2a9cf448eba90e9773c55738e42585))

* fix package installations ([`6fccc2f`](https://github.com/fhempy/fhempy/commit/6fccc2f98cf58b43ffe52cb70f9059ffeba515c6))

* relogin on errors ([`3263286`](https://github.com/fhempy/fhempy/commit/32632866113be574801849e20edad84283495748))

* update readme ([`6a7a9a8`](https://github.com/fhempy/fhempy/commit/6a7a9a83a6118b64ff43363cc51c2095d6b411e3))

* wait for result ([`26355be`](https://github.com/fhempy/fhempy/commit/26355be9f921481867d936c40227a0044752404c))

* wait for result ([`05665f3`](https://github.com/fhempy/fhempy/commit/05665f33ad3472af69f4bc1833090f3ee5ea1048))

* support americano,hotwater ([`67bc210`](https://github.com/fhempy/fhempy/commit/67bc2101f94f7cf652c1d9d986baf097adb87426))

* Merge branch &#39;development&#39; ([`1bcb0de`](https://github.com/fhempy/fhempy/commit/1bcb0dea9d101f834bed38083d60c4c85bc39e78))

* update remote installation ([`39735f8`](https://github.com/fhempy/fhempy/commit/39735f877b8592c81ebeec6fbb39ff1304d74889))

* add googlecast readme ([`cc28bdf`](https://github.com/fhempy/fhempy/commit/cc28bdf60168992fff39ef19bf06453885a57d60))

* update controls ([`f02b22a`](https://github.com/fhempy/fhempy/commit/f02b22ac5e06ae9fde1492394a69383a68c1eb41))

* Merge branch &#39;development&#39; ([`a8e91ba`](https://github.com/fhempy/fhempy/commit/a8e91ba9b4d936b87a5fcad0da6630c5d8665ab9))

* longer timeout ([`bd6f3fc`](https://github.com/fhempy/fhempy/commit/bd6f3fcc63695d679d989680f5aa8ff932ee75a0))

* fix absent on startup ([`ef075be`](https://github.com/fhempy/fhempy/commit/ef075be421e6cb6de1a108c6e990b88097c074f2))

* update controls ([`6792886`](https://github.com/fhempy/fhempy/commit/67928865071759680602eab584ee0f3a61729240))

* Merge branch &#39;development&#39; ([`07171ae`](https://github.com/fhempy/fhempy/commit/07171ae32ee07f44cb9a1df50138404d5223871f))

* install cryptography ([`c6f4afc`](https://github.com/fhempy/fhempy/commit/c6f4afc7c9c527bbff236c5554c968a9150a2147))

* update controls ([`e2e3b04`](https://github.com/fhempy/fhempy/commit/e2e3b04d7ea2fdb77309210b9d83e9d767f93fd9))

* Merge branch &#39;development&#39; ([`1b60bc2`](https://github.com/fhempy/fhempy/commit/1b60bc2d7747835bfe9366bc4735f5c7a33d13e1))

* add stacktrace logging ([`9662342`](https://github.com/fhempy/fhempy/commit/9662342e5e8401b59b0559c985d967ef80ff20ff))

* add timeout for connect ([`21ac975`](https://github.com/fhempy/fhempy/commit/21ac975cb8fbf19dddfc117cea084e806088d026))

* update controls ([`b063358`](https://github.com/fhempy/fhempy/commit/b063358db0a92ab089ed9143a191e7e61cbaf64c))

* Merge branch &#39;development&#39; ([`c517dfa`](https://github.com/fhempy/fhempy/commit/c517dfae53b42dd6e9b02d23feda9f0412f095e7))

* remove deps which are automatically installed ([`6a1684c`](https://github.com/fhempy/fhempy/commit/6a1684c87e4c830e493c7eae26f96f95211a2c92))

* automatically install depencies
fix IODev change ([`1953712`](https://github.com/fhempy/fhempy/commit/1953712e41fd94def437dbc685489521573ec52f))

* set offline after 4 failed updtes ([`f4a836a`](https://github.com/fhempy/fhempy/commit/f4a836a68c4f67a0b878fc1ee77cca04a48bb3c2))

* add version check ([`da2b6c3`](https://github.com/fhempy/fhempy/commit/da2b6c365569be748c6e3b55de5a42b0ce369e02))

* better error handling ([`32031e2`](https://github.com/fhempy/fhempy/commit/32031e255d23c8076375d5f7581c6b663367f917))

* update controls ([`2acefdd`](https://github.com/fhempy/fhempy/commit/2acefdd08a8f9450773260c84fd0f15ef1c1a652))

* Merge branch &#39;development&#39; ([`a8b37cc`](https://github.com/fhempy/fhempy/commit/a8b37ccf840c7b5080c6258095aa3f23ab8aee03))

* add set_attr_ on define ([`824c02a`](https://github.com/fhempy/fhempy/commit/824c02a6840f057ab3c88d40aab8387c58ff76f5))

* add hciconfig hciX up cmd ([`13e9ec5`](https://github.com/fhempy/fhempy/commit/13e9ec5b6a59e80b004bca0abed1a97a33b1e5d3))

* read all possible characteristics into readings ([`b0ff6bb`](https://github.com/fhempy/fhempy/commit/b0ff6bbd2dae45b0af6d1523f6513701fb60c2f1))

* update controls ([`8af6378`](https://github.com/fhempy/fhempy/commit/8af6378c5e03c2c2ebb4396a1e91238c732902e4))

* Merge branch &#39;development&#39; ([`714bb24`](https://github.com/fhempy/fhempy/commit/714bb241433865e5b3d509446c2a9446a4bcbe45))

* add attr scan_duration ([`619e36e`](https://github.com/fhempy/fhempy/commit/619e36e3344e8f0a29667b82b04ce9f18ff382ec))

* udpate controls ([`43be4e9`](https://github.com/fhempy/fhempy/commit/43be4e9327c4221ec7ec767ac26be4535bfd0d4c))

* Merge branch &#39;development&#39; ([`583e1a3`](https://github.com/fhempy/fhempy/commit/583e1a333cdf452f43eed99f1af18c4e59a45777))

* add esphome ([`d1f06a1`](https://github.com/fhempy/fhempy/commit/d1f06a16b67de20b0f00db8fb3ef023fc109aac7))

* add esphome readme ([`9e61b05`](https://github.com/fhempy/fhempy/commit/9e61b0533c8943f789e2cf915cc8d81918ef1d54))

* add esphome ([`53f7443`](https://github.com/fhempy/fhempy/commit/53f74433c59fcea43d4a019b5e0bcb67315c188d))

* fix readme ([`9446b77`](https://github.com/fhempy/fhempy/commit/9446b778a75bef78e867b640c1fb85fef4fc5492))

* fix name ([`6338588`](https://github.com/fhempy/fhempy/commit/633858849ca87712bcee2bdf40444e4da8570cc6))

* update controls ([`93f4b76`](https://github.com/fhempy/fhempy/commit/93f4b7687ed7cb7ecb6852685695f516f2dd7cba))

* Merge branch &#39;development&#39; ([`5cbfc8b`](https://github.com/fhempy/fhempy/commit/5cbfc8b569f4d16ba765b658f7d8e3e19e216eb0))

* fix readme
fix absent ([`7eb6512`](https://github.com/fhempy/fhempy/commit/7eb6512d167b7b97c3b6b8d780615c9e6fe19e49))

* Merge branch &#39;development&#39; ([`f4a69e1`](https://github.com/fhempy/fhempy/commit/f4a69e1b39dbaada81244f9eabed3806e46a5986))

* add permissions for bluepy scan ([`f563315`](https://github.com/fhempy/fhempy/commit/f56331580bfdb086d2b9d39e441cf52c50a8b377))

* update controls ([`907b8e3`](https://github.com/fhempy/fhempy/commit/907b8e3e764f085f181985c1dc5c54b8106e7402))

* Merge branch &#39;development&#39; ([`269969e`](https://github.com/fhempy/fhempy/commit/269969e100ca2b07d458d95512d6ff619f2a3be0))

* fix no departures ([`dd20c71`](https://github.com/fhempy/fhempy/commit/dd20c7183824069ff82fe36a4dc5531383e82c12))

* add state on define ([`4f6a45e`](https://github.com/fhempy/fhempy/commit/4f6a45e31eebc5fee9a9f191a3538799b06bfc2c))

* support poll_type ([`94bf8f8`](https://github.com/fhempy/fhempy/commit/94bf8f8d3c0be0e91bea66bd7815e1686d03b59e))

* new more stable ble_presence with bluepy ([`3e8b6dd`](https://github.com/fhempy/fhempy/commit/3e8b6dd7b9ece653df903dead258a8d5022c521b))

* use bluepy ([`c9d9d7b`](https://github.com/fhempy/fhempy/commit/c9d9d7b15418bb1765ba0ec02a038e31a506c80d))

* ble_presence with aioblescan ([`9f26527`](https://github.com/fhempy/fhempy/commit/9f26527b30807ab9b580602d2cfcf23e6f16c539))

* update controls ([`ab16877`](https://github.com/fhempy/fhempy/commit/ab16877518a8fb0c6a2c71fe5a680acb0217f7c3))

* Merge branch &#39;development&#39; ([`bb5b011`](https://github.com/fhempy/fhempy/commit/bb5b011a4c824cb5800620ef0ae818db707c85b4))

* fix possible reading update errors ([`778ff4e`](https://github.com/fhempy/fhempy/commit/778ff4e304450f066b7fde040534f416c4d48693))

* fix debug msg ([`af9a1ed`](https://github.com/fhempy/fhempy/commit/af9a1ed03bfeba2d045469c636583b0b8ad2eb63))

* update controls ([`9cb1e2f`](https://github.com/fhempy/fhempy/commit/9cb1e2f2ee33cadfaf13380718187f69e80a5f1b))

* Merge branch &#39;development&#39; ([`160ae27`](https://github.com/fhempy/fhempy/commit/160ae2715b7d48ad569955962216622b6b58a6a9))

* update readme ([`1115373`](https://github.com/fhempy/fhempy/commit/1115373644e5ee171d6c3eb7ac9a9a96dede030f))

* add mitemp module ([`4c746ab`](https://github.com/fhempy/fhempy/commit/4c746abb02457d18dddba748b1a6c3b482b23ca4))

* add update_interval reading ([`80dc798`](https://github.com/fhempy/fhempy/commit/80dc7987b9de0571c54e31bf214adc8821c5266b))

* update controls ([`5644ceb`](https://github.com/fhempy/fhempy/commit/5644ceb686d875e8f893471746b6e5afea5ad7b8))

* Merge branch &#39;development&#39; ([`b5d9898`](https://github.com/fhempy/fhempy/commit/b5d9898acaf4737a8e1bf51287db5785f9ac4723))

* fix miflora ([`f38b282`](https://github.com/fhempy/fhempy/commit/f38b282e3bf191f417d7105e73d2268914336606))

* fix convert2format ([`71e6260`](https://github.com/fhempy/fhempy/commit/71e6260a1d6822e4a33ea90cc649e2d6e874cb17))

* handle import errors ([`d0a5e23`](https://github.com/fhempy/fhempy/commit/d0a5e23cf5f0c0811f3153e1707d7b49c8a30087))

* fix status task ([`810c044`](https://github.com/fhempy/fhempy/commit/810c04485da9dc07849aa0b35300228039a10953))

* update controls ([`1fda60c`](https://github.com/fhempy/fhempy/commit/1fda60c61dd749447e6859ae0fcf1419f6f64fb8))

* Merge branch &#39;development&#39; ([`fc5b895`](https://github.com/fhempy/fhempy/commit/fc5b895a325538c9da11fa8ca8f07e363833dfba))

* poll device after alert ([`7c7dc1a`](https://github.com/fhempy/fhempy/commit/7c7dc1af5cb95e46f40ba1b7899a9a627c9360c9))

* add attr interval, hci_device ([`9daa50a`](https://github.com/fhempy/fhempy/commit/9daa50added2dfb302958d026ec7b93e1a05c8e8))

* add attr handling to helloworld ([`6d5b75b`](https://github.com/fhempy/fhempy/commit/6d5b75b38eed677265afa50d960ece92d620a48d))

* update controls ([`b95d744`](https://github.com/fhempy/fhempy/commit/b95d74458d4d8362da4b8b5368e013f4e41c15eb))

* Merge branch &#39;development&#39; ([`16dd72a`](https://github.com/fhempy/fhempy/commit/16dd72a2fe62f5d5c26f8db36d6a371aad244e8b))

* change binding names ([`e30bd63`](https://github.com/fhempy/fhempy/commit/e30bd63594c90534bb3752be12fb80ec3b42c11b))

* add timeout parameter ([`43217df`](https://github.com/fhempy/fhempy/commit/43217dfee88099a5ca0cbea31d1297d4e2da46aa))

* fix Undefine ([`a1ed53d`](https://github.com/fhempy/fhempy/commit/a1ed53dd4007253e6bbc21ebc7d6093a3d297956))

* update controls ([`cbdb80a`](https://github.com/fhempy/fhempy/commit/cbdb80a212ffa646cb0274829dbd612f1ac5dfeb))

* Merge branch &#39;development&#39; ([`069aba5`](https://github.com/fhempy/fhempy/commit/069aba5384ca78830afd7a5dd0ae8afbeeb8d551))

* init commit of miflora ([`01b32ef`](https://github.com/fhempy/fhempy/commit/01b32ef9e0181caab2562858728c06fc4223457f))

* Merge branch &#39;development&#39; ([`b9440c6`](https://github.com/fhempy/fhempy/commit/b9440c66711a0f6e49f1d3e34938eff5499ae4be))

* add links to readmes ([`2c27eeb`](https://github.com/fhempy/fhempy/commit/2c27eeb8c2348b17072ee13db77ab1ad3840ac19))

* add bluetooth configuration ([`a54603d`](https://github.com/fhempy/fhempy/commit/a54603de10ca47be21b10dd77c17d504431f73bb))

* add readme for ble_presence ([`70b836f`](https://github.com/fhempy/fhempy/commit/70b836f1eabc2b86f91488283406027daf28660b))

* update controls ([`f662be4`](https://github.com/fhempy/fhempy/commit/f662be4fcf00c6bfb21f4708103e59a792f98952))

* Merge branch &#39;development&#39; ([`ee94c52`](https://github.com/fhempy/fhempy/commit/ee94c52858c3bc2d276abb68d1fc4868b295b5f1))

* fix max volume ([`04dc44d`](https://github.com/fhempy/fhempy/commit/04dc44dd34bc276c77b841292ea98de728213f45))

* update controls ([`6089705`](https://github.com/fhempy/fhempy/commit/60897052d66f8fdfebb8c3c56299f76c589da728))

* Merge branch &#39;development&#39; ([`9c6a30a`](https://github.com/fhempy/fhempy/commit/9c6a30ad9356982a7c6499112cab6922faba7d8f))

* support format for set ([`df52347`](https://github.com/fhempy/fhempy/commit/df52347a09903fc0b626538c58b23d5e193ee0d7))

* support volume ([`0fffb37`](https://github.com/fhempy/fhempy/commit/0fffb3748f8d70010e7152d192780f274b2d52d6))

* add offline reading ([`a086690`](https://github.com/fhempy/fhempy/commit/a086690e6dbaa93b6b39a63ab545a9dead807bff))

* update controls ([`9c75e67`](https://github.com/fhempy/fhempy/commit/9c75e67fc6d658d3cfdec56233e243959ce7ecfe))

* Merge branch &#39;development&#39; ([`7b70013`](https://github.com/fhempy/fhempy/commit/7b7001340675bb19bd9d4549325cf215ebb0cdb5))

* update readme for remote peers ([`e772adb`](https://github.com/fhempy/fhempy/commit/e772adb53515d805053629285304fc586dc8aa41))

* update readme ([`690fb3a`](https://github.com/fhempy/fhempy/commit/690fb3a902122cb1921e173d094b5a11d91a4151))

* add usage ([`0ddf238`](https://github.com/fhempy/fhempy/commit/0ddf23810788d7aee29455d990ba8bc66999083f))

* support set volume ([`d54f330`](https://github.com/fhempy/fhempy/commit/d54f3305603a8910d7f655df3850c0259567752e))

* update controls ([`8c4ae4c`](https://github.com/fhempy/fhempy/commit/8c4ae4cbba3c1ba88df21c43a9e33f07a8ce3638))

* Merge branch &#39;development&#39; ([`e5d14ca`](https://github.com/fhempy/fhempy/commit/e5d14ca2e2b44cf4f8511a3d919727d5a73db4df))

* remove unstable notice ([`210e815`](https://github.com/fhempy/fhempy/commit/210e815eb1ddabcf25720ed2fa38a6c6e4e5f19d))

* support cmds with arguments ([`39dd448`](https://github.com/fhempy/fhempy/commit/39dd448c3b1df8dfb30a83c3061ab1c50d025747))

* further update ([`3d892ef`](https://github.com/fhempy/fhempy/commit/3d892ef94251e0728d76caf5e5c0ac6e92ba23bf))

* add info for remote devices ([`eaef19d`](https://github.com/fhempy/fhempy/commit/eaef19d02799b7b681b20877f45eda7c032d7a85))

* Merge branch &#39;development&#39; ([`51b7e7d`](https://github.com/fhempy/fhempy/commit/51b7e7d1248464352723aede08b414ebdf5c6a51))

* add miio readme ([`4896ffe`](https://github.com/fhempy/fhempy/commit/4896ffea36e565f2590b1bdd341b1ca14d989aab))

* update controls ([`8848ca4`](https://github.com/fhempy/fhempy/commit/8848ca48a1dd2e751e4ec7a59c576e7906282ba7))

* Merge branch &#39;development&#39; ([`98d018b`](https://github.com/fhempy/fhempy/commit/98d018bcc662f50afa48ed968660ea5a3a8fe948))

* initial miio release
only supports functions without args ([`f732b9d`](https://github.com/fhempy/fhempy/commit/f732b9d0749fb093cf7b5385776027bde172725b))

* support function setting ([`57a4479`](https://github.com/fhempy/fhempy/commit/57a44793fafbc7ceeb4baf62f6ced863f9dc2e11))

* add eq3bt readme ([`b9892b5`](https://github.com/fhempy/fhempy/commit/b9892b5fca18a11c0fff701dff3195841f32586d))

* add resetConsumption
change consumption calculation ([`7838446`](https://github.com/fhempy/fhempy/commit/7838446465aa22cbad60c3011f76ff845b0ed0dc))

* add consumption ([`e6bf398`](https://github.com/fhempy/fhempy/commit/e6bf3981fb93f84b63c0e648703991e1434a8082))

* reduce sleep ([`63da32d`](https://github.com/fhempy/fhempy/commit/63da32d3f801ebc5311839924b134bbd9fe83c6c))

* fix comment ([`56f9cb6`](https://github.com/fhempy/fhempy/commit/56f9cb6b5387a9c6adb7bfdb428a1d11f644e534))

* fix ble_reset ([`527c141`](https://github.com/fhempy/fhempy/commit/527c141e74fe69c439738fb302e2afef09d813c3))

* Merge branch &#39;development&#39; ([`ef9d25b`](https://github.com/fhempy/fhempy/commit/ef9d25bfe809e34beac397a971997e606e3c8bcf))

* update readme ([`943d4cf`](https://github.com/fhempy/fhempy/commit/943d4cf5ed8e73b418912f85b352138454127200))

* update controls ([`9f8c9ca`](https://github.com/fhempy/fhempy/commit/9f8c9ca04695b02c7e4cb7fe508bd95f3cc7fd1a))

* Merge branch &#39;development&#39; ([`ae30ac2`](https://github.com/fhempy/fhempy/commit/ae30ac24bbd25843cb5a7d9eb83c65fdef6b210e))

* support video stream ([`84159b7`](https://github.com/fhempy/fhempy/commit/84159b7ee176846f0a6f2667ac1dd7b47f3cc08d))

* add comment for threadsafe ([`9bc6ef2`](https://github.com/fhempy/fhempy/commit/9bc6ef22265e87564d436b5edc7b751d20bb29e7))

* return taskid ([`073176a`](https://github.com/fhempy/fhempy/commit/073176ad27a2f0c0e1f1ced84880fa501fd65f28))

* update controls ([`215a6c6`](https://github.com/fhempy/fhempy/commit/215a6c6e7f0da64b759fc253c9986bdefd496ed1))

* Merge branch &#39;development&#39; ([`9c18f7d`](https://github.com/fhempy/fhempy/commit/9c18f7d9d635ada3948c6ab28f5dddc93b74780e))

* change format to options ([`7efa368`](https://github.com/fhempy/fhempy/commit/7efa368ef19f6ef48476b7949b1eaa0a13af4e71))

* add ble_reset reset_time attr ([`dcc77d8`](https://github.com/fhempy/fhempy/commit/dcc77d879e517cf8f1ab6c743b84a4b21235f179))

* fix keep_connected
rename set_list format to options
add set_attr_... function ([`26bb713`](https://github.com/fhempy/fhempy/commit/26bb7135c5dfe0f27ad1329ac60c8650e814764c))

* update controls
update prepare_update ([`f744a5c`](https://github.com/fhempy/fhempy/commit/f744a5cf4dc8ab74525ae1115a8633d56b68d7c8))

* Merge branch &#39;development&#39; ([`109c24b`](https://github.com/fhempy/fhempy/commit/109c24bb160bd70831bfb6c48ce8d490cc205b70))

* add TensorFlow image object detection ([`b08588e`](https://github.com/fhempy/fhempy/commit/b08588e4f0b07774678015e91f9ae49a17ac4f05))

* update controls ([`0cc6735`](https://github.com/fhempy/fhempy/commit/0cc673558e2baeb15a566fd9dd87ff838078bb70))

* Merge branch &#39;development&#39; ([`0a8501c`](https://github.com/fhempy/fhempy/commit/0a8501c1ad841bac3a758f798a89f9daad28d787))

* add message status ([`254e332`](https://github.com/fhempy/fhempy/commit/254e332290352d43855d6fd2dc8e52b69c818f8f))

* add readingsBulkUpdate ([`40230f0`](https://github.com/fhempy/fhempy/commit/40230f0dd18a3bb2ec4f55f3b1962ac503cbf756))

* update controls ([`8a2ccac`](https://github.com/fhempy/fhempy/commit/8a2ccac75d61fae7abf5f727e640c365d5b66b7f))

* Merge branch &#39;development&#39; ([`4968781`](https://github.com/fhempy/fhempy/commit/4968781d3f890d65d02f32f7dbbce73b901a3327))

* fix ding poll errors ([`8041928`](https://github.com/fhempy/fhempy/commit/8041928bfd130d378362764266a0bb5cd3144b9f))

* update controls ([`a365927`](https://github.com/fhempy/fhempy/commit/a365927f4d9fd5ccf6a90c88bbde5595468cc089))

* Merge branch &#39;development&#39; ([`5048874`](https://github.com/fhempy/fhempy/commit/5048874132e475285c373a3533212f164a3c1149))

* add WienerLinien module ([`6cff498`](https://github.com/fhempy/fhempy/commit/6cff4989587c7b4db19d92bf48f013009b9052bc))

* add flatten_json ([`7ef90dd`](https://github.com/fhempy/fhempy/commit/7ef90ddb3c7e93155d186def52c77902ad236616))

* support CommandDeleteReading ([`e5cbf5d`](https://github.com/fhempy/fhempy/commit/e5cbf5d480e7d95be6a634c49d4e604c7b84237f))

* fix encoding errors ([`b7fb2db`](https://github.com/fhempy/fhempy/commit/b7fb2dbbf8476b67271a6afc7c05b49a4f5eada7))

* add interval attributes ([`2e59def`](https://github.com/fhempy/fhempy/commit/2e59defaea812df19d2967e21d046fb8df9256ac))

* do not set offline on startup ([`fbb6c47`](https://github.com/fhempy/fhempy/commit/fbb6c474d294cc945e0382319486b04c67d286fb))

* add attr helper functions ([`4f80eb4`](https://github.com/fhempy/fhempy/commit/4f80eb48ee747733d8c8eebb6c6dfbc8e6a5d710))

* update controls ([`e44e208`](https://github.com/fhempy/fhempy/commit/e44e208cc8c0371b8437ee2a1e6ebf46beaed83c))

* Merge branch &#39;development&#39; ([`caa3398`](https://github.com/fhempy/fhempy/commit/caa33984a15f9302b17d38bc820baa3b851e6399))

* support some attributes ([`812c3e2`](https://github.com/fhempy/fhempy/commit/812c3e23ddf4a12fa21b6042220cedddf8295f9e))

* remove unused function ([`b61075d`](https://github.com/fhempy/fhempy/commit/b61075dd68a7c842c894c6bca707ff19be2e3d08))

* fix Attr function ([`38769f8`](https://github.com/fhempy/fhempy/commit/38769f8140487b1b19fdc1b811e5d4a56ebb5f6c))

* fix hash ([`e4b6854`](https://github.com/fhempy/fhempy/commit/e4b6854a9fa3819500cea86499ba4b623903da39))

* change url ([`88323ce`](https://github.com/fhempy/fhempy/commit/88323ce50c7daa0e32949df69f9aff56b4829d8a))

* add lastreset reading ([`a106e9a`](https://github.com/fhempy/fhempy/commit/a106e9a19ddd08b6bf0a34c02017f37517608bd0))

* Merge branch &#39;development&#39; ([`61892ad`](https://github.com/fhempy/fhempy/commit/61892ad707edfcd739abc65aa7a8e0c7499d1f0c))

* fix README ([`90093cb`](https://github.com/fhempy/fhempy/commit/90093cb4815ed1fb7ec34843e5158b7d13f592f0))

* update controls ([`cfa40eb`](https://github.com/fhempy/fhempy/commit/cfa40ebeb5ef2dabc70b3b49ad359e885d74ef98))

* Merge branch &#39;development&#39; ([`197789e`](https://github.com/fhempy/fhempy/commit/197789e9d52cdec0926a1f02fb3206dc7c41475b))

* do 3 checks for presence ([`ecc4798`](https://github.com/fhempy/fhempy/commit/ecc4798b4e67382ae39438a5aa03129c25581b71))

* add bt_presence module ([`ed95215`](https://github.com/fhempy/fhempy/commit/ed95215416cd9e3dd46deb0f97fddb5ee248e1fe))

* bugfix reading update ([`885a237`](https://github.com/fhempy/fhempy/commit/885a2372918aae944b94485030d05afe35877b6c))

* update controls ([`6c787be`](https://github.com/fhempy/fhempy/commit/6c787bec4f84d9baf9ee0149506c27f46be885cd))

* Merge branch &#39;development&#39; ([`4c9a908`](https://github.com/fhempy/fhempy/commit/4c9a90815b25020887117a61780176ee6f4163bb))

* add ble_presence module ([`67b21fc`](https://github.com/fhempy/fhempy/commit/67b21fcc8dba85cba2a8a9a031927885a0d47f19))

* update controls ([`26ab251`](https://github.com/fhempy/fhempy/commit/26ab251afa7caa0c5de6363acc80ca8c17e005d5))

* Merge branch &#39;development&#39; ([`86c4639`](https://github.com/fhempy/fhempy/commit/86c4639f0963f50321e75c1fbafc2a6da59db3fe))

* Merge pull request #2 from tsoybe/development

fixed: HelloWorld ([`4a0cf08`](https://github.com/fhempy/fhempy/commit/4a0cf0858721ab792c098c903c224b1032252e8e))

* add ble_reset ([`e97e5b9`](https://github.com/fhempy/fhempy/commit/e97e5b92ac444ad229e8b2be2fdd47e6d9da907d))

* fix indent ([`3a84555`](https://github.com/fhempy/fhempy/commit/3a845557d678f61014f14da84d56487db060ff8d))

* set state = alert on alert
prepare snapshot (currently not working) ([`5ccc8cc`](https://github.com/fhempy/fhempy/commit/5ccc8cc12aae65e0e12c1e17897392666e3710c4))

* add CHANGED file ([`00d8536`](https://github.com/fhempy/fhempy/commit/00d85369e10e8e79b32330461c2d3b1f04b5a6ac))

* add commandref link ([`6ba47e8`](https://github.com/fhempy/fhempy/commit/6ba47e89c3f458e45dab246a54273b063fc1ec57))

* add ble_reset module ([`2386737`](https://github.com/fhempy/fhempy/commit/238673719ccde70837e0dc99f65b417ca1f82b69))

* add defaults to set_list_conf ([`a1752ed`](https://github.com/fhempy/fhempy/commit/a1752ed55d4152c8b9b10c36ea28c0aee16191a3))

* update controls ([`8c440aa`](https://github.com/fhempy/fhempy/commit/8c440aae05697b1f2441f200858644c115a56612))

* Merge branch &#39;development&#39; ([`791606e`](https://github.com/fhempy/fhempy/commit/791606e521d5db6c6c4f22715a9d0e24c89298eb))

* update readme ([`85aec00`](https://github.com/fhempy/fhempy/commit/85aec00d6612e938f124eed5c24c14e691650cbf))

* longer timeout for InitDefine
possibly finally fixed connection error ([`2e5b14f`](https://github.com/fhempy/fhempy/commit/2e5b14ff4325e98313ab90ff9f635eb17b207447))

* exit on connection error ([`df458cd`](https://github.com/fhempy/fhempy/commit/df458cd362f4899db206a100027c42d53c2721c1))

* do not reset bluetooth ([`4642db2`](https://github.com/fhempy/fhempy/commit/4642db2985ef6f4e0a14717b0f35fca49f21bb66))

* buxfix ([`b8525d0`](https://github.com/fhempy/fhempy/commit/b8525d0244dfe9530e69f59ddc403773adcd296f))

* Merge branch &#39;development&#39; ([`2b98869`](https://github.com/fhempy/fhempy/commit/2b988697a982dead56564660e567f48f11a00382))

* add ring README ([`457d633`](https://github.com/fhempy/fhempy/commit/457d6335b87d6bafba3e87928b81efc9afea20f6))

* update controls ([`b546213`](https://github.com/fhempy/fhempy/commit/b546213c9ff999cbfcdbc1155b666d72eff65af2))

* Merge branch &#39;development&#39; ([`4391c8d`](https://github.com/fhempy/fhempy/commit/4391c8d4857e4a07b3348a2cb1b562eb66014f6a))

* disable json livestream ([`65228b7`](https://github.com/fhempy/fhempy/commit/65228b7d23339e3b2c33e32e11065d837b0f77fe))

* encrypt password/token ([`c18f2c0`](https://github.com/fhempy/fhempy/commit/c18f2c0915cb014d37bc3888ee892a7b39a06079))

* try to fix disconnects ([`d6d34ce`](https://github.com/fhempy/fhempy/commit/d6d34ce8d333cb5f6f919501bab87ec420920f86))

* add getUniqueId for encryption/decryption ([`828c9b6`](https://github.com/fhempy/fhempy/commit/828c9b6b074ebe26305db8e1b9b7e2dc563935c6))

* encrypt/decrypt_string for readings ([`ce6f213`](https://github.com/fhempy/fhempy/commit/ce6f2136aca3d2431ff13dcb3af9f66129596356))

* update controls ([`6d98a87`](https://github.com/fhempy/fhempy/commit/6d98a870a855d26ce1ca38a8c415cc396780fbdf))

* Merge branch &#39;development&#39; ([`b3f6a76`](https://github.com/fhempy/fhempy/commit/b3f6a76df867930039a21326303d63f45e19d4c7))

* further ring integration (history, alert) ([`9451e44`](https://github.com/fhempy/fhempy/commit/9451e44edcfed2015f06feffbb8c6578af6a9fd1))

* update controls ([`7e21f28`](https://github.com/fhempy/fhempy/commit/7e21f28b66061094b0c9d147139e72fc56b43c28))

* Merge branch &#39;development&#39; ([`e811604`](https://github.com/fhempy/fhempy/commit/e81160450e73b0e4884bc19a63f1a8d848aec644))

* fix login ([`43301cf`](https://github.com/fhempy/fhempy/commit/43301cf921d93e18565b0020b4948d04e5cd3176))

* update controls ([`97507fa`](https://github.com/fhempy/fhempy/commit/97507fa2b2c38c1b14869dd63fcfab0fc6ffe5d0))

* Merge branch &#39;development&#39; ([`d29b93d`](https://github.com/fhempy/fhempy/commit/d29b93dfc096f10cbd4bf5a11ada930894dd1b01))

* fix missing import ([`e9c4331`](https://github.com/fhempy/fhempy/commit/e9c43311cc204aa949439102ddd6103f6dd9cc81))

* fix indent ([`dcc6e9c`](https://github.com/fhempy/fhempy/commit/dcc6e9c48538d2889d87f6d716bb12077c1c95b0))

* initial ring version ([`2cd1cb7`](https://github.com/fhempy/fhempy/commit/2cd1cb77828563b39b6ef7cd5a22e16022ac7dc3))

* update controls ([`e9ae6c3`](https://github.com/fhempy/fhempy/commit/e9ae6c3bd6a1909f7cdb5843d318c22c3583bddd))

* Merge branch &#39;development&#39; ([`46690a8`](https://github.com/fhempy/fhempy/commit/46690a8173b1593b2624fc87e046765e2b7416df))

* prepare ring_doorbell (not working) ([`9561ce0`](https://github.com/fhempy/fhempy/commit/9561ce0346fff00c0113925c6a3ecd871231b4c5))

* prepare gfprobt ([`5f1c852`](https://github.com/fhempy/fhempy/commit/5f1c8525dc4adea525630ff41a3d9cd91892d0bd))

* update controls ([`3ff6bcf`](https://github.com/fhempy/fhempy/commit/3ff6bcf62121e9ae52e3c8cd897582b15df46e33))

* Merge branch &#39;development&#39; ([`c019ed7`](https://github.com/fhempy/fhempy/commit/c019ed7253d1de269581480ac4779c6656ed2421))

* fix 30 degress/on ([`0d975a2`](https://github.com/fhempy/fhempy/commit/0d975a2f5cb37f0a369223fb60808d555358dc88))

* reset BLE on start ([`801ba9b`](https://github.com/fhempy/fhempy/commit/801ba9b049e446f0be28596cf8338f76ba58ad33))

* fix zeroconf version ([`ce06e14`](https://github.com/fhempy/fhempy/commit/ce06e14cb5dbf0052ac8a850847c395156c59324))

* fix Undefine error ([`3b54402`](https://github.com/fhempy/fhempy/commit/3b54402589639c671cc495b9e3b991b10f27255d))

* support rename ([`c9f43d9`](https://github.com/fhempy/fhempy/commit/c9f43d9b0d3ee49d28b427adcfbdabb42cd36a3d))

* fix UTF-8 messages ([`e5d6083`](https://github.com/fhempy/fhempy/commit/e5d608326075fec0f54834ef3101b18d19a5c053))

* update controls ([`dd205f0`](https://github.com/fhempy/fhempy/commit/dd205f05226bae4048fbca18f66e6e2d3dec78b3))

* Merge branch &#39;development&#39; ([`20169fa`](https://github.com/fhempy/fhempy/commit/20169fac92cf9e3f3fb23abb502c8938512cc9a6))

* further dev ([`7407bb5`](https://github.com/fhempy/fhempy/commit/7407bb58756ad67b58858cdd2efb3d26a2358c04))

* fix disconnect ([`f2b20f3`](https://github.com/fhempy/fhempy/commit/f2b20f314b62a99f8365c4c30d4456e3ec4ed3a2))

* update controls ([`c7b53f7`](https://github.com/fhempy/fhempy/commit/c7b53f7e469faf108f90ebef919e343fd7dec31d))

* Merge branch &#39;development&#39; ([`61f6017`](https://github.com/fhempy/fhempy/commit/61f601772b7335b579529d4be1b7d21eab0e484e))

* BLE fixes ([`0aa8827`](https://github.com/fhempy/fhempy/commit/0aa882770bfd42f757f80f4100b464ac197cdf80))

* fix CommandAttr ([`9213099`](https://github.com/fhempy/fhempy/commit/9213099fef8c64bde31f0e0badff7b7210e389e0))

* fix Undefine ([`0635210`](https://github.com/fhempy/fhempy/commit/0635210c50852c8fcdc4c04844351f4c9303bb2a))

* fix Undefine ([`d6309a7`](https://github.com/fhempy/fhempy/commit/d6309a784f42ff81b10c78b1aa7ec3cec92614e8))

* add retries ([`9feb6bd`](https://github.com/fhempy/fhempy/commit/9feb6bda85148a2d738f1b098f02bdb3633f8389))

* fix working dir ([`d727099`](https://github.com/fhempy/fhempy/commit/d72709904aee10481c413856a227b4c90596531b))

* fix IODev change ([`557145c`](https://github.com/fhempy/fhempy/commit/557145c9bc0aeacbc1b847d7909572a09149ddc5))

* update controls ([`3ecaf67`](https://github.com/fhempy/fhempy/commit/3ecaf67795bb5f3b00c7e52e0b22d84c4061bb9c))

* add dbus error msg ([`58bbb38`](https://github.com/fhempy/fhempy/commit/58bbb38759b0d801ce06033f47f2c3c765611fed))

* fix eq3bt ([`4195fee`](https://github.com/fhempy/fhempy/commit/4195fee1dce6849ef16bbcf00358ad24ff367855))

* add xiaomi_tokens ([`0956965`](https://github.com/fhempy/fhempy/commit/0956965d3b8b08c324ad27aafb43ac07997f6627))

* update controls ([`a098545`](https://github.com/fhempy/fhempy/commit/a098545b73431103847e38441470e724b1923891))

* fix await ([`70b6f1a`](https://github.com/fhempy/fhempy/commit/70b6f1a2969fd4defeb3afb98018cd959368d1c2))

* update controls ([`b5afeff`](https://github.com/fhempy/fhempy/commit/b5afeffb3b37c128101bdd9c6a5683f628aa7e3a))

* prepare miio (not ready) ([`42dea87`](https://github.com/fhempy/fhempy/commit/42dea8732c0e200972435462326d31dee24c2e29))

* prepare gfprobt (not ready) ([`bd4a828`](https://github.com/fhempy/fhempy/commit/bd4a828afd9b4956c13309285f078e16e835062b))

* set state ([`1692104`](https://github.com/fhempy/fhempy/commit/1692104da661ed4cc1b4803b4a1d9b97e6a373f3))

* support keep_connected ([`b61bab5`](https://github.com/fhempy/fhempy/commit/b61bab54c371bfd7816befeeb53c3278ec465c48))

* add remote configuration ([`8724ac1`](https://github.com/fhempy/fhempy/commit/8724ac13061d802305530caeb494b33b4fec1982))

* fix typo ([`e0a7aec`](https://github.com/fhempy/fhempy/commit/e0a7aec3828ad4f933d4516a5b65fbcaff6aa202))

* check for BindingsIo instead of PythonBinding ([`b7b8a8e`](https://github.com/fhempy/fhempy/commit/b7b8a8e2665ac94481f61000fe7465e89e3a22d5))

* remove disconnect on timeouts ([`eb76f83`](https://github.com/fhempy/fhempy/commit/eb76f83a89fea0719428145cfe0bf9875a829cbe))

* add xiaomi token retriever ([`4386a39`](https://github.com/fhempy/fhempy/commit/4386a399fa9a45bd4e80465cf504f263ddedfa3d))

* use handle_set for helloworld ([`f67ab3e`](https://github.com/fhempy/fhempy/commit/f67ab3e984b1738c16a438d1d1c6cb45e04b8b79))

* fix global var ([`3914f6f`](https://github.com/fhempy/fhempy/commit/3914f6ffd852da369be8908573cb251f65eb2e55))

* add keep_connected attr to eq3bt ([`b9179f0`](https://github.com/fhempy/fhempy/commit/b9179f0a1086099d6fd52c2a77414dadf343faf9))

* keep connection alive
add easybrew
fix online/offline ([`cc8041f`](https://github.com/fhempy/fhempy/commit/cc8041fa6456750a935ff1314ca57614af5aab8b))

* fix issue in handle_set ([`4ebca53`](https://github.com/fhempy/fhempy/commit/4ebca53c87288ac4c5256204ac769a21b9446b41))

* add systemd file for remote uage ([`d577175`](https://github.com/fhempy/fhempy/commit/d5771757a376f9b9f80472da9ea50fe7129b7ff6))

* update controls ([`21dca43`](https://github.com/fhempy/fhempy/commit/21dca4369c240d5990a8fcb4b19341dbbbaaa94a))

* fix startup issue ([`1039ff1`](https://github.com/fhempy/fhempy/commit/1039ff146b99c13dfd4bbd8c664ed23699af0ebf))

* update controls ([`bc7fd84`](https://github.com/fhempy/fhempy/commit/bc7fd843ec4638ba73cc78c43d4c0642c3840d41))

* link to nespresso readme ([`a321dfb`](https://github.com/fhempy/fhempy/commit/a321dfb78a6124154a1537d60c5d41a438806f98))

* support nespresso_ble ([`3374dc2`](https://github.com/fhempy/fhempy/commit/3374dc25c5a3f892d8b01b7c6f1bf5a39cf92d38))

* update controls ([`c389ac3`](https://github.com/fhempy/fhempy/commit/c389ac35162ab3df818a4aabe21420218a891c7a))

* add nespresso_ble ([`2000fdf`](https://github.com/fhempy/fhempy/commit/2000fdf0f1b836ac9be75488e526faf1b612270a))

* support Bluetooth Nespresso machines ([`c896533`](https://github.com/fhempy/fhempy/commit/c896533c2e91c775ff5975cf051883d3da21a954))

* use eq3bt from PythonModule ([`e6b2f55`](https://github.com/fhempy/fhempy/commit/e6b2f5589cc0f76dca791063cfe13ff26ee18d24))

* support bindings on remote server ([`d4ce567`](https://github.com/fhempy/fhempy/commit/d4ce567810084eeb2a1f9307a1c0a614c71da366))

* update controls ([`58ee2ce`](https://github.com/fhempy/fhempy/commit/58ee2ce533412e81643c9b3174c6f406e489ab0e))

* small icon fixes ([`93e7a7f`](https://github.com/fhempy/fhempy/commit/93e7a7f83f2609ec93204dedb3e78ff06a995b69))

* add icons ([`e013576`](https://github.com/fhempy/fhempy/commit/e013576b7200a0c88b8ae5e02e1e540fc02b3bcf))

* update controls ([`821e342`](https://github.com/fhempy/fhempy/commit/821e34276c14eb4af10d8ec858e95a9e2ca4612a))

* Merge branch &#39;development&#39; ([`adb0818`](https://github.com/fhempy/fhempy/commit/adb0818a7be168fef0d206593fbabb9e43df2986))

* fix usage
add icons ([`6ed93f0`](https://github.com/fhempy/fhempy/commit/6ed93f0e704ad73dda9da43046edbb095cb487a8))

* update controls ([`f131efe`](https://github.com/fhempy/fhempy/commit/f131efe891de67db3cc0773902eee63da1ceb01f))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`996d4d3`](https://github.com/fhempy/fhempy/commit/996d4d388f465b0b603a4313062695a9e917b99a))

* Merge branch &#39;development&#39; ([`c4d9ac4`](https://github.com/fhempy/fhempy/commit/c4d9ac4a201afc0e238f6be7f31438e7498098a6))

* error msg when used without args ([`768f0d5`](https://github.com/fhempy/fhempy/commit/768f0d5b4098b66eef1e9afd19f6208d68f9ffe9))

* add Xiaomi Gateway V3 ([`2d56612`](https://github.com/fhempy/fhempy/commit/2d566124947f3a6d9842009bc25dd8e7ed8d713c))

* Merge branch &#39;development&#39; ([`f8b2bd0`](https://github.com/fhempy/fhempy/commit/f8b2bd0846d237e9561fc1672dfcb706e3433340))

* remove not needed file ([`2601c7c`](https://github.com/fhempy/fhempy/commit/2601c7c17ddc4117bf7d2dac83b046bf43b9ebd1))

* fix issues with broken ws msgs ([`9ea056b`](https://github.com/fhempy/fhempy/commit/9ea056bd6aefcab30432aec1b7437aee71c7a447))

* add log if DevIo not yet open ([`1bb632d`](https://github.com/fhempy/fhempy/commit/1bb632dda7bd3a11393601f693226db91b82cb98))

* use userattr ([`274bc3f`](https://github.com/fhempy/fhempy/commit/274bc3ff1c4307881a94c7d54c2aef22d038ae44))

* fix allowed reading chars ([`a363fa0`](https://github.com/fhempy/fhempy/commit/a363fa09df5a1775ff5cd3409a617e14f0bfe6c8))

* support addToDevAttrList ([`7c2db3a`](https://github.com/fhempy/fhempy/commit/7c2db3a3d21c495e2a43808d4840affcd3f9493f))

* longer timeouts on startup ([`3234cef`](https://github.com/fhempy/fhempy/commit/3234cefab7f1767899d9ad9bdd90b77dfbb4eae0))

* cleanup ([`7831a09`](https://github.com/fhempy/fhempy/commit/7831a09d39c0ce73d6c668339aa8f09b4ae21816))

* add gateway as device
prepare pairing ([`fbb6754`](https://github.com/fhempy/fhempy/commit/fbb675426f97d78b943de29f73aea6bd0d45b550))

* handle reconnect
better readings
support attributes ([`1a1a370`](https://github.com/fhempy/fhempy/commit/1a1a37034b4553ba0877d00f5499d16e2900d118))

* support CommandAttr ([`9031482`](https://github.com/fhempy/fhempy/commit/9031482d0c78698456cedccb5fa2a4d405384c19))

* add $readingFnAttributes ([`11d75da`](https://github.com/fhempy/fhempy/commit/11d75daf0a7469d50a942eb38446a326e3d5b9ae))

* remove udp code ([`80077fd`](https://github.com/fhempy/fhempy/commit/80077fdd60b85191b876bdbae1103ea503a1f955))

* first working version of Xiaomi Gateway V3 ([`6fd941b`](https://github.com/fhempy/fhempy/commit/6fd941b6c36e92db64b21ed62f1c769ecafdc112))

* fix Undefine ([`84ae262`](https://github.com/fhempy/fhempy/commit/84ae262af226da2a2743fb72098d6336281f1e4d))

* change timeout ([`313d042`](https://github.com/fhempy/fhempy/commit/313d0428743826d66a1b278fe3a36c0d8c84a40e))

* get fhempy instance by name
change timeout ([`f52ec2a`](https://github.com/fhempy/fhempy/commit/f52ec2af72b3f60e81873e5133651ee1ef293d61))

* update controls ([`c4ab775`](https://github.com/fhempy/fhempy/commit/c4ab775702f1a953a190e5d329247e870862bd0c))

* Merge branch &#39;development&#39; ([`4b30b9a`](https://github.com/fhempy/fhempy/commit/4b30b9a6f31181e3624bc016b24bdd056f7b7fdb))

* start xiaomi_gateway3 (not working!) ([`fc1ea76`](https://github.com/fhempy/fhempy/commit/fc1ea7620f6ad5078483dd2c2272972c5ba06a87))

* support addToQueue ([`7fe59c6`](https://github.com/fhempy/fhempy/commit/7fe59c63ba18b2b28473ffbde463c83b12392ccc))

* update controls ([`7adc773`](https://github.com/fhempy/fhempy/commit/7adc773e4a2fb1dc86a41ca47eb8c26b61535a27))

* Merge branch &#39;development&#39; ([`f93868c`](https://github.com/fhempy/fhempy/commit/f93868c3079f527e82e5055fc039f11ebc140d93))

* fix cleanup ([`27e80e3`](https://github.com/fhempy/fhempy/commit/27e80e3793afe2dab0804a0c389b0c7cf9adf2cf))

* fix mode ([`a3e15d5`](https://github.com/fhempy/fhempy/commit/a3e15d54eb9a5f03b6b1de83eab1332a3b85ff0d))

* some fixes ([`d81108b`](https://github.com/fhempy/fhempy/commit/d81108bf517f6c1343d4c273fbe008d66ae350b2))

* use alnum instead of isalpha ([`d751063`](https://github.com/fhempy/fhempy/commit/d751063e361afef5bdeebd5395f9f78f14fbcb92))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`44b0c9d`](https://github.com/fhempy/fhempy/commit/44b0c9d3192d423c5026030835bc71d40347deee))

* Merge branch &#39;development&#39; ([`7c4d2a6`](https://github.com/fhempy/fhempy/commit/7c4d2a6c2ba6d2e7d73c7d377ab7507c6ddba32c))

* update controls ([`1bc261f`](https://github.com/fhempy/fhempy/commit/1bc261f07b86c44497306d34bfbda3f1866d09a5))

* better connection handling
fix boost/locked/mode ([`487f8c4`](https://github.com/fhempy/fhempy/commit/487f8c4cac576f390d4236c30a1a8411617a6a96))

* add missing CoProcess ([`fa150fb`](https://github.com/fhempy/fhempy/commit/fa150fb9eac353e94f6675adbfef90c3a4a3f070))

* Update README.md ([`a97ae0b`](https://github.com/fhempy/fhempy/commit/a97ae0b0e4b28b14132dd8f52aa966f03910ca15))

* Update README.md ([`83ab8eb`](https://github.com/fhempy/fhempy/commit/83ab8eb1f84c851a7bfab4200b861536bb5ba2c2))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`472c683`](https://github.com/fhempy/fhempy/commit/472c6835ae656d3079ceccffc646fe4d7e60179d))

* Merge branch &#39;development&#39; ([`3cdc101`](https://github.com/fhempy/fhempy/commit/3cdc10116a904230939573d7336417900b643bdd))

* update controls ([`1333088`](https://github.com/fhempy/fhempy/commit/13330882ea90cfcba4a266003fb243f42f469779))

* set to 30C with on ([`45375bd`](https://github.com/fhempy/fhempy/commit/45375bd1c62ea0d0c0273475d3df481deab4ea36))

* Update README.md ([`e86eccc`](https://github.com/fhempy/fhempy/commit/e86eccc81038787767cc05c8c1516175857c473f))

* Merge branch &#39;development&#39; ([`c7d5e96`](https://github.com/fhempy/fhempy/commit/c7d5e96647b94224a81f21cdce9f518d538ec3e2))

* udpate controls ([`0a90bfe`](https://github.com/fhempy/fhempy/commit/0a90bfe40177ecef6d276921dbffba9a0f5c40bb))

* remove comments ([`26f820d`](https://github.com/fhempy/fhempy/commit/26f820dffc55d855fcb8812c28c6f7ebf3ef20b3))

* working eq3bt with schedules
utils for blocking code
googlecast use utils ([`4960537`](https://github.com/fhempy/fhempy/commit/49605378a97929810d6c561cc0e2f8d3152be138))

* remove setter ([`41da6ca`](https://github.com/fhempy/fhempy/commit/41da6ca0938390d5426cf1326cb50c71ecc483a2))

* fix handle_set ([`f2380c2`](https://github.com/fhempy/fhempy/commit/f2380c23faeb45ba234e6c31a5e1cd3072ec676e))

* fix off ([`ce273a7`](https://github.com/fhempy/fhempy/commit/ce273a75fad4e524f2f1b40cb9214632d81a0ab8))

* fix cleanup ([`1253d25`](https://github.com/fhempy/fhempy/commit/1253d259a9e69e744a6913a91f8f07afda917ef1))

* add utils
add eq3bt (initial commit) ([`beeb64a`](https://github.com/fhempy/fhempy/commit/beeb64a8bae47d6e2f33c7c1a97db5d4e546cc1d))

* add dlna_dmr ([`e3f1807`](https://github.com/fhempy/fhempy/commit/e3f18071e493a22017ead2ab8eed93dda10017d1))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`f769728`](https://github.com/fhempy/fhempy/commit/f76972804c8849e1f261ff309d03264132d7529d))

* update controls ([`9efc7a0`](https://github.com/fhempy/fhempy/commit/9efc7a09215d974631d6ec1906d35207620ed3b7))

* create device from discover_upnp ([`e316f37`](https://github.com/fhempy/fhempy/commit/e316f37539e5fb01d2793fc76ee5ee78f6fdbd1a))

* fix undefine ([`f7ce7dd`](https://github.com/fhempy/fhempy/commit/f7ce7dd427c04df32783ffee460c0cca61f5c418))

* increase timeouts to avoid issues on startup ([`213c87f`](https://github.com/fhempy/fhempy/commit/213c87f08e4a448039bae9597cca4dc13659a50b))

* fix multiple ssdp searches ([`6827744`](https://github.com/fhempy/fhempy/commit/6827744e6e8dbfc9e78bae91811696f1cdde9f9e))

* move ssdp to discover_upnp
remove netdisco usage ([`5a59b59`](https://github.com/fhempy/fhempy/commit/5a59b596060bce7aadc535e8413822fccf64f620))

* use update_hash ([`602f8af`](https://github.com/fhempy/fhempy/commit/602f8afa8edbb5cd524b6045865546b861306874))

* add update_hash fct ([`8eb654d`](https://github.com/fhempy/fhempy/commit/8eb654dce1e1dd26fc55e9ab2f6b098fea0f114c))

* use locks to prevent multiple readingsBegin
lot of fixes for dlna_dmr ([`b738697`](https://github.com/fhempy/fhempy/commit/b738697edc09d0b1aa604fa7e5047ba5fa535615))

* fix verbose on first load
add dlna_dmr (in development) ([`e38665e`](https://github.com/fhempy/fhempy/commit/e38665e2500d874a08e5277f056ee4168cf8cd4f))

* Update TODO.md ([`30a20b7`](https://github.com/fhempy/fhempy/commit/30a20b761a2baac8a5397c85c584620285e50f54))

* update discover devices ([`7f3db0a`](https://github.com/fhempy/fhempy/commit/7f3db0a5ea46fb99cb581002d51fc2f9eb337747))

* update controls ([`4890401`](https://github.com/fhempy/fhempy/commit/48904016d91b0c13fca9d0b4d68f20762111a7cc))

* support playFavorite (googlecast)
support verbose log level
support AttrVal, InternalVal, setDevAttrList ([`3a77129`](https://github.com/fhempy/fhempy/commit/3a77129fafbac73f5cd5dec89c7f35fb49cd6a4d))

* update controls ([`bc9d15a`](https://github.com/fhempy/fhempy/commit/bc9d15a5ca085ec383f202a6894dcdf018293e8e))

* fix pkg installations ([`48faca4`](https://github.com/fhempy/fhempy/commit/48faca48c9df6e27dd4d7f21df34150443f10e06))

* add timeout handling ([`841b57d`](https://github.com/fhempy/fhempy/commit/841b57dac3b857c4f30aec9bf7babd431f2d2d61))

* rename discovery devices
add discover_upnp ([`6163718`](https://github.com/fhempy/fhempy/commit/6163718e5ec8ce66930defcc457136e9b216b5a7))

* code style ([`e45ed7b`](https://github.com/fhempy/fhempy/commit/e45ed7bb45e4a2fb18ec5e5ec221f4342774a625))

* add python3,python3-pip installation ([`0320399`](https://github.com/fhempy/fhempy/commit/0320399134fa8584b7589f058dd638ffa8f5a896))

* add info about pkg installation ([`6dad507`](https://github.com/fhempy/fhempy/commit/6dad5079d6cecd66f88367b3ee95fb2c7f2339e4))

* update controls ([`8fbcb4a`](https://github.com/fhempy/fhempy/commit/8fbcb4abc5cea2e68c4e0d8a2556837b260e7f94))

* fix pkg updates ([`3640dc6`](https://github.com/fhempy/fhempy/commit/3640dc63c032ea71bb325ba94a6fe75e9f9377ce))

* update controls ([`9338e00`](https://github.com/fhempy/fhempy/commit/9338e004fc79f1908c510613de28595f13a02594))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`795df63`](https://github.com/fhempy/fhempy/commit/795df6342bc2ef3c440a009e07f75e357a7c7fbc))

* fix detection of installed pkgs ([`0a76ed7`](https://github.com/fhempy/fhempy/commit/0a76ed700b3f9e0c1833fa5a0050d0793af57165))

* add importlib_metadata ([`0d552a4`](https://github.com/fhempy/fhempy/commit/0d552a400a6837592db42db3a0ea606b4205c7dd))

* add json to controls ([`ce7322c`](https://github.com/fhempy/fhempy/commit/ce7322c538ac8aa0f37c7aef42ee99d17d298611))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`b6ef5fd`](https://github.com/fhempy/fhempy/commit/b6ef5fd58f5e78223ed1b0788972d8ec1e820eec))

* update controls ([`c003953`](https://github.com/fhempy/fhempy/commit/c003953f41d44a63fd444825908fa40fc8dea084))

* add auto pip installer
support youtube on audio devices
change DEBUG to ERROR ([`55c02e0`](https://github.com/fhempy/fhempy/commit/55c02e092c91ea9c77f3b49ee431770bbbd0e80a))

* add youtube_dl ([`6d20f4c`](https://github.com/fhempy/fhempy/commit/6d20f4c3979ea5d65b559ffbd51865da1cfd8aae))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`cc14be8`](https://github.com/fhempy/fhempy/commit/cc14be838b2440063d4514bab911299251675a7c))

* update controls ([`fa0c38d`](https://github.com/fhempy/fhempy/commit/fa0c38da1efdab7fb5cb368fddaaf24005be1ca2))

* fix reconnect ([`30a2c96`](https://github.com/fhempy/fhempy/commit/30a2c965ba34c147147111c7eaf7c950327a1b00))

* fix shutdown restart ([`661532d`](https://github.com/fhempy/fhempy/commit/661532d35688b650c6c55f955663fc073fa988e9))

* add aiohttp ([`a665928`](https://github.com/fhempy/fhempy/commit/a66592807722194a1a9c531176cdae723f5fcc8f))

* update controls ([`bc620e9`](https://github.com/fhempy/fhempy/commit/bc620e912e83f999627b58bde9beb01e2826712f))

* fix default media app ([`edef1a3`](https://github.com/fhempy/fhempy/commit/edef1a31aca32bf952f756986bc105bd39836fc2))

* fix shutdown restart ([`6583c63`](https://github.com/fhempy/fhempy/commit/6583c639497fda138cc5c2a0c8369ce9a78dca38))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`beb6674`](https://github.com/fhempy/fhempy/commit/beb66742bdfdfaed4f7a072484f77e81d67bbc45))

* update controls ([`0965f20`](https://github.com/fhempy/fhempy/commit/0965f207b687f784faa3ba30a8420f3b9b36cb50))

* fix re-discover of same device ([`f19b5ed`](https://github.com/fhempy/fhempy/commit/f19b5edeb3950c41b00346d383973e84ac70f265))

* fix shutdown restart ([`4490c57`](https://github.com/fhempy/fhempy/commit/4490c57f0f824e402010486827803e0c326903ca))

* Add flowchart ([`46090f3`](https://github.com/fhempy/fhempy/commit/46090f3c4e1817270c0d8f4efd26ad1add42b89b))

* Add flowchart ([`84f73fa`](https://github.com/fhempy/fhempy/commit/84f73fab3871955ec1e29ef53cacbdcae2874aa5))

* Update README.md ([`a5727b0`](https://github.com/fhempy/fhempy/commit/a5727b01dc09537fb4b1a51f2596216aff8869f5))

* prepare DevIo_DecodeWS usage ([`b4f9b8a`](https://github.com/fhempy/fhempy/commit/b4f9b8ac8dcaa33cda2962c6c83fa65f472ac5e8))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`5ab96e8`](https://github.com/fhempy/fhempy/commit/5ab96e812b1f9922584d584ef03a1c8ad43c799e))

* fix chmod ([`7da00f8`](https://github.com/fhempy/fhempy/commit/7da00f81af74e6b47b24070b7062da4c30fafb1b))

* change Protocol::WebSocket installation ([`fd33453`](https://github.com/fhempy/fhempy/commit/fd33453b6beac2a68892c02ba55b83e5d7888063))

* Update README.md ([`2eae477`](https://github.com/fhempy/fhempy/commit/2eae477b6a298d791eeae726d23c52d0ff38bd7f))

* fix possible concurrency ([`765b163`](https://github.com/fhempy/fhempy/commit/765b1639c862e39d69c067f4b1dc00b7019b1989))

* update controls ([`d7e4b2a`](https://github.com/fhempy/fhempy/commit/d7e4b2a3f89354a0b6e2926a31b60d0016681a0b))

* better log ([`532c40f`](https://github.com/fhempy/fhempy/commit/532c40f788477aabe046951972cbb6950e1c01a2))

* fix websockets again ([`f808e22`](https://github.com/fhempy/fhempy/commit/f808e220699c3c09184cfc057b1ea06d9c912b81))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`520e45c`](https://github.com/fhempy/fhempy/commit/520e45c9197f37d64454d03ed86aadb2c546bb84))

* add blescanner ([`8ba400f`](https://github.com/fhempy/fhempy/commit/8ba400f0a39420a5e1f3b13fb97b4bace06d0e6b))

* update dependencies ([`5232213`](https://github.com/fhempy/fhempy/commit/523221379b63454813d3bb1eddf4f8bc0e72efc6))

* update controls ([`2b937ec`](https://github.com/fhempy/fhempy/commit/2b937ec188fcaca058ba95b8eb224be426c2f9e6))

* add blescanner ([`869ee2b`](https://github.com/fhempy/fhempy/commit/869ee2b8ddabd39bed61a87e121f0af1da6b0264))

* fix websocket issues ([`2eb624d`](https://github.com/fhempy/fhempy/commit/2eb624d65dd92957bd1a1bbb5a6bc904501affa6))

* fix dashcast
stop browser on Define ([`8cea161`](https://github.com/fhempy/fhempy/commit/8cea1618005a21cb448ade5519b07131e2de9928))

* stop scan on Undefine ([`33ab799`](https://github.com/fhempy/fhempy/commit/33ab799f4343002c87bab1b67e36f9a3db105743))

* update controls ([`4521571`](https://github.com/fhempy/fhempy/commit/4521571d263e42f7069cf21ff66f0d3e2914a9f1))

* add chmod ([`31235b4`](https://github.com/fhempy/fhempy/commit/31235b47eae9a2615ba86e6e5017a808ee70653d))

* handle connectionclosed ([`31603c9`](https://github.com/fhempy/fhempy/commit/31603c9564eb05e2d2694f0e8e3c5a3cb9ee1614))

* handle duration not present ([`bc2c7b5`](https://github.com/fhempy/fhempy/commit/bc2c7b51685968f5a5639334ae7076fbdd7debbb))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`79b5274`](https://github.com/fhempy/fhempy/commit/79b5274b1c1c9ab25de9e698d78fd41b625e9afa))

* change to Python3
remove dependencies ([`09d1131`](https://github.com/fhempy/fhempy/commit/09d1131644404d2b1bd99d26fc26d099c440271b))

* add chmod ([`54d6253`](https://github.com/fhempy/fhempy/commit/54d62535872d052a8e12695ff6511bd21eefd1cc))

* fix ([`458e243`](https://github.com/fhempy/fhempy/commit/458e243c59e11978c2fa4d1b4d8bfeced16d4c25))

* Update README.md ([`9c02bfd`](https://github.com/fhempy/fhempy/commit/9c02bfdc53b84f75c58f5bcc57e187997e5962d8))

* remove empty line ([`b947354`](https://github.com/fhempy/fhempy/commit/b94735404bd904657af4e38acf32b79544439e6d))

* update ([`242e09f`](https://github.com/fhempy/fhempy/commit/242e09fb27f2603c5fa212900770f801eda521e1))

* add comment ([`ece767e`](https://github.com/fhempy/fhempy/commit/ece767ea4221872abcbbbc4e05bf4f6474eea38f))

* control =&gt; controls ([`c005475`](https://github.com/fhempy/fhempy/commit/c00547509f8624eca0b3c4c2059af09ee317b0d9))

* rename ([`8e676f7`](https://github.com/fhempy/fhempy/commit/8e676f7fe91da397a4796d04fefe0d21fce67c0e))

* fix log ([`dbd8343`](https://github.com/fhempy/fhempy/commit/dbd83431a52eb7782ac96a2974b05d9ac7581ab3))

* only python3 supported ([`de2f73b`](https://github.com/fhempy/fhempy/commit/de2f73bfdaf62c160063c912d496fbd416e2d6c0))

* do not handle msgs when fct active ([`3be6b1d`](https://github.com/fhempy/fhempy/commit/3be6b1d7cd221ff3056b1719befd54d622ff6588))

* change reconnect time ([`81e710d`](https://github.com/fhempy/fhempy/commit/81e710d90e3a77572272ed0a8d14c90282e517a4))

* fix CancelledError ([`2a8e4d4`](https://github.com/fhempy/fhempy/commit/2a8e4d4162f785e0870d4e47ef82f352fba0a6e3))

* add reading lastFoundService
do not wait for zeroconf while Define ([`4e94cb1`](https://github.com/fhempy/fhempy/commit/4e94cb180a3a1ab395af426592929e7691f0ffe0))

* do not handle async msgs as long as fct is active ([`ce5bef0`](https://github.com/fhempy/fhempy/commit/ce5bef0251894b2bbd19209eb94cc9e1f7c42c4b))

* set state to active ([`5a53948`](https://github.com/fhempy/fhempy/commit/5a53948a90b4a95714aa7908e88fa4f0a2cd20ce))

* change nextOpenDelay to 2s
use verbose 5 for debugging
fix reopen when closed ([`cfb2247`](https://github.com/fhempy/fhempy/commit/cfb22470834214ffbd7319f9ca72156f960d8744))

* add reading ([`02596c6`](https://github.com/fhempy/fhempy/commit/02596c65468951aaa9d94f14b88bd67acedf491b))

* add error log ([`789bee4`](https://github.com/fhempy/fhempy/commit/789bee443de3d794e9a9a3d9ba264198a8e84a01))

* add log ([`8bf1284`](https://github.com/fhempy/fhempy/commit/8bf128402553dd860749eeae58f3323107e56300))

* remove test comment ([`630a975`](https://github.com/fhempy/fhempy/commit/630a975983d83e5db89d727027dd32384c4c2c2d))

* reconnect each second ([`219fec7`](https://github.com/fhempy/fhempy/commit/219fec7311b47f502f53ed77389f9a1b326a01b5))

* update FHEM controls ([`3133a7f`](https://github.com/fhempy/fhempy/commit/3133a7f844ec9aa4da9a3e172df5f39e14a35f71))

* update TODOs ([`7ce250e`](https://github.com/fhempy/fhempy/commit/7ce250eeee84ae2fcfb66970fa7dbedfdc2cb504))

* add helloworld
add cast youtube ([`5e53d7e`](https://github.com/fhempy/fhempy/commit/5e53d7e9d5d42d936f0474a8af2362c458ddd824))

* update imports ([`3302da2`](https://github.com/fhempy/fhempy/commit/3302da24e6260189cd69e598abf10b5d4079655f))

* do not cache cmds ([`decd1b2`](https://github.com/fhempy/fhempy/commit/decd1b26066ee03f67ff8445959473319c2c9974))

* move to hidden room ([`a08bc6d`](https://github.com/fhempy/fhempy/commit/a08bc6dffc60ee5f30c358c75c98248bc6495cff))

* fix connection error
move to hidden room ([`57873c5`](https://github.com/fhempy/fhempy/commit/57873c5f30ecadeaeaf5117bbf952f829e90269e))

* prepare spotify
update README/TODO ([`27b7327`](https://github.com/fhempy/fhempy/commit/27b732707a011d94d99c2cd04c701bf1aac91a2d))

* use websockets instead of autobahn
a lot of bugfixes ([`4bd050e`](https://github.com/fhempy/fhempy/commit/4bd050e48924455b573de2b33522c519d7f4f968))

* bugfixes and optimizations ([`d679cc1`](https://github.com/fhempy/fhempy/commit/d679cc1b4defec355736cbd7b14a2a520cbf1985))

* small fixes for ws handling ([`f3d9c68`](https://github.com/fhempy/fhempy/commit/f3d9c687254dc87272ae48d3d20de69796954242))

* message handling fixes ([`b7c5fda`](https://github.com/fhempy/fhempy/commit/b7c5fda42a7b8a7ffe2b55b6dad093a7da91dec5))

* msg handling fixes ([`507a2e2`](https://github.com/fhempy/fhempy/commit/507a2e276aa95f2f787ee18b5b4e91799f7470c9))

* lot of msg handling fixes ([`0f8fae0`](https://github.com/fhempy/fhempy/commit/0f8fae0f7e439a347301e22be3b9d36c0112f5f7))

* support Define on reconnect
better message handling
reconnect currently not working ([`bba05c1`](https://github.com/fhempy/fhempy/commit/bba05c11c3404fd380c1e531b081460bac192e06))

* fix multithreading issues ([`8a7a625`](https://github.com/fhempy/fhempy/commit/8a7a6251795e4d0c366690f0818775efa4209b3d))

* fix checkIfDeviceExists ([`9e411c5`](https://github.com/fhempy/fhempy/commit/9e411c55495e24b5e3fb27c32c272796b201a747))

* support BOSEST ([`a5cc3b6`](https://github.com/fhempy/fhempy/commit/a5cc3b6d746c1a16d6655c9868b3d795f5f193dc))

* create device only if not available ([`9a0ccd2`](https://github.com/fhempy/fhempy/commit/9a0ccd2c58a18ad7f353466989ee50b9bc3cace2))

* add checkIfDeviceExists ([`f1fd3fb`](https://github.com/fhempy/fhempy/commit/f1fd3fb46f255ee7957aee09f4715efd91df1cae))

* import all modules
change log level to INFO ([`64ab9c7`](https://github.com/fhempy/fhempy/commit/64ab9c79784456b714162907cde98461e4c9186a))

* fix return value ([`26ec8a5`](https://github.com/fhempy/fhempy/commit/26ec8a53ede852143b9a29f72ade795fa01c1c22))

* add helloworld example
add TODO ([`c129b99`](https://github.com/fhempy/fhempy/commit/c129b99dcdb3a965e241d6527f3a17314ba27f16))

* add controls to README ([`00264ca`](https://github.com/fhempy/fhempy/commit/00264ca31de09d0f1c206ce06821bbede2bfcc22))

* add dependencies ([`a785e7c`](https://github.com/fhempy/fhempy/commit/a785e7c179aec777c5b4fc26ffe030e777d24ea2))

* Merge branch &#39;master&#39; of https://github.com/dominikkarall/fhem_pythonbinding ([`a12b723`](https://github.com/fhempy/fhempy/commit/a12b723131e23ec5b57bb7933e06aa977e23c1d6))

* prepare control file ([`d3b8bae`](https://github.com/fhempy/fhempy/commit/d3b8baed5040dcb487e0c4ab71659d339761e412))

* Typo in README ([`e738a2c`](https://github.com/fhempy/fhempy/commit/e738a2c9f26fcbcf02699fda89ba8ee26cf21e17))

* Update README

restructure ([`5aade5a`](https://github.com/fhempy/fhempy/commit/5aade5a8b067cb4dfa46c3c06235246c96865420))

* Update README

add further details ([`79a17aa`](https://github.com/fhempy/fhempy/commit/79a17aa5da45e0568a3070d1c50835ad676c7e26))

* initial commit ([`46bc6cf`](https://github.com/fhempy/fhempy/commit/46bc6cf54351af5c35e1c18f45bf2e089502d4df))

* Initial commit ([`4210f19`](https://github.com/fhempy/fhempy/commit/4210f191c9774c12d18c6624272ab2f9248aab24))
