# Camera Kit Android scanner ownership reproduction

Reproducer for [teslamotors/react-native-camera-kit#811](https://github.com/teslamotors/react-native-camera-kit/issues/811).
Based on the required [React Native reproducer template](https://github.com/react-native-community/reproducer-react-native).
The app is pinned to that template's React Native 0.81.0 revision
[`e23019c`](https://github.com/react-native-community/reproducer-react-native/commit/e23019c91a8dce5502bf233012c28ae30e2bf03a),
matching Camera Kit's example, and installs the published `react-native-camera-kit@18.0.1`.

Clone the standard-template reproducer:

```sh
git clone https://github.com/zack-dev-cm/camera-kit-scanner-reproducer.git
cd camera-kit-scanner-reproducer
```

## Deterministic reproduction

Use Node 22, Yarn 1.22.22, JDK 17, Python 3 and an Android SDK:

```sh
cd ReproducerApp
yarn install --frozen-lockfile --ignore-scripts
cd ..
python3 reproduction/reproduce.py
```

The script first checks SHA-256 hashes of the three exercised production classes
against upstream `a2a81cee8995c831aca472836e2be446994ba070`. It adds only test
configuration and a regression class to the installed package, then requires
these three failures and four passing controls (seven tests, zero skips):

- Three frames create three scanners where one owned scanner is expected.
- A synchronous exception from the second image consumer leaves the image open
  after the first task finishes.
- A synchronous exception from the first consumer prevents the second from
  running and leaves the image open.

The regression compiles and invokes the real `CKCamera`/`QRCodeAnalyzer` code
under Robolectric. Scanner factories and asynchronous task completion are
controlled at the ML Kit boundary. This is not a translated model of the
implementation and is not a physical-device memory or battery measurement.
The script succeeds only when the expected native failures are observed;
setup/compiler failures do not count as reproduction. Raw Gradle logs, JUnit
XML and source hashes are written to `evidence/`.

## Minimal app

```sh
cd ReproducerApp
yarn start
# In a second terminal:
yarn android
```

Tap **Mount barcode camera**, allow camera access, show an authored QR code, and
then tap **Unmount camera**. Repeat as needed. The app shows actual barcode
callback counts; it does not infer scanner allocations from callback counts.
Use the native regression above to assert allocation and shared-image ownership.

This Android-only bug reproducer does not claim an iOS test. The independently
corrected source branch and its Android/iOS compatibility evidence are linked
from the upstream PR. No production correction is included in this repository.

Prepared with AI assistance; the template's MIT license is retained.
