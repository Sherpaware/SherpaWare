"""Fallback signing for CI (no Mac needed): create a short-lived Apple Distribution certificate and an
App Store profile through the App Store Connect API, print the files for the workflow to install,
and revoke them again with `cleanup`. Uses the API key already in ~/private_keys.
Usage: asc_signing.py create <outdir> | asc_signing.py cleanup <outdir>
Env: ISSUER, KEY_ID, BUNDLE (default com.sherpaware.n282bt)."""
import os, sys, json, time, base64, subprocess, urllib.request
import jwt  # pip install pyjwt cryptography
API='https://api.appstoreconnect.apple.com/v1'
ISS, KID = os.environ['ISSUER'], os.environ['KEY_ID']
BUNDLE = os.environ.get('BUNDLE', 'com.sherpaware.n282bt')
def tok():
    k = open(os.path.expanduser(f'~/private_keys/AuthKey_{KID}.p8')).read()
    return jwt.encode({'iss': ISS, 'iat': int(time.time()), 'exp': int(time.time()) + 1100, 'aud': 'appstoreconnect-v1'}, k, algorithm='ES256', headers={'kid': KID, 'typ': 'JWT'})
def call(method, path, body=None):
    r = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body else None,
                               headers={'Authorization': 'Bearer ' + tok(), 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(r) as f: t = f.read(); return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        sys.exit(f'{method} {path} -> HTTP {e.code}: {e.read().decode()[:800]}')
def create(out):
    os.makedirs(out, exist_ok=True)
    subprocess.run(['openssl', 'req', '-new', '-newkey', 'rsa:2048', '-nodes', '-keyout', f'{out}/dist.key',
                    '-out', f'{out}/dist.csr', '-subj', '/CN=SherpaWare CI/O=SherpaWare'], check=True, capture_output=True)
    csr = open(f'{out}/dist.csr').read()
    c = call('POST', '/certificates', {'data': {'type': 'certificates', 'attributes': {'certificateType': 'DISTRIBUTION', 'csrContent': csr}}})['data']
    open(f'{out}/dist.cer', 'wb').write(base64.b64decode(c['attributes']['certificateContent']))
    b = call('GET', f'/bundleIds?filter[identifier]={BUNDLE}&limit=5')['data']
    b = [x for x in b if x['attributes']['identifier'] == BUNDLE]
    if not b: sys.exit(f'bundle id {BUNDLE} not registered')
    name = f'SherpaWare CI {int(time.time())}'
    p = call('POST', '/profiles', {'data': {'type': 'profiles', 'attributes': {'name': name, 'profileType': 'IOS_APP_STORE'},
             'relationships': {'bundleId': {'data': {'type': 'bundleIds', 'id': b[0]['id']}},
                               'certificates': {'data': [{'type': 'certificates', 'id': c['id']}]}}}})['data']
    open(f'{out}/dist.mobileprovision', 'wb').write(base64.b64decode(p['attributes']['profileContent']))
    json.dump({'cert': c['id'], 'profile': p['id'], 'name': name, 'uuid': p['attributes']['uuid']}, open(f'{out}/ids.json', 'w'))
    print(f'created certificate and profile "{name}"')
def cleanup(out):
    try: ids = json.load(open(f'{out}/ids.json'))
    except FileNotFoundError: return print('nothing to clean up')
    call('DELETE', f"/profiles/{ids['profile']}"); call('DELETE', f"/certificates/{ids['cert']}")
    print('revoked CI certificate and deleted profile')
{'create': create, 'cleanup': cleanup}[sys.argv[1]](sys.argv[2])
