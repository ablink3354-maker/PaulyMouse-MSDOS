import json,hashlib
from pathlib import Path
manifest=json.loads(Path('release-manifest.json').read_text('utf8'))
for item in manifest['files']:
 p=Path('release-assets/releases')/item['name']
 assert p.is_file(),p
 assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==item['sha256'],p
 print('SHA256 verificado:',p.name)
