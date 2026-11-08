import json,struct,hashlib,importlib.util,warnings
from pathlib import Path
warnings.filterwarnings('ignore',category=DeprecationWarning)
import aifc,av,numpy as np
spec=importlib.util.spec_from_file_location('book',Path(__file__).with_name('localize-director-books.py'));book=importlib.util.module_from_spec(spec);spec.loader.exec_module(book)
original=Path('work/pauly/PaulyMouse_Win10/Data/PMNL');current=Path('work/pauly-localized/PMES');report={'scenes':[]}
for room in range(1,10):
 patch=book.DirectorPatcher(current/f'SCENE{room}.DXR');counts={}
 for p in (Path(f'work/pauly-assets/SCENE{room}')/'bin').iterdir():
  kind=p.suffix[1:]
  if kind not in ['BITD','CASt','VWSC']:continue
  entry=patch.map+8+patch.properties+int(p.stem)*patch.entry_size;size,offset=struct.unpack_from(patch.order+'II',patch.data,entry+4);actual=patch.data[offset+8:offset+8+size]
  assert bytes(actual)==p.read_bytes(),(room,p.name,'original artwork/score changed')
  counts[kind]=counts.get(kind,0)+1
 assert counts.get('BITD',0)>0 and counts.get('VWSC',0)>0,counts
 report['scenes'].append({'room':room,'unchangedOriginalResources':counts})
 print('ORIGINAL_SCENE_ART_AND_TIMELINE',room,counts,flush=True)
for p in original.glob('*.MOV'):assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((current/p.name).read_bytes()).digest(),p.name
expected={x[k] for x in json.loads(Path('work/pauly-book-audio-map.json').read_text('utf8')) for k in ['questionFile','answerFile']}
expected.update(x['file'] for x in json.loads(Path('work/pauly-spanish-instructions.json').read_text('utf8')))
characters=json.loads(Path('work/pauly-character-dialogues-es.json').read_text('utf8'));expected.update(x['file'] for x in characters if not x['preserveOriginal']);expected.update(['TBGM.AIF','HELPVOL.AIF','ECOC2.AIF'])
changed=[];preserved=[];seconds=0
for p in sorted((current/'SOUNDS').glob('*.AIF')):
 source=original/'SOUNDS'/p.name;same=hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(source.read_bytes()).digest()
 if p.name in expected:
  assert not same,(p.name,'Spanish file missing')
  with aifc.open(str(p),'rb') as f:
   assert (f.getnchannels(),f.getsampwidth(),f.getframerate())==(1,2,22050),p.name
   duration=f.getnframes()/22050
  if not p.name.startswith(('QUE','DEF')):
   with aifc.open(str(source),'rb') as f:old_duration=f.getnframes()/f.getframerate()
   assert abs(duration-old_duration)<=1/22050,(p.name,duration,old_duration)
  with av.open(str(p)) as audio:
   n=0;peak=0
   for frame in audio.decode(audio=0):
    data=frame.to_ndarray();assert np.all(np.isfinite(data)),p.name;n+=frame.samples;peak=max(peak,float(np.max(np.abs(data.astype(np.float32)))))
   assert n>0 and peak>0,p.name
  changed.append(p.name);seconds+=duration
 else:
  assert same,(p.name,'Unrequested sound alteration');preserved.append(p.name)
assert set(changed)==expected
report.update({'unchangedOriginalMovies':len(list(original.glob('*.MOV'))),'spanishAudioFiles':len(changed),'unchangedOriginalSoundFiles':len(preserved),'spanishCharacterLines':sum(not x['preserveOriginal'] for x in characters),'spanishAudioMinutes':round(seconds/60,2),'voiceDecodeErrors':0,'fixedDurationChecks':'passed','webCancelled':True})
Path('work/pauly-v04-integrity-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({k:v for k,v in report.items() if k!='scenes'},ensure_ascii=False),flush=True)
