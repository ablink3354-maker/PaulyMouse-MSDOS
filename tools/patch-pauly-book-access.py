"""Make each original scene's book usable before selecting an animal.

Preserve the selected animal; choose the first only when none is selected.
Only the book's mouseUp handler changes. Bytecode is round-trip decompiled.
"""
import importlib.util,json,struct,re,logging
from pathlib import Path
from drxtract.lingosrc.parse.lscr import parse_lrcr_file_header,parse_lrcr_file_data
from drxtract.lingosrc.parse import parse_lnam_file
from drxtract.lingosrc.codegen import generate_lingo_code
logging.disable(logging.CRITICAL)
spec=importlib.util.spec_from_file_location('book',Path(__file__).with_name('localize-director-books.py'));book=importlib.util.module_from_spec(spec);spec.loader.exec_module(book)
report=[];counts=[13,13,14,11,12,16,10,9,13]
for room in range(1,10):
 folder=Path(f'work/pauly-assets/SCENE{room}');scripts=json.loads((folder/'scripts.json').read_text('utf8'))
 matches=[k for k,v in scripts.items() if re.search(r'if not \(s\d = 0\)',v,re.I) and 'go "BOpen"' in v];assert len(matches)==1,(room,matches)
 member=folder/'cas'/matches[0];resource=next(member.glob('*.Lscr'));data=bytearray(resource.read_bytes());header=parse_lrcr_file_header(data);assert header.frb_nrecords==1
 function=header.frb_offset;length,offset=struct.unpack_from('>II',data,function+4);old=bytes(data[offset:offset+length]);assert old[0]==0x49 and old[2:8]==bytes.fromhex('030f14950009'),old.hex()
 variable=old[1];tail=old[8:];assert len(tail)==7 and tail[0]==0x44 and tail[2:5]==bytes.fromhex('420157') and tail[-1]==1,tail.hex()
 # Keep a valid selection when moving between habitats with different counts.
 # if (S<1) or (S>animalCount) then S=1; go "BOpen".
 code=bytes([0x49,variable,0x41,1,0x0c,0x49,variable,0x41,counts[room-1],0x10,0x13,0x95,0,7,0x41,1,0x4f,variable])+tail
 new_offset=len(data);data.extend(code);data.extend(b'\0\0')
 # Native ScummVM bounds the code store at the function table. Move that
 # table after the new code rather than placing executable bytes past it.
 props=bytes(data[header.prb_offset:header.grb_offset]);globals_=bytes(data[header.grb_offset:header.frb_offset]);record=bytearray(data[function:function+42]);struct.pack_into('>II',record,4,len(code),new_offset)
 prb=len(data);data.extend(props);grb=len(data);data.extend(globals_);frb=len(data);data.extend(record)
 for slot,value in [(62,prb),(68,grb),(74,frb)]:struct.pack_into('>I',data,slot,value)
 struct.pack_into('>II',data,8,len(data),len(data))
 names=parse_lnam_file(str(next((folder/'bin').glob('*.Lnam'))));source=generate_lingo_code(parse_lrcr_file_data(bytes(data),names));assert 'BOpen' in source and f'set {names[variable]} = 1' in source,source
 patch=book.DirectorPatcher(Path(f'work/pauly/PaulyMouse_Win10/Data/PMNL/SCENE{room}.DXR'));patch.replace(int(resource.stem),'Lscr',bytes(data));patch.write(Path(f'work/pauly-localized/PMES/SCENE{room}.DXR'))
 report.append({'scene':room,'handler':matches[0],'source':source});print(room,source,flush=True)
Path('work/pauly-book-access-patch.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
