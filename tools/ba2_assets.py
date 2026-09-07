import struct,zlib
from pathlib import Path
def index(path):
 with open(path,'rb') as f:
  magic,ver,kind,count,nt=struct.unpack('<4sI4sIQ',f.read(24))
  assert magic==b'BTDX' and kind==b'GNRL',(magic,ver,kind)
  rec=[]
  for i in range(count):
   h,ext,dh,flags,off,packed,size,align=struct.unpack('<I4sIIQIII',f.read(36));rec.append((off,packed,size))
  f.seek(nt);names=[]
  for i in range(count):names.append(f.read(struct.unpack('<H',f.read(2))[0]).decode())
 return {n.lower().replace('\\','/'):r for n,r in zip(names,rec)}
def extract(path,name):
 off,packed,size=index(path)[name.lower().replace('\\','/')]
 with open(path,'rb') as f:f.seek(off);data=f.read(packed or size)
 if packed:data=zlib.decompress(data)
 assert len(data)==size
 return data
