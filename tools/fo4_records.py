import struct,zlib,json
from pathlib import Path
GAME=Path(r'C:\Games\Steam\steamapps\common\Fallout 4 377160')
def records(path):
 data=Path(path).read_bytes()
 def walk(start,end):
  pos=start
  while pos+24<=end:
   sig=data[pos:pos+4];size=struct.unpack_from('<I',data,pos+4)[0]
   if sig==b'GRUP':
    yield from walk(pos+24,pos+size);pos+=size;continue
   flags,fid=struct.unpack_from('<II',data,pos+8)
   body=data[pos+24:pos+24+size]
   if flags&0x40000:body=zlib.decompress(body[4:])
   yield sig.decode(),fid,flags,body
   pos+=24+size
 yield from walk(0,len(data))
def subs(body):
 p=0;ext=None
 while p+6<=len(body):
  sig=body[p:p+4].decode();n=struct.unpack_from('<H',body,p+4)[0];p+=6
  if sig=='XXXX':ext=struct.unpack_from('<I',body,p)[0];p+=n;continue
  if ext is not None:n=ext;ext=None
  yield sig,body[p:p+n];p+=n
def edid(body):
 return next((b.rstrip(b'\0').decode(errors='replace') for s,b in subs(body) if s=='EDID'),'')
if __name__=='__main__':
 out=[]
 for typ,fid,flags,body in records(GAME/'Data/Fallout4.esm'):
  if typ not in ['NPC_','RACE','ARMO','ARMA','PACK','CELL','WRLD','FACT','SNDR','SOPM','KYWD','QUST','DIAL','GLOB','FLST']:continue
  name=edid(body)
  if any(x in name.lower() for x in ['yaoguai','dogmeat','redrocket','followers','companionfollow','companionwait','potentialcompanion','currentcompanion']):
   out.append({'type':typ,'id':f'{fid:08X}','edid':name})
 Path('build/vanilla_records.json').write_text(json.dumps(out,indent=2))
 for x in out:
  if x['type'] in ['PACK','RACE','ARMO','ARMA','FACT','CELL','WRLD']:print(x)
