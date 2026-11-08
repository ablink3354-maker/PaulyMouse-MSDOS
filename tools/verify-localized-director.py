"""Independently decode every localized text bitmap with drxtract."""
import sys,os,logging,json,io,re
from pathlib import Path
from PIL import Image
from drxtract import riffxtract,casxtract
from drxtract.bitd import bitd2bmp
from drxtract.clut import clut2palette
logging.disable(logging.CRITICAL);os.system=lambda command:0
src=Path('work/pauly-localized/PMES');dest=Path('work/pauly-localized-verification');dest.mkdir(exist_ok=True);report=[]
for movie in ['STARE','PANEL']+[f'BOOK{i}' for i in range(1,10)]:
 file=src/(movie+'.DXR');d=dest/movie;d.mkdir(exist_ok=True);mode='pc' if file.read_bytes()[:4]==b'XFIR' else 'mac'
 for module in (riffxtract,casxtract):module.byte_order='<' if mode=='pc' else '>';module.byte_order_type=mode
 sys.argv=['riffxtract',mode,str(file),str(d)];riffxtract.main();sys.argv=['casxtract',mode,str(d)];casxtract.main();count=0
 for p in (d/'cas').glob('*/data.json'):
  m=json.loads(p.read_text('utf8'));name=m.get('content',{}).get('name') or ''
  if m.get('type')!='bitmap' or not re.fullmatch(r'[NCQA]\d+[AB]?',name,re.I):continue
  m['width']-=m['w_padding'];m['height']-=m['h_padding'];m['w_padding']=m['h_padding']=0
  palette=clut2palette(next((d/'cas'/str(m['palette'])).glob('*.CLUT')).read_bytes())
  im=Image.open(io.BytesIO(bitd2bmp(m,palette,next(p.parent.glob('*.BITD')).read_bytes())))
  assert im.size==(m['width'],m['height']),(movie,name,im.size,m)
  assert len(set(im.convert('RGB').getdata()))>1,(movie,name,'blank')
  count+=1
 report.append({'movie':movie,'decodedLocalizedPages':count});print(movie,count,flush=True)
assert sum(r['decodedLocalizedPages'] for r in report)==496
Path('work/pauly-localized-verification.json').write_text(json.dumps(report,indent=2),'utf8');print('496 TEXT RESOURCES DECODED',flush=True)
