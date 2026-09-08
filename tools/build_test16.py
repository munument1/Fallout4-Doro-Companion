"""Use the combat-successful test15B with reference scaling instead of Race height.

Run --prepare, compile the PSC to build/test16_compile, then run --package.
"""
from pathlib import Path
import hashlib, json, struct, sys, zipfile
from fo4_records import records, subs

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'build'
BASE=OUT/'DoroFollower_FO4_test_0.2.5-test15B_HeightControl.zip'
UI=OUT/'DoroFollower_test15_UI2_StatusFix.zip'

def digest(b): return hashlib.sha256(b).hexdigest()

def prepare():
    with zipfile.ZipFile(UI) as z:
        src=z.read('Source/Scripts/DoroCompanionScript.psc').decode('utf-8-sig').replace('\r\n','\n')
    old='''    ; Keep test14 reference scale neutral. A/B differ only in RACE height.
    if GetScale() != 1.0
        SetScale(1.0)
    endif'''
    new='''    ; Preserve the working test15B Race height=1; shrink this reference only.
    if Math.Abs(GetScale() - 0.42) > 0.001
        SetScale(0.42)
    endif'''
    assert src.count(old)==1
    src=src.replace(old,new).replace('Doro test15 UI2 | state=', 'Doro test16 | state=')
    src=src.replace('    info += "\\nPackageID="', '    info += " scale=" + GetScale()\n    info += "\\nPackageID="')
    (ROOT/'tools/DoroCompanionScript.psc').write_text(src,encoding='utf-8')
    (OUT/'test16_compile').mkdir(exist_ok=True)
    print('Prepared test16; combat logic unchanged from test15B/UI2')

def scale_reference(data):
    result=bytearray(data)
    changed=[]
    def walk(start,end):
        pos=start
        while pos<end:
            typ,size=struct.unpack_from('<4sI',data,pos)
            if typ==b'GRUP':walk(pos+24,pos+size);pos+=size;continue
            flags,fid=struct.unpack_from('<II',data,pos+8)
            if fid==0x100080b:
                assert typ==b'ACHR' and not flags&0x40000
                p=pos+24
                while p<pos+24+size:
                    sig,n=struct.unpack_from('<4sH',data,p);p+=6
                    assert sig!=b'XXXX'
                    if sig==b'XSCL':
                        assert n==4 and struct.unpack_from('<f',data,p)[0]==1.0
                        struct.pack_into('<f',result,p,0.42);changed.append(fid)
                    p+=n
            pos+=24+size
        assert pos==end
    walk(0,len(data))
    assert changed==[0x100080b]
    return bytes(result)

README='''Doro test16 — Race height 1.0 / Reference scale 0.42

확인된 사용자 결과: test15A(종족 높이 0.42)는 공격하지 않음.
test15B(종족 높이 1.0)는 적극적으로 공격함.

이번 변경:
- 공격이 되는 B의 Race 높이 1.0과 전투 코드를 유지.
- 배치 도로롱의 XSCL과 로드 시 SetScale만 0.42로 적용.
- 정상 표시용 UI2 진단창 포함. 제목 test16, scale 값 추가.
- 모델/스켈레톤/의상/음성/제작법/팩션/공격 데이터는 B와 동일.

설치:
게임을 완전히 종료한 후 기존 test15A/B 및 UI2 패치를 비활성화하고
이 ZIP 하나만 활성화하세요. Full ESP이며 기존 FormID는 유지합니다.
UI2가 덮어쓰면 배율을 1.0으로 되돌리므로 반드시 비활성화하세요.

테스트:
1. B에서 공격을 확인한 원본 테스트 세이브를 불러옵니다.
2. 작은 크기로 표시되는지 확인하고 같은 장소/같은 종류 적에게 전투합니다.
3. 실제 공격/타격 여부, 몸 옆 접근 시 투명벽 여부, 문 통과 여부를 알려주세요.
4. 공격하지 않으면 전투 중 도로롱을 눌러 test16 상태창을 찍어주세요.
   scale은 약 0.42가 예상됩니다. 진단창 FormID는 10진수입니다.

이 비교는 낮은 종족 높이와 낮은 참조 배율의 동작 차이를 검사합니다.
소형 크기에서 공격이 유지되는지, 충돌이 작아지는지는 아직 미검증입니다.
실패하면 공격이 되는 B가 대조군으로 남아 있습니다. 세이브를 삭제할 필요는 없습니다.
'''

def package():
    with zipfile.ZipFile(BASE) as z:files={p:z.read(p) for p in z.namelist()}
    manifest=json.loads(files['SHA256.json'])
    assert all(digest(files[p])==h for p,h in manifest.items())
    original=dict(files)
    files.pop('SHA256.json');files.pop('review_test15.json')
    files['DoroFollower.esp']=scale_reference(files['DoroFollower.esp'])
    files['Scripts/DoroCompanionScript.pex']=(OUT/'test16_compile/DoroCompanionScript.pex').read_bytes()
    files['Source/Scripts/DoroCompanionScript.psc']=(ROOT/'tools/DoroCompanionScript.psc').read_bytes()
    assert b'Doro test16' in files['Scripts/DoroCompanionScript.pex']
    files['README_KO.txt']=README.encode('utf-8-sig')
    allowed={'DoroFollower.esp','Scripts/DoroCompanionScript.pex','Source/Scripts/DoroCompanionScript.psc','README_KO.txt'}
    assert all(b==original[p] for p,b in files.items() if p not in allowed)
    dest=OUT/'DoroFollower_FO4_test_0.2.5-test16_ReferenceScale'
    dest.mkdir(exist_ok=True)
    for p,b in files.items():
        f=dest/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
    before=list(records(OUT/'DoroFollower_FO4_test_0.2.5-test15B_HeightControl/DoroFollower.esp'))
    after=list(records(dest/'DoroFollower.esp'))
    assert len(before)==len(after)==43
    assert [a[1] for a,b in zip(before,after) if a!=b]==[0x100080b]
    for a,b in zip(before,after):
        assert a[:3]==b[:3]
        if a[1]==0x100080b:
            sa=list(subs(a[3]));sb=list(subs(b[3]))
            assert len(sa)==len(sb)
            assert [x[0] for x,y in zip(sa,sb) if x!=y]==['XSCL']
    report={'version':'test16','ingame_tested':False,'base':'test15B (user confirmed attacking)',
            'modified_esp_records':['0100080B XSCL only'],'race_heights':[1.0,1.0],
            'reference_scale':0.42,'all_assets_unchanged':True,'papyrus_compile':'success',
            'source_sha256':digest(files['Source/Scripts/DoroCompanionScript.psc']),
            'pex_sha256':digest(files['Scripts/DoroCompanionScript.pex'])}
    files['review_test16.json']=json.dumps(report,indent=2).encode()
    files['SHA256.json']=json.dumps({p:digest(b) for p,b in files.items()},indent=2).encode()
    archive=dest.parent/(dest.name+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p,b in files.items():z.writestr(p,b)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(digest(z.read(p))==h for p,h in json.loads(z.read('SHA256.json')).items())
    (OUT/'test16_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(archive)
    print('Validated: only ACHR scale changed in ESP; all assets identical; archive hashes pass')

if __name__=='__main__':
    if sys.argv[1:] == ['--prepare']:prepare()
    elif sys.argv[1:] == ['--package']:package()
    else:raise SystemExit('Use --prepare or --package')
