"""After `npx cap add ios`: add the location/background keys the app needs to Info.plist, and make it a universal iPhone + iPad app.
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
d['UIRequiresFullScreen'] = False  # allow iPad Split View, Slide Over and Stage Manager (all four orientations must stay supported)
d['UISupportedInterfaceOrientations~ipad'] = ['UIInterfaceOrientationPortrait','UIInterfaceOrientationPortraitUpsideDown','UIInterfaceOrientationLandscapeLeft','UIInterfaceOrientationLandscapeRight']
modes = set(d.get('UIBackgroundModes', [])); modes.add('location'); d['UIBackgroundModes'] = sorted(modes)
plistlib.dump(d, open(pl, 'wb'))
print('Info.plist updated')
# iPhone and iPad (TARGETED_DEVICE_FAMILY = 1,2)
pj = os.path.join(base, 'App.xcodeproj', 'project.pbxproj')
if os.path.exists(pj):
    s = open(pj).read(); s2 = re.sub(r'TARGETED_DEVICE_FAMILY = "?[0-9,]+"?;', 'TARGETED_DEVICE_FAMILY = "1,2";', s)
    open(pj, 'w').write(s2); print('device family set to iPhone + iPad')

# App icon: replace the template's icon with ours (1024 x 1024, no transparency)
import json, shutil
ic = os.path.join(base, 'App', 'Assets.xcassets', 'AppIcon.appiconset')
src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'icon-1024.png')
cj = os.path.join(ic, 'Contents.json')
if os.path.exists(cj) and os.path.exists(src):
    for im in json.load(open(cj)).get('images', []):
        fn = im.get('filename')
        if fn: shutil.copy(src, os.path.join(ic, fn)); print('icon ->', fn)

# Make sure every PNG in the icon set is ours, and say so in the log (md5 of the source vs the set).
import glob, hashlib
if os.path.exists(src) and os.path.isdir(ic):
    h = hashlib.md5(open(src, 'rb').read()).hexdigest()[:8]
    for f in glob.glob(os.path.join(ic, '*.png')): shutil.copy(src, f)
    print('icon set', sorted(os.listdir(ic)), 'source md5', h)
