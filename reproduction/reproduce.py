"""Require the three ownership failures in the installed, unchanged 18.0.1 library."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
package = root / 'ReproducerApp/node_modules/react-native-camera-kit'
assert json.loads((package / 'package.json').read_text())['version'] == '18.0.1'
expected = {
    'CKCamera.kt': '02c357c14e2f289ef418ca4f1d3e306ee203d98040f69c6581aac2c86cb284d0',
    'QRCodeAnalyzer.kt': '718f5ecc1db87006869f2ad5cd77b5d92d25137e04c8af4b794bcc892d017a9d',
    'FaceAnalyzer.kt': 'f4e14559f394093fc7fb381a98735f1081496e5a928e6acdaa0dad994bdb34f4',
}
for name, digest in expected.items():
    source = package / 'android/src/main/java/com/rncamerakit' / name
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest, name

build = package / 'android/build.gradle'
s = build.read_text()
if 'testImplementation' not in s:
    s = s.replace('android {', 'android {\n    testOptions { unitTests.includeAndroidResources = true }', 1)
    s = s.replace('dependencies {', "dependencies {\n    testImplementation 'junit:junit:4.13.2'\n    testImplementation 'org.robolectric:robolectric:4.14.1'\n    testImplementation 'org.mockito:mockito-core:5.18.0'", 1)
    build.write_text(s)
target = package / 'android/src/test/java/com/rncamerakit/BarcodeOwnershipRegressionTest.kt'
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(root / 'reproduction/BarcodeOwnershipRegressionTest.kt', target)
evidence = root / 'evidence'
evidence.mkdir(exist_ok=True)
command = ['./gradlew', ':react-native-camera-kit:testDebugUnitTest', '-PnewArchEnabled=true',
           '--tests', 'com.rncamerakit.BarcodeOwnershipRegressionTest', '--console=plain', '--max-workers=2']
with (evidence / 'baseline.log').open('w') as log:
    print('Running:', ' '.join(command), flush=True)
    result = subprocess.run(command, cwd=root / 'ReproducerApp/android', stdout=log, stderr=subprocess.STDOUT)
assert result.returncode == 1, result.returncode
report = package / 'android/build/test-results/testDebugUnitTest/TEST-com.rncamerakit.BarcodeOwnershipRegressionTest.xml'
suite = ET.parse(report).getroot()
assert [int(suite.attrib[k]) for k in ['tests', 'failures', 'errors', 'skipped']] == [7, 3, 0, 0], suite.attrib
failures = {case.attrib['name']: case.find('failure') for case in suite.findall('testcase') if case.find('failure') is not None}
assert set(failures) == {'repeatedFramesReuseOneOwnedScanner', 'secondConsumerThrowStillClosesAfterTheFirstCompletes', 'firstConsumerThrowStillRunsTheSecondAndClosesAfterIt'}
assert 'expected:<1> but was:<3>' in failures['repeatedFramesReuseOneOwnedScanner'].attrib['message']
assert 'imageProxy.close' in failures['secondConsumerThrowStillClosesAfterTheFirstCompletes'].attrib['message']
assert 'faceAnalyzer.analyzeWithoutClosing' in failures['firstConsumerThrowStillRunsTheSecondAndClosesAfterIt'].attrib['message']
shutil.copy2(report, evidence / 'baseline.xml')
(evidence / 'source-hashes.json').write_text(json.dumps(expected, indent=2) + '\n')
print('REPRODUCED: 3 intended native ownership failures, 4 passing controls, 0 skips.')
