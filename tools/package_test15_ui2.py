"""Package the display-only hotfix on top of either test15 A or B."""
from pathlib import Path
import hashlib, json, zipfile

r=Path(__file__).resolve().parent.parent
source=(r/'tools/DoroCompanionScript.psc').read_bytes()
pex=(r/'build/test15_ui2_compile/DoroCompanionScript.pex').read_bytes()
with zipfile.ZipFile(r/'build/DoroFollower_FO4_test_0.2.5-test15A_CombatHotfix.zip') as z:
    old=z.read('Source/Scripts/DoroCompanionScript.psc').decode('utf-8-sig')
new=source.decode('utf-8-sig')
assert old.split('; callable from')[0].strip()==new.split('; Avoid engine object strings')[0].strip()
assert b'StatusFormId' in pex
instructions='''Doro test15 UI2 — 진단창 표시 수정 전용

test15 진단창이 Target=[Actor에서 잘리는 문제를 피하기 위해
객체 문자열 대신 숫자 FormID를 출력합니다. ID는 10진수입니다.
전투 동작, ESP, 크기, 모델, 의상은 변경하지 않습니다.

1. 게임을 완전히 종료합니다.
2. 현재 test15A 또는 test15B를 유지한 채 이 ZIP을 MO2에 별도 모드로 설치합니다.
3. MO2 왼쪽 목록에서 이 패치를 사용 중인 test15보다 아래(높은 우선순위)에 두고 켭니다.
   플러그인 목록에 새 ESP는 추가되지 않습니다. 기존 A/B 중 하나만 활성화합니다.
4. 세이브를 불러와 전투 중 도로롱을 누르거나 비전투 메뉴의 Combat status를 선택합니다.
5. 제목이 Doro test15 UI2인지 확인하고 상태창 전체 화면을 보내주세요.
   A/B 중 어떤 버전에서 찍었는지와 실제 공격 여부도 함께 알려주세요.

단독 실행용 모드가 아닙니다. 원래 test15A/B 모드를 비활성화하면 안 됩니다.
컴파일 검사는 통과했으며 게임 내 표시 결과는 사용자 확인이 필요합니다.
'''
files={'Scripts/DoroCompanionScript.pex':pex,'Source/Scripts/DoroCompanionScript.psc':source,
       'README_UI2_KO.txt':instructions.encode('utf-8-sig')}
manifest={p:hashlib.sha256(b).hexdigest() for p,b in files.items()}
files['SHA256_UI2.json']=json.dumps(manifest,indent=2).encode()
path=r/'build/DoroFollower_test15_UI2_StatusFix.zip'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
    for p,b in files.items():z.writestr(p,b)
with zipfile.ZipFile(path) as z:
    assert z.testzip() is None
    assert all(hashlib.sha256(z.read(p)).hexdigest()==h for p,h in manifest.items())
print(path)
print('Verified: gameplay prefix unchanged; only status rendering and helper changed; no ESP/assets included')
