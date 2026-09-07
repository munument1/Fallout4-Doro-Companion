# 개발 체크포인트 — 2026-09-07

## 현재 단계

0.2.4 게임 테스트에서 다음 두 문제가 확인되었습니다.

- 도로롱 활성화 상호작용은 뜨지만 대화가 시작되지 않음.
- 화학작업대에 도로롱 머리 탈/도그밋 의상 제작 카테고리가 나타나지 않음.

이를 기준으로 **0.2.5 런타임 수정 소스**를 준비했습니다. 아직 실제 게임 재검증 전이므로 수정 완료로 간주하지 않습니다.

## 0.2.5에서 수정한 내용

### 대화

1. `DoroDialogueQuest`의 QUST DNAM 플래그를 `0x0119`에서 `0x8119`로 변경했습니다.
   - Fallout 4에서 `0x8000`은 `HasDialogueData`이며 대화 데이터를 소유하는 퀘스트에 필요합니다.
   - 이전 Gorilla 구조 이식 과정에서 이 비트가 빠져 있었습니다.
2. 액터 활성화 시 먼저 바닐라 Greeting 처리를 시도하고, 0.15초 뒤에도 대화에 들어가지 못하면 `DoroMainDialogueScene.Start()`를 호출하는 fallback을 추가했습니다.
3. 타이머에서 `dialogueScene == None`일 때 `IsPlaying()`을 호출하지 않도록 방어했습니다.
4. 퀘스트 alias 0은 기존처럼 런타임에서 Doro 본인에게 `ForceRefTo(Self)`로 바인딩합니다.

주요 로컬 Form ID:

- NPC `00000803`
- 배치 참조 `0000080B`
- 대화 퀘스트 `0000080C`
- 씬 `0000080D`
- 인사 토픽 `00000828`
- 인사 INFO `00000829`
- 대화 대기 패키지 `0000082A`
- 음성 유형 `0000082B`

실제 콘솔 Form ID에는 로드 순서 접두사가 필요합니다.

퀘스트 단계:

- 10 영입
- 20 대기
- 30 거래
- 40 해산

### 화학작업대 제작

0.2.4 조사에서는 `DoroCostumes.esp`가 실제 MO2 설치/활성 목록에 없었던 것이 먼저 확인되었습니다. 또한 기존 커스텀 카테고리 donor가 Recipe Filter 타입임을 보장하지 못했습니다.

0.2.5에서는 다음과 같이 변경했습니다.

1. 커스텀 `DoroRecipeCategory "DORO"` KYWD는 바닐라 `RecipeUtility [KYWD:0006980C]`를 복제합니다.
   - 따라서 donor의 `TNAM` Recipe Filter 타입을 그대로 유지합니다.
2. COBJ의 `BNAM`은 계속 `WorkbenchChemlab [KYWD:00102158]`를 사용합니다.
3. COBJ의 `FNAM`은 새 `DoroRecipeCategory`를 참조합니다.
4. 빌드 검증에서 새 카테고리의 `TNAM`이 donor와 동일한지 확인합니다.
5. `tools/package_current.py`를 추가하여 최신 테스트 ZIP에 `DoroFollower.esp`와 `DoroCostumes.esp`를 함께 넣습니다.

## 최신 통합 패키징

로컬 빌드 자산이 모두 생성된 뒤 다음 스크립트를 사용합니다.

`tools/package_current.py`

출력:

`build/Doro_FO4_test_0.2.5_combined.zip`

이 ZIP에는 최소한 다음이 함께 들어가야 합니다.

- `DoroFollower.esp`
- `DoroCostumes.esp`
- `Scripts/DoroCompanionScript.pex`
- `Scripts/DoroDialogueQuestScript.pex`
- 도로롱 동료 NIF/재질/텍스처/음성
- 도로롱 머리 탈 NIF
- 도그밋 도로롱 의상 NIF

`tools/package_v02.py`는 0.2용 옛 패키징 스크립트이므로 최신 테스트본 생성에 사용하지 않습니다.

## 다음 실제 게임 확인 순서

1. 수정된 Papyrus 두 개를 Creation Kit 컴파일러로 다시 컴파일합니다.
2. `build_doro_plugin.py`와 `build_costume_plugin.py`를 다시 실행합니다.
3. `package_current.py`로 0.2.5 통합 ZIP을 만듭니다.
4. MO2에서 0.2.3/0.2.4 같은 이전 도로롱 패키지를 비활성화하고 0.2.5 통합 패키지만 우선 테스트합니다.
5. Plugins에서 `DoroFollower.esp`와 `DoroCostumes.esp`가 둘 다 활성화되었는지 확인합니다.
6. 레드 로켓에서 도로롱을 활성화해 4방향 대화 선택지가 나타나는지 확인합니다.
7. `Follow me` 선택 후 플레이어를 따라오는지 확인합니다.
8. 화학작업대에서 `DORO` 카테고리가 나타나는지 확인하고 머리 탈/도그밋 의상을 제작합니다.
9. 문제가 남으면 xEdit `Check for Errors`와 Papyrus 로그로 QUST alias/SCEN/Greeting INFO 문제를 분리합니다.

## 아직 확인되지 않은 항목

- 실제 게임에서 0.2.5 대화가 정상 시작되는지
- 대화 선택 후 stage 이벤트가 `DoroDialogueQuestScript`에 전달되는지
- 영입 후 다른 바닐라 동료/도그밋과 동시에 동행 가능한지
- 화학작업대의 `DORO` 카테고리와 두 COBJ가 실제 UI에 노출되는지
- 도그밋 의상 실제 착용 상태
- 전투 지원, 대기, 거래, 해산
- 실제 게임 달리기에서 모델 이음새/변형

## 유지할 사용자 결정

- 소환 수류탄 DOROball 방식은 취소.
- 입을 벌리는 변경은 취소. 원본 닫힌 입 유지.
- 플레이어 의상은 전신이 아닌 머리 탈.
- 도그밋 의상은 이미 만든 테스트 자산까지만 우선 확인하고, 동료/머리 탈 안정화를 먼저 진행.
- 세이브 초기화나 삭제를 해결책으로 단정하지 않음.

## 재현성 제한

공개 저장소에는 Fallout 4 원본 파일, 추출 레코드, 외부 모드 자산, 변환된 NIF/텍스처/음성, Blender 작업 파일, 컴파일된 PEX 및 로컬 빌드 산출물이 포함되지 않습니다. 따라서 이 저장소만으로 여기서 실제 ESP/PEX/통합 ZIP을 다시 빌드하거나 게임 런타임을 검증할 수는 없습니다.
