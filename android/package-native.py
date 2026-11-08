"""Repackage the unmodified GPL ScummVM engine with an independent Pauly launcher.
The engine's Java/JNI names and resource IDs remain intact. Only the app manifest,
additional launcher DEX and locally supplied game/museum assets are changed.
"""
import struct,zipfile,pathlib,copy,sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
U16=lambda b,o:struct.unpack_from('<H',b,o)[0]
U32=lambda b,o:struct.unpack_from('<I',b,o)[0]
def chunk(kind,header,body):return struct.pack('<HHI',kind,8+len(header),8+len(header)+len(body))+header+body
def length8(n):return bytes([n]) if n<128 else bytes([(n>>8)|128,n&255])
def length16(n):return struct.pack('<H',n) if n<32768 else struct.pack('<HH',(n>>16)|32768,n&65535)
def decode_pool(b):
 count,style_count,flags,start,style_start=struct.unpack_from('<5I',b,8);utf8=bool(flags&256)
 offsets=struct.unpack_from('<'+str(count)+'I',b,U16(b,2));strings=[]
 def readlen(pos,wide):
  n=U16(b,pos) if wide else b[pos];pos+=2 if wide else 1
  if n&(32768 if wide else 128):n=((n&(32767 if wide else 127))<<(16 if wide else 8))+(U16(b,pos) if wide else b[pos]);pos+=2 if wide else 1
  return n,pos
 for offset in offsets:
  size,pos=readlen(start+offset,not utf8)
  if utf8:size,pos=readlen(pos,False)
  strings.append(b[pos:pos+size*(1 if utf8 else 2)].decode('utf8' if utf8 else 'utf-16le'))
 style_offsets=b[U16(b,2)+count*4:U16(b,2)+(count+style_count)*4]
 return strings,(style_count,flags,style_offsets,b[style_start:] if style_start else b'')
def encode_pool(strings,meta):
 style_count,flags,style_offsets,style_data=meta;data=bytearray();offsets=[]
 for s in strings:
  offsets.append(len(data));utf16=s.encode('utf-16le')
  if flags&256:
   raw=s.encode('utf8');data+=length8(len(utf16)//2)+length8(len(raw))+raw+b'\0'
  else:data+=length16(len(utf16)//2)+utf16+b'\0\0'
 data+=b'\0'*((-len(data))%4);start=28+4*len(strings)+len(style_offsets);style_start=start+len(data) if style_count else 0
 return chunk(1,struct.pack('<5I',len(strings),style_count,flags,start,style_start),struct.pack('<'+str(len(strings))+'I',*offsets)+style_offsets+data+style_data)
def patch_manifest(raw):
 parts=[];pos=U16(raw,2)
 while pos<len(raw):size=U32(raw,pos+4);parts.append(raw[pos:pos+size]);pos+=size
 pool_index=next(i for i,b in enumerate(parts) if U16(b,0)==1);strings,meta=decode_pool(parts[pool_index]);original=list(strings)
 def idx(s):
  if s not in strings:strings.append(s)
  return strings.index(s)
 android=idx('http://schemas.android.com/apk/res/android');new_activity=idx('mx.retro.pauly.PaulyLauncher');museum_name=idx('mx.retro.pauly.MuseumActivity');app_name=idx('Pauly Mouse');package=idx('mx.retro.pauly');orientation=idx('screenOrientation')
 res_index=next(i for i,b in enumerate(parts) if U16(b,0)==0x180);ids=list(struct.unpack('<'+'I'*((len(parts[res_index])-8)//4),parts[res_index][8:]));ids+=[0]*max(0,orientation+1-len(ids));ids[orientation]=0x0101001e
 def attrs(b):return [bytearray(b[o:o+20]) for o in range(16+U16(b,24),16+U16(b,24)+20*U16(b,28),20)]
 def attrname(a):return strings[U32(a,4)]
 def attrtext(a):return strings[U32(a,16)] if a[15]==3 else ''
 def value(a,typ,data):struct.pack_into('<I',a,8,data if typ==3 else 0xffffffff);a[15]=typ;struct.pack_into('<I',a,16,data);return a
 def set_attr(items,name,typ,data):
  for a in items:
   if attrname(a)==name:return value(a,typ,data)
  a=bytearray(struct.pack('<IIIHBBI',android,idx(name),0xffffffff,8,0,typ,data));items.append(a);return a
 def build_start(b,items):
  # Android looks up framework attributes by resource ID; keep aapt ordering
  # when adding an attribute to a node that did not previously contain it.
  items.sort(key=lambda a:ids[U32(a,4)] if U32(a,4)<len(ids) else 0)
  head=bytearray(b[:36]);struct.pack_into('<I',head,4,36+len(items)*20);struct.pack_into('<H',head,28,len(items));return bytes(head)+b''.join(items)
 result=[];activity_clone=None;splash_clone=None;game_clone=None
 for b in parts:
  kind=U16(b,0)
  if kind==0x102:
   name=strings[U32(b,20)];items=attrs(b)
   if name=='manifest':
    items=[a for a in items if attrname(a) not in ('sharedUserId','sharedUserMaxSdkVersion')]
    for a in items:
     n=attrname(a)
     if n=='package':value(a,3,package)
     elif n=='versionCode':value(a,16,4)
     elif n=='versionName':value(a,3,idx('0.4-es'))
   elif name=='uses-sdk':
    set_attr(items,'minSdkVersion',16,23)
   elif name=='application':
    set_attr(items,'label',3,app_name);set_attr(items,'allowBackup',18,0)
   elif name=='activity':
    name_attr=next(a for a in items if attrname(a)=='name');cls=attrtext(name_attr)
    if cls.endswith('.SplashActivity'):
     splash_items=copy.deepcopy(items);set_attr(splash_items,'exported',18,0);splash_clone=build_start(b,splash_items)
     value(name_attr,3,new_activity);set_attr(items,'screenOrientation',16,6)
    elif cls.endswith('.ScummVMActivity'):
     set_attr(items,'screenOrientation',16,6)
     clone=copy.deepcopy(items);set_attr(clone,'name',3,museum_name);clone=[a for a in clone if attrname(a)!='launchMode'];activity_clone=build_start(b,clone)
     clone=copy.deepcopy(items);set_attr(clone,'name',3,idx('mx.retro.pauly.PaulyGameActivity'));set_attr(clone,'exported',18,0);set_attr(clone,'launchMode',16,0);game_clone=build_start(b,clone)
    elif cls.endswith('.ShortcutCreatorActivity'):set_attr(items,'exported',18,0)
   b=build_start(b,items)
  elif kind==0x103 and strings[U32(b,20)]=='application':
   end=chunk(0x103,struct.pack('<II',1,0xffffffff),struct.pack('<II',0xffffffff,idx('activity')))
   if splash_clone:result.extend([splash_clone,end])
   if activity_clone:result.extend([activity_clone,end])
   if game_clone:result.extend([game_clone,end])
  result.append(b)
 result[pool_index]=encode_pool(strings,meta);result[res_index]=chunk(0x180,b'',struct.pack('<'+'I'*len(ids),*ids));body=b''.join(result);return struct.pack('<HHI',3,8,len(body)+8)+body
def package(reuse_game=False):
 source=ROOT/'vendor/scummvm-android-2.9.1-arm64.apk';dest=ROOT/'android/build/unsigned.apk';dest.parent.mkdir(parents=True,exist_ok=True)
 game=ROOT/'android/build/pauly-game.zip';game_root=ROOT/'assets/game'
 assert (game_root/'BOOK9.DXR').is_file(),'Primero hay que generar los recursos localizados'
 if not reuse_game or not game.exists():
  with zipfile.ZipFile(game,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for p in sorted(game_root.rglob('*')):
    if p.is_file():z.write(p,p.relative_to(game_root).as_posix())
 with zipfile.ZipFile(source) as original,zipfile.ZipFile(dest,'w') as out:
  for item in original.infolist():
   if item.filename.upper().startswith('META-INF/'):continue
   data=original.read(item.filename)
   if item.filename=='AndroidManifest.xml':data=patch_manifest(data)
   out.writestr(item,data)
  out.write(ROOT/'android/build/dex/classes.dex','classes2.dex')
  out.write(game,'assets/pauly-game.zip',compress_type=zipfile.ZIP_STORED)
  for p in (ROOT/'assets/museum').rglob('*'):
   if p.is_file():out.write(p,'assets/museum/'+p.relative_to(ROOT/'assets/museum').as_posix(),compress_type=zipfile.ZIP_DEFLATED)
 print(dest,dest.stat().st_size)
if __name__=='__main__':package('--reuse-game' in sys.argv)
