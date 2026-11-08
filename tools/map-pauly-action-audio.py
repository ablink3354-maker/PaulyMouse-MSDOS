import json,re
from pathlib import Path
review=json.loads(Path('work/pauly-spanish-reviewed.json').read_text('utf8'));out={}
for room in range(1,10):
 d=json.loads(Path(f'work/pauly-original-web/scene{room}.json').read_text('utf8'));markers=sorted([m for m in d['markers'] if re.fullmatch('A[0-9]+',m['name'])],key=lambda x:x['frame']);labels={}
 for code in d['scripts'].values():
  m=re.search(r'set s[0-9] = ([0-9]+).*?go "(A[0-9]+)"',code,re.I|re.S)
  if m:labels[m[2]]=int(m[1])
 for track in ['sound1','sound2']:
  for event in d['score'][track]:
   name=d['sounds'][str(event['castId'])]['name'].upper()
   if not name.startswith('SEF'):continue
   past=[m for m in markers if m['frame']<=event['startFrame']]
   if not past:continue
   label=past[-1]['name'];animal=labels.get(label,0);out[name]={'room':room,'action':label,'animal':animal,'name':review.get(f'{room}-{animal}',{}).get('name','Pauly')}
Path('work/pauly-action-audio-map.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
for name,item in sorted(out.items()):print(name,item['name'],item['action'])
