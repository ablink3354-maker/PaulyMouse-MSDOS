"""Mix Spanish cartoon voices with recovered original effects at original durations.

The separated background is used only where the vocal stem is active. Elsewhere
the original audio is retained. Music/ambience files outside dialogue are untouched.
"""
import av,numpy as np,aifc,wave,json,time,warnings,sys
from fractions import Fraction
from pathlib import Path
warnings.filterwarnings('ignore',category=DeprecationWarning)
ROOT=Path('work/pauly-audio-upgrade');SRC=Path('work/pauly/PaulyMouse_Win10/Data/PMNL/SOUNDS');DEST=Path('work/pauly-localized/PMES/SOUNDS');SR=44100
extras='--extras' in sys.argv;instructions='--instructions' in sys.argv
items=json.loads(Path('work/pauly-instructions-mix-input.json' if instructions else 'work/pauly-extra-voices-es.json' if extras else 'work/pauly-character-dialogues-es.json').read_text('utf8'));report=[]
def read(path,rate=SR):
 chunks=[]
 with av.open(str(path)) as c:
  r=av.AudioResampler(format='fltp',layout='mono',rate=rate)
  for f in c.decode(audio=0):
   for z in r.resample(f):chunks.append(z.to_ndarray()[0])
  for z in r.resample(None):chunks.append(z.to_ndarray()[0])
 return np.concatenate(chunks).astype(np.float32)
def fit(audio,limit):
 if len(audio)<=limit:return audio,1.0
 speed=len(audio)/limit*1.015
 if speed>1.55:raise ValueError(f'Frase demasiado larga para la animación ({speed:.2f}x)')
 graph=av.filter.Graph();src=graph.add_abuffer(sample_rate=SR,format='fltp',layout='mono',time_base=Fraction(1,SR));tempo=graph.add('atempo',str(speed));sink=graph.add('abuffersink');graph.link_nodes(src,tempo,sink);graph.configure()
 frame=av.AudioFrame.from_ndarray(audio.reshape(1,-1),format='fltp',layout='mono');frame.sample_rate=SR;frame.time_base=Fraction(1,SR);frame.pts=0;graph.push(frame);graph.push(None);parts=[]
 while True:
  try:parts.append(graph.pull().to_ndarray()[0])
  except (av.error.EOFError,av.error.BlockingIOError):break
 result=np.concatenate(parts);return result[:limit],speed
def original_duration(name):
 with aifc.open(str(SRC/name),'rb') as f:return f.getnframes()/f.getframerate()
def background(name):
 original=read(SRC/name);effects=read(ROOT/'stems'/(Path(name).stem+'-effects.wav'));vocal=read(ROOT/'stems'/(Path(name).stem+'-voice.wav'));n=min(len(original),len(effects),len(vocal));original=original[:n];effects=effects[:n];vocal=vocal[:n]
 block=882;count=(n+block-1)//block;rms=np.sqrt(np.mean(np.pad(vocal,(0,count*block-n)).reshape(count,block)**2,axis=1));threshold=max(.003,float(rms.max())*.035);active=rms>threshold
 # Spread a short margin around each detected vocal region, keeping effects
 # outside those regions exactly from the original decoded mix.
 active=np.convolve(active.astype(float),np.ones(5),mode='same')>0
 mask=np.interp(np.arange(n),np.arange(count)*block+block/2,active.astype(float)).astype(np.float32)
 clean=original*(1-mask)+effects*mask
 start=int(np.flatnonzero(active)[0]*block) if np.any(active) else min(int(.12*SR),n//12)
 return clean,start,original_duration(name)
def add_voice(mix,voice,start):
 peak=float(np.max(np.abs(voice))) if len(voice) else 0
 if peak:voice=voice*min(2.0,.82/peak)
 fade=min(int(.012*SR),len(voice)//2)
 if fade:voice[:fade]*=np.linspace(0,1,fade);voice[-fade:]*=np.linspace(1,0,fade)
 end=min(len(mix),start+len(voice));mix[start:end]+=voice[:end-start]
def write(name,mix,duration):
 peak=float(np.max(np.abs(mix)));mix=mix*(.96/max(.96,peak))
 f=av.AudioFrame.from_ndarray(mix.reshape(1,-1).astype(np.float32),format='fltp',layout='mono');f.sample_rate=SR;r=av.AudioResampler(format='s16',layout='mono',rate=22050);frames=r.resample(f)+r.resample(None);pcm=np.concatenate([x.to_ndarray()[0] for x in frames]);expected=round(duration*22050);pcm=np.pad(pcm[:expected],(0,max(0,expected-len(pcm))))
 with aifc.open(str(DEST/name),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050);w.writeframes(pcm.astype('>i2').tobytes())
 return len(pcm)/22050
for item in items:
 name=item['file'];effects=ROOT/'stems'/(Path(name).stem+'-effects.wav')
 while not effects.exists():print('WAITING_STEM',name,flush=True);time.sleep(5)
 mix,start,duration=background(name);voice=read(ROOT/'voices'/(Path(name).stem+'.mp3'));voice,speed=fit(voice,max(1,len(mix)-int(.06*SR)));start=max(0,min(start,len(mix)-len(voice)));add_voice(mix,voice,start);seconds=write(name,mix,duration)
 report.append({'file':name,'originalSeconds':duration,'dubbedSeconds':seconds,'tempo':round(speed,3),'character':item['character'],'adaptedDialogue':True});print('MIXED',name,round(seconds,3),flush=True)
 if name=='SEF101N.AIF':
  pcm=read(DEST/name,22050)
  with wave.open('outputs/Pauly-voz-y-efectos-espanol.wav','wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050);w.writeframes((np.clip(pcm,-1,1)*32767).astype('<i2').tobytes())
 Path('work/pauly-instructions-mix-report.json' if instructions else 'work/pauly-extra-mix-report.json' if extras else 'work/pauly-character-mix-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
if extras or instructions:print('INSTRUCTIONS_DUBBED' if instructions else 'EXTRAS_DUBBED',len(report),flush=True);sys.exit(0)
name='TBGM.AIF'
while not (ROOT/'stems/TBGM-effects.wav').exists():print('WAITING_STEM',name,flush=True);time.sleep(5)
mix,start,duration=background(name);starts=[.8,15.5,24,39,64,76];ends=[15,23.5,38.5,63.5,75.5,duration]
for i,(start,end) in enumerate(zip(starts,ends)):
 voice=read(ROOT/'voices'/f'TBGM-{i}.mp3');voice,speed=fit(voice,int((end-start)*SR));add_voice(mix,voice,int(start*SR))
write(name,mix,duration);report.append({'file':name,'originalSeconds':duration,'dubbedSeconds':duration,'voices':6,'adaptedDialogue':False});Path('work/pauly-character-mix-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print('ALL_DUBBED',len(report),flush=True)
