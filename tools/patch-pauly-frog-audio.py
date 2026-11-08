"""Replace the book's blocking soundBusy spin with frame-driven playback.

Question/answer file IDs stay identical. Each frame yields to input/render/audio;
the frog can be stopped and navigation remains available during narration.
"""
import importlib.util,json,struct,re,logging
from pathlib import Path
from drxtract.lingosrc.parse.lscr import parse_lrcr_file_header,parse_lrcr_file_data
from drxtract.lingosrc.parse.lnam import parse_lnam_file_data
from drxtract.lingosrc.codegen import generate_lingo_code
from drxtract.lingosrc.util import get_encoding
logging.disable(logging.CRITICAL)
spec=importlib.util.spec_from_file_location('book',Path(__file__).with_name('localize-director-books.py'));book=importlib.util.module_from_spec(spec);spec.loader.exec_module(book)
mapping=json.loads(Path('work/pauly-book-audio-map.json').read_text('utf8'))
def payload(patch,index):
 p=patch.map+8+patch.properties+index*patch.entry_size;size,offset=struct.unpack_from(patch.order+'II',patch.data,p+4);return bytes(patch.data[offset+8:offset+8+size])
def rewrite(original,names,replacements):
 raw=bytearray(original);h=parse_lrcr_file_header(raw);records=[];codes={};strings=[]
 for i in range(h.frb_nrecords):
  r=bytearray(original[h.frb_offset+i*42:h.frb_offset+(i+1)*42]);name=names[struct.unpack_from('>H',r)[0]]
  if name in replacements:
   source=replacements[name];idx=(h.crb_nconstants+len(strings))*6;literal=bytes([0x44,idx]) if idx<256 else b'\x84'+struct.pack('>H',idx);code=literal+bytes([0x42,1,0x57,names.index('do'),1]);start=len(raw);raw.extend(code+b'\0\0');struct.pack_into('>II',r,4,len(code),start);strings.append(source);codes[name]=source
  records.append(r)
 assert set(codes)==set(replacements)
 prb=len(raw);raw.extend(original[h.prb_offset:h.grb_offset]);grb=len(raw);raw.extend(original[h.grb_offset:h.frb_offset]);frb=len(raw)
 for record in records:raw.extend(record)
 crb=len(raw);raw.extend(original[h.crb_offset:h.crb_offset+h.crb_nconstants*6]);store=bytearray(original[h.con_offset:])
 for text in strings:
  raw.extend(struct.pack('>HI',1,len(store)));encoded=text.encode(get_encoding());store.extend(struct.pack('>I',len(encoded)+1)+encoded+b'\0')
 con=len(raw);raw.extend(store)
 for slot,value in [(62,prb),(68,grb),(74,frb),(80,crb),(88,con)]:struct.pack_into('>I',raw,slot,value)
 struct.pack_into('>H',raw,78,h.crb_nconstants+len(strings));struct.pack_into('>I',raw,84,len(store));struct.pack_into('>II',raw,8,len(raw),len(raw))
 decompiled=generate_lingo_code(parse_lrcr_file_data(bytes(raw),names));assert decompiled and 'do ' in decompiled
 return bytes(raw)
report=[]
for room in range(1,10):
 d=Path(f'work/pauly-assets/BOOK{room}');scripts=json.loads((d/'scripts.json').read_text('utf8'));patch=book.DirectorPatcher(Path(f'work/pauly-localized/PMES/BOOK{room}.DXR'));lnam=next((d/'bin').glob('*.Lnam'));names=parse_lnam_file_data(payload(patch,int(lnam.stem)));assert 'do' in names
 choices=[m for m in mapping if m['room']==room]
 question=''.join(f'if gSC = {m["animal"]} then puppetSound "{m["questionFile"]}"\r' for m in choices)
 answer=''.join(f'if gSC = {m["animal"]} then puppetSound "{m["answerFile"]}"\r' for m in choices)
 q='global gSC, paulyNarrationPhase\rif not (paulyNarrationPhase = 1) then\rset paulyNarrationPhase = 1\r'+question+'end if'
 a='global gSC, paulyNarrationPhase\rif soundBusy(1) then\rgo the frame\relse\rset paulyNarrationPhase = 0\r'+answer+'end if'
 changed=[]
 for cast,source in scripts.items():
  if 'repeat while soundBusy(1)' in source:replacements={'enterFrame':q,'exitFrame':a}
  elif re.search(r'go "Speak"',source):replacements={'mouseDown':'global paulyNarrationPhase\rset paulyNarrationPhase = 0\rpuppetSprite 10, 0\rgo "Speak"'}
  elif source.startswith('on mouseDown') and 'go "Shotup"' in source:replacements={'mouseDown':'global paulyNarrationPhase\rset paulyNarrationPhase = 0\rpuppetSound 0\rgo "Shotup"'}
  else:continue
  resource=next((d/'cas'/cast).glob('*.Lscr'));patch.replace(int(resource.stem),'Lscr',rewrite(resource.read_bytes(),names,replacements));changed.append(cast)
 assert len(changed)==3,(room,changed)
 patch.write(Path(f'work/pauly-localized/PMES/BOOK{room}.DXR'));report.append({'book':room,'patchedHandlers':changed,'blockingLoopRemoved':True});print(room,changed,flush=True)
Path('work/pauly-frog-audio-patch.json').write_text(json.dumps(report,indent=2),'utf8')
