# test14 보고서 독립 검증 — 2026-09-08

## 판정

보고서에 적힌 파일 식별 정보와 핵심 ESP 설정은 실제 패키지와 일치한다. 야오과이 스켈레톤에 별도의 CharacterController/CharacterBumper 물리 연결도 확인했다. 그러나 **충돌 크기 때문에 공격을 못 한다는 인과관계는 아직 입증되지 않았다.** 현재 자료로 공격 불능의 단일 원인이나 충돌 크기의 런타임 계산 우선순위를 확정할 수 없다.

이번 검증은 파일·소스·컴파일 및 바닐라 비교에 한정된다. 게임을 실행하거나 설치된 모드, 세이브, 의상 모델을 수정하지 않았다. 동봉 문서의 수정 제안은 검토 대상으로 읽었고 실행하지 않았다.

## 검증 범위와 결과

| 항목 | 결과 |
|---|---|
| 제공 ZIP SHA-256 | 보고서의 706ff2cb…fe4d89e2와 일치 |
| 동봉 SHA256.json | 나열된 18개 파일 모두 일치 |
| 동료 PEX / Doro NIF / 헬멧 NIF | 보고서의 세 해시 모두 일치 |
| ESP 헤더 | flags=0, Full ESP. TES4 포함 43개 레코드 |
| 통합 의상 | 0840~0846의 ARMO/ARMA/KYWD/COBJ가 단일 ESP 안에 존재 |
| 헬멧 슬롯 | ARMO 0840, ARMA 0841 모두 BOD2=1, slot 30만 사용 |
| Race 높이 / 크기 | 남녀 약 0.42 / Small |
| NPC 높이 / 배치 scale | 1.0 / 1.0 |
| 공격 데이터 | ATKD 20, ATKE 20. 이벤트 이름은 바닐라와 동일 |
| 템플릿 | TPLT=A0F33, TPTA의 Default Package List 및 Attack Data 슬롯=A0F33, flags=0x0C00 |
| Attack Race / 패키지 목록 | ATKR=A0F2F, ECOR=4223F, DPLT=22B33 |
| 전투 스타일 | ZNAM=B3D84, 바닐라 csYaoGuai |
| NPC Disable Combat | 설정되지 않음 |
| GitHub 소스 | e6b308bfa41f30d4f9b0bcb20975f0952728c732의 PSC와 줄바꿈 정규화 후 일치 |
| GitHub Actions | run 34188891075: completed / success, 해당 커밋과 일치 |
| 로컬 컴파일 | 제공 DoroCompanionScript.psc를 Papyrus Compiler 2.8.0.4로 컴파일 성공 |

동봉 PEX와 로컬 재컴파일 PEX는 바이트가 동일하지 않다. 컴파일 환경·옵션·메타데이터까지 동일하게 재현하거나 PEX 명령을 역분석한 검증은 하지 않았다. 컴파일 성공과 해시 일치를 게임 동작 보증으로 해석하면 안 된다.

[확인한 Actions 실행](https://github.com/munument1/Fallout4-Doro-Companion/actions/runs/34188891075)

## 충돌 문제: 실제 발견한 구조

사용자가 추출해 둔 YaoGuai/CharacterAssets/skeleton.nif는 로컬 Fallout4 - Meshes.ba2의 동일 파일과 바이트 단위로 일치했다. SHA-256은 d3ba508c40a9ed4e74762945888592c77187db5b5d3797248ab567f897f65401이다.

이 파일에는 다음 연결이 있다. 블록 번호는 이 파일에 한정된다.

| 블록 | 내용 | 연결 |
|---|---|---|
| 2 | BSBound, 이름 BBX | Center=(0,0,35.888), Dimensions=(51.637,80.945,70.778) |
| 149 | NiNode CharacterBumper | Collision Object → 150, Translation Y≈74.352, Scale=1 |
| 150 | bhkNPCollisionObject | Target=149, Data=151, Body ID=0 |
| 151 | bhkPhysicsSystem | Havok 2014 바이너리, hknpPhysicsSystemData 및 hknpCapsuleShape 클래스 문자열 포함 |
| 152 | NiNode CharacterController | Collision Object → 153, Translation=(0,0,0), Scale=1 |
| 153 | bhkNPCollisionObject | Target=152, Data=151, Body ID=1 |

즉 **BSBound 외에도 bumper와 controller가 공유하는 물리 시스템의 두 body를 조사할 근거가 있다.** 반면 Doro.nif에는 NiNode·렌더링 메시·스킨·셰이더 블록만 있고 BSBound/bhkPhysicsSystem/bhkNPCollisionObject는 없다. 제공 ZIP에도 커스텀 skeleton.nif는 없다.

FO4의 해당 데이터는 NIF 최상위의 독립 bhkCapsuleShape 블록이 아니다. `bhkPhysicsSystem > Binary Data` 안의 Havok 데이터다. 구형 게임의 bhkCapsuleShape 필드를 NifSkope에서 찾아 숫자만 바꾸는 절차를 그대로 적용할 수 없다. [Niftools의 FO4 스키마](https://raw.githubusercontent.com/niftools/nifxml/develop/nif.xml)

런타임 클래스에도 collisionBound, bumperCollisionBound, shapes, scale, radius, height가 별도로 정의되어 있다. 이는 외형 높이 한 값만으로 모든 충돌 정보를 설명하기 어렵다는 근거지만, 어느 파일 값이 최종 반지름보다 우선하는지까지 보여 주는 초기화 구현은 아니다. [CommonLibF4 bhkCharacterController](https://raw.githubusercontent.com/libxse/commonlibf4/main/include/RE/B/bhkCharacterController.h)

따라서 현 단계에서 특정 캡슐 반지름·끝점·body transform의 수정 값을 제시하면 추정이다. Binary Data 안의 body/shape를 올바르게 역직렬화하고, 게임에서 실제 로드되는 skeleton의 경로와 충돌 치수를 확인하는 단계가 남았다. 골격 전체를 일괄 축소하면 스킨 바인딩·애니메이션 이동·래그돌까지 바뀌므로 별도 검증 없이 진행하지 않는 편이 타당하다.

## 보고서에서 바로잡을 부분

### 1. AttemptAnimationSetSwitch는 test14에서 이미 호출한다

DoCommand(50)은 다음 순서다.

```text
AttemptAnimationSetSwitch()
Utility.Wait(0.1)
PlayIdle(YaoGuai_IdleLookAround)
```

따라서 사용자 보고의 idle 성공은 이 호출이 포함된 검사 결과다. 호출하지 않은 대조군은 없고, 이를 한 번 더 넣는 것만으로 새로운 원인 검사가 되지는 않는다. Setup 시점 호출과 호출 전후의 전투 비교는 별도 실험이다. 로컬 Actor.psc 설명도 이 함수가 애니메이션 세트 전환을 시도한다고 할 뿐, 커스텀 Race의 공격을 반드시 활성화하는 함수라고 하지는 않는다.

### 2. Idle 성공은 공격 graph 전체 정상의 증거가 아니다

00027075가 실제 YaoGuai_IdleLookAround인 것은 확인했다. 사용자가 실제 모션을 보았다는 결과를 받아들이면 일부 애니메이션 재생 경로가 정상이라는 판단은 타당하다. 하지만 공격 이벤트 수신, 전투 상태 전이, 공격 선택 조건, 타격 이벤트까지 정상이라는 뜻은 아니다.

PlaySubGraphAnimation이 subgraph에 이벤트를 보내는 함수라는 점도 로컬 Actor.psc와 일치한다. 그 실패만으로 주 graph 불량을 단정하지 않은 보고서의 수정은 타당하다.

### 3. 커스텀 Race에서 공격 graph 데이터가 빠졌다는 증거는 현재 없다

test14 DoroRace와 바닐라 YaoGuaiRace의 순서별 전체 subrecord 비교에서 차이는 EDID/FULL/DESC/WNAM, DATA, ATKD 피해 배율에 한정됐다. 골격·behavior 경로, subgraph 및 ATKE 데이터는 동일하다.

Race DATA는 높이와 Size 외에 Can't Open Doors 해제 및 Allow PC Dialogue 설정이 바뀌어 있다. Flags2는 0x00404280으로 원본과 같다. 패키지에 데이터가 누락됐다는 주장과, 동일한 데이터라도 런타임 Race ID에 따른 조건이 다르게 동작한다는 가설은 구분해야 한다.

### 4. 바닐라 Race로 바꾸는 실험은 높이까지 동시에 바뀐다

DoroRace 높이는 0.42지만 바닐라 Race는 약 1.0이다. NPC RNAM만 바꿔서 공격이 되더라도 Race ID 때문인지 크기·거리 조건 때문인지 분리되지 않는다. 그 결과만으로 custom Race 자체가 원인이라고 단정할 수 없다.

또한 NPC에 전용 skeleton 경로를 지정하는 필드는 이번 구조에서 쓰이지 않는다. vanilla Race를 유지하면서 그 Race의 skeleton 경로를 전역 수정하면 다른 야오과이도 영향을 받을 수 있다. 외형 WNAM 교체만으로 전용 controller skeleton을 선택할 수 있다고 전제하면 안 된다.

### 5. 전투 스크립트의 개입이 완전히 없어지지는 않았다

- RetaliateAgainst는 현재 같은 적과 싸우는지 검사하지 않고 매 OnHit마다 StartCombat(target,true)를 호출한다.
- Setup은 전투 여부와 무관하게 FollowerFollow/Wait 및 EvaluatePackage(false)를 호출할 수 있다.
- OnCombatStateChanged는 상태 2(searching)도 검사하고, IsFriendlyTarget(None)이 true이므로 대상 없는 알림도 StopCombat 조건에 들어간다. 실제 해당 이벤트가 None을 전달했는지는 로그가 없어 미확인이다.
- OnTimer의 전투 중 조기 return은 정상 전투 때 주기적인 추적 패키지 재평가를 줄인 것이 맞다.

따라서 예전 StartCombat→EvaluatePackage(true) 반복은 제거됐지만, 스크립트 간섭을 완전히 배제했다고 말하기는 이르다. 위 항목들은 확인된 코드 경로이며 공격 불능의 확정 원인은 아니다.

### 6. 공격 피해 배율이 실제로 적용되는지도 별도 문제다

DoroRace ATKD 피해 배율은 낮아져 있지만 NPC가 Attack Data를 바닐라 템플릿에서 상속하고 ATKR도 YaoGuaiRace를 가리킨다. 이 상태에서는 DoroRace의 낮춘 배율이 실제 선택되는지 별도 확인해야 한다. UnarmedDamage는 100으로 0이 아니다. 단순 공격 데이터 부재·비무장 피해 0으로 설명되지는 않는다.

## Katyusha와 아군 보호 검증

데스크톱의 YaoGuaiCompanionKatyushka.esl도 직접 읽었다. YCKatyushaCompanion의 TPLT/TPTA/ATKR/ECOR/DPLT, 전체 AIDT 바이트, ZNAM 전투 스타일이 보고서 주장과 일치한다. Follow/Wait/Home PKDT도 test14와 각각 동일하다. 단, 두 NPC의 모든 플래그·능력치·키워드·스크립트가 같지는 않으므로 이것만으로 전체 동작 동등성을 보장하지 않는다.

보호 코드가 쓰는 PlayerFaction, WorkshopNPCFaction, PlayerAllyFaction, PlayerFriendFaction, MinutemenFaction Form ID는 모두 정확하다. 다만 이것은 스크립트의 대상 거르기와 전투 중지이지 모든 아군에 대한 엔진 수준의 공격 금지 규칙은 아니다. 피해 이벤트, 광역 타격, 세력 상태와 실제 발동 여부까지 테스트가 필요하다.

## 다음 진단 순서 제안 — 이번에는 실행하지 않음

1. 같은 셀·같은 적·같은 모드 로드 순서에서 새 진단용 actor들을 비교한다. 기존 세이브의 actor를 수정했는지, 새로 생성한 actor인지 각 결과에 명시한다. 세이브를 삭제할 필요는 없다.
2. DoroRace 1.0과 vanilla YaoGuaiRace 1.0을 동일한 Doro 스킨/NPC 설정으로 비교한다. 다음으로 DoroRace 1.0과 0.42를 비교해 Race ID와 크기 변수를 분리한다.
3. 스크립트의 자동 전투 개입을 끈 진단용 actor에서 한 번만 동일 적에게 전투를 시작시켜, 반복 StartCombat·friendly guard·패키지 재평가 영향을 분리한다.
4. 충돌 검사는 위의 CharacterController/CharacterBumper와 공유 physics body 0/1을 중심으로 진행한다. BSBound만 바꾼 결과와 physics 도형을 바꾼 결과를 분리한다. 실제 적용 반경과 문 통과를 수치·영상으로 기록한다.
5. 직접 공격 검사는 확인된 ATKE 이벤트(예: meleeStart_1)를 출발점으로, 바닐라 actor와 Doro에 같은 타깃·상태에서 동일 이벤트를 보낸다. 실패가 잘못된 호출 경로 때문인지 먼저 바닐라 대조군으로 검증한다. ATKE 이벤트가 존재한다는 이유만으로 PlayIdle용 공격 IDLE FormID가 있다고 가정하지 않는다. 이번 조사에서는 검증된 공격 IDLE FormID를 확보하지 못했다.

현재로서는 **충돌 물리 연결을 조사할 근거는 강해졌지만, 그것을 수정하면 공격도 해결된다고 보장할 수 없다**는 결론이다.

## 검증 산출물

- `tools/verify_test14.py`: 파일을 수정하지 않는 레코드/NIF 검증 도구
- `build/test14_verification.json`: 전체 비교 결과와 블록 목록 (로컬 전용)
- `build/test14_compile_check/`: 별도 폴더의 재컴파일 결과 (로컬 전용)

기존 0.2.4 제작 소스는 test14로 덮어쓰지 않았다. 원래 작업 저장소 Fallout-Doro-Companion과 보고서의 새 저장소 Fallout4-Doro-Companion도 구분했으며, 이번 검증 결과를 원격에 push하지 않았다.
