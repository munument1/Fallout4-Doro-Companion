from pathlib import Path
import importlib.util,struct,wave,json
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'build/DoroFollower'
spec=importlib.util.spec_from_file_location('bgsm',ROOT/'tools/deps/pynifly28/io_scene_nifly/pyn/bgsmaterial.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class Tracked(mod.BGSMaterial):
 def __init__(self,p):self.offsets={};self.strings={};super().__init__(str(p))
 def read_field(self,name,typ):
  start=self.sourcefile.tell();super().read_field(name,typ);self.offsets[name]=(start,self.sourcefile.tell())
 def read_text(self,name,condition=True):
  if condition:
   start=self.sourcefile.tell();super().read_text(name,condition);self.strings[name]=(start,self.sourcefile.tell())
p=ROOT/'build/yaoguai_body.bgsm';m=Tracked(p);data=p.read_bytes();edits=[]
print('BGSM',m.version,m.textures)
for name,(a,b) in m.strings.items():
 text={'Diffuse':'Actors\\Doro\\Doro_d.dds','Normal':'Actors\\Doro\\Doro_n.dds','Specular':'Actors\\Doro\\Doro_s.dds'}.get(name,'')
 raw=text.encode()+b'\0';edits.append((a,b,struct.pack('<I',len(raw))+raw))
for name,val in {'rimLighting':False,'subsurfaceLighting':False,'specularEnabled':False,'grayscaleToPaletteColor':False,'environmentMapping':False,'emitEnabled':False,'glowmap':False,'tessellate':False,'twoSided':True,'Alpha':1.0}.items():
 if name in m.offsets:
  a,b=m.offsets[name]
  if b-a==1:edits.append((a,b,bytes([int(val)])))
  elif b-a==4:edits.append((a,b,struct.pack('<f',val)))
for a,b,replacement in sorted(edits,reverse=True):data=data[:a]+replacement+data[b:]
material=OUT/'Materials/Actors/Doro/Doro.bgsm';material.write_bytes(data)
print('OUTPUT_TEXTURES',Tracked(material).textures)
for name,color in [('Doro_n.dds',(128,128,255,255)),('Doro_s.dds',(0,0,0,255))]:Image.new('RGBA',(4,4),color).save(OUT/'Textures/Actors/Doro'/name)
# Source clips are long loops. Extract short utterances so menu sounds do not loop.
for i,(filename,start,end) in enumerate([('DORO_V001_LP.wav',0,0.8),('DORO_V002_LP.wav',2.5,4.8)],1):
 with wave.open(str(ROOT/'reference/skyrim_doro_source/Sound/FX'/filename)) as w:
  params=w.getparams();w.setpos(int(start*w.getframerate()));samples=w.readframes(int((end-start)*w.getframerate()))
 with wave.open(str(OUT/f'Sound/FX/Doro/Doro{i:02}.wav'),'wb') as w:w.setparams(params);w.writeframes(samples)
print('ASSETS_PREPARED')
