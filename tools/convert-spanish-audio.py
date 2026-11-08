import json,sys,warnings
warnings.filterwarnings('ignore',category=DeprecationWarning)
import aifc,av
from pathlib import Path
src=Path('work/pauly-spanish-audio');dest=Path('work/pauly-localized/PMES/SOUNDS');dest.mkdir(parents=True,exist_ok=True)
files=list(src.glob('*.mp3'))
if len(sys.argv)>1:files=[p for p in files if p.stem==sys.argv[1]]
report=[]
for p in files:
 output=dest/(p.stem+'.AIF')
 if output.exists() and output.stat().st_mtime>p.stat().st_mtime:continue
 frames=0
 with av.open(str(p)) as reader,aifc.open(str(output),'wb') as writer:
  writer.setnchannels(1);writer.setsampwidth(2);writer.setframerate(22050)
  resampler=av.AudioResampler(format='s16',layout='mono',rate=22050)
  for frame in reader.decode(audio=0):
   for converted in resampler.resample(frame):
    values=converted.to_ndarray();writer.writeframesraw(values.astype('>i2').tobytes());frames+=converted.samples
  for converted in resampler.resample(None):writer.writeframesraw(converted.to_ndarray().astype('>i2').tobytes());frames+=converted.samples
 report.append({'file':output.name,'seconds':round(frames/22050,3)});print(output.name,frames,flush=True)
Path('work/pauly-spanish-aiff-report.json').write_text(json.dumps(report,indent=2),'utf8');print('AIFF READY',len(report),flush=True)
