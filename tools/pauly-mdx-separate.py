"""Small CPU MDX pilot for dialogue replacement; original sources stay untouched.

STFT channel arrangement follows UVR's public MDX ONNX format. The model is not
perfect at distinguishing cartoon effects from speech; keep music/ambience
separately and restore the original wherever no speech-like stem is detected.
"""
import av,numpy as np,torch,onnxruntime as ort,json,hashlib,time,sys,wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
torch.set_num_threads(1)
ROOT=Path('work/pauly-audio-upgrade');MODEL=ROOT/'UVR_MDXNET_KARA_2.onnx';SR=44100
with MODEL.open('rb') as f:f.seek(-10000*1024,2);key=hashlib.md5(f.read()).hexdigest()
PARAMS=json.loads((ROOT/'model_data.json').read_text('utf8'))[key]
print('PARAMETERS',PARAMS,flush=True)
F=PARAMS['mdx_dim_f_set'];T=2**PARAMS['mdx_dim_t_set'];FFT=PARAMS['mdx_n_fft_scale_set'];HOP=1024;SIZE=HOP*(T-1);TRIM=FFT//2;STEP=SIZE-2*TRIM
opts=ort.SessionOptions();opts.intra_op_num_threads=1;opts.inter_op_num_threads=1
session=ort.InferenceSession(str(MODEL),sess_options=opts,providers=['CPUExecutionProvider']);input_name=session.get_inputs()[0].name
window=torch.hann_window(FFT,periodic=True)
def read(path,rate=SR):
 chunks=[]
 with av.open(str(path)) as c:
  resample=av.AudioResampler(format='fltp',layout='stereo',rate=rate)
  for frame in c.decode(audio=0):
   for out in resample.resample(frame):chunks.append(out.to_ndarray())
  for out in resample.resample(None):chunks.append(out.to_ndarray())
 return np.concatenate(chunks,axis=1)
def write(path,audio,rate=SR):
 with wave.open(str(path),'wb') as w:w.setnchannels(audio.shape[0]);w.setsampwidth(2);w.setframerate(rate);w.writeframes((np.clip(audio,-1,1).T*32767).astype('<i2').tobytes())
def split(audio):
 count=audio.shape[1];pad=STEP-count%STEP;padded=np.pad(audio,((0,0),(TRIM,pad+TRIM)));parts=[]
 for start in range(0,count+pad,STEP):
  x=torch.from_numpy(padded[:,start:start+SIZE].copy()).float()
  with torch.no_grad():
   z=torch.stft(x,FFT,HOP,window=window,center=True,return_complex=True)
   spec=torch.view_as_real(z).permute(0,3,1,2).reshape(1,4,FFT//2+1,T)[:,:,:F,:].numpy()
   prediction=session.run(None,{input_name:spec})[0]
   full=np.pad(prediction,((0,0),(0,0),(0,FFT//2+1-F),(0,0)))
   q=torch.from_numpy(full).reshape(2,2,FFT//2+1,T).permute(0,2,3,1).contiguous();q=torch.view_as_complex(q)
   result=torch.istft(q,FFT,HOP,window=window,center=True,length=SIZE).numpy()[:,TRIM:-TRIM]
   parts.append(result)
 stem=np.concatenate(parts,axis=1)[:,:count]*PARAMS.get('compensate',1.0)
 if PARAMS.get('primary_stem','Vocals')=='Instrumental':return audio-stem,stem
 return stem,audio-stem
source=Path('work/pauly/PaulyMouse_Win10/Data/PMNL/SOUNDS');out=ROOT/'stems';out.mkdir(exist_ok=True)
names=([p.name for p in sorted(source.glob('SEF*.AIF')) if p.stem!='SEF00009']+['TBGM.AIF']) if '--all' in sys.argv else ([s for s in sys.argv[1:] if not s.startswith('--')] or ['SEF101N.AIF','SEF109N.AIF','SEF508N.AIF'])
def one(name):
 target=out/(Path(name).stem+'-effects.wav')
 if target.exists():return
 begin=time.monotonic();audio=read(source/name);voice,effects=split(audio)
 write(target,effects);write(out/(Path(name).stem+'-voice.wav'),voice)
 print(name,'seconds',round(time.monotonic()-begin,2),'voiceRms',float(np.sqrt(np.mean(voice**2))),'effectsRms',float(np.sqrt(np.mean(effects**2))),flush=True)
with ThreadPoolExecutor(max_workers=3 if '--all' in sys.argv or '--parallel' in sys.argv else 1) as pool:list(pool.map(one,names))
print('STEMS_READY',len(names),flush=True)
