"""After `npx cap add ios`: add the location/background keys the app needs to Info.plist, and make it iPad-only.
Safe to run twice."""
import plistlib, os, re, sys
base = os.path.join(os.path.dirname(__file__), '..', 'ios', 'App')
pl = os.path.join(base, 'App', 'Info.plist')
if not os.path.exists(pl): sys.exit('no Info.plist at ' + pl + ' (run npx cap add ios first)')
d = plistlib.load(open(pl, 'rb'))
d['NSLocationWhenInUseUsageDescription'] = 'SherpaWare uses location to record block, takeoff, landing and block-in times at the aircraft.'
d['NSLocationAlwaysAndWhenInUseUsageDescription'] = 'SherpaWare keeps recording flight times while ForeFlight is on screen. Location is not sent anywhere.'
d['ITSAppUsesNonExemptEncryption'] = False  # no custom encryption: skips the export-compliance question on each upload
d['CFBundleDisplayName'] = 'SherpaWare'
modes = set(d.get('UIBackgroundModes', [])); modes.add('location'); d['UIBackgroundModes'] = sorted(modes)
plistlib.dump(d, open(pl, 'wb'))
print('Info.plist updated')
# iPad only (TARGETED_DEVICE_FAMILY = 2)
pj = os.path.join(base, 'App.xcodeproj', 'project.pbxproj')
if os.path.exists(pj):
    s = open(pj).read(); s2 = re.sub(r'TARGETED_DEVICE_FAMILY = "?[0-9,]+"?;', 'TARGETED_DEVICE_FAMILY = 2;', s)
    open(pj, 'w').write(s2); print('device family set to iPad')

# App icon: replace the template's icon with ours (1024 x 1024, no transparency)
import json, shutil
ic = os.path.join(base, 'App', 'Assets.xcassets', 'AppIcon.appiconset')
src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'icon-1024.png')
cj = os.path.join(ic, 'Contents.json')
if os.path.exists(cj) and os.path.exists(src):
    for im in json.load(open(cj)).get('images', []):
        fn = im.get('filename')
        if fn: shutil.copy(src, os.path.join(ic, fn)); print('icon ->', fn)
