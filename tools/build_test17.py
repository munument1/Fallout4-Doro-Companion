"""Isolate Doro's skeleton and resize its two locomotion collision capsules.

Strictly restricted to the audited vanilla Yao Guai skeleton SHA; this is not
a general Havok scaler. Preserve ragdoll, bones, animation controllers, fixups,
materials, body filters and all unknown fields. Run --prepare, compile, --package.
Container/relative-array decoding uses the locally installed PyNifly 28.2.
"""
from pathlib import Path
import hashlib, json, math, struct, sys, zipfile
from fo4_records import records, subs

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'build'
sys.path.insert(0, str(ROOT/'tools/deps/pynifly28/io_scene_nifly/pyn'))
from bhk_autounpack import _parse_nif_blocks, parse_convex_polytope
from havok_packfile import parse_packfile

SOURCE = Path('C:/Users/seung/OneDrive/Desktop/Meshes/Actors/YaoGuai/CharacterAssets/skeleton.nif')
SOURCE_SHA = 'd3ba508c40a9ed4e74762945888592c77187db5b5d3797248ab567f897f65401'
BASE = OUT/'DoroFollower_FO4_test_0.2.5-test16_ReferenceScale.zip'
DEST = OUT/'DoroFollower_FO4_test_0.2.5-test17_DedicatedSkeleton'
SKELETON = 'Meshes/Actors/Doro/CharacterAssets/skeleton.nif'
FACTOR = .42

def sha(b): return hashlib.sha256(b).hexdigest()

def resize_skeleton():
    original = SOURCE.read_bytes()
    assert sha(original) == SOURCE_SHA
    blocks, count = _parse_nif_blocks(original)
    assert count == 154 and blocks[151]['type'] == 'bhkPhysicsSystem'
    b = blocks[151]
    assert struct.unpack_from('<I', b['blob'])[0] == len(b['blob'])-4
    hk = b['blob'][4:]
    pack = parse_packfile(hk)
    assert hk[16] == 8, 'Requires 64-bit Havok layout'
    capsules = pack.objects_of('hknpCapsuleShape')
    assert len(capsules) == 2 and len(pack.objects) == 3
    result = bytearray(original)
    allowed = set()
    changes = []

    def scale(offset, label):
        value = struct.unpack_from('<f', original, offset)[0]
        assert math.isfinite(value) and abs(value) < 1e6
        struct.pack_into('<f', result, offset, value*FACTOR)
        allowed.update(range(offset, offset+4))
        changes.append({'field':label, 'offset':offset, 'before':value,
                        'after':struct.unpack_from('<f',result,offset)[0]})

    hkbase = b['offset']+4
    for i, obj in enumerate(capsules):
        a = obj.abs_off
        # Audited FO4 64-bit capsule: polytope base 0x50, endpoints at 0x50/60.
        # RelArrays themselves locate vertices and planes; never scale IDs or w.
        assert obj.size == 0x1b0
        assert math.isclose(struct.unpack_from('<f',hk,a+0x14)[0], .780749023)
        assert struct.unpack_from('<f',hk,a+0x5c)[0] == 1
        assert struct.unpack_from('<f',hk,a+0x6c)[0] == 1
        scale(hkbase+a+0x14, f'capsule{i}.radius')
        for endpoint in (0x50,0x60):
            for axis in range(3):
                scale(hkbase+a+endpoint+axis*4, f'capsule{i}.endpoint{endpoint:x}.{axis}')
        nv, vo = struct.unpack_from('<HH', hk, a+0x30)
        np, po = struct.unpack_from('<HH', hk, a+0x40)
        assert (nv,vo,np,po) == (8,0x40,8,0xb0)
        for v in range(nv):
            for axis in range(3):
                scale(hkbase+a+0x30+vo+v*16+axis*4, f'capsule{i}.vertex{v}.{axis}')
        for plane in range(np):
            pos = a+0x40+po+plane*16
            normal = struct.unpack_from('<3f',hk,pos)
            if sum(x*x for x in normal) < 1e-12:
                assert struct.unpack_from('<f',hk,pos+12)[0] < -1e30
                continue  # Padding plane sentinel must remain untouched.
            assert math.isclose(sum(x*x for x in normal),1,abs_tol=1e-5)
            scale(hkbase+pos+12, f'capsule{i}.plane{plane}.distance')
    bodies,n = pack.array(0,0x40)
    assert n == 2
    for i in range(n):
        assert pack.gptr(bodies-pack.data_start+i*0x60,0) == (2,capsules[i].rel)
        for axis in range(3):
            scale(hkbase+bodies+i*0x60+0x30+axis*4, f'body{i}.position.{axis}')
    assert blocks[2]['type'] == 'BSBound'
    for i in range(6): scale(blocks[2]['offset']+4+i*4, f'BSBound.{i}')
    for bid in (149,152):
        node = blocks[bid]
        extras = struct.unpack_from('<I',node['blob'],4)[0]
        for axis in range(3):
            scale(node['offset']+16+4*extras+axis*4, f'node{bid}.translation.{axis}')

    assert all(x==y or i in allowed for i,(x,y) in enumerate(zip(original,result)))
    updated,_ = _parse_nif_blocks(result)
    assert [i for i,(x,y) in enumerate(zip(blocks,updated)) if x['blob']!=y['blob']] == [2,149,151]
    newhk = updated[151]['blob'][4:]
    newpack = parse_packfile(newhk)
    assert (pack.hdrs,pack.local,pack.glob,pack.objects)==(newpack.hdrs,newpack.local,newpack.glob,newpack.objects)
    for o in capsules:
        v,f,r = parse_convex_polytope(hk,o.abs_off)
        vv,ff,rr = parse_convex_polytope(newhk,o.abs_off)
        assert f==ff and math.isclose(rr,r*FACTOR,rel_tol=1e-6)
        assert all(math.isclose(y,x*FACTOR,rel_tol=1e-6,abs_tol=1e-8) for p,q in zip(v,vv) for x,y in zip(p,q))
        # Verify resized hull vertices still satisfy every resized face plane.
        for i in range(6):
            nx,ny,nz,d = struct.unpack_from('<4f',newhk,o.abs_off+0xf0+i*16)
            assert all(nx*x+ny*y+nz*z+d < 2e-6 for x,y,z in vv)
    assert sha(SOURCE.read_bytes()) == SOURCE_SHA
    return bytes(result), changes

def patch_esp(data):
    old = b'Actors\\YaoGuai\\CharacterAssets\\skeleton.nif\0'
    new = b'Actors\\Doro\\CharacterAssets\\skeleton.nif\0'
    hits = []
    def walk(start,end):
        pos=start; out=[]
        while pos<end:
            head=bytearray(data[pos:pos+24]); size=struct.unpack_from('<I',head,4)[0]
            if head[:4]==b'GRUP':
                body=walk(pos+24,pos+size);pos+=size
                struct.pack_into('<I',head,4,len(body)+24)
            else:
                body=data[pos+24:pos+24+size];pos+=24+size
                flags,fid=struct.unpack_from('<II',head,8)
                if fid==0x1000800:
                    assert head[:4]==b'RACE' and not flags&0x40000
                    ss=[]
                    for sig,value in subs(body):
                        if sig=='ANAM' and value.lower()==old.lower():
                            hits.append(sig);value=new
                        ss.append(sig.encode()+struct.pack('<H',len(value))+value)
                    body=b''.join(ss)
                struct.pack_into('<I',head,4,len(body))
            out.append(bytes(head)+body)
        assert pos==end
        return b''.join(out)
    out=walk(0,len(data));assert len(hits)==2,hits
    return out

def prepare():
    with zipfile.ZipFile(BASE) as z:
        src=z.read('Source/Scripts/DoroCompanionScript.psc').decode('utf-8-sig').replace('\r\n','\n')
    assert src.count('Doro test16 | state=')==1
    (ROOT/'tools/DoroCompanionScript.psc').write_text(src.replace('Doro test16 | state=','Doro test17 | state='),encoding='utf-8')
    (OUT/'test17_compile').mkdir(exist_ok=True)
    nif, changes = resize_skeleton()
    target=DEST/SKELETON;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(nif)
    (OUT/'test17_collision_changes.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
    print('Dedicated skeleton validated:',target)

README='''Doro test17 — 전용 스켈레톤 / 이동 충돌 축소 시험

test16과 같은 작은 크기: Race height 1.0, reference scale 0.42.
DoroRace 남녀 스켈레톤 경로를 Actors/Doro/CharacterAssets/skeleton.nif로 분리.
야오과이 복사본의 이동 충돌 캡슐 2개 반지름/끝점/정점/평면 거리,
물리 바디 위치, Bumper 노드 위치, BSBound를 0.42배로 조정.
뼈/애니메이션/래그돌/전투 로직/팩션/의상/제작법은 test16과 동일.
기존 야오과이 공용 경로에는 파일을 넣지 않습니다.

이 파일은 원인 분리를 위한 시험본이며 공격/투명벽 해결은 아직 인게임 미검증.
엔진이 전용 물리 크기에 참조 배율을 추가 적용하는지도 시험이 필요합니다.

설치: 게임을 완전히 종료하고 이전 test14~16 및 UI2를 끈 뒤 이 ZIP 하나만 활성화.
DoroFollower.esp는 기존 Full ESP/FormID를 유지합니다.
공격됐던 B 테스트의 원본 세이브로 비교하며 시험 중 저장은 별도 슬롯을 쓰세요.
가능하면 도로롱과 다른 실내에서 불러온 뒤 밖으로 나와 3D를 새로 로드하세요.
세이브 삭제나 동료 삭제 콘솔 명령은 필요 없습니다.

확인할 것:
1. 몸 옆 투명벽이 줄었는지 / 좁은 통로를 통과하는지.
2. 같은 적에게 자발적으로 앞발 공격하고 실제 피해를 주는지.
3. 바닥에 파묻힘/뜸/떨림 등 이동 충돌의 부작용이 있는지.
실패하면 Combat status 창(test17 / scale 약 0.42)을 함께 알려주세요.
공격이 되던 test15B는 그대로 남아 있는 대조군입니다.
'''

def package():
    with zipfile.ZipFile(BASE) as z: files={p:z.read(p) for p in z.namelist()}
    assert all(sha(files[p])==h for p,h in json.loads(files['SHA256.json']).items())
    original=dict(files)
    files.pop('SHA256.json');files.pop('review_test16.json')
    files['DoroFollower.esp']=patch_esp(files['DoroFollower.esp'])
    files[SKELETON],changes=resize_skeleton()
    files['Source/Scripts/DoroCompanionScript.psc']=(ROOT/'tools/DoroCompanionScript.psc').read_bytes()
    files['Scripts/DoroCompanionScript.pex']=(OUT/'test17_compile/DoroCompanionScript.pex').read_bytes()
    assert b'Doro test17' in files['Scripts/DoroCompanionScript.pex']
    before_src=original['Source/Scripts/DoroCompanionScript.psc'].decode('utf-8-sig').replace('\r\n','\n')
    after_src=files['Source/Scripts/DoroCompanionScript.psc'].decode('utf-8-sig').replace('\r\n','\n')
    assert after_src==before_src.replace('Doro test16 | state=','Doro test17 | state=')
    files['README_KO.txt']=README.encode('utf-8-sig')
    allowed={'DoroFollower.esp',SKELETON,'Scripts/DoroCompanionScript.pex','Source/Scripts/DoroCompanionScript.psc','README_KO.txt'}
    assert all(value==original[name] for name,value in files.items() if name not in allowed)
    assert not any(name.lower().startswith('meshes/actors/yaoguai/') for name in files)
    for name,value in files.items():
        p=DEST/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(value)
    prev=OUT/'test17_before.esp';prev.write_bytes(original['DoroFollower.esp'])
    r1=list(records(prev));r2=list(records(DEST/'DoroFollower.esp'))
    assert len(r1)==len(r2)==43
    assert [x[1] for x,y in zip(r1,r2) if x!=y]==[0x1000800]
    a=next(x for x in r1 if x[1]==0x1000800);b=next(x for x in r2 if x[1]==0x1000800)
    assert [s for (s,x),(t,y) in zip(subs(a[3]),subs(b[3])) if (s,x)!=(t,y)]==['ANAM','ANAM']
    report={'version':'test17','ingame_tested':False,'base':'test16 (B-derived)',
            'collision_factor':FACTOR,'race_height':1,'reference_scale':.42,
            'skeleton_sha256':sha(files[SKELETON]),'vanilla_skeleton_sha256':SOURCE_SHA,
            'changed_nif_blocks':[2,149,151],'all_bones_and_ragdoll_unchanged':True,
            'esp_changes':['DoroRace male/female ANAM only'],'other_assets_unchanged':True,
            'havok_fixups_unchanged':True,'collision_hull_validation':'passed',
            'papyrus_compile':'success','changes':changes}
    files['review_test17.json']=json.dumps(report,indent=2).encode()
    files['SHA256.json']=json.dumps({p:sha(v) for p,v in files.items()},indent=2).encode()
    archive=DEST.parent/(DEST.name+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name,value in files.items():z.writestr(name,value)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(sha(z.read(p))==h for p,h in json.loads(z.read('SHA256.json')).items())
    (OUT/'test17_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Validated package:',archive)

if __name__=='__main__':
    if sys.argv[1:]==['--prepare']:prepare()
    elif sys.argv[1:]==['--package']:package()
    else:raise SystemExit('Use --prepare or --package')
