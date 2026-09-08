"""Build release candidate from the user-verified test17; no asset re-export."""
from pathlib import Path
import hashlib,json,re,struct,sys,zipfile
from fo4_records import records,subs
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'build'
BASE=OUT/'DoroFollower_FO4_test_0.2.5-test17_DedicatedSkeleton.zip'
DEST=OUT/'DoroFollower_FO4_0.2.6_RC1'
def sha(b):return hashlib.sha256(b).hexdigest()

def prepare():
    with zipfile.ZipFile(BASE) as z:
        src=z.read('Source/Scripts/DoroCompanionScript.psc').decode('utf-8-sig').replace('\r\n','\n')
    src=src[:src.index('; Avoid engine object strings')].rstrip()+'\n'
    for line in ['int combatRequests = 0','int friendlyStops = 0','int lastCombatState = 0','Actor lastCombatEventTarget','Bool clearedLegacyScene = false',
                 '        clearedLegacyScene = true','    combatRequests += 1','    lastCombatState = aeCombatState','    lastCombatEventTarget = akTarget','            friendlyStops += 1']:
        assert line+'\n' in src
        src=src.replace(line+'\n','')
    src=re.sub(r'^.*Debug\.Trace\(.*\)\n','',src,flags=re.M)
    src=src.replace('        ShowCombatStatus()\n','')
    src=src.replace('    elseif choice == 4\n        DoCommand(50)\n    elseif choice == 5\n','')
    a=src.index('    elseif choice == 50\n');b=src.index('\nEndFunction',a)
    src=src[:a]+'    endif'+src[b:]
    src=src.replace('; Preserve the working test15B Race height=1; shrink this reference only.',
                    '; Match the dedicated Doro skeleton at Race height 1 and reference scale 0.42.')
    src=src.replace('Doro: command menu missing from DoroFollower.esp','Doro: please check that DoroFollower.esp is enabled.')
    src=src.replace('    IgnoreFriendlyHits(true)\n    ; This mod', '''    IgnoreFriendlyHits(true)
    ; Retire the old Yao Guai damage override in existing saves as well.
    ActorValue unarmedDamage = Game.GetForm(0x000002DF) as ActorValue
    if unarmedDamage != None && GetBaseValue(unarmedDamage) != 0.0
        SetValue(unarmedDamage, 0.0)
    endif
    ; This mod''')
    assert not any(x in src for x in ['test15','test17','ShowCombatStatus','testIdle','Debug.Trace','DoCommand(50)'])
    (ROOT/'tools/DoroCompanionScript.psc').write_text(src,encoding='utf-8')
    (OUT/'release026_compile').mkdir(exist_ok=True)
    print('Prepared release source')

def patch(data,damage):
    hits=[]
    def walk(start,end):
        pos=start;result=[]
        while pos<end:
            head=bytearray(data[pos:pos+24]);size=struct.unpack_from('<I',head,4)[0]
            if head[:4]==b'GRUP':
                body=walk(pos+24,pos+size);pos+=size
                struct.pack_into('<I',head,4,len(body)+24)
            else:
                body=data[pos+24:pos+24+size];pos+=24+size
                flags,fid=struct.unpack_from('<II',head,8)
                if fid in (0x1000805,0x1000803,0x1000800):
                    assert not flags&0x40000
                    out=[]
                    for sig,value in subs(body):
                        if fid==0x1000800 and sig=='UNWP':
                            assert value==struct.pack('<I',0xc2c38)
                            value=struct.pack('<I',0xc2c2b);hits.append('weapon')
                        if fid==0x1000800 and sig=='ATKD':
                            value=bytearray(value)
                            attackflags=struct.unpack_from('<I',value,12)[0]
                            # Keep Yao Guai events, reach, chances and geometry.
                            # Dogmeat normal=1, standing power=1.5, moving power=2.
                            mult=2.0 if attackflags&4 and attackflags&16 else 1.5 if attackflags&4 else 1.0
                            if struct.unpack_from('<f',value,0)[0]<.1: mult=.1
                            struct.pack_into('<f',value,0,mult);hits.append('attack')
                        if fid==0x1000803 and sig=='ATKR':
                            assert value==struct.pack('<I',0xa0f2f)
                            value=struct.pack('<I',0x1000800)
                        if fid==0x1000803 and sig=='TPTA':
                            value=bytearray(value);struct.pack_into('<I',value,44,0)
                        if fid==0x1000803 and sig=='ACBS':
                            value=bytearray(value)
                            assert struct.unpack_from('<H',value,6)[0]==1000
                            assert struct.unpack_from('<I',value,0)[0]&0x80
                            struct.pack_into('<HH',value,8,1,65535)
                            template=struct.unpack_from('<H',value,14)[0]
                            struct.pack_into('<H',value,14,template&~0x800)
                        if fid==0x1000805 and sig=='ITXT' and value in (b'Yao Guai idle test\0',b'Combat status\0'):
                            hits.append('menu');continue
                        if fid==0x1000803 and sig=='PRPS':
                            value=bytearray(value)
                            for i in range(0,len(value),8):
                                av,old=struct.unpack_from('<If',value,i)
                                if av==0x2df:
                                    assert old==100
                                    struct.pack_into('<f',value,i+4,damage);hits.append('damage')
                        out.append(sig.encode()+struct.pack('<H',len(value))+value)
                    body=b''.join(out)
                struct.pack_into('<I',head,4,len(body))
            result.append(bytes(head)+body)
        assert pos==end
        return b''.join(result)
    result=walk(0,len(data));assert sorted(hits)==sorted(['damage','menu','menu','weapon']+['attack']*20)
    return result

def package(damage):
    assert damage==0, 'Use Dogmeat weapon damage with no Yao Guai bonus'
    with zipfile.ZipFile(BASE) as z:files={p:z.read(p) for p in z.namelist()}
    assert all(sha(files[p])==h for p,h in json.loads(files['SHA256.json']).items())
    old=dict(files)
    files.pop('SHA256.json');files.pop('review_test17.json')
    files['DoroFollower.esp']=patch(files['DoroFollower.esp'],damage)
    files['Source/Scripts/DoroCompanionScript.psc']=(ROOT/'tools/DoroCompanionScript.psc').read_bytes()
    files['Scripts/DoroCompanionScript.pex']=(OUT/'release026_compile/DoroCompanionScript.pex').read_bytes()
    src=files['Source/Scripts/DoroCompanionScript.psc'].decode('utf-8-sig')
    assert not any(x in src for x in ['ShowCombatStatus','testIdle','Debug.Trace','DoCommand(50)'])
    files['README_KO.txt']=(ROOT/'docs/RELEASE_026_KO.txt').read_bytes()
    changed={'DoroFollower.esp','Source/Scripts/DoroCompanionScript.psc','Scripts/DoroCompanionScript.pex','README_KO.txt'}
    assert all(v==old[p] for p,v in files.items() if p not in changed)
    for name,value in files.items():
        path=DEST/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value)
    original=OUT/'release026_before.esp';original.write_bytes(old['DoroFollower.esp'])
    a=list(records(original));b=list(records(DEST/'DoroFollower.esp'))
    assert len(a)==len(b)==43
    assert {x[1] for x,y in zip(a,b) if x!=y}=={0x1000805,0x1000803,0x1000800}
    menu=next(row for row in b if row[1]==0x1000805)
    assert [v for s,v in subs(menu[3]) if s=='ITXT']==[b'Follow me\0',b'Wait here\0',b'Carry items\0',b'Return to Red Rocket\0',b'Cancel\0']
    npc1=next(row for row in a if row[1]==0x1000803)
    npc2=next(row for row in b if row[1]==0x1000803)
    assert set(s for (s,v),(t,w) in zip(subs(npc1[3]),subs(npc2[3])) if (s,v)!=(t,w))=={'ACBS','ATKR','TPTA','PRPS'}
    race1=next(row for row in a if row[1]==0x1000800)
    race2=next(row for row in b if row[1]==0x1000800)
    assert set(s for (s,v),(t,w) in zip(subs(race1[3]),subs(race2[3])) if (s,v)!=(t,w))=={'ATKD','UNWP'}
    for (s,v),(t,w) in zip(subs(race1[3]),subs(race2[3])):
        if s=='ATKD':assert v[4:]==w[4:]
    report={'version':'0.2.6 RC1','test17_ingame':'user confirmed attacking and reduced invisible wall',
            'rc_ingame_tested':False,'unarmed_damage_before':100,'unarmed_damage_after':damage,
            'unchanged_assets':True,'papyrus_compile':'passed','menu_dispatch':'4 commands + Cancel',
            'level_mult':1.0,'level_bounds':[1,65535],'unarmed_weapon':'000C2C2B UnarmedDogmeat',
            'note':'No public upload performed. Existing save actor-value overrides may need verification.'}
    files['release_validation.json']=json.dumps(report,indent=2).encode()
    files['SHA256.json']=json.dumps({p:sha(v) for p,v in files.items()},indent=2).encode()
    dest=DEST.parent/(DEST.name+'.zip')
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for p,v in files.items():z.writestr(p,v)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert all(sha(z.read(p))==h for p,h in json.loads(z.read('SHA256.json')).items())
    print(dest)

if __name__=='__main__':
    if sys.argv[1:]==['--prepare']:prepare()
    elif len(sys.argv)==3 and sys.argv[1]=='--package':package(float(sys.argv[2]))
    else:raise SystemExit('--prepare or --package DAMAGE')
