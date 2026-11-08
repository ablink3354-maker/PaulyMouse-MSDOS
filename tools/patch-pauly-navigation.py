"""Add context-aware, keyboard-accessible side-panel actions to original movies.

The original sprite handlers, scores and animations remain in place. A movie
keyDown handler accepts b(book), r(back), l(locations), n(next), p(previous).
Android and Web both send these same ordinary key events.
"""
import importlib.util,json,struct,re,logging
from pathlib import Path
from drxtract.lingosrc.parse.lscr import parse_lrcr_file_header,parse_lrcr_file_data
from drxtract.lingosrc.parse.lnam import parse_lnam_file_data
from drxtract.lingosrc.codegen import generate_lingo_code
from drxtract.lingosrc.util import get_encoding
logging.disable(logging.CRITICAL)
spec=importlib.util.spec_from_file_location('book',Path(__file__).with_name('localize-director-books.py'));book=importlib.util.module_from_spec(spec);spec.loader.exec_module(book)
BASE=Path('work/pauly-assets');OUT=Path('work/pauly-localized/PMES')
counts=[13,13,14,11,12,16,10,9,13]
def action(key,body):return f'if the key = "{key}" then\r{body}\rend if\r'
def book_open(room):return f'global S{room}, gSC, gSNum\rif (S{room} < 1) or (S{room} > {counts[room-1]}) then set S{room} = 1\rset gSNum = {room}\rset gSC = S{room}\rgo 1, "BOOK{room}"'
def program(movie):
 if movie.startswith('SCENE'):
  r=int(movie[5:]);return action('b',f'global S{r}\rif (S{r} < 1) or (S{r} > {counts[r-1]}) then set S{r} = 1\rgo "BOpen"')+action('r','go "Back"')+action('l','go "Back"')+action('n','go "Nxt"')+action('p','go "Pre"')
 if movie.startswith('BOOK'):
  r=int(movie[4:]);n=counts[r-1]
  back='puppetSound 0\r'+''.join(f'puppetSprite {i}, 0\r' for i in [4,5,6,7,8,9,12,10,14])+'go "Back"'
  return action('r',back)+action('l','puppetSound 0\rgo "Sselect", "PANEL"')+action('n',f'global gSC\rpuppetSound 0\rset gSC = gSC + 1\rif gSC > {n} then set gSC = 1\rgo "start"')+action('p',f'global gSC\rpuppetSound 0\rset gSC = gSC - 1\rif gSC < 1 then set gSC = {n}\rgo "start"')
 if movie=='PANEL':
  select=action('n','global gSNum\rset gSNum = gSNum + 1\rif gSNum > 9 then set gSNum = 1\rgo "Sselect"')+action('p','global gSNum\rset gSNum = gSNum - 1\rif gSNum < 1 then set gSNum = 9\rgo "Sselect"')
  return select+action('b','global gSNum\rif gSNum < 1 then set gSNum = 1\r'+''.join(f'if gSNum = {r} then\r{book_open(r)}\rend if\r' for r in range(1,10)))
 return action('b',book_open(1))+action('l','go "Sselect", "PANEL"')

def append_handler(original,names,source):
 raw=bytearray(original);h=parse_lrcr_file_header(raw)
 key=names.index('keyDown');do=names.index('do');assert do<256
 byte_index=h.crb_nconstants*6
 literal=bytes([0x44,byte_index]) if byte_index<256 else bytes([0x84])+struct.pack('>H',byte_index)
 code=literal+bytes([0x42,1,0x57,do,1]);code_start=len(raw);raw.extend(code+b'\0\0')
 props=original[h.prb_offset:h.grb_offset];glob=original[h.grb_offset:h.frb_offset]
 prb=len(raw);raw.extend(props);grb=len(raw);raw.extend(glob);frb=len(raw);raw.extend(original[h.frb_offset:h.frb_offset+42*h.frb_nrecords])
 record=bytearray(42);struct.pack_into('>H',record,0,key);struct.pack_into('>II',record,4,len(code),code_start);struct.pack_into('>I',record,14,code_start);struct.pack_into('>I',record,20,code_start);raw.extend(record)
 crb=len(raw);raw.extend(original[h.crb_offset:h.crb_offset+h.crb_nconstants*6]);store=original[h.con_offset:];raw.extend(struct.pack('>HI',1,len(store)));con=len(raw);raw.extend(store)
 encoded=source.encode(get_encoding());raw.extend(struct.pack('>I',len(encoded)+1)+encoded+b'\0')
 for slot,value in [(62,prb),(68,grb),(74,frb),(80,crb),(88,con)]:struct.pack_into('>I',raw,slot,value)
 struct.pack_into('>H',raw,72,h.frb_nrecords+1);struct.pack_into('>H',raw,78,h.crb_nconstants+1);struct.pack_into('>I',raw,84,len(raw)-con);struct.pack_into('>II',raw,8,len(raw),len(raw))
 decompiled=generate_lingo_code(parse_lrcr_file_data(bytes(raw),names));assert 'on keyDown' in decompiled and 'do ' in decompiled,decompiled
 # These bounds are checked by native ScummVM, independently of drxtract.
 assert code_start>=struct.unpack_from('>H',raw,16)[0] and code_start+len(code)<frb
 return bytes(raw),decompiled

report=[]
for movie in [f'SCENE{i}' for i in range(1,10)]+[f'BOOK{i}' for i in range(1,10)]+['PANEL','STARE']:
 d=BASE/movie;lnam=next((d/'bin').glob('*.Lnam'));name_data=bytearray(lnam.read_bytes());names=parse_lnam_file_data(name_data)
 main=[]
 for p in (d/'cas').glob('*/*.lingo'):
  if 'on startMovie' in p.read_text('utf8'):main.append(p)
 assert len(main)==1,(movie,main)
 script=main[0];assert 'on keyDown' not in script.read_text('utf8')
 for name in ['keyDown','do']:
  if name not in names:names.append(name)
 name_data=name_data[:20]+b''.join(bytes([len(n.encode(get_encoding()))])+n.encode(get_encoding()) for n in names);struct.pack_into('>II',name_data,8,len(name_data),len(name_data));struct.pack_into('>H',name_data,18,len(names))
 resource=next(script.parent.glob('*.Lscr'));raw,code=append_handler(resource.read_bytes(),names,program(movie))
 patch=book.DirectorPatcher(OUT/(movie+'.DXR'));patch.replace(int(lnam.stem),'Lnam',bytes(name_data));patch.replace(int(resource.stem),'Lscr',raw);patch.write(OUT/(movie+'.DXR'))
 report.append({'movie':movie,'keys':['b','r','l','n','p'],'program':program(movie)});print(movie,'OK',flush=True)
Path('work/pauly-navigation-patch.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
