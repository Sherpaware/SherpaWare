"""Copy the published public page (repo root index.html, no trip data) into www/ for Capacitor.
Usage: python3 scripts/prepare_web.py [path to index.html]"""
import sys, os, shutil
here = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', '..', 'index.html')
if not os.path.exists(src): sys.exit('missing ' + src)
out = os.path.join(here, '..', 'www'); os.makedirs(out, exist_ok=True)
shutil.copy(src, os.path.join(out, 'index.html'))
print('www/index.html written,', os.path.getsize(os.path.join(out, 'index.html')), 'bytes')
