"""Restore verified test17 combat; retain clean menu and player level bounds."""
import json,struct,sys,zipfile
from pathlib import Path
import build_release_026 as rc1
from fo4_records import records,subs
ROOT=rc1.ROOT
OUT=rc1.OUT
DEST=OUT/'DoroFollower_FO4_0.2.6_RC2'

def prepare():
    rc1.prepare()
    path=ROOT/'tools/DoroCompanionScript.psc'
    src=path.read_text(encoding='utf-8')
    start=src.index('    ; Retire the old Yao Guai damage override')
    end=src.index('    ; This mod now uses',start)
    src=src[:start]+'''    ; RC1 could store a zero damage override in a saved actor.
    if !releaseCombatRestored
        ActorValue unarmedDamage = Game.GetForm(0x000002DF) as ActorValue
        if unarmedDamage != None && GetBaseValue(unarmedDamage) == 0.0
            SetValue(unarmedDamage, 100.0)
        endif
        releaseCombatRestored = true
    endif
'''+src[end:]
    src=src.replace('Bool menuOpen = false','Bool menuOpen = false\nBool releaseCombatRestored = false')
    path.write_text(src,encoding='utf-8')
    (OUT/'release026_rc2_compile').mkdir(exist_ok=True)

def patch(data):
    def walk(start,end):
        pos=start;out=[]
        while pos<end:
            head=bytearray(data[pos:pos+24]);size=struct.unpack_from('<I',head,4)[0]
            if head[:4]==b'GRUP':
                body=walk(pos+24,pos+size);pos+=size
                struct.pack_into('<I',head,4,len(body)+24)
            else:
                body=data[pos+24:pos+24+size];pos+=24+size
                flags,fid=struct.unpack_from('<II',head,8)
                if fid in (0x1000805,0x1000803):
                    assert not flags&0x40000
                    ss=[]
                    for s,v in subs(body):
                        if fid==0x1000805 and s=='ITXT' and v in (b'Yao Guai idle test\0',b'Combat status\0'):continue
                        if fid==0x1000803 and s=='ACBS':
                            v=bytearray(v);assert struct.unpack_from('<H',v,10)[0]==100
                            struct.pack_into('<H',v,10,65535)
                        ss.append(s.encode()+struct.pack('<H',len(v))+v)
                    body=b''.join(ss)
                struct.pack_into('<I',head,4,len(body))
            out.append(bytes(head)+body)
        assert pos==end
        return b''.join(out)
    return walk(0,len(data))

README='''Doro Follower 0.2.6 RC2

RC1에서 사용자가 공격 불능을 확인하여 전투 설정을 test17로 복원했습니다.
공격 무기, 공격 데이터 상속, 공격 배율, 기본 공격력 100을 모두 복원.
test17의 전용 스켈레톤과 축소 충돌은 그대로 유지합니다.
시험 메뉴/진단창/로그는 제거한 상태로 유지합니다.
플레이어 레벨 1배 연동, 최소 1/최대 65535 설정은 유지합니다.
RC1에서 저장된 공격력 0은 최초 로드 때 100으로 복원합니다.

설치: 게임을 완전히 종료하고 RC1/test17/기타 이전 Doro 모드 및 UI2를 끄고
RC2 ZIP 하나만 활성화하세요. DoroFollower.esp와 기존 FormID는 유지합니다.
우선 test17에서 공격됐던 원본 세이브로 같은 적에게 공격을 확인하세요.
RC1에서 저장한 세이브도 복구 처리가 있지만 별도로 확인이 필요합니다.
정상 메뉴는 동행/대기/보관/귀환/취소의 5개 항목입니다.
세이브 삭제나 동료 삭제는 필요 없습니다.

공격력이 강한 test17 밸런스를 유지하는 복구판이며 도그밋 피해 조정은 취소했습니다.
RC2 인게임 동작은 아직 확인 전입니다.
'''

def package():
    with zipfile.ZipFile(rc1.BASE) as z:files={p:z.read(p) for p in z.namelist()}
    assert all(rc1.sha(files[p])==h for p,h in json.loads(files['SHA256.json']).items())
    old=dict(files);files.pop('SHA256.json');files.pop('review_test17.json')
    files['DoroFollower.esp']=patch(old['DoroFollower.esp'])
    files['Source/Scripts/DoroCompanionScript.psc']=(ROOT/'tools/DoroCompanionScript.psc').read_bytes()
    files['Scripts/DoroCompanionScript.pex']=(OUT/'release026_rc2_compile/DoroCompanionScript.pex').read_bytes()
    files['README_KO.txt']=README.encode('utf-8-sig')
    for name,value in files.items():
        p=DEST/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(value)
    before=OUT/'rc2_before.esp';before.write_bytes(old['DoroFollower.esp'])
    a=list(records(before));b=list(records(DEST/'DoroFollower.esp'))
    assert len(a)==len(b)==43
    assert {x[1] for x,y in zip(a,b) if x!=y}=={0x1000805,0x1000803}
    for x,y in zip(a,b):
        if x[1]==0x1000803:
            assert [s for (s,v),(t,w) in zip(subs(x[3]),subs(y[3])) if (s,v)!=(t,w)]==['ACBS']
            v=dict(subs(x[3]))['ACBS'];w=dict(subs(y[3]))['ACBS']
            assert v[:10]==w[:10] and v[12:]==w[12:]
        if x[1]==0x1000805:
            assert [v for s,v in subs(y[3]) if s=='ITXT']==[b'Follow me\0',b'Wait here\0',b'Carry items\0',b'Return to Red Rocket\0',b'Cancel\0']
    allowed={'DoroFollower.esp','Scripts/DoroCompanionScript.pex','Source/Scripts/DoroCompanionScript.psc','README_KO.txt'}
    assert all(v==old[p] for p,v in files.items() if p not in allowed)
    src=files['Source/Scripts/DoroCompanionScript.psc'].decode('utf-8-sig').replace('\r\n','\n')
    original=old['Source/Scripts/DoroCompanionScript.psc'].decode('utf-8-sig').replace('\r\n','\n')
    import re
    for name in ['IsFriendlyTarget','RetaliateAgainst','AssistPlayerAgainst','FindAndAttackNearbyHostile','OnHit','OnCombatStateChanged','OnTimer']:
        pattern=rf'(?m)^[^\n]*(?:Function|Event) {name}\(.*?^End(?:Function|Event)'
        def clean(text):
            block=re.search(pattern,text,re.S|re.M).group()
            return '\n'.join(line for line in block.splitlines() if not any(s in line for s in ['Debug.Trace','combatRequests +=','friendlyStops +=','lastCombatState =','lastCombatEventTarget =']))
        assert clean(src)==clean(original),name
    files['release_validation.json']=json.dumps({'version':'0.2.6 RC2','ingame_tested':False,
        'combat_records_match_test17':True,'combat_functions_match_except_diagnostics':True,
        'only_esp_changes':['MESG debug buttons removed','NPC ACBS max level 100 to 65535'],
        'assets_identical_to_test17':True,'rc1_zero_damage_migration':True,'compile':'passed'},indent=2).encode()
    files['SHA256.json']=json.dumps({p:rc1.sha(v) for p,v in files.items()},indent=2).encode()
    archive=DEST.parent/(DEST.name+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p,v in files.items():z.writestr(p,v)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(rc1.sha(z.read(p))==h for p,h in json.loads(z.read('SHA256.json')).items())
    print(archive)

if __name__=='__main__':
    if sys.argv[1:]==['--prepare']:prepare()
    elif sys.argv[1:]==['--package']:package()
    else:raise SystemExit('--prepare or --package')
