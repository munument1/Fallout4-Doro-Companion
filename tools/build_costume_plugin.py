import struct,collections,json
from pathlib import Path
from fo4_records import GAME,records,subs
r=Path(__file__).resolve().parent.parent;out=r/'build/DoroCostumes'
U=lambda n:struct.pack('<I',n)
S=lambda s:s.encode()+b'\0'
F=lambda f:struct.pack('<f',f)
def sub(s,v):return s.encode()+struct.pack('<H',len(v))+v
def rec(t,f,ss,flags=0):
 b=b''.join(sub(s,v) for s,v in ss);return struct.pack('<4sIIIIHH',t.encode(),len(b),flags,f,0,131,0)+b
def group(t,b):return struct.pack('<4sI4siIHH',b'GRUP',len(b)+24,t.encode(),0,0,0,0)+b
ids={0x11e46d,0x11e46c,0x1c32c8,0x212db7,0x102150}
van={f:list(subs(b)) for t,f,flags,b in records(GAME/'Data/Fallout4.esm') if f in ids}
def clone(f,replace,drop=()):return [(s,replace.get(s,v)) for s,v in van[f] if s not in drop]
own=lambda n:0x1000000+n
helmet,hAA,dog,dAA,category,hRecipe,dRecipe=map(own,range(0x800,0x807))
pool=collections.defaultdict(list)
def add(t,f,ss):pool[t].append(rec(t,f,ss))
add('KYWD',category,clone(0x102150,{'EDID':S('DoroRecipeCategory'),'FULL':S('DORO')}))
base='Armor\\DoroCostumes\\'
for fid,baseid,name,aa,race,mask,path,weight in [(helmet,0x11e46d,'Doro Mascot Head',hAA,0x13746,7,'DoroHelmet.nif',1.),(dog,0x1c32c8,'Doro Dogmeat Costume',dAA,0x1d698,(1<<3)|(1<<11)|(1<<16)|(1<<20),'DoroDogSuit.nif',2.)]:
 ss=clone(baseid,{'EDID':S('DoroHelmet' if fid==helmet else 'DoroDogSuit'),'FULL':S(name),'DESC':S(''),'BOD2':U(mask),'RNAM':U(race),'MOD2':S(base+'DoroHelmetGO.nif'),'DATA':struct.pack('<IfI',0,weight,0),'FNAM':b'\0'*8},['MO2T','INDX','MODL','PTRN'])
 i=next(i for i,(s,v) in enumerate(ss) if s=='DATA');ss[i:i]=[('INDX',b'\0\0'),('MODL',U(aa))]
 add('ARMO',fid,ss)
 ss=clone(0x11e46c if fid==helmet else 0x212db7,{'EDID':S('DoroHelmetAA' if fid==helmet else 'DoroDogSuitAA'),'BOD2':U(mask),'RNAM':U(race),'MOD2':S(base+path),'DNAM':bytes([10,10])+b'\0'*10},['MO2T'])
 i=next(i for i,(s,v) in enumerate(ss) if s=='MOD2')+1;ss.insert(i,('MOD3',S(base+path)))
 add('ARMA',aa,ss)
for fid,item,name in [(hRecipe,helmet,'DoroRecipeHelmet'),(dRecipe,dog,'DoroRecipeDogSuit')]:
 add('COBJ',fid,[('EDID',S(name)),('DESC',S('')),('CNAM',U(item)),('BNAM',U(0x102158)),('FNAM',U(category)),('INTV',U(1))])
count=sum(map(len,pool.values()));header=rec('TES4',0,[('HEDR',struct.pack('<fII',1.,count,0x807)),('CNAM',S('Doro costumes')),('SNAM',S('Free chemistry crafting: Dogmeat costume and player mascot head.')),('MAST',S('Fallout4.esm')),('DATA',b'\0'*8)],0x200)
(out/'DoroCostumes.esp').write_bytes(header+b''.join(group(t,b''.join(v)) for t,v in pool.items()))
rows=list(records(out/'DoroCostumes.esp'));assert len(rows)==8
for t,f,fl,b in rows:
 if t=='COBJ':
  ss=dict(subs(b));assert not any(s in ss for s in ['FVPA','CTDA','COCT','CNTO']);assert ss['BNAM']==U(0x102158)
(r/'build/costume_plugin_validation.json').write_text(json.dumps({'records':len(rows),'recipes':2,'ingredient_and_perk_requirements':0,'master':'Fallout4.esm','esl_flagged':True,'ingame_tested':False},indent=2))
print('COSTUME_PLUGIN_OK',len(rows))
