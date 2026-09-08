import struct,json,collections
from pathlib import Path
from fo4_records import GAME,records,subs,edid

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'build/DoroFollower'
U=lambda x:struct.pack('<I',x)
F=lambda x:struct.pack('<f',x)
S=lambda x:x.encode('utf-8')+b'\0'

def sub(s,b):return s.encode()+struct.pack('<H',len(b))+b
def body(ss):return b''.join(sub(s,b) for s,b in ss)
def rec(typ,fid,ss,flags=0):
 b=body(ss)
 return struct.pack('<4sIIIIHH',typ.encode(),len(b),flags,fid,0,131,0)+b
def group(label,typ,data):
 return struct.pack('<4sI4siIHH',b'GRUP',24+len(data),label,typ,0,0,0)+data

ids={
 0xa0f2f,0xa0f30,0xa0f31,0xa0f33,0x21e76,0x1d568,0x1d162,0x18aa2,
 0xbeba4,0xbeba5,0x1ab276,
 0x11e46d,0x11e46c,0x1c32c8,0x212db7,0x6980c,
}
van={fid:(typ,flags,list(subs(b))) for typ,fid,flags,b in records(GAME/'Data/Fallout4.esm') if fid in ids}
def clone(fid,replace={},drop=()):
 return [(s,replace.get(s,b)) for s,b in van[fid][2] if s not in drop]
def own(i):return 0x01000000+i

RACE,ARMOR,AA,NPC,MODE,MENU,FOLLOW,WAIT,HOME,VOICE,AUDIO,PLACED=[own(i) for i in range(0x800,0x80c)]
# 0x80c-0x82b is reserved by dialogue records. Keep craftable costume records separate.
COSTUME_HELMET,COSTUME_HELMET_AA,COSTUME_DOG,COSTUME_DOG_AA,RECIPE_CATEGORY,RECIPE_HELMET,RECIPE_DOG=[own(i) for i in range(0x840,0x847)]

pool=collections.defaultdict(list)
def add(typ,fid,ss,flags=0):pool[typ].append(rec(typ,fid,ss,flags))

race=clone(0xa0f2f,{'EDID':S('DoroRace'),'FULL':S('Doro'),'DESC':S(''),'WNAM':U(ARMOR)})
for i,(s,b) in enumerate(race):
 if s=='DATA':
  b=bytearray(b)
  struct.pack_into('<I',b,32,struct.unpack_from('<I',b,32)[0]|0x200000)
  race[i]=(s,bytes(b))
add('RACE',RACE,race)

armor=clone(0xa0f31,{'EDID':S('DoroSkin'),'RNAM':U(RACE),'DESC':S('')},['INDX','MODL'])
ix=next(i for i,(s,b) in enumerate(armor) if s=='DATA')
armor[ix:ix]=[('INDX',b'\0\0'),('MODL',U(AA))]
add('ARMO',ARMOR,armor)
add('ARMA',AA,clone(0xa0f30,{'EDID':S('DoroSkinAA'),'RNAM':U(RACE),'MOD2':S('Actors\\Doro\\Doro.nif'),'MOD3':S('Actors\\Doro\\Doro.nif')},['MO2T','MO3T']))
add('GLOB',MODE,[('EDID',S('DoroFollowState')),('FNAM',b's'),('FLTV',F(0))])
add('MESG',MENU,[('EDID',S('DoroCommandMenu')),('DESC',S('Choose a command for Doro.')),('FULL',S('Doro')),('INAM',U(0)),('DNAM',U(1))]+[('ITXT',S(s)) for s in ['Follow me','Wait here','Carry items','Return to Red Rocket','Cancel']])

def condition(value):return struct.pack('<B3sfH2sIIIII',0,b'\0'*3,float(value),74,b'\0'*2,MODE,0,0,0,0xffffffff)
def package(base,fid,name,state=None,radius=None):
 ss=clone(base,{'EDID':S(name)},['QNAM','CTDA','CIS1','CIS2'])
 for i,(s,b) in enumerate(ss):
  if s=='PKDT':
   b=bytearray(b)
   flags=struct.unpack_from('<I',b)[0]&~(1<<20)
   if state in [1,2]:flags|=1<<4
   struct.pack_into('<I',b,0,flags)
   ss[i]=(s,bytes(b))
 if state is not None:
  i=next(i for i,(s,b) in enumerate(ss) if s=='PSDT')+1
  ss.insert(i,('CTDA',condition(state)))
 if radius is not None:
  i=next(i for i,(s,b) in enumerate(ss) if s=='PLDT')
  b=bytearray(ss[i][1])
  struct.pack_into('<I',b,8,radius)
  ss[i]=('PLDT',bytes(b))
 add('PACK',fid,ss)

package(0x21e76,FOLLOW,'DoroFollowPlayer',1)
package(0x1d568,WAIT,'DoroWaitHere',2,0)
package(0x1d568,HOME,'DoroSandboxHome',None,256)

sound=clone(0xbeba5,{'EDID':S('DoroVoice'),'LNAM':b'\0'*4,'BNAM':struct.pack('<bbBBH',0,2,128,0,300)},['ANAM'])
i=next(i for i,(s,b) in enumerate(sound) if s=='ONAM')
sound[i:i]=[('ANAM',S('Sound\\FX\\Doro\\Doro01.wav')),('ANAM',S('Sound\\FX\\Doro\\Doro02.wav'))]
add('SNDR',VOICE,sound)
audio=clone(0xbeba4,{'EDID':S('DoroAudioTemplate'),'FULL':S('Doro'),'RNAM':U(RACE),'CS2D':U(VOICE)})
add('NPC_',AUDIO,audio)

script=S('DoroCompanionScript')[:-1]
vmad=struct.pack('<HHHH',6,2,1,len(script))+script+b'\0'+struct.pack('<H',0)
npc=clone(0xa0f33,{
 'EDID':S('DoroCompanion'),'RNAM':U(RACE),'ATKR':U(RACE),'WNAM':U(ARMOR),
 'FULL':S('Doro'),'CSCR':U(AUDIO),'VTCK':U(own(0x82b)),
 'DNAM':struct.pack('<HHHBB',350,150,0,1,0)
},['SNAM','INAM','DPLT','ECOR','PRKZ','PRKR'])
npc.insert(1,('VMAD',vmad))
for i,(s,b) in enumerate(npc):
 if s=='ACBS':
  b=bytearray(b)
  struct.pack_into('<I',b,0,2|32|64|4096)
  struct.pack_into('<H',b,6,20)
  struct.pack_into('<H',b,14,0)
  npc[i]=(s,bytes(b))
  npc.insert(i+1,('SNAM',U(0x1c21c)+b'\0'))
  break
for i,(s,b) in enumerate(npc):
 if s=='AIDT':
  b=bytearray(b)
  b[0]=1;b[1]=4;b[3]=0;b[5]=2;b[6]=0
  npc[i]=(s,bytes(b))
i=next(i for i,(s,b) in enumerate(npc) if s=='AIDT')+1
npc[i:i]=[('PKID',U(x)) for x in [FOLLOW,WAIT,HOME]]
add('NPC_',NPC,npc)

from doro_dialogue import build_dialogue
dialogue_groups,dialogue_record_count=build_dialogue(add,clone,own,U,F,S,rec,group,PLACED,NPC,VOICE)

# Craftable player mascot head and Dogmeat costume are part of DoroFollower.esp.
# RecipeUtility is cloned so TNAM remains the FO4 Recipe Filter keyword type.
add('KYWD',RECIPE_CATEGORY,clone(0x6980c,{'EDID':S('DoroRecipeCategory'),'FULL':S('DORO')}))
costume_base='Armor\\DoroCostumes\\'
costume_specs=[
 (COSTUME_HELMET,0x11e46d,'Doro Mascot Head',COSTUME_HELMET_AA,0x13746,7,'DoroHelmet.nif',1.0),
 (COSTUME_DOG,0x1c32c8,'Doro Dogmeat Costume',COSTUME_DOG_AA,0x1d698,(1<<3)|(1<<11)|(1<<16)|(1<<20),'DoroDogSuit.nif',2.0),
]
for fid,baseid,name,aa,race_id,mask,path,weight in costume_specs:
 ss=clone(baseid,{
  'EDID':S('DoroHelmet' if fid==COSTUME_HELMET else 'DoroDogSuit'),
  'FULL':S(name),'DESC':S(''),'BOD2':U(mask),'RNAM':U(race_id),
  'MOD2':S(costume_base+'DoroHelmetGO.nif'),
  'DATA':struct.pack('<IfI',0,weight,0),'FNAM':b'\0'*8,
 },['MO2T','INDX','MODL','PTRN'])
 i=next(i for i,(s,v) in enumerate(ss) if s=='DATA')
 ss[i:i]=[('INDX',b'\0\0'),('MODL',U(aa))]
 add('ARMO',fid,ss)
 ss=clone(0x11e46c if fid==COSTUME_HELMET else 0x212db7,{
  'EDID':S('DoroHelmetAA' if fid==COSTUME_HELMET else 'DoroDogSuitAA'),
  'BOD2':U(mask),'RNAM':U(race_id),'MOD2':S(costume_base+path),
  'DNAM':bytes([10,10])+b'\0'*10,
 },['MO2T'])
 i=next(i for i,(s,v) in enumerate(ss) if s=='MOD2')+1
 ss.insert(i,('MOD3',S(costume_base+path)))
 add('ARMA',aa,ss)

for fid,item,name in [
 (RECIPE_HELMET,COSTUME_HELMET,'DoroRecipeHelmet'),
 (RECIPE_DOG,COSTUME_DOG,'DoroRecipeDogSuit'),
]:
 add('COBJ',fid,[
  ('EDID',S(name)),('DESC',S('')),('CNAM',U(item)),
  ('BNAM',U(0x102158)),('FNAM',U(RECIPE_CATEGORY)),('INTV',U(1)),
 ])

pos=bytearray(next(b for s,b in van[0x1d162][2] if s=='DATA'))
x,y,z,rx,ry,rz=struct.unpack('<6f',pos)
struct.pack_into('<6f',pos,0,x+160,y+100,z,rx,ry,rz)
dog=json.loads((ROOT/'build/dogmeat_bounds.json').read_text())
scale=(dog['max'][2]-dog['min'][2])/155.31235
placed=rec('ACHR',PLACED,[('EDID',S('DoroRef')),('NAME',U(NPC)),('XSCL',F(scale)),('DATA',bytes(pos))],0x400)
cell=rec('CELL',0x18aa2,van[0x18aa2][2],van[0x18aa2][1]&~0x40000)
children=group(U(0x18aa2),6,group(U(0x18aa2),8,placed))
world=group(b'WRLD',0,group(U(0x3c),1,cell+children))

count=sum(len(v) for v in pool.values())+2+dialogue_record_count
# ESL-flagged ESP (ESP-FE): all new local IDs stay in the 0x800-0xFFF light-plugin range.
header=rec('TES4',0,[
 ('HEDR',struct.pack('<fII',1.0,count,0x900)),
 ('CNAM',S('Doro FO4 conversion')),
 ('SNAM',S('Standalone Doro follower, dialogue and craftable costumes')),
 ('MAST',S('Fallout4.esm')),('DATA',b'\0'*8),
],0x200)
plugin=header+b''.join(group(k.encode(),0,b''.join(v)) for k,v in pool.items())+dialogue_groups+world
(OUT/'DoroFollower.esp').write_bytes(plugin)

manifest={
 'plugin':'DoroFollower.esp',
 'plugin_type':'ESL-flagged ESP (ESP-FE)',
 'npc_local_form':'00000803',
 'reference_local_form':'0000080B',
 'costume_local_forms':{
  'helmet':'00000840','helmet_arma':'00000841',
  'dogmeat_costume':'00000842','dogmeat_arma':'00000843',
  'recipe_category':'00000844','helmet_recipe':'00000845','dogmeat_recipe':'00000846',
 },
 'scale':scale,'placement':[x+160,y+100,z],
 'new_records':count-1,
 'commands':['Follow','Wait','Inventory','Return to Red Rocket'],
 'runtime_tested':False,
}
(ROOT/'build/plugin_manifest.json').write_text(json.dumps(manifest,indent=2))

parsed=list(records(OUT/'DoroFollower.esp'))
assert len(parsed)==count+1
assert sum(t=='ACHR' for t,*_ in parsed)==1
assert any(t=='NPC_' and f==NPC and edid(b)=='DoroCompanion' for t,f,fl,b in parsed)
assert any(t=='ARMO' and f==COSTUME_HELMET for t,f,fl,b in parsed)
assert any(t=='ARMO' and f==COSTUME_DOG for t,f,fl,b in parsed)
assert sum(t=='COBJ' for t,f,fl,b in parsed)==2
recipe_filter_tnam=dict(van[0x6980c][2]).get('TNAM')
assert recipe_filter_tnam is not None
for t,f,fl,b in parsed:
 if t=='NPC_' and f==NPC:
  ss=dict(subs(b))
  assert ss['RNAM']==U(RACE)
  assert ss['ATKR']==U(RACE)
 if t=='KYWD' and f==RECIPE_CATEGORY:
  assert dict(subs(b)).get('TNAM')==recipe_filter_tnam
 if t=='COBJ':
  ss=dict(subs(b))
  assert ss['BNAM']==U(0x102158)
  assert ss['FNAM']==U(RECIPE_CATEGORY)

print('PLUGIN_WRITTEN',len(plugin),'bytes','scale',scale)
print('PLUGIN_STRUCTURAL_CHECK_PASSED',len(parsed),'records','ESP-FE','ATKR=DoroRace')
