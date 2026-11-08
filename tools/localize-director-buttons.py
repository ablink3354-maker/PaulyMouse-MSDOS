"""Generate Spanish menu glyph resources without changing scripts or hotspots.

Run after localize-director-books.py. Idempotent: always rebuild from book output
or original resources rather than repeatedly appending replacement chunks.
"""
import json,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import importlib.util
spec=importlib.util.spec_from_file_location('book_localization',Path(__file__).with_name('localize-director-books.py'));book=importlib.util.module_from_spec(spec);spec.loader.exec_module(book)
DirectorPatcher,palette_for,raw_bitmap,BOLD=book.DirectorPatcher,book.palette_for,book.raw_bitmap,book.BOLD

BASE=Path('work/pauly-assets');OUT=Path('work/pauly-localized/PMES')
ORIGINAL=Path('work/pauly/PaulyMouse_Win10/Data/PMNL')
def button(label,w,h,palette,pressed):
 def color(rgb):return min(range(256),key=lambda n:sum((palette[n][i]-rgb[i])**2 for i in range(3)))
 image=Image.new('P',(w,h),color((0,0,0)));image.putpalette([v for c in palette for v in c]);d=ImageDraw.Draw(image)
 d.rounded_rectangle((0,0,w-1,h-1),radius=min(7,h//3),fill=color((96,65,30) if pressed else (161,119,50)),outline=color((246,216,145)),width=1)
 for size in range(min(15,h-6),7,-1):
  font=ImageFont.truetype(BOLD,size)
  if d.textlength(label,font=font)<=w-6:break
 box=d.textbbox((0,0),label,font=font);x=(w-d.textlength(label,font=font))/2;y=(h-(box[3]-box[1]))/2-box[1]+int(pressed)
 d.text((x,y),label,font=font,fill=color((255,244,207)))
 return image

report=[]
for movie in ['STARE','PANEL']+[f'BOOK{i}' for i in range(1,10)]:
 d=BASE/movie;file=OUT/(movie+'.DXR');source=file if movie.startswith('BOOK') else ORIGINAL/file.name
 patch=DirectorPatcher(source);count=0
 for p in (d/'cas').glob('*/data.json'):
  m=json.loads(p.read_text('utf8'));cast=int(p.parent.name);name=(m.get('content',{}).get('name') or '').lower();label=None;pressed=False
  if movie=='STARE' and cast in (41,42,43,44,55):label='JUGAR' if cast in (41,42) else 'OPCIONES';pressed=cast in (42,44,55)
  elif movie=='PANEL' and name in ('exit1','exit2'):label='SALIR';pressed=name=='exit2'
  elif movie.startswith('BOOK') and name.replace(' ','') in ('back1','back2'):label='VOLVER';pressed=name.replace(' ','')=='back2'
  if label is None:continue
  w=m['width']-m['w_padding'];h=m['height']-m['h_padding'];palette=palette_for(d,m);image=button(label,w,h,palette,pressed)
  bitd=next(p.parent.glob('*.BITD'));patch.replace(int(bitd.stem),'BITD',raw_bitmap(image));count+=1
 patch.write(file);report.append({'movie':movie,'buttons':count});print(movie,count,flush=True)
Path('work/pauly-spanish-buttons-report.json').write_text(json.dumps(report,indent=2),'utf8')
