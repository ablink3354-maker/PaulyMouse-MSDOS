from pathlib import Path
import urllib.request,hashlib
root=Path(__file__).resolve().parent.parent
dest=root/'vendor/scummvm-android-2.9.1-arm64.apk';dest.parent.mkdir(exist_ok=True)
expected='83b6b8d9c1f8edc262cba66f18738a5e6ad155684525ab32d14c0bd0f84e6016'
if not dest.exists() or hashlib.sha256(dest.read_bytes()).hexdigest()!=expected:
 temp=dest.with_suffix('.part')
 urllib.request.urlretrieve('https://downloads.scummvm.org/frs/scummvm/2.9.1/scummvm-2.9.1-android-arm64-v8a.apk',temp)
 assert hashlib.sha256(temp.read_bytes()).hexdigest()==expected,'La descarga del motor no coincide'
 temp.replace(dest)
print('Motor oficial 2.9.1 verificado.')
