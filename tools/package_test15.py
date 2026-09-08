"""Preserve the verified test14 package, replacing only the combat script/menu.

A is the intended hotfix. B differs from A only in RACE male/female height.
Compile tools/DoroCompanionScript.psc to build/test15_compile before running.
"""
from pathlib import Path
import hashlib, json, struct, zipfile
from fo4_records import records, subs

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT/'reference/test14_review'
OUT = ROOT/'build'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def sub(sig, data):
    assert len(data) < 65536
    return sig.encode() + struct.pack('<H', len(data)) + data

def patch_esp(data, large=False):
    def walk(start, end):
        parts = []
        pos = start
        while pos < end:
            header = bytearray(data[pos:pos+24])
            assert len(header) == 24
            size = struct.unpack_from('<I', header, 4)[0]
            if header[:4] == b'GRUP':
                body = walk(pos+24, pos+size)
                struct.pack_into('<I', header, 4, len(body)+24)
                parts.append(bytes(header)+body)
                pos += size
                continue
            flags, fid = struct.unpack_from('<II', header, 8)
            body = data[pos+24:pos+24+size]
            if fid == 0x01000805:
                assert not flags & 0x40000
                ss = list(subs(body))
                labels = [b.rstrip(b'\0') for s,b in ss if s=='ITXT']
                assert labels[-1] == b'Cancel' and len(labels)==6, labels
                new = []
                for s,b in ss:
                    if s=='ITXT' and b.rstrip(b'\0')==b'Cancel':
                        new.append(('ITXT', b'Combat status\0'))
                    new.append((s,b))
                body = b''.join(sub(s,b) for s,b in new)
            elif fid == 0x01000800 and large:
                assert not flags & 0x40000
                ss = list(subs(body))
                body = b''.join(sub(s, struct.pack('<ff',1.,1.)+b[8:] if s=='DATA' else b) for s,b in ss)
            struct.pack_into('<I', header, 4, len(body))
            parts.append(bytes(header)+body)
            pos += 24+size
        assert pos == end
        return b''.join(parts)
    return walk(0,len(data))

instructions = '''Doro test15 — 전투 스크립트 수정 및 크기 대조

이 패키지는 test14를 기준으로 만들었습니다. 공격 불능의 해결 여부는 인게임 확인이 필요합니다.
Full ESP, 기존 FormID와 DoroRace, 모델·스켈레톤 경로·의상·제작법을 유지합니다.
기존 제작 도구 build_doro_plugin.py/package_v02.py는 최신 패키지 생성에 사용하지 않습니다.

수정 사항:
- 전투 중 피격마다 StartCombat을 재호출하지 않음. 전투 시작 요청 사이에 1초 대기.
- 검색 상태/None/죽은 대상 이벤트를 아군 공격으로 오인해 StopCombat하지 않음.
- Setup의 추적/대기 패키지 재평가는 비전투 상태에만 수행.
- 독립 메뉴 동료이므로 teammate의 favor 허용을 끄고 남은 favor 상태 정리.
- 이 모드의 구형 대화 씬 080D가 재생 중이면 종료. 다른 모드 씬은 종료하지 않음.
- 메뉴에 Combat status 추가. 전투 중 도로롱 활성화 시에는 상태창만 표시.

설치/시험:
1. 게임을 완전히 종료하고 test14 및 이전 도로롱 모드를 비활성화합니다.
2. A만 설치/활성화합니다. DoroFollower.esp 하나가 활성화되어야 합니다.
   의상과 제작법은 통합되어 있으므로 별도 DoroCostumes.esp는 함께 켜지 않습니다.
3. 원래 test14로 사용하던 테스트 세이브를 불러와 도로롱에게 Follow me를 선택합니다.
4. 넓은 실외에서 확실한 적과 전투합니다. 도로롱의 실제 앞발 공격과 타격을 확인합니다.
5. 공격하지 않으면 전투 중 도로롱을 활성화하여 Combat status 화면을 찍습니다.
   활성화가 불가능하면 콘솔에서 도로롱을 선택한 뒤 cf ShowCombatStatus 로도 호출할 수 있습니다.
6. 게임을 종료한 뒤 A 대신 B를 활성화하고 같은 원본 세이브/같은 조건에서 반복합니다.
   A/B 둘을 동시에 활성화하지 마세요. 비교 중 저장한 세이브로 다음 비교를 하지 마세요.

A: test14와 같은 RACE height 0.42. 우선 시험할 수정본.
B: A와 동일하되 RACE male/female height만 1.0. 도로롱이 크게 보이는 진단용입니다.
   B는 최종 배포용이 아닙니다. 검사가 끝나면 A로 돌아가세요.

결과 전달:
- A 공격 여부 / B 공격 여부
- Combat status 화면 (target, distance, package, scene, favor, counters)
- 체력바 깜박임 여부 / oldSceneCleared 값

해석:
- A부터 공격: 이번 스크립트/상태 정리 묶음이 효과 있음. 개별 원인은 추가 분리 필요.
- A 실패, B 성공: 크기 관련 조건을 우선 조사. 캡슐이 원인이라고 즉시 확정하지 않음.
- 둘 다 실패: 상태창으로 타깃·패키지·씬을 확인 후 Race ID/공격 graph 경로 대조.

정착민/플레이어 팩션 보호 필터는 유지했습니다. 무관한 NPC를 적으로 강제 지정하지 마세요.
세이브 삭제/초기화, 게임 원본이나 확정 의상 수정은 필요하지 않습니다.
'''

def main():
    base = {str(p.relative_to(BASE)).replace('\\','/'):p.read_bytes() for p in BASE.rglob('*') if p.is_file()}
    manifest = json.loads(base['SHA256.json'])
    assert all(sha(base[p]) == h for p,h in manifest.items())
    base_rows = list(records(BASE/'DoroFollower.esp'))
    compiled = (OUT/'test15_compile/DoroCompanionScript.pex').read_bytes()
    source = (ROOT/'tools/DoroCompanionScript.psc').read_bytes()
    assert b'ShowCombatStatus' in compiled
    reports = []
    for letter, large in [('A',False),('B',True)]:
        name = 'DoroFollower_FO4_test_0.2.5-test15'+letter+('_HeightControl' if large else '_CombatHotfix')
        dest = OUT/name
        dest.mkdir(exist_ok=True)
        files = dict(base)
        files.pop('SHA256.json')
        files.pop('review_0.2.5-test14.json')
        files['DoroFollower.esp'] = patch_esp(base['DoroFollower.esp'], large)
        files['Scripts/DoroCompanionScript.pex'] = compiled
        files['Source/Scripts/DoroCompanionScript.psc'] = source
        files['README_KO.txt'] = (f'현재 패키지: test15{letter}\n\n'+instructions).encode('utf-8-sig')
        # Verify all assets and all other compiled scripts remain byte-for-byte identical.
        allowed = {'DoroFollower.esp','Scripts/DoroCompanionScript.pex','Source/Scripts/DoroCompanionScript.psc','README_KO.txt'}
        assert all(v==base[p] for p,v in files.items() if p not in allowed)
        (dest/'DoroFollower.esp').write_bytes(files['DoroFollower.esp'])
        current = list(records(dest/'DoroFollower.esp'))
        assert len(current)==len(base_rows)==43
        changed = []
        for a,b in zip(base_rows,current):
            assert a[:3]==b[:3]
            if a[3]!=b[3]:changed.append(f'{a[1]:08X}')
        assert set(changed)==({'01000805','01000800'} if large else {'01000805'})
        height = next(struct.unpack_from('<ff',dict(subs(b))['DATA']) for t,f,fl,b in current if f==0x1000800)
        report = {'version':'test15'+letter,'ingame_tested':False,'base_esp_sha256':sha(base['DoroFollower.esp']),
                  'modified_records':changed,'race_height':height,'pex_sha256':sha(compiled),'source_sha256':sha(source),
                  'records_including_header':43,'all_other_assets_unchanged':True,'papyrus_compile':'success'}
        files['review_test15.json'] = json.dumps(report,indent=2).encode()
        files['SHA256.json'] = json.dumps({p:sha(b) for p,b in files.items()},indent=2).encode()
        for p,b in files.items():
            target=dest/p; target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        archive=OUT/(name+'.zip')
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for p,b in files.items():z.writestr(p,b)
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            checks=json.loads(z.read('SHA256.json'))
            assert all(sha(z.read(p))==h for p,h in checks.items())
        report['zip_sha256']=sha(archive.read_bytes())
        report['zip']=str(archive)
        reports.append(report)
        print(archive)
    # A/B differ only by two height floats in a single RACE DATA field.
    a=OUT/'DoroFollower_FO4_test_0.2.5-test15A_CombatHotfix/DoroFollower.esp'
    b=OUT/'DoroFollower_FO4_test_0.2.5-test15B_HeightControl/DoroFollower.esp'
    ar=list(records(a));br=list(records(b))
    for ra,rb in zip(ar,br):
        if ra[1]!=0x1000800:assert ra==rb
        else:
            for sa,sb in zip(subs(ra[3]),subs(rb[3])):
                if sa[0]=='DATA':assert sa[1][8:]==sb[1][8:]
                else:assert sa==sb
    (OUT/'test15_package_validation.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
    (OUT/'TEST15_TEST_INSTRUCTIONS_KO.txt').write_text(instructions,encoding='utf-8-sig')
    print('Validated: 43 records, same FormIDs/assets, A/B height-only difference, ZIP integrity and hashes')

if __name__=='__main__':
    main()
