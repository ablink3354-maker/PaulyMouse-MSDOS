import json,shutil
from pathlib import Path
items=json.loads(Path('work/pauly-spanish-instructions.json').read_text('utf8'))
for item in items:
 item['character']='Narrador';name=Path(item['file']).stem+'.mp3';shutil.copy2(Path('work/pauly-spanish-audio')/name,Path('work/pauly-audio-upgrade/voices')/name)
Path('work/pauly-instructions-mix-input.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),'utf8')
