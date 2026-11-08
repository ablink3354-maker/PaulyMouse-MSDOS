"""Keep nonverbal reactions, calls, musical gags and effects as original bytes.

Only spoken dialogue needs a Spanish dub. This final pass avoids replacing
recognizable laughs, roars, whistles, boings and songs without words by new lines.
Run AFTER all dubbing/mixing, before building the APK.
"""
import json,shutil,hashlib
from pathlib import Path
src=Path('work/pauly/PaulyMouse_Win10/Data/PMNL/SOUNDS');dest=Path('work/pauly-localized/PMES/SOUNDS')
numbers=[107,108,113,202,204,206,208,301,302,303,306,309,312,403,404,405,408,409,410,411,507,510,603,604,605,606,607,610,612,613,701,703,705,708,709,801,802,805,807,810,901,904,907,909,911]
preserve={f'SEF{n}N.AIF' for n in numbers}|{'SEF00009.AIF','SEF200N.AIF','SEF803AN.AIF','SEF803BN.AIF','ECOC1.AIF'}
preserve.update(p.name for p in src.glob('SEF*.AIF') if p.stem.endswith(('N1','N2')))
report=[]
for name in sorted(preserve):
 assert (src/name).is_file(),name
 shutil.copy2(src/name,dest/name);digest=hashlib.sha256((src/name).read_bytes()).hexdigest();assert digest==hashlib.sha256((dest/name).read_bytes()).hexdigest();report.append({'file':name,'sha256':digest,'reason':'Original nonverbal reaction / animal call / instrumental effect'})
items=json.loads(Path('work/pauly-character-dialogues-es.json').read_text('utf8'))
for item in items:item['preserveOriginal']=item['file'] in preserve
Path('work/pauly-character-dialogues-es.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),'utf8')
Path('work/pauly-preserved-effects.json').write_text(json.dumps(report,indent=2),'utf8');print('ORIGINAL_NONVERBAL_FILES',len(report),'SPANISH_CHARACTER_LINES',sum(not x['preserveOriginal'] for x in items),flush=True)
