# Fallout Doro Companion

현재 배포판은 **0.2.6**입니다. [다운로드](https://github.com/munument1/Fallout4-Doro-Companion/releases/tag/v0.2.6) · [설치 설명](docs/RELEASE_026_FINAL_KO.md)

레드 로켓 주유소의 도로롱 독립 동료입니다. 도로롱을 활성화하면 동행·대기·물건 보관·귀환을 선택할 수 있고 도그밋 및 기존 동료를 강제로 해산시키지 않습니다.

- 도로롱 전용 스켈레톤과 축소한 이동 충돌
- 공격이 작동한 test17의 전투 설정 유지
- 시험 메뉴와 진단 로그 제거
- 플레이어 레벨 1배 연동, 최대 65535
- 기존 머리 탈/의상과 무료 화학작업대 제작 자산 유지
- **DoroFollower.esp 하나만 활성화하는 Full ESP 배포판**

0.2.6의 게임 파일은 RC2와 동일합니다. RC1의 도그밋 피해 조정은 공격 회귀로 취소했습니다. [RC2 변경 기록](docs/RELEASE_026_RC2_NOTES.md)

## 소스와 빌드

최종 빌드는 `build_release_026_rc2.py --prepare` → Papyrus 컴파일(`build/release026_rc2_compile`) → `build_release_026_rc2.py --package` → `package_release_026.py` 순서입니다. 입력은 로컬 test17 패키지입니다.

전용 스켈레톤 생성 과정은 `tools/build_test17.py`, 구조 검증은 `tools/verify_test14.py`에 있습니다. 상세 전투/충돌 비교는 [test17 기록](docs/TEST17_CHANGELOG_KO.md)을 참고하세요.

이전 `build_doro_plugin.py`, `package_current.py` 등의 0.2.5 생성 경로는 역사적 테스트 도구이며 **최신 정식 배포판을 재현하지 않습니다**. 초기 ESP-FE 설정과 현재 Full ESP 설정을 혼동하지 마세요.

Git에는 제작 소스와 문서만 저장합니다. 게임에 설치할 패키지는 Releases 첨부 파일로 배포합니다. 추출 자산, 참고 모드, 외부 라이브러리와 Blender 파일은 Git에 포함하지 않으므로 저장소만으로 완전한 모드를 빌드할 수 없습니다.

Windows, Blender/PyNifly, Fallout 4 Creation Kit Papyrus 컴파일러를 사용합니다. 로컬 절대 경로 및 `tools/deps` 의존성이 필요합니다. 기존 개발 기록과 제작 도구는 보존했습니다.
