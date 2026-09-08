# test17: 도로롱 전용 스켈레톤과 이동 충돌 축소

## 확인된 증상과 검증 범위

사용자 결과: test15A는 공격하지 않음, 큰 test15B는 적극적으로 공격함.
test16(B의 Race height 1 + reference scale 0.42)은 공격하지 않고 투명벽도 남음.
작은 크기와 공격 실패의 연관성은 확인됐지만 충돌이 공격 실패의 원인이라고 확정하지 않는다.

test17은 test16과 비교한다. 외형 배율, 전투 코드, 팩션, 의상과 제작법은 그대로다.
공격/충돌/지면 접촉 동작은 사용자가 게임에서 확인한다.

## 변경

- DoroRace 01000800의 남녀 ANAM만 `Actors\Doro\CharacterAssets\skeleton.nif`로 변경.
- 원본 야오과이 스켈레톤의 복사본을 해당 전용 경로에 추가. 공용 야오과이 파일을 배포하거나 수정하지 않음.
- 151 bhkPhysicsSystem의 두 hknpCapsuleShape 반지름/끝점/내부 정점/평면 거리를 0.42배 축소.
- 두 바디 위치, CharacterBumper 노드 위치, BSBound도 동일 배율 적용.
- 반지름 약 0.780749 → 0.327915 Havok 단위. 전체 NIF를 재수출하지 않고 검증된 필드만 수정.
- 비활성 평면의 최솟값 센티널, 정점 w, 법선, 회전, 충돌 필터, 재질, 포인터/fixup 유지.
- 뼈 이름/계층/변환, 애니메이션 제어기, 래그돌 물리 블록은 원본과 바이트 단위 동일.
- Papyrus는 진단 제목 test16 → test17만 변경.

이것은 이동 충돌 수정 시험이며 소형 모델/래그돌 전체를 새로 제작한 최종 스켈레톤은 아니다.
엔진이 충돌에 참조 배율을 추가 적용할 가능성, 캐시된 3D, 공격 거리 선택은 인게임 확인 대상이다.

## 검증

- 원본 SHA256 `d3ba508c40a9ed4e74762945888592c77187db5b5d3797248ab567f897f65401`을 빌드 전후 확인.
- 수정 NIF 154블록 유지; 실제 변경 블록은 2(BSBound), 149(Bumper), 151(PhysicsSystem)뿐.
- Havok 오브젝트 목록과 local/global/virtual fixup 구조 동일.
- 두 캡슐의 내부 다면체 정점/면 연결 재해석, 배율 일치 및 평면 내부 조건 검사 통과.
- 별도 NiflyDLL 리더로 전용 NIF 로드 성공: 노드 90개, Bumper 149→150→151,
  Controller 152→153→151, 물리 페이로드 1872바이트, 오류 로그 없음.
- ESP 43레코드 유지. DoroRace의 두 ANAM 외 레코드/필드 동일.
- 기존 모델/의상/음성/제작 자산 바이트 비교 통과.
- Papyrus 컴파일 성공. 최초 줄바꿈 중복 오류는 생성기에서 CRLF 정규화하여 수정.
- ZIP 무결성 및 SHA256 매니페스트 검사 통과.
- NifSkope 창이 닫혀 있어 수정본의 화면 검증은 수행하지 않음. DLL 로드는 렌더링/게임 검증을 대신하지 않음.

## 재현

`python tools/build_test17.py --prepare` → tools 폴더에서 Papyrus 컴파일러로
DoroCompanionScript.psc를 build/test17_compile에 컴파일 →
`python tools/build_test17.py --package`.

생성물: `build/DoroFollower_FO4_test_0.2.5-test17_DedicatedSkeleton.zip`.
필드별 수정 전후 값은 `build/test17_collision_changes.json` 및 ZIP의 review_test17.json에 기록.
로컬 PyNifly 28.2의 havok_packfile.py와 bhk_autounpack.py로 컨테이너/상대 배열을 해석한다.
캡슐 끝점은 이 SHA의 FO4 64비트 레이아웃(0x50/0x60)으로 제한한다.
다른 버전 스켈레톤이나 32비트 Havok 구조에 재사용하지 않는다.

## 게임 테스트

게임 종료 후 이전 Doro 모드/test15/test16/UI2를 비활성화하고 test17 하나만 활성화.
공격이 됐던 B 테스트의 원본 세이브로 동일한 적/장소에서 비교한다.
가능하면 다른 실내에서 불러온 뒤 밖으로 이동하여 3D를 새로 로드한다.
투명벽 범위, 실제 공격/피해, 지면 파묻힘/뜸/떨림을 각각 관찰한다.
공격 실패 시 test17 Combat status 창을 확인한다. scale 예상값은 약 0.42.
세이브 삭제나 동료 삭제는 요구하지 않는다.
