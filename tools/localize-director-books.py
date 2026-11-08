"""Build Spanish font resources for the original Director books.

New text bitmaps are rendered from reviewed strings. Original sprite timelines,
scripts, cast IDs, hotspots, palettes and photographs are preserved. Resources
are appended and their existing mmap entries updated; originals stay untouched.
"""
import json,re,struct,shutil,io
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from drxtract.cast.cast import parse_cast_data_struct_dir4
from drxtract.clut import clut2palette

BASE=Path('work/pauly-assets');ORIGINAL=Path('work/pauly/PaulyMouse_Win10/Data/PMNL');OUT=Path('work/pauly-localized/PMES');REVIEW=json.loads(Path('work/pauly-spanish-reviewed.json').read_text('utf8'))
GROUPS={
1:['Ave','Mamífero','Mamífero','Mamífero','Mamífero','Mamífero','Ave','Mamífero','Mamífero','Mamífero','Mamífero','Anfibio','Molusco'],
2:['Reptil','Reptil','Insecto','Mamífero','Mamífero','Reptil','Mamífero','Ave','Mamífero','Mamífero','Insecto','Anfibio','Mamífero'],
3:['Mamífero','Mamífero','Mamífero','Mamífero','Mamífero','Mamífero','Mamífero','Ave','Mamífero','Mamífero','Ave','Mamífero','Insecto','Ave'],
4:['Reptil','Mamífero','Ave','Reptil','Reptil','Mamífero','Mamífero','Ave','Ave','Arácnido','Arácnido'],
5:['Ave','Equinodermo','Mamífero','Mamífero','Molusco','Reptil','Molusco','Crustáceo','Pez','Pez','Mamífero','Crustáceo'],
6:['Cnidario y pez','Pez','Molusco','Reptil','Crustáceo','Equinodermo','Pez','Crustáceo','Pez','Cnidario','Mamífero','Pez','Pez','Pez','Molusco','Molusco'],
7:['Mamífero','Mamífero','Mamífero','Mamífero','Mamífero','Ave','Ave','Mamífero','Mamífero','Mamífero'],
8:['Reptil','Ave','Mamífero marsupial','Mamífero marsupial','Mamífero monotrema','Mamífero marsupial','Ave','Mamífero monotrema','Mamífero marsupial'],
9:['Arácnido','Insecto','Mamífero','Mamífero','Mamífero','Mamífero','Mamífero','Mamífero','Mamífero','Ave','Ave','Ave','Insecto']}
RANGES={
1:['Europa, Asia, América y África','América del Norte, Europa y Asia','Europa, Asia y América del Norte','Europa, Asia y América del Norte','Europa, Asia, América y África','América del Norte, Europa y Asia','Diversas regiones del mundo, salvo la Antártida','Bosques templados del hemisferio norte','Diversas regiones del mundo','Europa, Asia, América y África','América, Europa, Asia y África','Diversas regiones del mundo','Diversas regiones del mundo'],
2:['África, Asia y otras regiones cálidas','América, Australia, África y Asia','Diversas regiones del mundo','Europa, Asia y América','Asia','Regiones tropicales de América','Islas del sudeste de Asia','África y Asia','Islas de Borneo y Sumatra','Isla de Borneo','Diversas regiones del mundo','América del Sur','América'],
3:['África y una pequeña región de Asia','África','África','Asia y África','África','África y algunas regiones de Asia','África','África','África y Asia','África y la península arábiga','América, África, Europa y Asia','América del Norte','Regiones tropicales y templadas','Europa, Asia, África, América y Australia'],
4:['Suroeste de Estados Unidos y noroeste de México','África y Asia','América, Europa, Asia y otras regiones','Regiones áridas de América del Norte','América','América del Norte','Asia y el norte de África','Europa, Asia, África y otras regiones','África','Regiones cálidas de varios continentes','África, Asia y otras regiones'],
5:['Océanos, especialmente del hemisferio sur','Océanos de distintas regiones','Océanos; algunas especies viven en ríos','Océanos de todo el mundo','Aguas marinas de distintas regiones','Mares cálidos y templados','Océanos y arrecifes de regiones cálidas','Costas y aguas marinas poco profundas','Océanos de todo el mundo','Océanos, principalmente aguas cálidas','Océanos de todo el mundo','Costas de regiones cálidas y templadas'],
6:['Mares de distintas regiones','Océanos de distintas regiones','Océanos y mares de distintas regiones','Aguas cálidas del Índico y del Pacífico','Costas y mares de distintas regiones','Océanos de todo el mundo','Aguas costeras de distintas regiones','Mares tropicales y templados','Aguas marinas cálidas','Océanos de todo el mundo','Costas y ríos cálidos del Atlántico','Mares de distintas regiones','Océanos tropicales y templados','Mares de distintas regiones','Mares de distintas regiones','Océanos Índico y Pacífico'],
7:['Costas de diversas regiones del mundo','Ártico','Ártico','Ártico y mares cercanos','Ártico','Regiones de ambos hemisferios','Hemisferio sur','Distintos océanos','Océano Ártico','Océanos del hemisferio sur y Pacífico norte'],
8:['Australia y Nueva Guinea','Australia','Este de Australia','Tasmania','Australia y Nueva Guinea','Australia y regiones cercanas','Nueva Zelanda','Este de Australia y Tasmania','Vivió en Australia y Tasmania; especie extinta'],
9:['Diversas regiones del mundo','Diversas regiones del mundo','Junto a las personas en todo el mundo','Junto a las personas en todo el mundo','Granjas de distintas regiones','Granjas de distintas regiones','Diversas regiones del mundo','Diversas regiones del mundo','Diversas regiones del mundo','Europa, Asia y África, según la especie','Europa, Asia, América y otras regiones','Diversas regiones del mundo','Diversas regiones del mundo']}

REGULAR='C:/Windows/Fonts/arial.ttf';BOLD='C:/Windows/Fonts/arialbd.ttf'
def wrap(draw,text,font,width):
 lines=[]
 for paragraph in text.split('\n'):
  line=''
  for word in paragraph.split():
   test=(line+' '+word).strip()
   if line and draw.textlength(test,font=font)>width:lines.append(line);line=word
   else:line=test
  lines.append(line)
 return lines
def text_image(text,w,h,palette,bold=False,center=False):
 image=Image.new('P',(w,h),0);image.putpalette([channel for color in palette for channel in color]);draw=ImageDraw.Draw(image)
 black=min(range(256),key=lambda n:sum(c*c for c in palette[n]))
 for size in range(14,6,-1):
  font=ImageFont.truetype(BOLD if bold else REGULAR,size);lines=wrap(draw,text,font,w-6);line_height=size+2
  if len(lines)*line_height<=h-4:break
 if len(lines)*line_height>h-4:raise ValueError(f'Text does not fit {w}x{h}: {text}')
 y=max(1,(h-len(lines)*line_height)//2) if center else 2
 for line in lines:
  x=max(2,int((w-draw.textlength(line,font=font))/2)) if center else 3
  draw.text((x,y),line,font=font,fill=black,stroke_width=0);y+=line_height
 return image
def palette_for(d,m):
 b=clut2palette(next((d/'cas'/str(m['palette'])).glob('*.CLUT')).read_bytes())
 return [(b[i+2],b[i+1],b[i]) for i in range(0,len(b),4)]
def raw_bitmap(image):
 pitch=(image.width+1)&~1;raw=image.tobytes();encoded=bytearray()
 for y in range(image.height):
  row=raw[y*image.width:(y+1)*image.width]+b'\0'*(pitch-image.width);i=0
  while i<len(row):
   run=1
   while i+run<len(row) and row[i+run]==row[i] and run<128:run+=1
   if run>=3:encoded.extend((257-run,row[i]));i+=run;continue
   start=i;i+=run
   while i<len(row) and i-start<128:
    run=1
    while i+run<len(row) and row[i+run]==row[i] and run<128:run+=1
    if run>=3:break
    i+=min(run,128-(i-start))
   encoded.append(i-start-1);encoded.extend(row[start:i])
 return bytes(encoded)
class DirectorPatcher:
 def __init__(self,path):
  self.data=bytearray(path.read_bytes());self.order='<' if self.data[:4]==b'XFIR' else '>';self.map=struct.unpack_from(self.order+'I',self.data,24)[0];self.properties,self.entry_size=struct.unpack_from(self.order+'HH',self.data,self.map+8)
 def replace(self,index,kind,payload):
  position=self.map+8+self.properties+index*self.entry_size;expected=kind.encode() if self.order=='>' else kind[::-1].encode()
  assert self.data[position:position+4]==expected,(index,kind,self.data[position:position+4])
  offset=len(self.data);self.data+=expected+struct.pack(self.order+'I',len(payload))+payload
  if len(payload)%2:self.data+=b'\0'
  struct.pack_into(self.order+'II',self.data,position+4,len(payload),offset)
 def write(self,path):
  struct.pack_into(self.order+'I',self.data,4,len(self.data)-8);path.write_bytes(self.data)
def localized_pages(room,index,folder):
 item=REVIEW[f'{room}-{index}'];names=[json.loads(p.read_text('utf8')).get('content',{}).get('name','').upper() for p in folder.glob('*/data.json')]
 if f'A{index}A' in names:
  words=item['answer'].split();cut=len(words)//2;return {'A':' '.join(words[:cut]),'B':' '.join(words[cut:])}
 return {'':item['answer']}
def run():
 OUT.mkdir(parents=True,exist_ok=True)
 if not (OUT/'PMOUSE.EXE').exists():shutil.copytree(ORIGINAL,OUT,dirs_exist_ok=True)
 previews=Path('work/pauly-spanish-page-previews');previews.mkdir(exist_ok=True);report=[]
 for room in range(1,10):
  d=BASE/f'BOOK{room}';patch=DirectorPatcher(ORIGINAL/f'BOOK{room}.DXR');count=0
  for p in (d/'cas').iterdir():
   if not p.is_dir() or not (p/'data.json').exists():continue
   m=json.loads((p/'data.json').read_text('utf8'));name=m.get('content',{}).get('name','').upper();match=re.fullmatch(r'([NCQA])(\d+)([AB]?)',name)
   if m.get('type')!='bitmap' or not match:continue
   role,index,suffix=match[1],int(match[2]),match[3];item=REVIEW[f'{room}-{index}'];w=m['width']-m['w_padding'];h=m['height']-m['h_padding'];palette=palette_for(d,m)
   if role=='N':
    text=item['name'];w=max(w,min(200,int(ImageDraw.Draw(Image.new('L',(1,1))).textlength(text,font=ImageFont.truetype(BOLD,12)))+8));h=max(h,20)
   elif role=='Q':text=item['question']
   elif role=='A':
    text=localized_pages(room,index,d/'cas')[suffix];w=max(w,200);h=max(h,220)
   else:text='Clasificación\n'+GROUPS[room][index-1]+'\n\nDistribución\n'+RANGES[room][index-1]+'\n\nSobre este animal\n'+item['answer'].split('. ')[0].rstrip('.')+'.'
   image=text_image(text,w,h,palette,bold=role in ('N','Q'),center=role=='N');bitd=next(p.glob('*.BITD'));patch.replace(int(bitd.stem),'BITD',raw_bitmap(image))
   if role in ('N','A'):
    cast=next(p.glob('*.CASt'));raw=bytearray(cast.read_bytes());header=parse_cast_data_struct_dir4(raw).headerData;pitch=struct.unpack_from('>H',header,0)[0];old_top,old_left,old_bottom,old_right=struct.unpack_from('>4h',header,2);old_ry,old_rx=struct.unpack_from('>2h',header,18);new_ry=old_top+round((old_ry-old_top)*h/(old_bottom-old_top));new_rx=old_left+round((old_rx-old_left)*w/(old_right-old_left))
    struct.pack_into('>H',raw,8,(pitch&0xf000)|((w+1)&~1));struct.pack_into('>4h',raw,10,old_top,old_left,old_top+h,old_left+w)
    if role=='N':struct.pack_into('>2h',raw,26,new_ry,new_rx)
    patch.replace(int(cast.stem),'CASt',raw)
   if index==1:image.save(previews/f'{room}-{name}.png')
   count+=1
  patch.write(OUT/f'BOOK{room}.DXR');report.append({'book':room,'translatedBitmaps':count});print(room,count,flush=True)
 Path('work/pauly-spanish-book-patch-report.json').write_text(json.dumps(report,indent=2),'utf8')
if __name__=='__main__':run()
